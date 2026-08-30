---
title: Green-function zero surfaces
page_type: concept
status: provisional
updated: 2026-08-23
source_refs:
- papers/lu2023gfzif/paper.pdf
idea_ids: []
topics:
- Correlated Systems
---

# Green-function zero surfaces

**Summary**: In a symmetry-preserving interacting insulator, zeros of the single-particle Green's function can retain the Luttinger volume of a parent Fermi surface after low-energy quasiparticle poles disappear.

**Sources**: [Lu et al. (2023)](../../papers/lu2023gfzif/paper.pdf)

**Last updated**: 2026-08-23

---

## Pole-to-zero diagnostic

For the bilayer square-lattice Fermi-surface SMG model, translation and charge conservation preserve the Luttinger count while the gapped, nondegenerate SMG state has no low-energy quasiparticle poles. The sign-changing zero-frequency Green's function therefore realizes the required Fermi volume through a surface of zeros [Lu et al. (2023), §II.B](../../papers/lu2023gfzif/paper.pdf#page=3).

Strong-coupling cluster perturbation produces gapped poles near \(\omega=\pm J\) and a narrow zero dispersion with bandwidth \(w_{\mathrm{zero}}\sim J^{-2}\). A separate weak-coupling treatment of phase-disordered bilinear order also yields a zero crossing at the parent Fermi surface after symmetry restoration [Lu et al. (2023), §III](../../papers/lu2023gfzif/paper.pdf#page=5).

## What is robust

Luttinger constraints protect the enclosed volume under the stated translation and charge symmetries. Exact coincidence of the zero-surface shape with the noninteracting Fermi surface additionally uses particle–hole and reflection symmetries of the chosen square-lattice model; generic symmetry-preserving hopping perturbations can deform the shape [Lu et al. (2023), §II.C](../../papers/lu2023gfzif/paper.pdf#page=4).

The zero is not measured directly by ARPES. The proposed route reconstructs \(\operatorname{Re}G\) from the measured spectral function through a Kramers–Kronig transform. In the model calculation, broadening changes the zero dispersion but not its zero-frequency surface [Lu et al. (2023), §IV](../../papers/lu2023gfzif/paper.pdf#page=7). Experimental feasibility still depends on frequency coverage, background subtraction, and reconstruction stability.

## Benchmark hooks

- Reproduce poles and zeros from exact cluster Green's functions, then quantify cluster-perturbation error.
- Break particle–hole symmetry while preserving translation and charge, and test volume preservation versus shape deformation.
- Stress-test Kramers–Kronig zero reconstruction under finite windows, noise, and dissipation.
- Distinguish an SSB gap from a symmetry-restored SMG gap using basis-independent matrix Green-function diagnostics.

## Related pages

- [[concepts/fermi-surface-anomalies|Fermi-surface anomalies]]
- [[concepts/symmetric-mass-generation|Symmetric mass generation]]
- [[comparisons/smg-regimes-and-diagnostics|SMG regimes and diagnostics]]
- [[papers/lu2023gfzif|Green's function zeros in Fermi surface symmetric mass generation]]
