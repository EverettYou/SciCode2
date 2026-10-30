"""Batch runner: builds the job list for a named plan and runs the jobs with a
bounded number of concurrent subprocesses. Skips jobs whose output JSON exists.

Usage: python code/batch.py <plan> [--max_jobs 15] [--threads 4] [--dry]
Plans: halfcut_L4, quartercut_L4, grid_L4, half_L6, quarter_L6, ...
"""
from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
import queue

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, ".venv", "bin", "python")
BC = {4: {0.125: "pa", 0.25: "aa", 0.375: "pa", 0.5: "pa", 0.625: "pa", 0.75: "aa", 0.875: "pa"},
      6: {0.25: "pp", 0.5: "pa", 0.75: "pp"},
      8: {0.25: "pa", 0.5: "aa"}}


def sector_jobs(L, nu, J, sectors=("gs_fl", "gs_sg", "sz1_0", "sz1_pp", "p2", "m2", "p1", "m1"),
                n_iter=300, n_samples=2048, n_hidden=16, n_final_gs=8192, n_final_gap=16384, tag="",
                measure="spin,nk,pair,local,dens", n_iter_gap=None, gap_init="bcs", extra=()):
    nc = L * L
    n = int(round(2 * nu * nc))  # electrons per layer
    bc = BC[L][nu]
    delta0 = str(max(0.25, 0.5 * J))
    jobs = []
    pref = f"L{L}_{bc}_nu{nu:.3f}_J{J:.2f}{tag}"
    for s in sectors:
        out = os.path.join(ROOT, "data", f"{pref}_{s}")
        is_gap = not s.startswith("gs")
        ni = n_iter_gap if (is_gap and n_iter_gap) else n_iter
        base = ["--Lx", str(L), "--Ly", str(L), "--bc", bc, "--J", str(J), "--n_iter", str(ni),
                "--n_samples", str(n_samples), "--n_hidden", str(n_hidden), "--momentum", "0.8",
                "--n_chains", "64"]

        if s == "gs_fl":
            args = ["--N1", str(n), "--N2", str(n), "--Nup", str(n), "--Ndn", str(n), "--init", "fl",
                    "--n_final", str(n_final_gs), "--measure", measure]
        elif s == "gs_sg":
            args = ["--N1", str(n), "--N2", str(n), "--Nup", str(n), "--Ndn", str(n), "--init", "singlet",
                    "--n_final", str(n_final_gs), "--measure", measure]
        elif s == "gs_bcs":
            args = ["--N1", str(n), "--N2", str(n), "--Nup", str(n), "--Ndn", str(n), "--init", "bcs",
                    "--delta0", delta0, "--n_final", str(n_final_gs), "--measure", measure]
        elif s == "sz1_0":
            args = ["--N1", str(n), "--N2", str(n), "--Nup", str(n + 1), "--Ndn", str(n - 1), "--init", "bcs",
                    "--delta0", delta0, "--triplet", "--qx", "0", "--qy", "0", "--n_final", str(n_final_gap), "--measure", ""]
        elif s == "sz1_pp":
            args = ["--N1", str(n), "--N2", str(n), "--Nup", str(n + 1), "--Ndn", str(n - 1), "--init", "bcs",
                    "--delta0", delta0, "--triplet", "--qx", "1", "--qy", "1", "--n_final", str(n_final_gap), "--measure", ""]
        elif s == "sz1_trip":
            args = ["--N1", str(n), "--N2", str(n), "--Nup", str(n + 1), "--Ndn", str(n - 1), "--init", "bcs",
                    "--delta0", delta0, "--triplet", "--qx", "1", "--qy", "1", "--g0", "1.0", "--u_scale", "0.1",
                    "--n_final", str(n_final_gap), "--measure", ""]
        elif s == "sz1_p0":
            args = ["--N1", str(n), "--N2", str(n), "--Nup", str(n + 1), "--Ndn", str(n - 1), "--init", "bcs",
                    "--delta0", delta0, "--triplet", "--qx", "1", "--qy", "0", "--n_final", str(n_final_gap), "--measure", ""]
        elif s == "p2":
            args = ["--N1", str(n + 1), "--N2", str(n + 1), "--Nup", str(n + 1), "--Ndn", str(n + 1), "--init", "bcs",
                    "--delta0", delta0, "--n_final", str(n_final_gap), "--measure", ""]
        elif s == "m2":
            args = ["--N1", str(n - 1), "--N2", str(n - 1), "--Nup", str(n - 1), "--Ndn", str(n - 1), "--init", "bcs",
                    "--delta0", delta0, "--n_final", str(n_final_gap), "--measure", ""]
        elif s == "p1":
            args = ["--N1", str(n + 1), "--N2", str(n), "--Nup", str(n + 1), "--Ndn", str(n), "--init", "bcs",
                    "--delta0", delta0, "--n_final", str(n_final_gap), "--measure", ""]
        elif s == "m1":
            args = ["--N1", str(n), "--N2", str(n - 1), "--Nup", str(n), "--Ndn", str(n - 1), "--init", "bcs",
                    "--delta0", delta0, "--n_final", str(n_final_gap), "--measure", ""]
        else:
            raise ValueError(s)
        if is_gap and gap_init == "auto":
            args = [a for a in args]  # keep; the auto init is appended last so it overrides "--init bcs"
            args += ["--init", "auto:" + os.path.join(ROOT, "data", pref)]
        jobs.append((out, base + args + list(extra) + ["--out", out]))
    return jobs


