---
title: Learned statistical gravity from entanglement
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/lam2021mlsgf/paper.pdf
idea_ids: []
topics:
- Machine Learning
- Quantum Information
---

# Learned statistical gravity from entanglement

**Summary**: Multi-region entanglement data can train a generative distribution of fluctuating tensor-network geometries, extending static Ryu–Takayanagi reconstruction to a statistical bulk model.

**Sources**: [Lam and You (2021)](../../papers/lam2021mlsgf/paper.pdf)

**Last updated**: 2026-08-23

---

## Model and inverse problem

A random tensor network with fluctuating bond entanglement maps second-Rényi observables to an Ising model with fluctuating couplings. In a semiclassical continuum description, the dual Ising field becomes a massive scalar on a hyperbolic background whose Weyl factor \(\omega\) fluctuates [Lam and You (2021), §II](../../papers/lam2021mlsgf/paper.pdf#page=2).

A latent-variable generator parameterizes \(P_\theta[\omega]\). Samples are passed through a bulk lattice solver to predict single- and multi-region purities, and the generator, scalar mass, and background parameters are trained against boundary entanglement data [Lam and You (2021), §III](../../papers/lam2021mlsgf/paper.pdf#page=5).

## Demonstration

On synthetic entanglement data from a large-central-charge free-fermion chain, a static geometry fits single intervals but cannot simultaneously reproduce disjoint-region mutual information. The fluctuating model improves held-out single-, double-, and triple-region predictions and learns a Weyl covariance approximately local in the chosen bulk discretization [Lam and You (2021), §IV](../../papers/lam2021mlsgf/paper.pdf#page=8).

## Validation boundary

The construction assumes a fixed planar RTN graph, second-Rényi data, weak semiclassical fluctuations, and a ratio-of-ensemble-averages approximation. Better predictive fit establishes usefulness of the fluctuating ansatz, not uniqueness of the inferred geometry or a fundamental gravity dual. Locality is inferred within the model class and coordinate/discretization choice; alternative bulk fields or priors may explain the same boundary data.

## Benchmark hooks

- Recover known synthetic Weyl covariance under controlled noise and incomplete region sampling.
- Quantify non-identifiability across graph, prior, scalar-mass, and coordinate choices.
- Compare static and fluctuating models on held-out region topologies, not only random train/test splits.
- Test whether learned bulk locality survives finer discretization and different boundary states.

## Related pages

- [[topics/deep-learning-renormalization-and-holography|Deep learning, renormalization, and holography]]
- [[topics/entanglement-structure-and-dynamics|Entanglement structure and dynamics]]
- [[methods/machine-learning-renormalization-group|Machine-learning renormalization group]]
- [[papers/lam2021mlsgf|Machine learning statistical gravity from multi-region entanglement entropy]]
