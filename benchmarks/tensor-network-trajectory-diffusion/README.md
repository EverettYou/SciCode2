# Scalable Tensor-Network Quantum Trajectory Diffusion

This benchmark asks whether trajectory-level learned reverse diffusion can become a genuinely scalable many-body algorithm.

## Research goal

**Central question:** Can a translation-equivariant local tensor-network controller trained on short MPS trajectories reverse weak-measurement diffusion on unseen longer 1D chains with controlled physical and distributional error?

**Objective:** Develop the scalable replacement in stages. First qualify the companion dense-QR behavior and its refactored encoder/gate interface at one and two qubits. Then implement the MPS execution path and require it to reproduce the identical dense-vector trajectory, reverse update, loss, and gradient results at $N=1,2,3$ before using it at larger $N$. A future controller will compose generic QR-parameterized gates supported on at most $R$ consecutive sites; locality is tested only when $N>R$.

**Success means:** One frozen controller transfers to at least two unseen sizes; errors converge in bond dimension, controller range, and record window; measured runtime and memory scale polynomially over the tested regime.

**Scope boundary:** This is a conditioned pure-trajectory problem. Petz/CMI mixed-state recovery remains in the separate [`local-petz-recovery-ladder`](../local-petz-recovery-ladder/README.md) benchmark.

## Current research status

- **Stage:** `researching`; `expert_review: reviewed` for the bounded Lab 002 design in closed checkpoint `T-0006`.
- **Overall state:** Lab 001 has completed its dense-baseline/interface qualification: frozen splits, a three-seed 128-update loss checkpoint, held-out reversal fidelity, and exact QR-refactor regression are recorded.
- **Current thesis:** Generic one- and two-site gates may retain dense QR internally. The open question is whether composing bounded-support blocks works when $N>R$, not whether a different full-system parameterization matches QR at $N\leq2$; see [the synthesis](wiki/thesis.md).
- **Active frontier:** Lab 003 has passed small-system MPS/dense execution parity at $N=1,2,3$. Lab 004 then ran the MPS forward backend through $N=32$ in a product-state regime. The next algorithmic task is a scalable bounded-support reverse controller; the companion global dense-QR policy cannot run at large $N$.
- **Completed lab:** [Lab 001](labs/lab-001-local-controller-feasibility/REPORT.md) is the one- and two-qubit dense-baseline and interface qualification.
- **Active lab:** [Lab 002](labs/lab-002-dense-bounded-support-isolation/REPORT.md) has closed both product-family panels and the weak-local/coefficient panel as uninformative, completed the weak-local/depth-gate full-reference row, and completed four of five paired $R=2$ cells; the test split remains sealed.
- **Latest supported evidence:** MPS/dense probability and state-update parity passes at $N=1,2,3$ with errors below $1.1\times10^{-15}$. In the fixed-record product regime, untruncated MPS forward trajectories complete through $N=32$ with realized bond dimension one and a 5.0-second $N=32$ sweep. These results establish backend correctness and a low-entanglement forward regime, not learned reverse scalability.
- **Main uncertainty:** Whether a controller composed of gates on at most $R$ consecutive sites can reverse the task when $N>R$, and how the required $R$ changes with size and regime.
- **Next decisive action:** Implement and validate a bounded-support MPS reverse controller, then measure its frozen-policy rollout at larger $N$; retain Lab 002's remaining reviewed cell and sealed test split unchanged.
- **Blockers or pending human input:** None for the reviewed dense Lab 002 stages. The MPS parity suite must be specified and passed before any large-$N$ experiment; truncation, transfer, spatial sharing, and Hamiltonian heads still need their own controlled tests.
- **Last meaningful update:** 2026-08-23.

## Start here

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
