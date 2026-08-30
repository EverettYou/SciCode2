---
document_type: lab_report
lab_id: lab-001
status: completed
idea_ids:
  - x-001
  - c-002
  - x-002
  - c-004
wiki_context:
  - ../../wiki/thesis.md
  - ../../wiki/questions/scalable-trajectory-reversal.md
  - ../../wiki/ideas/research-frontier.md
related_labs:
  - Lab 002 (prospective dense $N>R$ controller test; create only after review)
---

# Lab 001: Dense-baseline and controller-interface qualification

## Narrow question

Can the companion dense-QR controller be reproduced and refactored without behavioral change, providing a trustworthy low-qubit reference and a reusable QR-parameterized block-gate interface for later $N>R$ research?

This is a baseline and interface qualification, not a comparison of distinct local controller families and not a scalability experiment.

## Motivation

The companion code already supplies the correct generic gate parameterization for a block containing one or two qubits: a full complex matrix followed by QR. If the allowed range satisfies $R\geq N$, that block covers the whole system, so a separate "local-gate head" is not a distinct hypothesis class. Lab 001 therefore qualifies the companion behavior and its refactoring; the first meaningful locality experiment must have $N>R$.

## Design

## Methods and execution

All runtime checks used the benchmark-local uv project defined by `pyproject.toml`, `.python-version`, and `uv.lock`; the locked environment contains Quimb 1.11.2, NumPy 2.2.6, Numba 0.61.2, Torch 2.13.0, and Transformers 4.57.6. Commands were run as `uv run python <lab-script> ...` from the benchmark directory. `prepare_dense_splits.py` generated immutable `dense-splits-v1` train/validation/test tensors for $N=1,2$ with $\epsilon=0.5$, $T=6$, computational-zero initial states, 256/64/64 trajectories, and distinct fixed split seeds; [`artifacts/dense-splits-v1/manifest.json`](artifacts/dense-splits-v1/manifest.json) records tensor shapes, token ranges, source path, Torch version, and SHA-256 hashes.

`train_dense_qr_baseline.py` trained the unmodified companion `PolicyModel` separately for $N=1$ seeds 2301/2303/2305 and $N=2$ seeds 2302/2304/2306, using 128 Adam updates, batch size 16, and learning rate $10^{-3}$. `qr_refactor_regression.py` copied the same weights into the explicit encoder-plus-QR seam and compared unitaries, `QuantumDiffusionLoss`, and parameter gradients on eight frozen validation trajectories at seeds 2401 and 2402. `quimb_parity_gradient_check.py` ran zero optimizer steps and compared the retained exploratory gate sketches with Quimb exact `Circuit`, a central finite difference with step $3\times10^{-4}$, and the $N=2$ no-truncation `CircuitMPS` state. Finally, `evaluate_dense_qr_reversal_fidelity.py` retrained each declared seed cell and applied the companion `trajectory_reversal` convention for $T-1=5$ updates on all held-out test records. Every command writes a reloadable JSON record under `results/`; the frozen inputs remain under `artifacts/`.

## Qualified system

The sole behavioral reference is the unmodified companion `PolicyModel`, with an exactly equivalent encoder-plus-QR refactor. Exploratory Pauli-Hamiltonian and Euler/entangler prototypes remain implementation sketches only; they are not co-primary Lab 001 baselines and will not be trained merely to reproduce an expressive class already covered by generic QR at $N\leq2$.

For future work, a local gate means a generic QR-parameterized unitary on at most $R$ consecutive sites. A many-body controller composes these bounded-support blocks. The locality restriction lies in support and composition when $N>R$, not in how each fixed-size block is internally parameterized.

## Controlled variables

Freeze the trajectory seeds and train/validation/test split. Keep the measurement strength, $T$, transformer configuration and initialization protocol, optimizer, update count, loss normalization, dtype, and reversal indexing identical. Do not redesign the record encoder in this lab.

## Primary evidence

- held-out one- and two-step reverse loss;
- held-out state fidelity or infidelity under the companion reversal convention;
- multistep trajectory-reversal fidelity if the reference path is validated;
- dense-QR training curves across seeds, gradient norms/failures, and final uncertainty;
- refactored-versus-original output, loss, and gradient regression;
- unitary residual, wall time, and peak memory.

## Review gate

Lab 001 can qualify the dense reference and interface, but it cannot decide whether bounded-range feedback works. Its completion permits proposing—not automatically executing—a follow-on dense-state lab with $N>R$, explicit block schedule, fixed $R$, and controlled record conditioning. MPS execution and size-transfer work remain separately gated.

## Findings

