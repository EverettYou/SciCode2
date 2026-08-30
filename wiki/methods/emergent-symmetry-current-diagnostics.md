---
title: Emergent-symmetry current diagnostics
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/huang2019esacc/paper.pdf
idea_ids: []
topics:
- Topological Phases
- Correlated Systems
---

# Emergent-symmetry current diagnostics

**Summary**: Emergent continuous symmetry at a critical point can be tested jointly through symmetry-related operator dimensions and the protected scaling of microscopic conserved-current candidates.

**Sources**: [Huang et al. (2019)](../../papers/huang2019esacc/paper.pdf)

**Last updated**: 2026-08-23

---

## Field-theory-to-lattice protocol

For a spin-chain transition between VBS and (z)-ferromagnetic phases, an anisotropic (O(4)) nonlinear sigma model with a level-1 WZW term predicts two emergent (O(2)) rotations. Bosonization expresses their order parameters and Noether currents in lattice-accessible channels, while one Luttinger parameter constrains the family of critical dimensions [Huang et al. (2019), §§II and V](../../papers/huang2019esacc/paper.pdf#page=3).

Infinite-MPS finite-entanglement scaling locates the critical point and estimates central charge and operator dimensions. Equal dimensions within each proposed symmetry multiplet are one check; a stronger check identifies current correlators whose scaling dimension is fixed to (Delta=1) by charge conservation. The reported fits give current-correlation exponents near 2 and mutually consistent Luttinger parameters [Huang et al. (2019), §§III–VI](../../papers/huang2019esacc/paper.pdf#page=5).

## Validation boundary

This is a controlled one-dimensional Luttinger-liquid example, not proof that the same current operators diagnose higher-dimensional or weakly first-order DQCPs. Finite bond dimension, subleading oscillatory components, fitting windows, and microscopic operator mixing can mimic or obscure degeneracies. A convincing test should require both multiplet structure and current conservation across systematic scaling ranges.

## Benchmark hooks

- Recover the critical coupling, central charge, Luttinger parameter, and all linked exponents from finite-entanglement data.
- Infer microscopic current operators from a proposed emergent action and test their exact dimensions independently.
- Perturb explicit symmetries to distinguish robust emergent multiplets from accidental exponent crossings.
- Compare current-based diagnostics with histogram or order-parameter-only claims near weakly first-order transitions.

## Related pages

- [[topics/topological-phase-transitions|Topological phase transitions]]
- [[concepts/self-duality-protected-multicriticality|Self-duality-protected multicriticality]]
- [[concepts/intrinsically-gapless-topological-states|Intrinsically gapless topological states]]
- [[papers/huang2019esacc|Emergent symmetry and conserved current at a one-dimensional incarnation of deconfined quantum critical point]]
