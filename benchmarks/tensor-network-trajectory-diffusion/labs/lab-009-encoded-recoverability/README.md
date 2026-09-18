# Encoded recovery reference: reproduce and verify

This lab solves the constructed physical problem in
[the candidate task](../../problem/recoverability/TASK.md). It uses its own
`pyproject.toml`, `uv.lock`, and Python version file. Source inputs and author
certificates must not be present in a blind solver workspace.

From the repository root:

```bash
uv sync --project benchmarks/tensor-network-trajectory-diffusion/labs/lab-009-encoded-recoverability --frozen
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 uv run --project benchmarks/tensor-network-trajectory-diffusion/labs/lab-009-encoded-recoverability --frozen python -m pytest -q benchmarks/tensor-network-trajectory-diffusion/labs/lab-009-encoded-recoverability/scripts/test_physics.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 uv run --project benchmarks/tensor-network-trajectory-diffusion/labs/lab-009-encoded-recoverability --frozen python benchmarks/tensor-network-trajectory-diffusion/labs/lab-009-encoded-recoverability/scripts/solve.py --n 4 --g .5 --eta .75 --output /tmp/encoded-n4-reference
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 uv run --project benchmarks/tensor-network-trajectory-diffusion/labs/lab-009-encoded-recoverability --frozen python benchmarks/tensor-network-trajectory-diffusion/labs/lab-009-encoded-recoverability/scripts/verify_saved.py /tmp/encoded-n4-reference
```

Use a fresh output directory; solvers refuse overwrite. Run the verifier on an
existing saved result directory to avoid recomputation. It rebuilds the physical
objectives and does not import CVXPY. Every branch archive contains raw solver
matrices plus repaired recovery/dual matrices and PSD factors. The aggregate
`summary.json` records weights, statuses, errors, time, versions and source hashes.

`solve_compressed.py` exploits each record's output support and then lifts and
repairs certificates in full space. `solve_adaptive.py` caps solver work on large
supports; its achieved interval, rather than its requested solver tolerance, is
the accuracy criterion. Its `--reuse` option rechecks completed certificates from
an interrupted run. Warm reuse costs belong to the combined experiment budget.

`baselines.py` computes a no-training transpose recovery and a full-record upper
bound. Its v2 output supersedes the overly conservative normalization in v1.
The small reference grid, source provenance and decision are in [REPORT.md](REPORT.md).
