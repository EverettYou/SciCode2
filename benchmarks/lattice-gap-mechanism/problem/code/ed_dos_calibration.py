"""Calibrate the half-filled single-particle spectrum on the 3x3 cluster data.

Reads reference/data/ed_3x3_path.json (N = 18 electrons on 3x3 rungs, periodic,
antiperiodic-periodic and antiperiodic-antiperiodic twists, t1 = 1, t2 = 0.2,
J = 8) and writes author/ed_dos_calibration.json.

Differences from reference/code/analyze_ed.py: poles that appear twice in the
cluster lists (momenta whose symmetry images were summed with half weight)
are merged before the dominant pole is chosen, so the coherent weight is the
full quasiparticle residue and the remainder is the genuinely incoherent
weight, which sits several D beyond the coherent band.  The incoherent
weight is described by its weighted centroid offset and spread per branch.

Also recomputes Re G(k, 0) at the gap midpoint from the calibrated model and
from the exact cluster pole sums, and the fraction of the zone on the (0,0)
side of the zero contour, for the item-5 key.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "reference" / "data" / "ed_3x3_path.json"
OUT = ROOT / "author" / "ed_dos_calibration.json"
T1, T2 = 1.0, 0.2


def eps(kx, ky):
    return -2 * T1 * (np.cos(kx) + np.cos(ky)) - 4 * T2 * np.cos(kx) * np.cos(ky)


def basis(kx, ky, n=4):
    kx = np.asarray(kx, float)
    ky = np.asarray(ky, float)
    cols = [
        np.ones_like(kx),
        np.cos(kx) + np.cos(ky),
        np.cos(kx) * np.cos(ky),
        np.cos(2 * kx) + np.cos(2 * ky),
    ]
    return np.stack(cols[:n], -1)


def fit(kx, ky, y, n=4):
    X = basis(kx, ky, n)
    coef, *_ = np.linalg.lstsq(X, np.asarray(y, float), rcond=None)
    rms = float(np.sqrt(np.mean((X @ coef - y) ** 2)))
    return coef.tolist(), rms


def ev(coef, kx, ky):
    coef = np.asarray(coef, float)
    return basis(kx, ky, len(coef)) @ coef


def merge(poles, weights, tol=1e-6):
    order = np.argsort(poles)
    p = np.asarray(poles, float)[order]
    w = np.asarray(weights, float)[order]
    mp, mw = [], []
    for pi, wi in zip(p, w):
        if mp and abs(pi - mp[-1]) < tol:
            mw[-1] += wi
        else:
            mp.append(pi)
            mw.append(wi)
    return np.array(mp), np.array(mw)


def split(poles, weights):
    p, w = merge(poles, weights)
    i = int(np.argmax(w))
    rest = np.delete(np.arange(len(p)), i)
    w_inc = float(w[rest].sum())
    if w_inc > 1e-9:
        cen = float((p[rest] * w[rest]).sum() / w_inc)
        spread = float(np.sqrt(((p[rest] - cen) ** 2 * w[rest]).sum() / w_inc))
    else:
        cen, spread = float("nan"), float("nan")
    return dict(E=float(p[i]), w=float(w[i]), w_inc=w_inc, E_inc=cen, s_inc=spread, total=float(w.sum()), poles=(p, w))


def main():
    d = json.load(open(SRC))
    rows = []
    for key in ("N18_pp", "N18_ap", "N18_aa"):
        for kk, v in d[key]["A"].items():
            kx, ky = map(float, kk.split(","))
            a = split(*v["add"])
            r = split(*v["rem"])
            rows.append(dict(kx=kx, ky=ky, eps=float(eps(kx, ky)), add=a, rem=r, n_k=float(v.get("n_k", r["total"])), bc=key))
    rows.sort(key=lambda r: r["eps"])
    kx = np.array([r["kx"] for r in rows])
    ky = np.array([r["ky"] for r in rows])
    fits = {}
    for name, y in (
        ("Ep", [r["add"]["E"] for r in rows]),
        ("Eh", [r["rem"]["E"] for r in rows]),
        ("wp", [r["add"]["w"] for r in rows]),
        ("wh", [r["rem"]["w"] for r in rows]),
        ("nk", [r["n_k"] for r in rows]),
    ):
        c, rms = fit(kx, ky, np.array(y))
        fits[name] = c
        fits[name + "_rms"] = rms
    n = 400
    k = (np.arange(n) + 0.5) * 2 * np.pi / n - np.pi
    KX, KY = np.meshgrid(k, k, indexing="ij")
    Ep = ev(fits["Ep"], KX, KY)
    Eh = ev(fits["Eh"], KX, KY)
    mu = 0.5 * (Ep.min() + Eh.max())

    def sat(branch):
        w = np.array([r[branch]["w_inc"] for r in rows])
        off = np.array([r[branch]["E_inc"] - r[branch]["E"] for r in rows])
        s = np.array([r[branch]["s_inc"] for r in rows])
        ok = w > 1e-3
        wsum = w[ok].sum()
        return dict(offset=float((w[ok] * off[ok]).sum() / wsum), spread=float((w[ok] * s[ok]).sum() / wsum), mean_weight=float(w.mean()))

    out = dict(
        source=str(SRC.relative_to(ROOT)),
        params=d["params"],
        nbasis=4,
        fits=fits,
        mu=float(mu),
        gap=float(Ep.min() - Eh.max()),
        Ep_range=[float(Ep.min() - mu), float(Ep.max() - mu)],
        Eh_range=[float(Eh.min() - mu), float(Eh.max() - mu)],
        sat_add=sat("add"),
        sat_rem=sat("rem"),
        points=[
            dict(
                kx=r["kx"], ky=r["ky"], eps=r["eps"], bc=r["bc"], n_k=r["n_k"],
                Ep=r["add"]["E"], wp=r["add"]["w"], wp_inc=r["add"]["w_inc"], Ep_inc=r["add"]["E_inc"], sp_inc=r["add"]["s_inc"],
                Eh=r["rem"]["E"], wh=r["rem"]["w"], wh_inc=r["rem"]["w_inc"], Eh_inc=r["rem"]["E_inc"], sh_inc=r["rem"]["s_inc"],
            )
            for r in rows
        ],
    )
    print(f"mu={mu:.4f} gap={out['gap']:.4f} add band {out['Ep_range']} rem band {out['Eh_range']}")
    for name in ("Ep", "Eh", "wp", "wh", "nk"):
        print(f"  {name}: {np.round(fits[name], 4)} rms {fits[name + '_rms']:.4f}")
    print("  sat_add", out["sat_add"], "\n  sat_rem", out["sat_rem"])
    for r in rows:
        print(
            f"  k=({r['kx']/np.pi:.2f},{r['ky']/np.pi:.2f})pi eps={r['eps']:+.1f} n_k={r['n_k']:.3f} "
            f"add {r['add']['E']:.2f} w {r['add']['w']:.3f}/{r['add']['total']:.3f} inc {r['add']['E_inc']:.2f}+-{r['add']['s_inc']:.2f} "
            f"rem {r['rem']['E']:.2f} w {r['rem']['w']:.3f}/{r['rem']['total']:.3f} inc {r['rem']['E_inc']:.2f}+-{r['rem']['s_inc']:.2f}"
        )

    # ---- Re G(k,0) at the midpoint: model and exact cluster sums ----
    wp = np.clip(ev(fits["wp"], KX, KY), 0.02, 1)
    wh = np.clip(ev(fits["wh"], KX, KY), 0.02, 1)
    nk = np.clip(ev(fits["nk"], KX, KY), 0.05, 0.95)
    wpr = np.clip(1 - nk - wp, 0, None)
    whr = np.clip(nk - wh, 0, None)
    Epm, Ehm = Ep - mu, Eh - mu
    op, oh = out["sat_add"]["offset"], out["sat_rem"]["offset"]

    def frac(G):
        s0 = np.sign(G[n // 2, n // 2])
        return float(np.mean(np.sign(G) == s0))

    lut = {}
    for dmu in (-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3):
        G = -wp / (Epm - dmu) - wh / (Ehm - dmu) - wpr / (Epm + op - dmu) - whr / (Ehm + oh - dmu)
        Gc = -wp / (Epm - dmu) - wh / (Ehm - dmu)
        lut[f"{dmu:+.1f}"] = dict(fraction_00_side=frac(G), coherent_only=frac(Gc), G_00=float(G[n // 2, n // 2]), G_pipi=float(G[0, 0]))
    exact = []
    for r in rows:
        g = 0.0
        for br in ("add", "rem"):
            p, w = r[br]["poles"]
            g += -float((w / (p - mu)).sum())
        exact.append(dict(kx=r["kx"], ky=r["ky"], eps=r["eps"], ReG0=g))
    e_ = np.array([x["eps"] for x in exact])
    g_ = np.array([x["ReG0"] for x in exact])
    cz = np.polyfit(e_, g_, 1)
    cross = -cz[1] / cz[0]
    E = eps(KX, KY)
    out["luttinger"] = dict(
        model_vs_reference_shift=lut,
        exact_points=exact,
        exact_linear_fit=dict(slope=float(cz[0]), offset=float(cz[1]), crossing_eps=float(cross), fraction_00_side=float(np.mean(E < cross))),
    )
    print("fraction on (0,0) side, model (with satellites, coherent only):", {k: (round(v["fraction_00_side"], 3), round(v["coherent_only"], 3)) for k, v in lut.items()})
    print("exact cluster Re G(k,0):", [(round(x["eps"], 1), round(x["ReG0"], 4)) for x in exact])
    print(f"exact linear fit crossing eps={cross:.3f} fraction={np.mean(E < cross):.3f}")
    json.dump(out, open(OUT, "w"), indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
