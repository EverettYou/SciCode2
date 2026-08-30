---
title: Classical shadow tomography
page_type: concept
status: active
updated: '2026-08-22'
source_refs:
- papers/akhtar2023safcs/paper.pdf
- papers/hu2023cstwl/paper.pdf
- papers/hu2022hstoq/paper.pdf
idea_ids: []
topics:
- Quantum Information
---

# Classical shadow tomography

**Summary**: Classical shadows trade complete state reconstruction for randomized measurements and observable-specific estimators whose sample complexity is governed by the measurement ensemble and target observable.

**Sources**: [Akhtar et al. (2023)](../../papers/akhtar2023safcs/paper.pdf) [Hu et al. (2023)](../../papers/hu2023cstwl/paper.pdf) [Hu et al. (2022)](../../papers/hu2022hstoq/paper.pdf)

**Last updated**: 2026-08-22

---

## Current synthesis

A shadow protocol randomizes a state, measures in a fixed basis, and applies an inverse reconstruction map to each snapshot. Its utility is not a single universal “tomography efficiency”: local Pauli measurements favor low-weight observables, while more strongly scrambling ensembles can reduce variance for extended or low-rank targets at greater circuit and reconstruction cost [Akhtar et al. (2023), §Sec.1](../../papers/akhtar2023safcs/paper.pdf#Sec.1).

Locally scrambled dynamics generalize the reconstruction map beyond the two endpoints of product Pauli and global Clifford measurements. The required coefficients can be expressed through average entanglement features of snapshots [Hu et al. (2023), §Abstract](../../papers/hu2023cstwl/paper.pdf#Abstract). Hamiltonian time evolution provides another experimentally motivated scrambling ensemble, with performance varying continuously with evolution time [Hu et al. (2022), §Abstract](../../papers/hu2022hstoq/paper.pdf#Abstract).

## Benchmark variables

- observable family and support;
- circuit depth, geometry, gate ensemble, and hardware noise;
- shadow norm or estimator variance;
- calibration bias from an imperfect implemented ensemble;
- classical cost of reconstructing or contracting each estimator.

## Related pages

- [[methods/entanglement-feature-dynamics|Entanglement-feature dynamics]]
- [[methods/holographic-classical-shadows|Holographic classical shadows]]
- [[methods/hybrid-circuit-classical-shadows|Hybrid-circuit classical shadows]]
- [[comparisons/structured-classical-shadow-protocols|Structured classical-shadow protocols]]
- [[concepts/learned-quantum-state-models|Learned quantum-state models]]
- [[papers/akhtar2023safcs|Scalable and flexible classical shadow tomography with tensor networks]]
- [[papers/hu2023cstwl|Classical shadow tomography with locally scrambled quantum dynamics]]
