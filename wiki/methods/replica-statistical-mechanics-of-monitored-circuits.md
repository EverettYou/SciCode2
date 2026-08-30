---
title: Replica statistical mechanics of monitored circuits
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/jian2020mcirq/paper.pdf
idea_ids: []
topics:
- Quantum Information
---

# Replica statistical mechanics of monitored circuits

**Summary**: Averaged Rényi observables in monitored Haar-random circuits map to a two-dimensional permutation-spin model, turning an area-to-volume-law entanglement transition into an ordering transition with conformal scaling.

**Sources**: [Jian et al. (2020)](../../papers/jian2020mcirq/paper.pdf)

**Last updated**: 2026-08-23

---

## Replica mapping

The nonlinear trajectory average for Rényi entropy is represented with (Q=nm+1) replicas followed by (m\to0). Haar averaging converts circuit gates into permutation-valued degrees of freedom, while measurement outcomes set local statistical weights. Entanglement boundary conditions insert permutation domain walls, so the entropy becomes a free-energy difference in a two-dimensional statistical-mechanics model [Jian et al. (2020), §§II–III](../../papers/jian2020mcirq/paper.pdf#page=2).

Low measurement rate favors an ordered phase and a domain-wall cost proportional to subsystem length, corresponding to volume-law entanglement. High measurement rate disorders the model and screens the boundary domain wall, giving area-law entanglement. At a continuous transition, boundary-condition-changing operators imply logarithmic entropy and mutual information determined by a conformal cross ratio [Jian et al. (2020), §IV](../../papers/jian2020mcirq/paper.pdf#page=6).

## Percolation limit and finite-d boundary

At infinite on-site dimension, the weights reduce to a (Q!\)-state Potts model and then, under the replica limit, to bond percolation with (p_c=1/2). A careful boundary-layer treatment gives (\overline S_{n,A}=\frac13\log L_A+\cdots) for periodic boundaries and every integer (n\ge1); this result is not captured by the zeroth-Rényi minimal-cut picture alone [Jian et al. (2020), §V](../../papers/jian2020mcirq/paper.pdf#page=7).

This exact percolation description is not generic at finite (d). Finite-(d) corrections reduce the enlarged permutation symmetry and introduce a relevant two-hull perturbation, so the infrared theory should be a different, then-unidentified CFT rather than ordinary percolation [Jian et al. (2020), §§VI–VII](../../papers/jian2020mcirq/paper.pdf#page=9).

## Validation boundary

The derivation averages over Haar gates and measurement realizations and relies on replica continuation; it does not predict individual circuit trajectories. Conformal formulas assume a continuous transition. The exact coefficient and (p_c=1/2) belong to (d=\infty), while finite local Hilbert space requires independent numerical or analytic identification of its universality class.

## Benchmark hooks

- Derive the permutation-spin weights for a small replica number and verify them by exact Haar integration.
- Collapse entropy and mutual-information data against the CFT finite-size forms while testing corrections to scaling.
- Compare (S_0) minimal-cut observables with (S_{n\ge1}) replica observables in the large-(d) limit.
- Track the crossover away from percolation as finite-(d) symmetry-breaking terms are introduced.

## Related pages

- [[topics/random-quantum-circuits-and-measurements|Random quantum circuits and measurements]]
- [[concepts/self-organized-error-correction|Self-organized error correction in monitored circuits]]
- [[methods/hybrid-circuit-classical-shadows|Hybrid-circuit classical shadows]]
- [[methods/entanglement-feature-dynamics|Entanglement-feature dynamics]]
- [[papers/jian2020mcirq|Measurement-induced criticality in random quantum circuits]]
