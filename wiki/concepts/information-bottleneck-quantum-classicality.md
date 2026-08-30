---
title: Information-bottleneck quantum classicality
page_type: concept
status: provisional
updated: 2026-08-23
source_refs:
- papers/zhang2024oscwa/paper.pdf
idea_ids: []
topics:
- Machine Learning
- Quantum Information
---

# Information-bottleneck quantum classicality

**Summary**: A learned model of complete randomized-measurement data can preserve robust classical correlations while discarding exponentially costly global coherence, creating a capacity-dependent quantum–classical boundary.

**Sources**: [Zhang and You (2024)](../../papers/zhang2024oscwa/paper.pdf)

**Last updated**: 2026-08-23

---

## Controlled GHZ setting

Random local Pauli measurements of an \(N\)-qubit GHZ state produce basis strings \(x\) and outcome strings \(y\). A transformer \(\beta\)-VAE learns \(p_\theta(y|x)\); increasing \(\beta\) limits how much basis information the latent state can retain. Synthetic shadows from the model are inverted to a density-matrix estimate and evaluated by fidelity, entropy, classical-cat classification, and coherence prediction [Zhang and You (2024), Methods and Results](../../papers/zhang2024oscwa/paper.pdf#page=3).

Strong models learn both the locations of \(Z\) measurements and the number of \(Y\) operators in all-X/Y strings, retaining GHZ coherence. Intermediate models preserve the robust all-equal \(Z\) outcomes but merge the X/Y latent classes and predict coherence at chance. Weak models lose both structures [Zhang and You (2024), Figs. 3–7](../../papers/zhang2024oscwa/paper.pdf#page=5).

## Bottleneck interpretation

The quantum coherence is encoded in an \(N\)-body correlator whose sampling variance grows exponentially with system size. Under lossy compression it is discarded before lower-order classical correlations. The resulting boundary therefore moves with both \(N\) and model information-processing capacity; it is a property of inference from classical data, not an additional physical collapse process [Zhang and You (2024), Discussion](../../papers/zhang2024oscwa/paper.pdf#page=9).

## Validation boundary

The demonstrated boundary is specific to GHZ states, local Pauli measurements, and the selected variational language model. It does not establish a universal account of macroscopic classicality. Generated shadow distributions can also invert to non-positive density matrices, so good token likelihood or classical-task accuracy does not guarantee a physical quantum-state model.

## Benchmark hooks

- Recover the phase diagram over qubit count, bottleneck strength, data volume, and latent dimension.
- Compare likelihood, low-order observables, global coherence, positivity, fidelity, and entropy as distinct scores.
- Test whether importance-weighted training or structured measurements postpone coherence loss at fixed resources.
- Repeat on stabilizer, area-law, volume-law, and mixed states to separate GHZ-specific from generic scaling.

## Related pages

- [[concepts/learned-quantum-state-models|Learned quantum-state models]]
- [[concepts/classical-shadow-tomography|Classical shadow tomography]]
- [[topics/machine-learning-and-quantum-physics|Machine learning and quantum physics]]
- [[papers/zhang2024oscwa|Observing Schrödinger’s Cat with Artificial Intelligence]]