def plan_jobs(plan: str):
    jobs = []
    G = dict(n_iter_gap=150, gap_init="auto")
    if plan == "halfcut_L4":
        for J in (0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0):
            secs = ("gs_fl", "gs_sg", "sz1_0", "sz1_pp", "p2", "m2", "p1", "m1") + (("sz1_trip",) if J >= 3 else ())
            jobs += sector_jobs(4, 0.5, J, sectors=secs, n_iter_gap=200, gap_init="auto")
    elif plan == "halfcut_L4_extra":
        for J in (2.5, 3.5, 5.0):
            jobs += sector_jobs(4, 0.5, J, sectors=("gs_fl", "gs_sg", "p2", "m2", "sz1_pp", "sz1_trip"), **G)
    elif plan == "quartercut_L4":
        for J in (0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0):
            jobs += sector_jobs(4, 0.25, J, sectors=("gs_fl", "gs_sg", "p2", "m2", "p1", "m1", "sz1_pp", "sz1_trip"), **G)
    elif plan == "quartercut_L4_extra":
        for J in (2.5, 5.0):
            jobs += sector_jobs(4, 0.25, J, sectors=("gs_fl", "gs_sg", "p2", "m2", "sz1_pp"), **G)
    elif plan == "grid_L4":
        for nu in (0.375, 0.125, 0.75):
            for J in (1.0, 2.0, 4.0, 8.0):
                jobs += sector_jobs(4, nu, J, sectors=("gs_fl", "gs_sg", "p2", "m2"), n_iter=200, n_iter_gap=120, gap_init="auto")
        for nu in (0.625,):
            for J in (4.0, 8.0):
                jobs += sector_jobs(4, nu, J, sectors=("gs_fl", "gs_sg", "p2", "m2"), n_iter=200, n_iter_gap=120, gap_init="auto")
    elif plan == "grid_L4_extra":
        for nu in (0.375, 0.125, 0.75):
            for J in (6.0, 3.0):
                jobs += sector_jobs(4, nu, J, sectors=("gs_fl", "gs_sg", "p2", "m2"), n_iter=200, n_iter_gap=120, gap_init="auto")
        for nu in (0.875,):
            for J in (2.0, 8.0):
                jobs += sector_jobs(4, nu, J, sectors=("gs_fl", "gs_sg", "p2", "m2"), n_iter=200, n_iter_gap=120, gap_init="auto")
    elif plan == "half_L6":
        for J in (4.0, 6.0):
            jobs += sector_jobs(6, 0.5, J, sectors=("gs_bcs", "gs_fl", "p2", "m2"), n_iter=120, n_samples=1024,
                                n_final_gs=2048, n_final_gap=4096, measure="spin_lite,nk_lite,pair,local,dens",
                                n_iter_gap=80, gap_init="auto", extra=("--no_ntk",))
    elif plan == "L6_J4gaps":
        jobs += sector_jobs(6, 0.5, 4.0, sectors=("p2", "m2"), n_iter=120, n_samples=1024, n_final_gs=2048, n_final_gap=4096,
                            measure="spin_lite,nk_lite,pair,local,dens", n_iter_gap=80, gap_init="auto", extra=("--no_ntk",))
    elif plan == "L6_J6":
        jobs += sector_jobs(6, 0.5, 6.0, sectors=("gs_bcs", "p2", "m2"), n_iter=120, n_samples=1024, n_final_gs=2048, n_final_gap=4096,
                            measure="spin_lite,nk_lite,pair,local,dens", n_iter_gap=80, gap_init="auto", extra=("--no_ntk",))
    elif plan == "half_L6_extra":
        for J in (3.0,):
            jobs += sector_jobs(6, 0.5, J, sectors=("gs_bcs", "gs_fl", "p2", "m2"), n_iter=120, n_samples=1024,
                                n_final_gs=2048, n_final_gap=4096, measure="spin_lite,nk_lite,pair,local,dens",
                                n_iter_gap=80, gap_init="auto", extra=("--no_ntk",))
    elif plan == "quarter_L6":
        for J in (6.0,):
            jobs += sector_jobs(6, 0.25, J, sectors=("gs_bcs", "gs_fl", "p2", "m2"), n_iter=120, n_samples=1024,
                                n_final_gs=2048, n_final_gap=4096, measure="spin_lite,nk_lite,pair,local,dens",
                                n_iter_gap=80, gap_init="auto", extra=("--no_ntk",))
    else:
        raise ValueError(plan)
    gs = [j for j in jobs if "_gs_" in os.path.basename(j[0])]
    rest = [j for j in jobs if "_gs_" not in os.path.basename(j[0])]
    return gs + rest


