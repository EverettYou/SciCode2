---
title: Decoherent Kibble–Zurek scaling
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/kuo2021dqdaq/paper.pdf
idea_ids: []
topics:
- Quantum Information
- Topological Phases
---

# Decoherent Kibble–Zurek scaling

**Summary**: Continuous quantum-nondemolition monitoring of a driven Hamiltonian introduces a decoherence timescale that can replace coherent critical slowing down and produce a distinct universal freeze-out law.

**Sources**: [Kuo et al. (2021)](../../papers/kuo2021dqdaq/paper.pdf)

**Last updated**: 2026-08-23

---

## Open-system quench

Weak continuous measurement of the instantaneous Hamiltonian leads, after averaging outcomes and taking a Markovian limit, to
\[
\partial_t\rho=-i[H(t),\rho]-\gamma[H(t),[H(t),\rho]].
\]
For levels separated by \(\Delta\), coherence decays on \(\tau_{\rm dec}=(\gamma\Delta^2)^{-1}\), whereas the coherent correlation time scales as \(\xi_t\sim\Delta^{-1}\) [Kuo et al. (2021), §II.A–B](../../papers/kuo2021dqdaq/paper.pdf#page=2).

For a linear quench with equilibrium exponents \(\nu,z\), coherent Kibble–Zurek behavior controls weak decoherence. When \(\tau_{\rm dec}<\xi_t\) at freeze-out, the strong-decoherence scaling becomes
\[
\bar t\sim(\gamma^{-1}\tau^{2\nu z})^{1/(1+2\nu z)},\qquad
\bar\xi\sim(\gamma\tau)^{\nu/(1+2\nu z)}.
\]
The crossover is controlled jointly by quench duration and monitoring strength [Kuo et al. (2021), §II.C](../../papers/kuo2021dqdaq/paper.pdf#page=4).

## Chern-insulator validation

Two-band Chern-insulator simulations confirm the predicted time scaling through delayed Hall-conductivity relaxation. Adding weak bond disorder creates spatially inhomogeneous excitation regions whose correlation length follows the predicted freeze-out length [Kuo et al. (2021), §III](../../papers/kuo2021dqdaq/paper.pdf#page=5).

## Validation boundary

The bath performs energy-basis QND monitoring, is Markovian, and exchanges information rather than energy. A generic thermal bath or local measurement not commuting with the Hamiltonian can produce different dynamics. The explicit test is a noninteracting two-band model; interacting critical points, relevant disorder, finite-temperature initial states, and non-Markovian environments require separate validation.

## Benchmark hooks

- Recover coherent and strong-decoherence exponents from the same solver across the crossover.
- Infer \(\bar t\) independently from state distance, excitation production, and Hall relaxation.
- Test scaling collapse for several \((\nu,z)\) universality classes.
- Perturb the Lindblad operator away from exact Hamiltonian monitoring and map the loss of universality.

## Related pages

- [[topics/topological-phase-transitions|Topological phase transitions]]
- [[topics/random-quantum-circuits-and-measurements|Random quantum circuits and measurements]]
- [[papers/kuo2021dqdaq|Decoherent quench dynamics across quantum phase transitions]]
