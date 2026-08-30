---
title: Introspective latent-dynamics discovery
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/wang2019eseia/paper.pdf
idea_ids: []
topics:
- Machine Learning
---

# Introspective latent-dynamics discovery

**Summary**: A second recurrent model can compress a task network's hidden-state trajectory into minimal variables and an explicit update law without constraining the task model during training.

**Sources**: [Wang et al. (2019)](../../papers/wang2019eseia/paper.pdf)

**Last updated**: 2026-08-23

---

## Two-level architecture

A translator RNN first learns the sequential map from a one-dimensional potential profile to a particle-density profile. A separate recurrent autoencoder then encodes the translator's hidden states, propagates a lower-dimensional latent state, and decodes future hidden states. Because distillation is downstream, its bottleneck does not trade off against translation accuracy [Wang et al. (2019), Figs. 1–3](../../papers/wang2019eseia/paper.pdf#page=1).

Reconstruction loss rises sharply below two latent dimensions. Under constant potentials, the two components have twice the density period and a relative quarter-cycle phase, matching a real wavefunction and its derivative. Inspecting the learned Taylor-expanded update matrices gives a discrete first-order form equivalent, up to a linear latent-basis transform, to the stationary Schrödinger equation. A classical Boltzmann-density control needs no recurrent latent memory [Wang et al. (2019), Fig. 4 and conclusion](../../papers/wang2019eseia/paper.pdf#page=4).

## Identifiability boundary

The experiment uses synthetic, noiseless one-dimensional single-particle data, negative potentials, fixed energy convention, and an architecture aligned with local sequential propagation. The latent variables are not unique under invertible reparameterization, and matching one equation family does not establish open-ended law discovery. Robust use requires interventions, out-of-distribution potentials, noise tests, dimensionality controls, and symbolic equivalence checks.

## Benchmark hooks

- Recover latent dimension and update law under unknown linear changes of physical state coordinates.
- Add observational noise, irregular grids, turning points, and withheld potential families.
- Compare post-hoc distillation with joint bottlenecks and direct sparse equation discovery.
- Plant alternative first- and second-order dynamics to test whether architecture priors bias the discovered law.

## Related pages

- [[topics/physics-of-artificial-intelligence|Physics of artificial intelligence]]
- [[methods/machine-learning-symmetry-discovery|Machine-learning symmetry discovery]]
- [[methods/data-driven-self-similar-dynamics|Data-driven self-similar dynamics]]
- [[papers/wang2019eseia|Emergent Schrödinger equation in an introspective machine learning architecture]]
