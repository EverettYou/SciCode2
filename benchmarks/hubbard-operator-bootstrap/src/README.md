# Stable Hubbard bootstrap implementation

The primary portable solution reconstructs a **2257-dimensional operator space**, solves its reduced anticommutator relaxation, independently checks every physical affine map, verifies an exact dyadic SOS certificate, and proves the operator count. It needs only this src/ directory and the locked Python environment. No laboratory module, discovery cache, or absolute source path is loaded.

## Reproduce the complete selected-space result

From the benchmark root:

```sh
uv sync --frozen
uv run --frozen python src/reproduce.py --out /tmp/hubbard-reproduction
```

The completed reference run is preserved under `labs/lab-004-exact-dual-verification/results/portable-reproduction/`. It certifies **E0 >= -8.763353354793**. Construction, solve, export, independent physical audit, exact certificate arithmetic, and operator-rank proof took **22.953 seconds total**, including Python startup for every stage. The largest stage process peak was **404.5 MB**. Construction took 0.835 s, solver call 11.277 s, and factor/map export 0.234 s. Earlier pilot timings remain in the lab history; timings and process peaks can vary.

`reproduction.json` records stage wall times, exact result, process peaks, and input hashes. Logs and all exported proof data remain in the selected output directory. The physical audit, exact certificate, and rank proof are separate stages. Discovery of the operators is charged separately below; this command reuses the explicitly supplied operator definition.

## Operators and proof inputs

`input/source_blocks.json` defines six momentum-sector raw cubic bases and exact integer projection matrices in `input/*.npz`. Their sixteen selected cubic directions, all D4/spin images, and adjoints supplement the 2081-dimensional quadratic core. Exact closure/rank gives 88 net+1 cubic directions and 88 adjoints, hence dimension 2257 before further fixed-input-sector identities. The new reduced blocks have dimensions 4,4,4,4,3,3; the whole program has 331 variables, 54 cones, maximum 32, and 11446 full matrix entries.

`compact_replay.py` reconstructs the affine maps from CAR, using integer operations and exact 2^-40 scaling with overflow guards. `audit_physics.py` uses a separate exterior-product CAR algorithm and enumerates the physical bases independently. `verify_exact.py` reconstructs the exact Hubbard objective and uses exact Gram factors/residual correction. `distill_operator_space.py` proves closure/span ranks with rational relations and matching modular lower bounds. The solved anticommutator SDP need not equal the complete literal cubic Gram SDP; its verified dual squares lie in the declared space and certify the bound requested in the problem.

## Reproduce the discovery comparison

```sh
uv run --frozen python src/reproduce.py --full --out /tmp/hubbard-full-reproduction
```

This constructs, solves, exports, physically audits, and exactly verifies the full T2prime anticommutator model, with 33825 ambient operators, 244 cones, maximum 233, and 410274 matrix entries. It can take several minutes. The original discovery observation was 50.88 s construction and 511.52 s solving, with 266 MB process peak; original export duration was not separately measured. The fresh full-pipeline reproduction records the previously missing export/total durations. `input/selection_summary.json` preserves the original discovery and selection observations. The lab002 scripts preserve the eigenvector-selection procedure and failed alternatives.

## Individual commands and comparisons

```sh
uv run --frozen python src/compact_replay.py --out /tmp/hubbard-selected
uv run --frozen python src/audit_physics.py /tmp/hubbard-selected /tmp/hubbard-physical.json --operator-input src/input
uv run --frozen python src/verify_exact.py /tmp/hubbard-selected /tmp/hubbard-exact
uv run --frozen python src/distill_operator_space.py src/input /tmp/hubbard-exact /tmp/hubbard-operators
uv run --frozen python src/momentum_pqg.py --out /tmp/hubbard-pqg --eps 1e-6
uv run --frozen python src/run_compact.py --out /tmp/hubbard-two-site --solver CLARABEL --eps 1e-8 --max-iters 100
```

Use `run_full.py` directly for optional T1, mixed-spin, or theorem-backed singlet comparisons. The singlet option changes the source's original fixed-N relaxation and must be reported separately; its physical audit requires `--allow-singlet`. `refine_dual.py` fits equality multipliers while holding the Gram factors fixed and then reruns exact certification.

All energies are total energies for 32 distinct nearest-neighbor bonds, t=1, U=8, Nup=Ndown=8. The source specifies no public target or memory ceiling. Global outer-search optimality and exact ground energy are not claimed.

The completed full-model replay is recorded in `labs/lab-004-exact-dual-verification/results/full-reproduction/reproduction.json`: 5.666 s construction, 183.911 s solving, 0.763 s export, and 198.865 s summed successful stages including startup, physical audit and exact certificate. Its largest process peak was 388.2 MB. The first audit found a missing operator-kind metadata field; after correcting that descriptor, the successful solver output was reused and auditing resumed. The 2.858 s failed audit and manual restart gap are recorded separately. SCS and Clarabel use different algorithms and tolerances; the exact matrix/operator counts provide the direct structural comparison.
