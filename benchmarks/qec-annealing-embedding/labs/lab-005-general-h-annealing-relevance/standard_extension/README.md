# Standard-compiler necessary-optimality extension

This branch is isolated from the frozen main and theory_extensions snapshots.
Read `RESEARCH_REPORT.md` for all controls and limitations, `THEORY.md` for the
proof and `*_PROTOCOL.md` for the timing of adaptive choices. It is continuing
reference research, not calibration or a clean autonomous test.

The reusable primitive is `scripts/optimality_lp.py`. `evaluate(input, moments,
delta, method)` returns an exact lower bound for an unknown original optimum's
second-order coefficient difference. The method is `basis`, `pairs` or
`triangles`. HiGHS only proposes multipliers; exact residual L1 evaluation is
the certificate. Necessary constraints hold for global optima, not arbitrary
feasible errors. No optimal error is supplied or computed by this evaluator.

From this directory:

```sh
python3 scripts/run.py
python3 scripts/upper_diagnostic.py
python3 scripts/witness_followup.py
python3 scripts/witness_followup.py --particular
python3 scripts/upper_only_control.py
python3 scripts/run.py --upper particular
python3 scripts/run.py --upper witness
python3 scripts/check.py
python3 scripts/audit.py
```

Runners overwrite only this branch's own results. Main inputs and actual programs
are read from `../results/certified_mapping/`. The parent already computed
GF2 characters, physical q2/q4 coefficients and exact event tails. This extension
charges incremental work separately; it does not claim standalone end-to-end
cost. Python/NumPy/SciPy versions are inherited from the main lab requirements.
No QPU or network service is used.

Exact Fractions are serialized as `numerator_hex`/`denominator_hex`. Recover one
with `Fraction(int(numerator_hex,16),int(denominator_hex,16))`. All ordinary
selector decisions use exact rational signs and tie-breaking.

The feasible search uses16 fixed starts and at most4n accepted basis/pair moves
per start. It is an approximate feasible-cost search with no optimality claim.
Weights are scaled by an LCM of exact binary64 Fraction denominators, supporting
finite signed binary64 weights; arbitrary large bit precision can increase cost.
No planted error or reference optimum is consulted. True optimum enumeration is
confined to `check.py`'s small implementation/proof-validation instances.

Artifact map:

- `results/*_standard.json`, `summary.json`: moment-upper nested LP controls.
- `results/upper/`, `upper_summary.json`: retained inconclusive negative-curvature
  diagnostic.
- `results/particular/`, `particular_summary.json`: existing particular solution
  upper witness plus strongest LP.
- `results/witness/`, `witness_summary.json`: bounded feasible search and strongest
  LP, including original-error masks and search counts.
- `results/upper_only/`, `upper_only_summary.json`: tightened-upper cost-only
  controls; neither certifies a change.
- `results/{particular,witness}_nested/`: all basis/pair/triangle controls with
  tightened upper bounds.
- `results/check*.json`:60 arbitrary small matrix checks, separate from selection.
- `results/exact_audit.json`: exact replay of1,728 dual certificates,12,096 event
  bound updates and48 ordinary feasible witnesses without optimization.
- `manifest.json`: branch hashes and read-only dependency provenance.

Three searched-witness+triangle comparisons certify smaller standard embeddings
at all declared early durations; all are n16. Every n32/64 case is retained as
inconclusive. This is an actual original-optimum finite-forward statement, with
tiny probability advantages, rather than a cost/Gibbs surrogate. It does not
establish useful moderate-time or QPU performance.
