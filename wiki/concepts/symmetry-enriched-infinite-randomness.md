---
title: Symmetry-enriched infinite-randomness criticality
page_type: concept
status: provisional
updated: 2026-08-23
source_refs:
- papers/duque2021tasrq/paper.pdf
idea_ids: []
topics:
- Topological Phases
- Quantum Information
---

# Symmetry-enriched infinite-randomness criticality

**Summary**: Strong-disorder fixed points with identical local bulk scaling can remain topologically distinct because symmetry acts differently on nonlocal operators and boundary modes.

**Sources**: [Duque et al. (2021)](../../papers/duque2021tasrq/paper.pdf)

**Last updated**: 2026-08-23

---

## Bulk equivalence, boundary distinction

Random Ising and symmetry-enriched random Ising★ chains flow to the same infinite-randomness bulk fixed point under periodic boundary conditions. They differ by the time-reversal charge of the nonlocal disorder operator, \(T\mu T=\pm\mu\), and therefore by boundary conditions and protected edge structure [Duque et al. (2021), §§Random-Ising-transition and SBRG-results](../../papers/duque2021tasrq/paper.pdf#page=2).

SBRG calculations find the expected common bulk correlation exponent while boundary–bulk correlations separate the two classes. At Ising★, boundary magnetization remains finite as its probe field vanishes and the edge-state splitting decays parametrically faster than the bulk gap. This is a topological distinction invisible to local periodic-bulk diagnostics [Duque et al. (2021), §SBRG-results](../../papers/duque2021tasrq/paper.pdf#page=3).

## Critical phase and Floquet extensions

A decorated-domain-wall construction twists a random XXZ singlet phase with gapped auxiliary spins. The bulk retains random-singlet criticality, while DMRG supports exponentially localized edge modes protected by the auxiliary gap [Duque et al. (2021), §Symmetry-enriched-random-singlet-phase](../../papers/duque2021tasrq/paper.pdf#page=3).

Related Floquet Ising transitions inherit an emergent \(Z_2\) from discrete time translation, yielding symmetry-enriched random critical boundaries next to the \(0\pi\) paramagnet [Duque et al. (2021), §Floquet-Ising-criticality](../../papers/duque2021tasrq/paper.pdf#page=4). This relies on a localized driven regime; generic interacting thermalization can remove the sharp MBL phase structure.

## Validation boundary

SBRG is asymptotically controlled at strong disorder but approximate at finite disorder. DMRG averages require large disorder ensembles and finite bond dimension. The demonstrated constructions are one-dimensional; extension to higher-dimensional strong-randomness fixed points remains an open proposal.

## Benchmark hooks

- Reproduce local bulk equivalence while resolving distinct boundary exponents and edge splittings.
- Compare transfer-matrix, SBRG, and DMRG diagnostics on the free and interacting limits.
- Add symmetry-preserving boundary perturbations and quantify edge-mode localization length.
- Test Floquet edge protection against interaction-induced heating and finite drive duration.

## Related pages

- [[concepts/intrinsically-gapless-topological-states|Intrinsically gapless topological states]]
- [[concepts/symmetry-protected-topological-ensembles|Symmetry-protected topological ensembles]]
- [[topics/topological-phase-transitions|Topological phase transitions]]
- [[papers/duque2021tasrq|Topological and symmetry-enriched random quantum critical points]]