No trained multi-head comparison has run, and the clarified plan no longer requires one. Static inspection confirms the reusable seam: `PolicyModel.out_proj` emits `2 * dim * dim` real values and `qr_to_unitary` produces the dense unitary, while `QuantumDiffusionLoss` consumes only the resulting $U$. In later $N>R$ work, the same QR construction can parameterize each bounded-support block gate.

An initial dense-compatible prototype now implements the companion `forward(m_future, dtype) -> U` contract for both heads. The smoke test passes at $N=1,2$: maximum $U^\dagger U-I$ residuals are below $9\times10^{-16}$ in complex128 and all backpropagated parameter gradients are finite. This establishes interface and numerical-unitarity feasibility only; it does not yet compare reverse performance with the QR baseline or validate Quimb parity.

The benchmark-local uv environment now imports Quimb 1.11.2 with NumPy 2.2.6 and Numba 0.61.2, removing the ambient-environment import blocker. Its lockfile also pins Torch 2.13.0 and Transformers 4.57.6. The same smoke test passes inside this isolated environment; exact Quimb circuit parity remains to be implemented.

Lab execution has begun by freezing a qualification fixture before any controller training. `prepare_dense_splits.py` used the companion `ForwardDiffusion` path with $\epsilon=0.5$, $T=6$, computational-zero initial states, and distinct fixed seeds to generate train/validation/test records for $N=1,2$. Each system has 256/64/64 trajectories; the manifest records shapes, source path, Torch version, and SHA-256 hashes. Reload validation confirms every tensor has the declared shape and tokens in $0,\ldots,5$. These frozen inputs are an execution checkpoint, not evidence that any controller succeeds.

A second bounded checkpoint ran the unmodified companion `PolicyModel` (dense QR head) for four fixed Adam updates on the frozen fixture, separately at $N=1$ and $N=2$. Its held-out losses were 0.02636 ($N=1$, seed 2301) and 0.002591 ($N=2$, seed 2302). These figures are only a deterministic execution checkpoint.

The declared behavioral-reference checkpoint budget is now 128 Adam updates, batch size 16, learning rate $10^{-3}$, and three initialization seeds per approved system size; all other settings and frozen splits are unchanged. The locked benchmark environment completed seeds 2301/2303/2305 at $N=1$ and 2302/2304/2306 at $N=2$. Mean held-out validation/test losses (sample standard deviation across seeds) are 0.0229442 $\pm$ 0.0000211 / 0.0226270 $\pm$ 0.0000118 for $N=1$, and 0.00240927 $\pm$ 0.000000868 / 0.002370824 $\pm$ 0.000000017 for $N=2$. The six reloadable per-seed results establish a reproducible low-qubit loss checkpoint, but do not establish convergence, fidelity, or bounded-range locality.

That QR-refactor gate now passes. `RefactoredQRPolicy` copies the companion transformer and dense QR projection into an explicit shared encoder plus QR head, without changing the companion QR convention. On eight frozen validation trajectories at each approved system size, the copied and original policies agree exactly (maximum absolute error 0.0) for dense complex128 unitaries, `QuantumDiffusionLoss`, and all compared parameter gradients. Reloadable results are stored for $N=1$ (seed 2401) and $N=2$ (seed 2402). This validates the reusable encoder/QR seam; it is not evidence about bounded-range control.

An exploratory integration checkpoint also exercised Pauli-Hamiltonian and Euler/entangler prototypes at $N=1,2$. Their finite gradients and unitary residuals establish only that those sketches execute. They do not motivate a trained three-head comparison: at these sizes, a generic allowed block can cover the entire system and is already parameterized by dense QR. These artifacts are retained as unsuccessful/reframed branch history. The next Lab 001 action is completion of the companion behavioral reference, not local-head optimization or Quimb parity for the deprecated low-qubit comparison.

Under the current reviewed Lab 001 controller-comparison boundary, an additional zero-step execution gate rebuilt both local prototype families as raw gates in Quimb 1.11.2 exact `Circuit`. Across $N=1,2$, dense Torch and Quimb unitaries agree to at most $5.7\times10^{-16}$. A central finite-difference coordinate of the unchanged reverse loss agrees with autograd to at most $1.65\times10^{-6}$ using a $3\times10^{-4}$ step, which avoids cancellation in the loss's effective float32 path. At $N=2$, a no-truncation `CircuitMPS` state agrees with dense $U\lvert00\rangle$ to at most $5.7\times10^{-16}$. These checks contain zero optimizer steps and establish only the local-head circuit/gradient execution path; they are not evidence of performance parity with dense QR. The remaining Lab 001 evidence is held-out reversal fidelity under the companion convention; no local-head optimization is authorized.

