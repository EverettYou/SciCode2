# Labs

Each lab contains a prospective report, executable plan, and node-local scripts, results, and figures.

## Nodes

- [lab-001-local-controller-feasibility](lab-001-local-controller-feasibility/REPORT.md) — qualifies the companion dense-QR behavior and exact encoder/QR refactor at one and two qubits; meaningful bounded-range controller tests require a separately reviewed $N>R$ lab.
- [lab-002-dense-bounded-support-isolation](lab-002-dense-bounded-support-isolation/REPORT.md) — approved dense $N=3$, $R=2$ state-aware support test; prerequisite gates pass and the bounded one-step validation matrix is in progress.

## Graph conventions

Exploratory code remains node-local. Only parity-tested reusable MPS, controller, contraction, and metric interfaces are promoted to `src/`. Prospective expectations are not findings.
