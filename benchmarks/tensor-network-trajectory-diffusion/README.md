# Scalable Tensor-Network Quantum Trajectory Diffusion

This benchmark asks whether trajectory-level learned reverse diffusion can become a genuinely scalable many-body algorithm.

## Research goal

**Central question:** Can a translation-equivariant local tensor-network controller trained on short MPS trajectories reverse weak-measurement diffusion on unseen longer 1D chains with controlled physical and distributional error?

**Objective:** Develop the scalable replacement in stages. First qualify the companion dense-QR behavior and its refactored encoder/gate interface at one and two qubits. Then implement the MPS execution path and require it to reproduce the identical dense-vector trajectory, reverse update, loss, and gradient results at $N=1,2,3$ before using it at larger $N$. A future controller will compose generic QR-parameterized gates supported on at most $R$ consecutive sites; locality is tested only when $N>R$.

**Success means:** One frozen controller transfers to at least two unseen sizes; errors converge in bond dimension, controller range, and record window; measured runtime and memory scale polynomially over the tested regime.

**Scope boundary:** This is a conditioned pure-trajectory problem. Petz/CMI mixed-state recovery remains in the separate [`local-petz-recovery-ladder`](../local-petz-recovery-ladder/README.md) benchmark.

## Current research status

- **Current thesis:** Corrected local-Hamiltonian execution is validated at small N; frozen recovery at larger N retains a quantitative accuracy boundary.
- **Active lab:** [Lab 007](labs/lab-007-paper-hamiltonian-score-matching/REPORT.md), with the bounded continuation completed and follow-on controller controls documented.
- **Stage:** researching. User-authorized Lab 007 continuation completed on 2026-09-07.
- **Latest supported evidence:** corrected projector-splitting TDVP matches dense small-system states and gradients, including complete 300-step AD checks. On frozen five-qubit weights, paired fidelity rises from legacy 0.2853 to 0.8050, matching dense evaluation.
- **Active frontier:** a frozen shared controller trained at N=5 runs on entangled chains through N=32. F=0.8896, 0.6667, 0.4157 and 0.04674 at N=6,8,12,32 (chi=4). These are partial recovery results, not uniform high-fidelity scalability.
- **Controls:** N=3 training fails earlier. Ancilla-locked transfer is tested through N=12. Chi and projector-refinement controls at N=6,8 leave substantial controller error; convergence is not established at N=32.
- **Main uncertainty:** local state expectations are supplied directly; short-chain training remains dense. Record decoding, robust scalable training, multiple training seeds and broader state ensembles remain open.
- **Next decisive action:** matched-budget controller-support and mixed-size-training controls, preserving the failed branches.
- **Blockers or pending human input:** durable state is initialized but schedules are paused because this session lacks automation management. Cached schedule IDs are unverified. Manual checkpoints and steering decisions are saved; no user decision is pending.
- **Evidence:** [Lab 007 report](labs/lab-007-paper-hamiltonian-score-matching/REPORT.md), [implementation synthesis](wiki/implementations/corrected-tdvp-controller.md), [figure](labs/lab-007-paper-hamiltonian-score-matching/figures/tdvp-transfer-v2/repair-and-transfer.png).
- **Historical work:** Lab 001 dense QR qualification and the separate Lab 002 reviewed cells remain preserved.
- **Last meaningful update:** 2026-09-07.

## Start here

New SciCode 2 draft: [recoverability candidate](problem/recoverability/README.md),
a physical-optimum task with verified N=2,4 reference grids and an N=6 pilot
(width 1.51e-5). Next calibrate N=8 at width 1e-4; AI difficulty remains unmeasured. It is a candidate alongside the existing task.

The latest results are in [Lab 007](labs/lab-007-paper-hamiltonian-score-matching/REPORT.md). The earlier phase documents below remain as history.

1. [metadata.yml](metadata.yml)
2. [problem/TASK.md](problem/TASK.md)
3. [wiki/index.md](wiki/index.md) and [wiki/thesis.md](wiki/thesis.md)
4. [wiki/ideas/research-frontier.md](wiki/ideas/research-frontier.md)
5. [Lab 002 report](labs/lab-002-dense-bounded-support-isolation/REPORT.md) and [plan](labs/lab-002-dense-bounded-support-isolation/PLAN.md)
6. [Lab 001 report](labs/lab-001-local-controller-feasibility/REPORT.md) and [plan](labs/lab-001-local-controller-feasibility/PLAN.md)
7. [src/](src/) and [note/](note/)

## Independent numerical environment

This benchmark is a standalone uv project. Its `.venv` and `uv.lock` are independent of the repository-root dashboard environment so its Quimb/NumPy/Numba constraints cannot destabilize other benchmarks or workspace tools.

```bash
cd benchmarks/tensor-network-trajectory-diffusion
uv sync
uv run python labs/lab-001-local-controller-feasibility/smoke_test.py
```

Run commands from this directory or pass `--project benchmarks/tensor-network-trajectory-diffusion`. Do not activate the root `.venv` and use `uv sync --active`: that would install benchmark packages into the wrong environment. The benchmark may read the companion snapshot through repository-relative paths, but it does not inherit root `site-packages`.

## Source foundation

- [`liu2025mqdm`](../../wiki/papers/liu2025mqdm.md) — trajectory-level weak-measurement diffusion and record-conditioned reverse control.
- [Companion implementation](../../wiki/implementations/liu-quantum-diffusion-companion.md) — dense behavioral baseline and scaling bottleneck.
- [Quimb tensor optimization](https://quimb.readthedocs.io/en/main/tensor/tensor-optimization.html) and [quantum circuits](https://quimb.readthedocs.io/en/latest/tensor/tensor-circuit.html) — reference APIs for parametrized tensor-network circuits, automatic differentiation, and MPS execution.

## Reading discipline

- Do not claim trajectory recovery from a few local observables.
- Do not claim scalability without frozen train-short-test-long transfer and measured resource scaling.
- Separate tensor representation, controller capacity, record decoding, and rollout errors.
