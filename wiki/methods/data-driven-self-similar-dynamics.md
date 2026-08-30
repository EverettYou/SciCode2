---
title: Data-driven self-similar dynamics
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/tao2025ddmfs/paper.pdf
idea_ids: []
topics:
- Machine Learning
---

# Data-driven self-similar dynamics

**Summary**: Learn a microscopic evolution law and a nontrivial coarse-graining map whose macroscopic states obey the same law, turning scale consistency into a diagnostic for dynamical fixed points.

**Sources**: [Tao et al. (2025)](../../papers/tao2025ddmfs/paper.pdf)

**Last updated**: 2026-08-23

---

## Two-stage construction

A translation-equivariant dynamics learner first predicts the next microscopic state. With that learner frozen, a coarse-graining network is trained so that evolving before or after coarse-graining gives consistent macrostates under the same dynamics parameters. A decoder reconstructs microscopic blocks from predicted macrostates to prevent trivial maps that collapse every input to one constant [Tao et al. (2025), §II](../../papers/tao2025ddmfs/paper.pdf#page=3).

The discrepancy between the two paths is a dynamic-consistency score. It diagnoses self-similarity only when the learned macrovariables remain informative; a low score produced by a trivial macrostate is not evidence of a fixed point.

## Demonstrations

For elementary one-dimensional cellular automata, the framework learns all 256 microscopic rules at near-perfect reported accuracy and recovers the 21 rules and block sizes known to admit self-similar coarse-graining. For diffusion, it recovers the required space–time scaling and consistent microscopic and macroscopic diffusion coefficients as discretization is refined [Tao et al. (2025), §§III.A–III.B](../../papers/tao2025ddmfs/paper.pdf#page=4).

For lattice-processed Vicsek trajectories at density 0.3, decoder error is lowest in the independently estimated noise-critical region \(\eta\approx1.6\)–2.2, with better results for a space–time kernel compatible with the assumed dynamic exponent \(z\approx2\). At stronger disorder the learned macrostate becomes trivial or training fails, so the raw consistency minimum there is explicitly judged meaningless [Tao et al. (2025), §III.C](../../papers/tao2025ddmfs/paper.pdf#page=7).

## Validation boundary

The method assumes homogeneous dynamics and a reusable local map. Its examples are controlled or low-dimensional, and architecture, block shape, decoder capacity, and known scaling guesses can influence apparent self-similarity. Validation should require out-of-sample multiscale prediction, nontrivial information retention, recovery of known exponents or kernels, and negative controls from non-self-similar rules.

## Benchmark hooks

- Recover known cellular-automaton coarse-graining maps while rejecting all trivial encoders.
- Infer the diffusion dynamic exponent and coefficient without supplying the correct block aspect ratio.
- Separate critical-region detection from predictability loss and macrostate collapse in the Vicsek model.
- Test transfer of a learned scale-invariant kernel to sizes and times absent from training.

## Related pages

- [[methods/machine-learning-renormalization-group|Machine-learning renormalization group]]
- [[topics/deep-learning-renormalization-and-holography|Deep learning, renormalization, and holography]]
- [[papers/tao2025ddmfs|Data Driven Modeling for Self-Similar Dynamics]]