The final held-out reversal-fidelity gate retrained the unmodified companion dense-QR policy for the declared 128 Adam updates on each frozen seed cell, then reconstructed each test record's normalized forward final state and applied the companion's $T-1=5$ `trajectory_reversal` updates toward $\lvert0\rangle$. Mean test fidelity across initialization seeds is $0.652636\pm0.022455$ for $N=1$ (seeds 2301, 2303, 2305) and $0.420085\pm0.005803$ for $N=2$ (seeds 2302, 2304, 2306); per-trajectory fidelity has substantial spread, so this is a bounded behavioral reference rather than a convergence claim. Together with the frozen splits, three-seed loss checkpoint, and exact refactor regression, this completes Lab 001's approved qualification contract. It does not pass the separate review gate for any $N>R$, MPS, truncation, or transfer experiment.

- Prototype: [`prototype.py`](prototype.py)
- Reproducible smoke test: `python3 benchmarks/tensor-network-trajectory-diffusion/labs/lab-001-local-controller-feasibility/smoke_test.py`
- Split generator: [`prepare_dense_splits.py`](prepare_dense_splits.py)
- Frozen qualification manifest: [`artifacts/dense-splits-v1/manifest.json`](artifacts/dense-splits-v1/manifest.json)
- Dense QR checkpoint runner: [`train_dense_qr_baseline.py`](train_dense_qr_baseline.py)
- Dense QR checkpoint outputs: [`results/dense-qr-baseline-v1/`](results/dense-qr-baseline-v1/)
- QR-refactor regression: [`qr_refactor_regression.py`](qr_refactor_regression.py)
- QR-refactor outputs: [`results/dense-qr-refactor-v1/`](results/dense-qr-refactor-v1/)
- Local-head encoder integration check: [`local_head_encoder_smoke.py`](local_head_encoder_smoke.py)
- Integration outputs: [`results/local-head-encoder-smoke-v1/`](results/local-head-encoder-smoke-v1/)
- Quimb exact-circuit and finite-difference gate: [`quimb_parity_gradient_check.py`](quimb_parity_gradient_check.py)
- Parity/gradient outputs: [`results/local-head-quimb-parity-v1/`](results/local-head-quimb-parity-v1/)
- Held-out reversal-fidelity evaluator: [`evaluate_dense_qr_reversal_fidelity.py`](evaluate_dense_qr_reversal_fidelity.py)
- Fidelity outputs: [`results/dense-qr-reversal-fidelity-v1/`](results/dense-qr-reversal-fidelity-v1/)

## Analysis and limitations

The exact QR-refactor agreement makes the encoder/gate seam trustworthy for later controller work, and the three-seed loss and fidelity records provide a reproducible behavioral reference. They do not demonstrate optimizer convergence or high-quality reversal: the budget is only 128 updates, the fidelity distributions are broad, and the experiment covers one measurement strength, one trajectory length, computational-zero initial states, three initialization seeds, and only $N=1,2$. The unusually smaller reverse loss at $N=2$ should not be interpreted as better physical reversal because the loss normalization and dimensional dependence have not been calibrated across sizes; the lower held-out fidelity directly cautions against that reading.

The Quimb, finite-difference, and `CircuitMPS` checks contain zero optimization steps and validate execution only. The retained Hamiltonian/Euler sketches are not scientific baselines after the locality clarification. No result probes $N>R$, bounded-support composition, spatial sharing, record-memory requirements, tensor-network truncation, entanglement growth, runtime scaling, or train-short-test-long transfer. Consequently, Lab 001 supports only the dense low-qubit reference and interface qualification claimed above.

## Search decision

Mark Lab 001 complete and retain its dense-QR fixture, behavioral metrics, and exact encoder/QR regression as the reference boundary for descendants of `x-001` and `c-002`. Reframe the proposed $N\leq2$ local-Hamiltonian versus local-gate training comparison as an uninformative branch because any generic block with $R\geq N$ spans the full system; preserve its executable smoke/parity artifacts as negative design history rather than performance evidence. The next high-information experiment is a separately reviewed dense-state lab with $N>R$, fixed block range and schedule, identical record conditioning, and no MPS or transfer claims. Do not create or execute that lab until its plan passes a new human checkpoint.

## Wiki ingest handoff

Ingest the frozen baseline configuration, refactor regression, low-qubit behavioral metrics, the generic QR local-block convention, and the reviewed boundary for a future $N>R$ experiment. Preserve the deprecated prototype branch without treating it as a required controller comparison.
