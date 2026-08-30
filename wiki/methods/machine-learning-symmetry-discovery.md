---
title: Machine-learning symmetry discovery
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/hou2026mlsdf/paper.pdf
idea_ids: []
topics:
- Machine Learning
- Correlated Systems
---

# Machine-learning symmetry discovery

**Summary**: Conserved quantities and their continuous Lie algebra can be learned jointly from canonical phase-space trajectories by combining neural observables with Poisson-bracket conservation, closure, and independence constraints.

**Sources**: [Hou et al. (2026)](../../papers/hou2026mlsdf/paper.pdf)

**Last updated**: 2026-08-23

---

## Current synthesis

Machine-Learning Symmetry Discovery (MLSD) assigns a separate neural network to each candidate conserved quantity and learns antisymmetric structure coefficients at the same time. Its objective asks the generators to Poisson-commute with the Hamiltonian, close under Poisson brackets, and remain functionally independent rather than collapsing onto repeated invariants [Hou et al. (2026), §II.B](../../papers/hou2026mlsdf/paper.pdf#Sec.II.B).

The symmetry dimension is not assumed known. The method trains several candidate dimensions with multiple random seeds and uses the separation of converged closure losses as a practical model-selection diagnostic. Lie-algebra identity is evaluated only up to a basis transformation, using structure-coefficient matching or Killing-form spectra [Hou et al. (2026), §II.C and App.B](../../papers/hou2026mlsdf/paper.pdf#Sec.II.C-and-App.B).

On clean simulated trajectories, the reported experiments recover the hidden (so(4)) algebra of the three-dimensional Kepler problem and the (su(3)) algebra of the isotropic three-dimensional harmonic oscillator [Hou et al. (2026), §III](../../papers/hou2026mlsdf/paper.pdf#Sec.III).

## Validation boundary

The evidence is deliberately restricted to integrable systems with canonical coordinates and globally defined compact invariants. Network expressivity, the independence regularizer, phase-space coverage, and optimization variability can all change the recovered algebra. Narrow data from KAM islands or chaotic subsets may identify only a local effective algebra; noisy observations, mixed dynamics, and formal uncertainty-calibrated dimension selection remain open [Hou et al. (2026), §IV.B-C](../../papers/hou2026mlsdf/paper.pdf#Sec.IV.B-C).

This differs from [[methods/systematic-fermion-symmetry-analysis|systematic fermion symmetry analysis]], which derives symmetries from a known Hamiltonian's operator algebra, and from [[methods/machine-learning-renormalization-group|machine-learning renormalization group]], which learns scale transformations rather than conserved generators.

## Benchmark opportunities

- Recover known algebras under controlled observation noise, incomplete canonical coordinates, and restricted phase-space coverage.
- Distinguish global symmetry from region-dependent effective symmetry across regular, KAM, and chaotic regimes.
- Compare loss-gap dimension selection with calibrated hypothesis tests and uncertainty estimates.
- Test whether learned generators transfer across energies, initial-condition families, or weak integrability-breaking perturbations.

## Related pages

- [[papers/hou2026mlsdf|Machine learning symmetry discovery for integrable Hamiltonian dynamics]]
- [[methods/systematic-fermion-symmetry-analysis|Systematic fermion symmetry analysis]]
- [[methods/machine-learning-renormalization-group|Machine-learning renormalization group]]
- [[topics/machine-learning-and-physics|Machine learning and physics]]
