---
title: Intervalley coherence
page_type: concept
status: provisional
updated: 2026-08-23
source_refs:
- papers/you2022ksaic/paper.pdf
- papers/you2019sfvfa/paper.pdf
idea_ids: []
topics:
- Correlated Systems
---

# Intervalley coherence

**Summary**: Intervalley coherence hybridizes electronic valleys and reconstructs nested Fermi surfaces, while fluctuations of the same channel can mediate nearby intervalley superconductivity.

**Sources**: [You and Vishwanath (2019)](../../papers/you2019sfvfa/paper.pdf); [You and Vishwanath (2022)](../../papers/you2022ksaic/paper.pdf)

**Last updated**: 2026-08-23

---

## Order and Fermi-surface reconstruction

The IVC order parameter \(c_K^\dagger\sigma^\mu c_{K'}\) transfers the large valley momentum. It is uniform in the low-energy valley description at optimal nesting but appears as a Kekulé-scale charge- or spin-density modulation microscopically. In the RTG RPA calculation it is the leading local bilinear instability near the relevant Van Hove singularities [You and Vishwanath (2022), §§Interaction-and-IVC](../../papers/you2022ksaic/paper.pdf#page=3).

IVC hybridizes the two valley Fermi surfaces, partially gaps the VHS, and can double the shared Fermi-sea area rather than produce a full insulator. That reconstruction offers one explanation for a doubled quantum-oscillation frequency and leaves residual Fermi surfaces available for secondary density-wave or pairing instabilities [You and Vishwanath (2022), §Inter-Valley-Coherence](../../papers/you2022ksaic/paper.pdf#page=4).

## Relation to pairing

In weak-coupling twisted bilayer graphene slightly away from the magic angle, triangular opposite-valley Fermi pockets have parallel nested segments. RPA enhances valley fluctuations and yields leading zero-momentum intervalley pairing with symmetry-mixed chiral \(d+id/p-ip\) or helical form factors. Approximate \(SU(2)_K\times SU(2)_{K'}\simeq SO(4)\) makes spin-singlet and triplet pairs degenerate before Hund-type perturbations select between them [You and Vishwanath (2019), §§I–III](../../papers/you2019sfvfa/paper.pdf#page=2).

The same intervalley nesting enhances zero-momentum pairing between time-reversed valleys. In a two-patch one-loop flow, a small Hund term breaks the approximate \(SO(4)\) degeneracy between spin-singlet and spin-triplet sectors. With antiferromagnetic \(J_H\), the leading instability is intervalley spin-singlet s-wave pairing, and VHS double-logarithmic flow yields \(T_c\sim\Lambda\exp[-1/\sqrt{\nu_0V_{\mathrm{eff}}}]\) [You and Vishwanath (2022), §Superconductivity](../../papers/you2022ksaic/paper.pdf#page=4).

## Evidence boundary

The IVC boundary is an RPA/mean-field instability and does not include competing Stoner spin/valley polarization. The tBLG construction assumes weak coupling away from the most strongly correlated magic-angle regime; its commensurate IVCW fully gaps a filling displaced from half filling, and dispersion renormalization needed to move that gap is outside the treatment [You and Vishwanath (2019), §III](../../papers/you2019sfvfa/paper.pdf#page=12). The RTG superconducting mechanism likewise assumes weak coupling, patch reduction, and a doping-dependent sign of \(J_H\) that requires microscopic calculation. Phase-boundary agreement and Pauli-limit consistency support these scenarios but do not uniquely identify IVC or pairing symmetry [You and Vishwanath (2022), §Discussion](../../papers/you2022ksaic/paper.pdf#page=5).

## Benchmark hooks

- Reproduce the IVC susceptibility map directly from the two-band RTG dispersion.
- Compare RPA, two-patch RG, and symmetry-complete hot-spot RG under identical parameters.
- Add Stoner channels and determine whether IVC survives unbiased channel competition.
- Infer the sign and doping dependence of intervalley Hund coupling from a microscopic screened interaction.
- Compare tBLG RPA and RTG patch-RG flows under controlled changes of pocket geometry, nesting, and \(SO(4)\)-breaking interactions.

## Related pages

- [[methods/symmetry-complete-hot-spot-rg|Symmetry-complete hot-spot renormalization group]]
- [[topics/unconventional-superconductivity|Unconventional superconductivity]]
- [[papers/you2022ksaic|Kohn-Luttinger superconductivity and intervalley coherence in rhombohedral trilayer graphene]]
- [[papers/you2019sfvfa|Superconductivity from valley fluctuations and approximate SO(4) symmetry in twisted bilayer graphene]]
