---
title: Vestigial and charge-4e superconducting order
page_type: concept
status: provisional
updated: 2026-08-23
source_refs:
- papers/zeng2024htsbn/paper.pdf
idea_ids: []
topics:
- Correlated Systems
---

# Vestigial and charge-4e superconducting order

**Summary**: Phase fluctuations of two nearly degenerate pairing channels can order a composite relative or total phase before ordinary charge-2e superconducting coherence appears.

**Sources**: [Zeng et al. (2024)](../../papers/zeng2024htsbn/paper.pdf)

**Last updated**: 2026-08-23

---

## Composite phase variables

For gaps \(\Delta_a=|\Delta_a|e^{i\theta_a}\), a second-order Josephson term gives the relative channel \(\theta_-=\theta_1-\theta_2\) an Ising-like \(Z_2\) symmetry while the total channel \(\theta_+=\theta_1+\theta_2\) retains \(U(1)\). In the phase-fluctuation regime, gap amplitudes can be substantial even though neither \(\langle\Delta_a\rangle\) is coherent [Zeng et al. (2024), §§II–III](../../papers/zeng2024htsbn/paper.pdf#page=2).

Locking only \(\theta_-\) orders the four-fermion composite \(\Delta_1^*\Delta_2\): relative phase \(\pm\pi/2\) breaks time reversal, while 0 or \(\pi\) gives nematic order, both in an electrically normal state. Ordering only \(\theta_+\) gives a charge-4e or quartetting phase through \(\Delta_1\Delta_2\), without either charge-2e gap ordering separately.

## Four-phase RG structure

The two-component XY model maps to coupled sine-Gordon fields with vortices, half-vortices, Josephson locking, and cross-channel perturbations. Numerical integration of the RG equations produces the normal, composite-\(Z_2\) normal, charge-4e, and \(Z_2\)-broken charge-2e superconducting phases. Depending on couplings, a tetracritical intersection can split into two tricritical points and allow a direct superconducting-to-normal boundary [Zeng et al. (2024), §IV](../../papers/zeng2024htsbn/paper.pdf#page=3).

## Validation boundary

This is a two-dimensional phase-only theory assuming near-degenerate pairing channels and sufficiently developed amplitudes. Its material discussions connect symmetry-compatible experimental signatures to the framework but do not derive microscopic couplings or establish that the proposed composite mechanism is the unique cause. Finite-temperature \(U(1)\) order is quasi-long-range via a Kosterlitz–Thouless transition [Zeng et al. (2024), §§V–VI](../../papers/zeng2024htsbn/paper.pdf#page=7).

## Benchmark hooks

- Integrate the coupled RG equations and classify basins by \(U(1)\) and \(Z_2\) observables.
- Locate topology changes among tetra- and tricritical phase diagrams as half-vortex coupling varies.
- Simulate the coupled XY model to test RG transition lines and finite-size KT/Ising diagnostics.
- Derive experimental distinctions among composite TRS order, nematicity, and charge-4e flux quantization.

## Related pages

- [[topics/unconventional-superconductivity|Unconventional superconductivity]]
- [[concepts/doped-smg-superconductivity|Doped SMG and superconductivity]]
- [[concepts/fermi-surface-anomalies|Fermi-surface anomalies]]
- [[papers/zeng2024htsbn|High-order Time-Reversal Symmetry Breaking Normal State]]
