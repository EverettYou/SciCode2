---
title: Dense QR trajectory-controller reference
page_type: implementation
status: active
updated: '2026-08-23'
source_refs:
- labs/lab-001-local-controller-feasibility/REPORT.md
- labs/lab-001-local-controller-feasibility/results/dense-qr-baseline-v1/summary-updates128.md
- labs/lab-001-local-controller-feasibility/results/dense-qr-reversal-fidelity-v1/summary.json
idea_ids:
- x-001
- c-002
- x-002
topics:
- Quantum Information
- Machine Learning
---

# Dense QR trajectory-controller reference

**Summary**: Lab 001 qualifies the companion dense-QR policy and an exactly equivalent encoder-plus-QR seam at one and two qubits. This is a reproducible low-qubit behavioral reference, not evidence for bounded-range locality or scaling.

**Sources**: [Lab 001 report](../../labs/lab-001-local-controller-feasibility/REPORT.md#findings); [loss summary](../../labs/lab-001-local-controller-feasibility/results/dense-qr-baseline-v1/summary-updates128.md); [fidelity results](../../labs/lab-001-local-controller-feasibility/results/dense-qr-reversal-fidelity-v1/summary.json)

**Last updated**: 2026-08-23

---

## Architecture and data flow

Frozen future-measurement records enter the unmodified companion `PolicyModel`, whose transformer encoder feeds a dense complex projection followed by the companion QR convention. The qualified refactor exposes that encoder/QR boundary without changing the emitted unitary, loss, or gradients [Lab 001 methods](../../labs/lab-001-local-controller-feasibility/REPORT.md#methods-and-execution).

## Interfaces

- Policy contract: `forward(m_future, dtype) -> U`.
- Frozen fixture: $N=1,2$, $\epsilon=0.5$, $T=6$, computational-zero initial state, and 256/64/64 train/validation/test records.
- Behavioral budget: 128 Adam updates, batch size 16, learning rate $10^{-3}$, and three initialization seeds per size.
- Future bounded-block seam: emit generic QR-parameterized unitaries on at most $R$ contiguous sites, then compose them across a chain. This remains untested when $N>R$.

## Algorithm and conventions

The held-out evaluator reconstructs each normalized forward final state and applies the companion `trajectory_reversal` convention for $T-1=5$ updates toward $\lvert0\rangle$. QR remains an internal fixed-block parameterization; locality is imposed only by support and composition when $N>R$ [Lab 001 search decision](../../labs/lab-001-local-controller-feasibility/REPORT.md#search-decision).

## Evidence and failure modes

The original and refactored policies agree exactly on compared complex128 unitaries, losses, and parameter gradients at both qualified sizes. Across three seeds, held-out test loss is $0.022626974\pm0.000011772$ at $N=1$ and $0.002370824\pm0.000000017$ at $N=2$ [loss checkpoint](../../labs/lab-001-local-controller-feasibility/results/dense-qr-baseline-v1/summary-updates128.md). Mean held-out reversal fidelity is $0.652636\pm0.022455$ and $0.420085\pm0.005803$, respectively, with broad per-trajectory spread [fidelity records](../../labs/lab-001-local-controller-feasibility/results/dense-qr-reversal-fidelity-v1/summary.json).

These results do not establish convergence, cross-size comparability of the reverse loss, bounded-range control, MPS correctness, or transfer. The lower $N=2$ loss alongside lower fidelity is an explicit warning not to interpret raw loss across sizes without calibration [Lab 001 limitations](../../labs/lab-001-local-controller-feasibility/REPORT.md#analysis-and-limitations).

## Paper and method mapping

- [Companion implementation](../../../../wiki/implementations/liu-quantum-diffusion-companion.md) — reproduced-behavior-of.
- [[questions/scalable-trajectory-reversal|Scalable trajectory reversal]] — motivates the first nontrivial $N>R$ test.

## Related pages

- [[thesis|Current synthesis]]
- [[ideas/research-frontier|Research frontier]]
- [[questions/scalable-trajectory-reversal|Scalable trajectory reversal]]
