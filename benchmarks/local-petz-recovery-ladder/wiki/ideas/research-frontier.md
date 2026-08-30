---
title: Petz-gap criticality research frontier
page_type: ideas
status: provisional
updated: '2026-08-22'
source_refs:
- wiki/papers/liu2025mqdm.md
- problem/TASK.md
idea_ids:
- x-001
- c-001
- k-001
- c-002
- k-002
- k-003
- x-002
- x-003
- k-004
- c-003
- k-005
- c-004
---

# Petz-gap criticality research frontier

**Summary**: The active search asks whether the recovery radius needed for local Petz to match global Petz is a critical length scale. Model qualification precedes implementation scale-up.

**Sources**: [MQDM paper synthesis](../../../../wiki/papers/liu2025mqdm.md); [benchmark task](../../problem/TASK.md)

**Last updated**: 2026-08-22

---

The frontier makes model qualification a prerequisite for Petz-gap scaling and defines the operational recovery length in the benchmark task [Benchmark task specification, Model-selection-gate-and-Primary-observable](../../problem/TASK.md#Model-selection-gate-and-Primary-observable).

## Active ideas

- **x-003 · cross · active** — Define $\Delta_R(r,g,L)$ and $r_\varepsilon(g,L)$ as transition diagnostics and test common scaling with CMI Markov length.
- **k-004 · knowledge · active** — Determine whether a suitable equal-time 1D mixed-state family has a finite interior parameter where Markov length diverges.
- **c-003 · code · active** — Derive and validate the reduction of commuting twirled Petz recovery to a Bayesian reverse channel.

## Qualified default branch

- **k-005 · knowledge · frontier** — Use the decohered toric-code decodability transition if 1D qualification fails.
- **c-004 · code · frontier** — Scale with stabilizer enumeration, random-bond-Ising tensor contraction, and Monte Carlo.

## Preserved but superseded branches

- **x-001 · cross · pruned** — The original exact-to-local 1D ladder was method-centered and did not establish a transition.
- **c-001 · code · kept** — Dense Petz construction remains useful for smallest-system validation.
- **k-001 · knowledge · kept** — CMI remains the independent locality diagnostic.
- **k-003 · knowledge · pruned** — The pure 1D TFIM point is not a mixed-state critical anchor without CMI scaling.
- **c-002 · code · pruned** — Generic MPS scale-up is not the next step for the qualified commuting model.
- **k-002 · knowledge · kept** — Diagnostic disagreement remains relevant.
- **x-002 · cross · pruned** — Adaptive 1D MPS windows depended on an unqualified transition.

## Decision rules

- Promote a 1D model only with an interior critical parameter, growing $\xi_M$, and stable finite-size evidence.
- Otherwise select the 2D toric-code model without treating the negative 1D result as failure.
- Distill code only after dense or commuting overlap and full-radius equality pass.

## Related pages

- [Current synthesis](../thesis.md)
- [[questions/recovery-locality-boundary|Petz gap and the Markov-length transition]]
