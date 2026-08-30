---
title: Hybrid-circuit classical shadows
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/akhtar2024mcito/paper.pdf
idea_ids: []
topics:
- Quantum Information
---

# Hybrid-circuit classical shadows

**Summary**: Intermittent measurements throughout a random circuit define reconstructible snapshots whose Pauli sample complexity is optimized at the circuit's measurement-induced transition.

**Sources**: [Akhtar et al. (2024)](../../papers/akhtar2024mcito/paper.pdf)

**Last updated**: 2026-08-23

---

## Generalized snapshots

A measurement record \(b\) and circuit realization \(C\) define a positive snapshot \(\sigma_{b|C}=K_{b|C}^\dagger K_{b|C}/\operatorname{Tr}(K_{b|C}^\dagger K_{b|C})\), even when projective measurements occur at arbitrary spacetime positions. For random Clifford gates and Pauli measurements, the snapshot is a stabilizer state reconstructed efficiently by tracing the circuit backward from the maximally mixed state [Akhtar et al. (2024), generalized-snapshot construction](../../papers/akhtar2024mcito/paper.pdf#page=2).

The prior snapshot ensemble determines each Pauli learning rate and inverse shadow norm; posterior snapshots sampled from the unknown state provide unbiased observable estimators. This separates calibration of the measurement ensemble from data acquired on the target state.

## Critical optimum

For consecutive Pauli strings of support \(k\), tensor-network calculations give \(\|P\|_{\rm sh}^2\simeq\beta(p)^k\operatorname{poly}(k)\). The fitted base is minimized at the measurement-induced transition, with \(\beta_{\min}=2.23\pm0.006\) and a critical correction \(k^{2\Delta}\), \(\Delta=0.33\pm0.02\) [Akhtar et al. (2024), Fig. 4 and Eq. 13](../../papers/akhtar2024mcito/paper.pdf#page=4).

On the high-measurement area-law side, frequent collapse prevents enough spreading to expose large observables. On the low-measurement volume-law side, error-correcting scrambling hides the initial information from sparse local measurements. Criticality balances these effects across scale.

## Validation boundary

“Tomographically optimal” means optimal within the studied hybrid-circuit family and asymptotic contiguous-Pauli criterion, not among all possible tomography protocols. The direct estimator demonstration uses a 12-qubit GHZ state and 50,000 samples; critical exponents and mappings used in analytic interpretation need larger-size and independent checks [Akhtar et al. (2024), numerical demonstration and discussion](../../papers/akhtar2024mcito/paper.pdf#page=3).

## Benchmark hooks

- Reconstruct stabilizer snapshots by reverse circuit processing and verify estimator unbiasedness.
- Sweep measurement rate and system size to recover the \(\beta(p)\) minimum independently of entanglement postselection.
- Compare fitted \(\Delta\) and critical point across boundary conditions and circuit ensembles.
- Contrast tuned hybrid shadows with scale-invariant hierarchical shadows at matched quantum and classical cost.

## Related pages

- [[concepts/classical-shadow-tomography|Classical shadow tomography]]
- [[methods/holographic-classical-shadows|Holographic classical shadows]]
- [[comparisons/structured-classical-shadow-protocols|Structured classical-shadow protocols]]
- [[papers/akhtar2024mcito|Measurement-Induced Criticality is Tomographically Optimal]]
