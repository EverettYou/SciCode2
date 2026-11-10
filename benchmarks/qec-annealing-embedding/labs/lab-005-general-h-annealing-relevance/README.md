# Lab005: general-H readout and annealing relevance

This is supervised continuing research, not SciCode2 difficulty calibration.
The child contribution develops thermally balanced general-H compilation,
decoder-free original-error readout evaluation, a local classical mixing
limitation, and resource-accounted classical annealing diagnostics. Parent-owned
independent penalty and quantum-forward branches are described in `REPORT.md`.

Read `RESEARCH_REPORT.md` for results and limitations, `THEORY.md` for proofs,
and the frozen protocol files for timing of methodological choices. The balanced
compiler is an analytical control with about twice the physical qubits. Its
endpoint advantage does not establish practical finite-time performance.

## Environment and inherited sources

Python and exact package versions are in `requirements.txt` and
`results/research_environment.json`. The native sampler was built using:

```sh
clang++ -O3 -std=c++17 scripts/anneal.cpp -o scripts/anneal_backend
```

The saved binary is specific to Apple arm64; rebuild it on other platforms.
The child scripts read Lab004's evaluator, allocation, auditing and generators,
and Lab002's compiler/embedding utilities, without modifying prior labs. The
parent's new-lab `independent/penalty_bound.py` supplies the verified GF2 repair
witness. Their hashes are recorded in `results/source_provenance.json`; the
child artifact manifest separately records all child sources and outputs.

## Decoder-free evaluation

From this lab directory:

```sh
python3 scripts/evaluate_readout.py --input results/input_example.json \
  --output /tmp/lab005-readout.json --scheme balanced --alpha 0.04 --beta 20
```

Input JSON contains `n`, sparse `rows`, `syndrome` and finite signed `weights`.
Duplicate row indices cancel over GF2. The evaluator checks dimensions,
syndrome membership and the sufficient `M>C` static-fidelity condition. It
constructs a repair witness and evaluates row partition bounds; it does not solve
minimum-cost decoding. Ordinary row-envelope enumeration returns inconclusive
above degree 20. Balanced row formulas have linear output-size cost.

Optional `--penalty`, `--chain-bound` and `--rounding-tv` specify the compiler
penalty and independently certified physical errors. Defaults of zero physical
errors describe the logical model only. The beta convention is reciprocal
programmed-Ising energy; for the original prompt's B/2 convention it is
`beta = beta_physical B/2` at Gamma zero. Output numbers evaluate proved formulas
in binary64; a strict numerical comparison requires outward evaluation, as in
the independent interval audit. Supplied physical bounds are not verified by
this CLI.

## Reproducing the child studies

Existing experiment files are retained. The main runner reuses completed cases;
other runners may overwrite their own outputs. Copy the lab before rerunning
if exact preservation is needed. No QPU or network connection is used.

```sh
python3 scripts/run_suite.py
python3 scripts/analyze.py
python3 scripts/audit_readout_curves.py
python3 scripts/dynamics.py
python3 scripts/prepare_relaxation.py
python3 scripts/run_anneals.py
python3 scripts/audit_anneals.py
python3 scripts/prepare_standard_relaxation.py
python3 scripts/run_anneals.py --standard
python3 scripts/audit_anneals.py --standard
python3 scripts/repair_followup.py
python3 scripts/profile_readout.py
python3 scripts/figures.py
```

The method sequence and exploratory status are fixed in `PROTOCOL.md`,
`DYNAMICS_PROTOCOL.md`, `CHAIN_RELAXATION_PROTOCOL.md`,
`CLASSICAL_COMPILER_PROTOCOL.md`, and `REPAIR_COMPILER_PROTOCOL.md`.
Local checks can be reproduced with `theory_checks.py`, `repair_checks.py`,
`check_dynamics.py` and `backend_check.py`. They validate formulas/implementation;
the ordinary suite, rather than the small checks, supplies scope evidence.

Classical simulations start from uniform physical spins and use random-scan
single-site heat-bath updates with midpoint `beta(u)=20u`. Budgets are attempted
site updates, not sweeps or hardware time. Original-error optima are exact
reference-only labels for affine nullity at most 18; larger cases retain
feasibility and cost without invented optimum labels. Paired chain allocations
share initial/proposal streams. Compiler comparisons have the same original
inputs and physical target/ranges but different qubit counts.

## Artifact map

| Artifact | Contents |
|---|---|
| `results/*_n*_s*_{standard,balanced}.json` | Input, exact compiler, graph, candidate pools, selected embedding/program, thermal curves; failed case retained |
| `results/target.json` | Complete target graph, signed groups and software versions |
| `results/readout_audits/` | Actual programs and rational coefficient audits for every beta-specific curve |
| `results/analysis_summary.json` | All matched compiler comparisons, not only improvements |
| `results/dynamics/` | Kernel witnesses, original-root marginal and local mixing bounds |
| `results/relaxation/`, `relaxation_standard/` | Same-embedding before/after chain programs and audits |
| `results/anneals/` | Native sampler inputs and individual physical outputs |
| `results/anneal*_summary.json`, `anneal*_score_audit.json` | Every budget, uncertainty, paired counts and rescoring |
| `results/repair_compilers/` | Parent-collaboration M=C+1 models, actual programs and readout references |
| `results/readout_profile.json` | Repeated evaluator cost measurements |
| `figures/original_error_and_dynamics.{png,pdf}` | Main comparison and finite-work limitation |
| `results/independent_readout_intervals.json` | Parent's outward actual-root optimum intervals on all 64 n=16 thermal programs |
| `results/independent_child_program_audit.json` | Parent's separate exact physical-program audit |
| `results/research_artifact_manifest.json` | Child-owned artifact hashes and counts; excludes changing parent-owned work |

Two import-collision attempts are preserved in `results/*attempt1_import_collision.txt`.
They were repaired and do not count as scientific model failures. The only main
embedding failure is balanced mixed-hypergraph n=64 development seed 8807; eight
heuristic search failures do not certify a resource impossibility.
