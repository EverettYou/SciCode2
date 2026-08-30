# Lab 001 execution plan

## Objective

Qualify the companion dense-QR controller and its reusable encoder/gate interface at one and two qubits. Do not treat a one- or two-qubit "local-gate head" as a distinct controller family: when the allowed gate range satisfies $R\geq N$, a generic contiguous-block gate is the same full-system unitary already parameterized by the companion QR head.

## Implementation boundary

Import or wrap the companion implementation as a behavioral reference; do not edit the paper snapshot. Factor its future-record transformer pooling from its QR unitary map while preserving `forward(m_future, dtype) -> U`, so the existing `QuantumDiffusionLoss` and reversal code can be reused unchanged.

The scalable gate controller will later emit and compose generic QR-parameterized unitaries on contiguous blocks of at most $R$ sites. Locality is imposed by block support, overlap pattern, parameter sharing, and circuit composition—not by replacing QR with Euler-angle or Pauli-coefficient parameterizations on $N\leq2$.

## Stable interfaces

The initial stable seam is the companion policy contract `forward(m_future, dtype) -> U`. The trajectory generator, `QuantumDiffusionLoss`, and reversal evaluator remain unchanged. The refactored encoder plus QR map becomes qualified only after exact output, loss, and gradient regression against the companion implementation. A later $N>R$ controller requires a separate reviewed interface for emitting multiple overlapping local block gates.

## Locality convention

- $R$ is the maximum number of consecutive sites covered by one Hamiltonian term or gate.
- A gate on a block of $r\leq R$ sites may be a generic $U(2^r)$ unitary parameterized by a dense complex matrix followed by QR. QR inside each bounded-size block is compatible with locality.
- For $N=1$ or $N=2$ with $R\geq N$, one allowed block covers the entire system. A generic "local" gate is therefore identical in expressive class to the companion global QR unitary and supplies no independent head comparison.
- A full-range Hamiltonian on $N\leq2$ is likewise only an alternative parameterization of full-system control. Hamiltonian/Trotter comparisons may be studied later for numerical or interpretability reasons, but they are not a prerequisite for testing bounded-range gates.
- The scientific locality question begins only when $N>R$. No answer—positive or negative—is assumed in advance.

## Steps

1. Create an isolated locked environment. Pin the companion Torch/Transformers stack and a mutually compatible Quimb/NumPy/Numba stack; the ambient Quimb install is not evidence because it currently fails to import.
2. Reproduce the unmodified dense-QR baseline separately for $N=1$ and $N=2$. Freeze trajectory files and train/validation/test indices. Record the exact QR convention, tokenization, dtype, loss normalization, time indexing, seeds, and reference commands.
3. Extract a shared future-record encoder whose outputs reproduce the original policy. Add exact output, loss, and gradient regression tests using copied weights.
4. Reproduce the companion dense-QR learning behavior sufficiently to establish the low-qubit behavioral reference, including held-out loss/fidelity and seed variation under a declared budget.
5. Specify the future local-block contract: for a contiguous block of size $r\leq R$, the controller emits a generic QR-parameterized $U(2^r)$; a schedule composes such blocks over the chain. Do not implement or train the $N>R$ controller in this lab.
6. Record the boundary decision and request review for a follow-on dense-state experiment with $N>R$. MPS execution, truncation, size transfer, and resource-scaling sweeps remain separately gated.

## Predeclared qualification contract

- Primary systems: $N=1$ and $N=2$ only.
- Primary backend: dense complex state vectors.
- Fixed components: trajectory data, record encoder, loss, optimizer family, update budget, dtype, and evaluation code.
- Changed component: none in the behavioral baseline; the refactor must be exactly equivalent.
- Primary endpoint: held-out reverse loss plus state infidelity.
- Equivalence tolerance: floating-point regression tolerance for the refactor; statistical uncertainty for the behavioral baseline.
- Secondary endpoints: multistep reversal, unitary residual, gradient agreement, runtime, and peak memory.

## Completion criteria

- The refactored QR path reproduces the companion output, loss, and gradients to floating-point tolerance.
- The companion behavioral reference has reproducible held-out metrics on the frozen $N=1,2$ splits under a declared training budget.
- The local-block locality convention and generic QR parameterization are recorded without inventing a distinct low-qubit gate head.
- The report ends with an explicit review gate for a later $N>R$ experiment; it does not infer locality or scalability from $N\leq2$.

## Stop conditions

- Do not begin MPS scaling, truncation sweeps, $N>2$ training, or size transfer in this lab.
- Do not spend compute comparing QR with Euler-angle, Pauli-Hamiltonian, or other full-system parameterizations merely to label them "local" at $N\leq2$.
- Do not infer bounded-range controller behavior from the low-qubit baseline.
- Do not begin the $N>R$ controller experiment without a new reviewed plan.
