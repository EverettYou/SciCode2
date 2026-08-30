# Wiki log

<!-- Append entries; never rewrite prior entries. Format: ## [YYYY-MM-DD] operation | subject -->

## [2026-08-29] experiment | MPS dense-parity and forward resource gates

- Lab 003: untruncated MPS execution reproduced the dense selected-outcome probabilities, normalized forward states, and frozen-policy reverse updates for eight validation trajectories at each of $N=1,2,3$, with all maximum state errors below $1.1\times10^{-15}$.
- Lab 004: the validated MPS forward path ran eight six-step fixed-record product trajectories at $N=4,8,16,24,32$ with realized bond dimension one and wall times of 0.116, 0.391, 1.305, 2.659, and 4.997 seconds.
- Boundary: these are execution-correctness and low-entanglement forward-backend results. The current companion policy emits a global dense QR unitary, so a bounded-support MPS reverse controller remains required before any learned-reversal scalability claim.

## [2026-08-23] query | reframe MPS as a small-system algorithm-correctness gate

- Human clarification: adopting an MPS algorithm does not itself require large $N$. The first purpose of the MPS path is to reproduce the dense-vector trajectory-diffusion result on exactly checkable $N=1,2,3$ systems, yielding confidence that the implementation is correct before large-$N$ testing.
- Decision: require identical frozen inputs, controller weights, and schedules to match dense normalized states, outcome probabilities, reverse updates, loss, automatic gradients, and fixed-budget training/held-out behavior in a no-effective-truncation MPS regime. Treat truncation as a later error study.
- Boundary: passing this suite validates the MPS algorithm but is not evidence of scalability. Large-$N$ tests may begin only after parity passes; scaling claims still require resource and accuracy sweeps.

## [2026-08-23] ingest | initial trajectory-diffusion benchmark references

- Source references: `wiki/papers/liu2025mqdm.md`, its companion-implementation page, and `problem/TASK.md`.
- Registry entries: `global:liu2025mqdm`, `benchmark:task`.
- Pages created: `ideas/research-frontier.md`, `questions/scalable-trajectory-reversal.md`.
- Pages updated: `index.md`, `thesis.md`.
- Summary: Initialized a benchmark separate from the Petz project. The active hypothesis is that MPS trajectories plus a translation-equivariant finite-range controller can transfer from short to longer chains while $\chi$, $R$, and $W$ remain controlled.

## [2026-08-23] query | local quantum control and Quimb backend

- Human direction: learn an explicitly local control Hamiltonian that can be Trotterized, or learn local quantum gates and execute the reverse unitary as a circuit.
- Sources consulted: Quimb official tensor-optimization, quantum-circuit, CircuitMPS, 1D algorithm, and TEBD documentation.
- Environment check: the ambient Quimb installation currently fails to import because Numba rejects NumPy 2.4; Lab 001 now requires an isolated pinned environment.
- Pages updated: `thesis.md`, `questions/scalable-trajectory-reversal.md`, and `ideas/research-frontier.md`.
- Lab updated: `labs/lab-001-mps-trajectory-baseline/` now compares local-Hamiltonian and direct-gate controllers and validates gradients before training.
- Summary: Quimb is the reference differentiable tensor-network backend. Hamiltonian and gate controllers are co-primary architectures matched by causal radius, parameter count, and two-site-gate cost.

## [2026-08-23] query | narrow Lab 001 to low-qubit controller feasibility

- Human direction: begin from the companion dense-vector single- and two-qubit experiments and test the new circuit-shaped architecture there before attempting many-body scaling.
- Controlled change: keep trajectories, future-record encoder, loss, split, and training budget fixed; replace only the dense QR output head by a local-Hamiltonian or local-gate head.
- Scope moved later: $N>2$ training, MPS truncation, short-to-long transfer, and resource scaling are excluded from Lab 001 and gated on its go/no-go result.
- Lab path: `labs/lab-001-local-controller-feasibility/`.
- Summary: exact dense execution is the Phase-1 truth backend; Quimb exact circuits validate the architecture, while `CircuitMPS` is only a two-qubit no-truncation smoke test.

## [2026-08-23] query | local-controller interface smoke test

- Prototype added: `labs/lab-001-local-controller-feasibility/prototype.py` with companion-compatible local-Hamiltonian and direct-gate policies.
- Test added: `smoke_test.py` checks $N=1,2$ output shapes, complex128 unitarity, and finite backpropagated gradients.
- Result: all four system/family combinations passed; maximum unitary residual was below $9\times10^{-16}$.
- Boundary: this is not a trained QR-baseline comparison and supplies no MPS or scaling evidence.

## [2026-08-23] ingest | benchmark-local uv environment

- Added standalone `pyproject.toml`, `.python-version`, `uv.lock`, and a local `.venv` for this benchmark.
- Locked stack: Quimb 1.11.2, NumPy 2.2.6, Numba 0.61.2, Torch 2.13.0, and Transformers 4.57.6.
- Verification: Quimb imports successfully and the $N=1,2$ controller smoke test passes inside the locked environment.
- Repository convention: benchmark environments do not inherit root `site-packages`; the reusable benchmark scaffold and validator now enforce the standalone-project boundary.

## [2026-08-23] query | define locality by block support, not low-qubit head type

