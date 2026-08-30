---
title: Material-facing DQCP diagnostics
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/lee2019soadp/paper.pdf
idea_ids: []
topics:
- Correlated Systems
- Topological Phases
---

# Material-facing DQCP diagnostics

**Summary**: Candidate deconfined criticality in a quantum magnet can be triangulated from phase structure, symmetry-resolved transfer spectra, and lattice-selected spectroscopic continua.

**Sources**: [Lee et al. (2019)](../../papers/lee2019soadp/paper.pdf)

**Last updated**: 2026-08-23

---

## Numerical and symmetry diagnostics

For the Shastry–Sutherland model, infinite-cylinder DMRG resolves a twofold plaquette-VBS phase between dimer and Néel orders and a potentially continuous pVBS–Néel boundary. Near that boundary, singlet and triplet correlation-length levels approach degeneracy, as expected if Néel and pVBS components rotate under an emergent (O(4)) symmetry [Lee et al. (2019), §II](../../papers/lee2019soadp/paper.pdf#page=3).

Space-group analysis determines which monopole perturbations are allowed and explains why the leading anisotropy differs from square-lattice realizations. The nonsymmorphic structure also creates diffraction extinction points where ordinary elastic weight vanishes but deconfined spinon continua should remain visible in magnon and phonon spectra [Lee et al. (2019), §§III–V and VII](../../papers/lee2019soadp/paper.pdf#page=5).

## Scale-dependent boundary

The largest simulated circumference is ten sites, so an ultimately weak first-order transition cannot be excluded. Weak interlayer coupling may also drive the material's zero-temperature transition first order. The predicted DQCP spectra can nevertheless survive above the small gap scale and below the inverse in-plane correlation length, making the claim explicitly dependent on the experimental energy and temperature window [Lee et al. (2019), §§VI–VIII](../../papers/lee2019soadp/paper.pdf#page=12).

## Benchmark hooks

- Extract symmetry-resolved transfer-matrix levels across cylinder widths and quantify multiplet convergence.
- Derive monopole quantum numbers from a nonsymmorphic space group and enumerate allowed anisotropies.
- Compute neutron and phonon structure factors at ordinary and extinction momenta.
- Fit one dataset to continuous, weak-first-order, and crossover scenarios with explicit resolution windows.

## Related pages

- [[methods/emergent-symmetry-current-diagnostics|Emergent-symmetry current diagnostics]]
- [[topics/topological-phase-transitions|Topological phase transitions]]
- [[concepts/self-duality-protected-multicriticality|Self-duality-protected multicriticality]]
- [[papers/lee2019soadp|Signatures of a deconfined phase transition on the Shastry-Sutherland lattice]]
