---
title: Dynamical signatures of compact QED3
page_type: concept
status: provisional
updated: 2026-08-23
source_refs:
- papers/wang2019docqe/paper.pdf
idea_ids: []
topics:
- Correlated Systems
- Topological Phases
---

# Dynamical signatures of compact QED3

**Summary**: Spin and dimer continua distinguish a deconfined Dirac-spinon phase from a gapped VBS phase in a fermion-coupled compact (U(1)) lattice gauge theory.

**Sources**: [Wang et al. (2019)](../../papers/wang2019docqe/paper.pdf)

**Last updated**: 2026-08-23

---

## Spectral evidence chain

Determinantal QMC samples a (2+1)-dimensional compact (U(1)) rotor gauge field coupled to (N_f=8) fermions. Imaginary-time spin and dimer correlations are analytically continued with stochastic analytic continuation to momentum-resolved spectra [Wang et al. (2019), §II](../../papers/wang2019docqe/paper.pdf#page=3).

In the weak-fluctuation deconfined phase, broad continua in both channels are interpreted as fractionalized Dirac spinons coupled to an emergent gauge field. Near the U1D–VBS boundary, gapless dimer fluctuations at ((\pi,0)) are consistent with QED(_3)–Gross–Neveu chiral-(O(2)) criticality. In the confined VBS phase, a zero-frequency Bragg contribution is separated from a gapped continuum using a weak pinning field [Wang et al. (2019), §§III–IV](../../papers/wang2019docqe/paper.pdf#page=5).

## Validation boundary

The calculation is at large finite flavor and system sizes only up to roughly (L=20); it does not establish the small-(N_f) regime or accurate critical exponents. Stochastic analytic continuation is ill-conditioned and can blur gaps, sharp modes, and thresholds, particularly when a Bragg delta peak coexists with a continuum. Spectral interpretation should therefore be cross-checked against imaginary-time data, sum rules, alternative continuation priors, and finite-size trends.

## Benchmark hooks

- Reconstruct synthetic spectra containing a delta peak, gap, and continuum to calibrate SAC resolution and bias.
- Track spin/dimer spectral weight and gap estimates across the confinement transition and lattice sizes.
- Compare continuum thresholds with free-spinon and gauge-dressed field-theory predictions.
- Repeat across fermion flavor to test where the deconfined phase and QED(_3)-GN interpretation persist.

## Related pages

- [[topics/quantum-spin-liquids|Quantum spin liquids]]
- [[methods/material-facing-dqcp-diagnostics|Material-facing DQCP diagnostics]]
- [[methods/emergent-symmetry-current-diagnostics|Emergent-symmetry current diagnostics]]
- [[papers/wang2019docqe|Dynamics of compact quantum electrodynamics at large fermion flavor]]