- Human clarification: $R$ is the maximum number of consecutive sites covered by one Hamiltonian term or gate and is an adjustable research parameter. Scalability for $N>R$ is an open question, not an assumption.
- Controller convention: each allowed block gate may remain a generic dense complex matrix followed by QR. Its cost depends on the bounded block size $R$, while locality comes from support, scheduling, and spatial sharing across the full chain.
- Low-qubit consequence: for $N=1,2$ with $R\geq N$, one block covers the entire system, so a separately parameterized local-gate or full-range Hamiltonian head is not a distinct locality test. The previously planned three-head training comparison is deprecated.
- Lab 001 scope: qualify the companion dense-QR behavior and exact encoder/QR refactor only. Preserve existing Hamiltonian/Euler prototype artifacts as reframed branch history; do not continue their optimization or parity gates merely for a low-qubit comparison.
- Next research gate: after Lab 001 qualification, propose a dense-state $N>R$ bounded-block controller experiment for separate review. MPS execution, truncation, $N>2$ training, and size transfer remain unauthorized by this clarification.

## [2026-08-23] query | keep unresolved rationale and scope concise

- Human direction: `Why this is unresolved` and `Scope and approach` are living context for the current central question, not containers for detailed controller ansatzes or execution recipes.
- Task update: removed the direct local-gate and Hamiltonian implementation subsections from the scope; the two bounded sections now contain 82 and 112 words respectively.
- Evolution rule: when evidence or steering changes the central question, update both bounded sections in the same transition and synchronize metadata, README, thesis, and active frontier while preserving the former formulation in history.
- Reusable guardrail: the benchmark validator now caps each section at 250 words, checks the TASK research question against metadata, and has dependency-free boundary tests. The scaffold, design guide, project strategy, and auto-research supervisor instructions carry the same rule.

## [2026-08-23] ingest | completed Lab 001 dense QR qualification

- Source: `labs/lab-001-local-controller-feasibility/REPORT.md` at revision `sha256:dc32def94cb08ad944f33183ae9e85879eda374dcab7614dc1f4d2d2c9c34578`.
- Registry entry: `lab:lab-001`.
- Page created: `implementations/dense-qr-controller-reference.md`.
- Pages updated: `index.md`, `thesis.md`, `questions/scalable-trajectory-reversal.md`, and `ideas/research-frontier.md`.
- Supported evidence: frozen $N=1,2$ splits, three-seed dense-QR loss/fidelity references, and exact encoder/QR output-loss-gradient regression.
- Boundary: no result tests $N>R$, bounded-range composition, MPS truncation, or size transfer. The deprecated low-qubit head comparison is retained as negative design evidence, and the next dense $N>R$ plan requires separate human review.

## [2026-08-23] query | select minimal dense bounded-support proposal

- Sources consulted: the benchmark thesis, open question, research frontier, completed Lab 001 report, dense-QR implementation reference, benchmark task, and the global companion-implementation and trajectory-recovery syntheses.
- Candidates compared: a position-specific $N=3,R=2$ support-isolation test; an $N=3,R=2$ spatially shared controller; and an $N=4,R=2$ brickwork controller.
- Decision: propose the position-specific $N=3,R=2$ design first because it isolates bounded support and composition from spatial parameter sharing at the cheapest nontrivial size.
- Controls: retain the qualified global future-record encoder and compare full-system QR, composed $R=2$ QR blocks, $R=1$ product gates, and no control on identical dense trajectories.
- Review state: checkpoint `T-0006` is open and blocking. No Lab 002 was created, and no $N>2$ training, MPS execution, truncation, or size transfer is authorized.

## [2026-08-23] query | make the bounded-support proposal state-aware

- Human review: checkpoint `T-0006` rejected a universal $R=2>R=1$ rule because state-family saturation, unequal resources, causal capacity, and optimization can produce the same pooled outcome.
- Proposal revision: stratify $N=3$ trajectories into product-like, shallow locally entangled, and $W_3$ long-range-correlated families; require the full-QR-versus-$R=1$ informativeness gate separately in each family.
- Resource revision: use complementary coefficient-matched and depth/gate-count-matched panels because generic QR support classes cannot simultaneously match all three quantities without changing the hypothesis class. Keep record, seed, optimizer, and wall-time budgets identical within each panel.
- Decision revision: compute the normalized conditional recovery score only when the full-QR advantage exceeds a declared tolerance; distinguish saturation, local-circuit capacity, learned-head optimization or record decoding, and resource-confounded outcomes with an oracle gate-schedule diagnostic.
- Review state: the revised proposal awaits explicit approval in `T-0006`. Lab 002 still does not exist and no $N>2$ execution is authorized.

## [2026-08-23] query | approve state-aware dense N=3 support-isolation plan

- Source: user decision M-007 in closed checkpoint `T-0006`.
- Approval covers only the predeclared dense $N=3$, $R=2$ support-isolation design: its three state families, complementary coefficient- and depth/gate-matched panels, five-seed per-family uncertainty, conditional informativeness and recovery criteria, oracle attribution, and staged numerical gates.
- Next action: create the prospective Lab 002 plan. Do not start MPS, truncation, size transfer, spatial sharing, Hamiltonian-head work, or $N>3$ experiments.

## [2026-08-23] query | create reviewed Lab 002 prospective node

- Lab created: `labs/lab-002-dense-bounded-support-isolation/` with a planned report and executable staged plan.
- Registered design: three frozen state families, coefficient-matched and depth/gate-count-matched panels, five paired initialization seeds, conditional informativeness and recovery tolerances, and an oracle attribution diagnostic.
- Execution boundary: this transition created planning artifacts only. No $N=3$ fixture, controller code, optimizer step, MPS path, truncation, transfer, spatial sharing, Hamiltonian head, or $N>3$ experiment ran.
- Next action: Lab 002 Stage 1 may freeze and validate the dense $N=3$ state-family fixtures in the benchmark-local uv environment.
