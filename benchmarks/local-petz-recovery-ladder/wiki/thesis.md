---
title: Current synthesis
page_type: thesis
status: provisional
updated: '2026-08-22'
source_refs:
- wiki/papers/liu2025mqdm.md
- problem/TASK.md
idea_ids:
- x-003
- k-004
- c-003
---

# Current synthesis

**Summary**: The scientifically meaningful quantity is the recovery radius required to match global Petz and whether that radius diverges with the CMI Markov length at a mixed-state transition.

**Sources**: [MQDM paper synthesis](../../../wiki/papers/liu2025mqdm.md); [benchmark task](../problem/TASK.md)

**Last updated**: 2026-08-22

---

## Current synthesis

The source paper makes local recovery error contingent on finite Markov length and cites the Sang--Hsieh result connecting Markov-length divergence to a mixed-state decodability transition [Global MQDM knowledge page, compiled-knowledge](../../../wiki/papers/liu2025mqdm.md#compiled-knowledge). This motivates using the local-global Petz gap as a candidate critical observable and comparing its recovery length with CMI scaling [Benchmark task specification, Primary-observable](../problem/TASK.md#Primary-observable).

The previous 1D TFIM design was insufficient: criticality of the initial pure Hamiltonian does not imply a diverging mixed-state Markov length. A 1D GHZ family supplies an endpoint or nonlocal-recovery control, while the source-supported finite-noise example is the 2D toric code under decoherence. Model selection therefore precedes scale-up.

## Strongest support

- Finite CMI across a buffer guarantees approximate local recoverability; divergence obstructs a fixed recovery radius.
- The decohered toric-code decodability transition has a source-supported divergent Markov length and random-bond-Ising representation.
- In commuting Pauli models, Petz recovery can be represented as classical Bayesian reversal, subject to benchmark verification.

## Tensions and alternatives

- Long-range CMI in a 1D constrained or GHZ state is not automatically a finite-parameter transition.
- Spacetime repetition-code thresholds are alternatives, but their Markov length is spacetime rather than equal-time spatial length.
- Petz-gap and CMI scaling may share a critical point but have different finite-size corrections.

## Frontier

Lab 001 first decides whether any 1D candidate qualifies. If not, it validates the commuting Petz/Bayesian reduction on a small toric code and opens the 2D scaling lab. See [[questions/recovery-locality-boundary|Petz gap and the Markov-length transition]] and [Research frontier](ideas/research-frontier.md).

## Related pages

- [[wiki/concepts/finite-markov-length|Finite Markov length]]
- [[wiki/methods/twirled-petz-recovery|Twirled Petz recovery]]
- [[wiki/comparisons/global-vs-local-petz|Global versus local Petz recovery]]
