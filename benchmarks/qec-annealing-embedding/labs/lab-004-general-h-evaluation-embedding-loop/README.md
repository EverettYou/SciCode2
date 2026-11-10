# Lab004: certified thermal evaluation guiding general-H embeddings

Read `RESEARCH_REPORT.md` for outcomes and limits, `THEORY.md` for proofs.
This is user-authorized continuing research; prior Lab002 imports are read-only
and hashed. No QPU or hidden error/observable data is used by construction.

## Reusable constructor

Input JSON contains only `n`, sparse row-support lists `rows`, `syndrome`, and
finite `weights`. Syndrome must lie in the image of H. The optional `penalty`
must strictly exceed the weight L1 norm. Default hardware is ideal Zephyr g6/t4
under explicitly illustrative h/J/group ranges. A custom target requires both
its node/edge witness and explicit coupling-group lists.

```text
python3 scripts/construct.py --input results/input_example.json --output results/constructor_example.json
```

The output includes the full logical model, target/groups, checked embedding,
all physical coefficients/offsets, tree repair certificate and exact-rational
static-fidelity audit. `--uniform` disables contact-allocation LP. `--beta` and
`--epsilon` declare the terminal-equilibrium model and defect budget. The default
constructor selects among8 automatic proposals; it does not run the optional
experimental deletion pass. It never solves the decoding problem classically.
Failure means no certified program found in this search/certificate regime.
It does not prove that an input cannot embed, except explicit count obstructions.

## Experiments and references

All commands below run from this lab directory with `requirements.txt` installed:

```text
python3 scripts/run_suite.py
python3 scripts/postprocess.py
python3 scripts/theory_checks.py
python3 scripts/logical_gibbs.py
python3 scripts/physical_gibbs.py
python3 scripts/run_extension.py
python3 scripts/update_audit.py
python3 scripts/run_lp.py
python3 scripts/lp_refinement.py
python3 scripts/figures.py
```

`--resume` on `run_suite.py` reuses existing instance files. To regenerate main
inputs without reuse, omit it; recorded timings are environment-specific and
need not repeat exactly. Supplementary seed/target files remain distinct.
The base Python path imports the two source-hashed Lab002 modules in place.
Optional plotting requires matplotlib; scientific algorithms do not.

The expensive reference solves in `logical_gibbs.py` and `physical_gibbs.py` are
verification only; they are not imported or used by `construct.py`. Exact-state
enumeration still evaluates Gibbs exponentials numerically; rigorous interval
checks and independent quantum tests live under the separately owned
`independent/` directory. The research report distinguishes these guarantees.

Main aggregate outcomes are in `results/analysis_summary.json`. Every main
instance file saves full H/input/model, all candidate embeddings and selected
physical witnesses. LP and LP+deletion witnesses live in `results/lp/` and
`results/lp_refinement/`; failed search records remain alongside successful ones.
Graph versions, node/edge lists and groups are in `results/target.json` and
`results/defect_target.json`. The first event-mismatch assertion is retained in
`results/physical_gibbs_attempt1_event_mismatch.txt` and explained in the report.

The model concerns conditional terminal thermal equilibrium and static fidelity.
There is no theorem about achieving that equilibrium in a finite anneal and no
real-hardware performance claim.