SLOTS = None


def run_job(job, threads):
    out, args = job
    if os.path.exists(out + ".json"):
        return out, "skip"
    slot = SLOTS.get() if SLOTS is not None else None
    try:
        return _run_job(job, threads, slot)
    finally:
        if SLOTS is not None:
            SLOTS.put(slot)


def _run_job(job, threads, slot):
    out, args = job
    env = dict(os.environ)
    env["XLA_FLAGS"] = f"--xla_cpu_multi_thread_eigen=false intra_op_parallelism_threads={threads}"
    env["OMP_NUM_THREADS"] = str(threads)
    env["JAX_PLATFORMS"] = "cpu"
    log = os.path.join(ROOT, "logs", os.path.basename(out) + ".log")
    t0 = time.time()
    # reruns after a failed quality check: new seed, weaker momentum, longer optimization
    n_bad = len(glob.glob(out + ".bad*.json"))
    if n_bad > 0:
        args = args + ["--seed", str(1 + n_bad), "--momentum", "0.5"]
    pre = []
    if slot is not None:
        c0 = slot * threads
        pre = ["taskset", "-c", f"{c0}-{c0 + threads - 1}"]
    with open(log, "w") as f:
        r = subprocess.run(pre + [PY, os.path.join(ROOT, "code", "run_point.py")] + args, stdout=f, stderr=subprocess.STDOUT, env=env)
    return out, f"rc={r.returncode} {time.time()-t0:.0f}s"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("plan")
    p.add_argument("--max_jobs", type=int, default=15)
    p.add_argument("--threads", type=int, default=4)
    p.add_argument("--dry", action="store_true")
    p.add_argument("--slot0", type=int, default=0, help="first core slot (each slot = threads cores)")
    a = p.parse_args()
    global SLOTS
    SLOTS = queue.Queue()
    for s in range(a.slot0, a.slot0 + a.max_jobs):
        SLOTS.put(s)
    jobs = plan_jobs(a.plan)
    todo = [j for j in jobs if not os.path.exists(j[0] + ".json")]
    print(f"plan {a.plan}: {len(jobs)} jobs, {len(todo)} to run", flush=True)
    if a.dry:
        for j in todo:
            print(os.path.basename(j[0]))
        return
    with ThreadPoolExecutor(max_workers=a.max_jobs) as ex:
        for out, status in ex.map(lambda j: run_job(j, a.threads), todo):
            print(f"{time.strftime('%H:%M:%S')} {os.path.basename(out)}: {status}", flush=True)


if __name__ == "__main__":
    main()
