# Tensor-network trajectory-diffusion research map

Read this page first for benchmark-specific synthesis and decisions.

## Synthesis

- [Current synthesis](thesis.md) — corrected TDVP parity, frozen reversal through 32 qubits, and the remaining accuracy boundary.

## Ideas

- [Certified recoverability candidate](ideas/recoverability-candidate.md) — verified N=2,4 optima and one N=6 pilot; N=8 and difficulty calibration next.

- [Research frontier](ideas/research-frontier.md) — MPS engine, local shared controller, TDVP alternative, and resource-boundary study.

## Source coverage

- [Sources ledger](sources.yml) cites the global paper and companion-code knowledge; source files remain in the canonical paper bundle.

## Concepts

- [Weak-measurement quantum diffusion](../../../wiki/concepts/weak-measurement-quantum-diffusion.md)
- [Trajectory versus ensemble recovery](../../../wiki/comparisons/trajectory-vs-ensemble-recovery.md)

## Methods and comparisons

- [Benchmark task](../problem/TASK.md) defines MPS, TEBD/TDVP, oracle-versus-record ablations, and train-short-test-long evaluation.

## Implementations

- [Corrected TDVP controller and transfer boundary](implementations/corrected-tdvp-controller.md) — numerical repair and evidence through 32 qubits.

- [Companion implementation](../../../wiki/implementations/liu-quantum-diffusion-companion.md) is the dense parity baseline, not a scalable implementation.
- [[implementations/dense-qr-controller-reference|Dense QR trajectory-controller reference]] — completed Lab 001 baseline, exact refactor seam, held-out loss/fidelity, and explicit non-scalability boundary.

## Open questions

- [Scalable trajectory reversal](questions/scalable-trajectory-reversal.md)
