# Candidate: certified quantum-information recoverability

Status: **author draft, updated 2026-09-08; not a release-ready SciCode 2 problem**.

This candidate follows the user's request to evaluate a physical conclusion rather
than reproduce a particular learned controller. It is a proposed branch from the
existing trajectory-diffusion project; it does not replace [the active task](../TASK.md)
or change the benchmark's reviewed scope.

## Reading path

1. [TASK.md](TASK.md): prospective solver-facing physical problem and deliverables.
2. [EVALUATION.md](EVALUATION.md): author-only correctness and certificate contract.
3. [EVIDENCE.md](EVIDENCE.md): what existing research actually establishes.
4. [DIFFICULTY.md](DIFFICULTY.md): shortcut audit and blind difficulty calibration.
5. [Lab 008](../../labs/lab-008-recoverability-anchors/REPORT.md): executable exact
   one-qubit anchors and independent primal/dual certificate verification.

A nontrivial numerical reference exists for the complete N=2,4 grid and one N=6 pilot:
[Lab 009](../../labs/lab-009-encoded-recoverability/REPORT.md) saves recovery and
upper-bound certificates and verifies them with an independent channel construction.
Lab 008 remains the analytic anchor layer. Lab 007 is numerical infrastructure
rather than an optimal-recovery reference solution. The N=6 pilot achieves width 1.51e-5 with all records verified. N=8 release and
blind-model difficulty remain unvalidated.

The [pilot instance manifest](instances-pilot.json) explicitly lists gate schedules,
angles as rational multiples of pi, measurement axes, and the current reference grid.

## Author decision

Start with finite-size optimal entanglement recovery and the value of measurement
records. Make a phase transition an optional later research branch. Do not require
a critical exponent until a transition, accessible scaling regime, and reliable
reference analysis exist. Do not claim that AI success is below 10% without trials.

The proposed sizes, tolerance, and compute budget in TASK.md are concrete pilot
targets. Freeze them only after one reference implementation passes, an independent
check passes, and blind trials establish the desired active-work duration/difficulty.

## Reproduce the currently available verification

From the repository root, using the historical available NumPy/Pytest environment:

```bash
/usr/bin/python benchmarks/tensor-network-trajectory-diffusion/labs/lab-008-recoverability-anchors/scripts/anchors.py --output /tmp/recoverability-anchors.json
/usr/bin/python -m pytest -q benchmarks/tensor-network-trajectory-diffusion/labs/lab-008-recoverability-anchors/scripts/test_anchors.py
/usr/bin/python benchmarks/tensor-network-trajectory-diffusion/labs/lab-008-recoverability-anchors/scripts/audit_existing.py
```

This is not a locked release environment. Versions and source hashes are recorded
in the lab output. No companion code is copied or required for these checks.

For encoded-reference reproduction and verification, use [Lab 009 instructions](../../labs/lab-009-encoded-recoverability/README.md). Its uv lock is independent of the historical anchor environment.
