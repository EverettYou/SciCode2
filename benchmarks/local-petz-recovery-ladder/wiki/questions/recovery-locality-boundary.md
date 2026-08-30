---
title: Petz gap and the Markov-length transition
page_type: question
status: open
updated: '2026-08-22'
source_refs:
- wiki/papers/liu2025mqdm.md
- problem/TASK.md
idea_ids:
- x-003
- k-004
- k-005
---

# Petz gap and the Markov-length transition

**Summary**: Does the minimum support radius needed for local Petz recovery to match global Petz behave as a critical length and locate the same mixed-state transition as CMI?

**Sources**: [MQDM paper synthesis](../../../../wiki/papers/liu2025mqdm.md); [benchmark task](../../problem/TASK.md)

**Last updated**: 2026-08-22

---

## Current synthesis

Finite Markov length motivates exponential convergence of local recovery with radius, while a divergent length implies that no fixed-radius recovery remains uniformly accurate. The benchmark turns this into $r_\varepsilon(g,L)$ [Benchmark task specification, Primary-observable](../../problem/TASK.md#Primary-observable).

A 1D model qualifies only if CMI establishes an interior finite-parameter divergence. Otherwise, the decohered toric code is the primary model and 1D families are controls.

## Evidence and tensions

- Finite CMI controls local recoverability and the cited toric-code transition has divergent Markov length [Global MQDM knowledge page, compiled-knowledge](../../../../wiki/papers/liu2025mqdm.md#compiled-knowledge).
- The relation between global Petz, local Bayesian truncation, and logical decoding must be derived for the chosen Pauli model.
- $r_\varepsilon$ can saturate at system size, so fits must separate truncation from true divergence.

## Open questions

- Is there a source-supported equal-time 1D model with an interior Markov-length transition?
- Do CMI and Petz-gap estimates of $g_c$ and $\nu$ agree within uncertainty?
- Which recovered-output distance preserves the scalable commuting equivalence?

## Related pages

- [[wiki/concepts/finite-markov-length|Finite Markov length]]
- [[wiki/methods/twirled-petz-recovery|Twirled Petz recovery]]
- [Current synthesis](../thesis.md)
- [Research frontier](../ideas/research-frontier.md)
