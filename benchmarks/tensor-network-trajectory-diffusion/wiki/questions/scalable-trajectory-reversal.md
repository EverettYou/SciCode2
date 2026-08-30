---
title: Scalable trajectory reversal
page_type: question
status: open
updated: '2026-08-23'
source_refs:
- wiki/papers/liu2025mqdm.md
- problem/TASK.md
- labs/lab-001-local-controller-feasibility/REPORT.md
idea_ids:
- x-001
- c-002
- k-001
- k-002
- x-002
- c-004
---

# Scalable trajectory reversal

**Summary**: Can bounded-range, record-conditioned tensor-network feedback learned on short chains reproduce weak-measurement trajectory distributions on longer chains?

**Sources**: [MQDM paper synthesis](../../../../wiki/papers/liu2025mqdm.md); [benchmark task](../../problem/TASK.md); [completed Lab 001](../../labs/lab-001-local-controller-feasibility/REPORT.md)

**Last updated**: 2026-08-23

---

## Current synthesis

The dense companion policy uses the full future record and emits a global QR-parameterized unitary [implementation analysis](../../../../wiki/implementations/liu-quantum-diffusion-companion.md). A scalable replacement can reuse QR inside each gate on at most $R$ consecutive sites, then compose such blocks across the chain. The open problem is whether bounded-support composition succeeds when $N>R$, and how the required $R$, temporal window $W$, and MPS environment information change with size. No bounded locality is assumed.

Lab 001 now supplies the frozen low-qubit reference and exact encoder/QR seam needed to isolate that question. It also shows why the first controller experiment must use $N>R$: at $N\leq R$, a generic QR block covers the whole system and a renamed local head cannot discriminate locality [Lab 001 search decision](../../labs/lab-001-local-controller-feasibility/REPORT.md#search-decision). The observed $N=1,2$ loss and fidelity are behavioral baselines only, not evidence that bounded-range control will work.

## Open questions

- For the first dense $N>R$ test, what block schedule and record interface isolate controller range from record decoding under matched resource budgets?
- Which predeclared state families are informative for locality, and which saturate at $R=1$ or lie outside the full-controller capacity?
- How does performance change as the maximum contiguous support $R=1,2,3,\ldots$ is varied below $N$?
- Does an optional Hamiltonian/Trotter parameterization offer any benefit over generic QR block gates at matched support and applied-gate cost?
- How much future record is needed for one-step and autoregressive reversal?
- When does reduced-state accuracy imply acceptable trajectory-distribution accuracy, if ever?
- Is differentiable TEBD sufficient, or is a tangent-space TDVP score flow materially better?
- Which Quimb execution path preserves useful gradients after MPS gate splitting and bond truncation?
- Which resource first grows at the failure boundary: $\chi$, $R$, $W$, data, or optimization time?
- Which evaluation normalization makes reverse loss comparable across $N$, given Lab 001's lower $N=2$ loss but lower fidelity?

## Related pages

- [Current synthesis](../thesis.md)
- [Research frontier](../ideas/research-frontier.md)
- [[implementations/dense-qr-controller-reference|Dense QR trajectory-controller reference]]
