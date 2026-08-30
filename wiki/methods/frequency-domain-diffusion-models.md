---
title: Frequency-domain diffusion models
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/sheshmani2025rgfot/paper.pdf
idea_ids: []
topics:
- Machine Learning
---

# Frequency-domain diffusion models

**Summary**: Fourier- or DCT-domain diffusion can use scale-dependent noise to trade fine-detail fidelity for substantially lower computation, motivated by an optimal-transport view of renormalization flow.

**Sources**: [Sheshmani et al. (2025)](../../papers/sheshmani2025rgfot/paper.pdf)

**Last updated**: 2026-08-23

---

## RG and optimal-transport framing

Exact renormalization flow can be formulated as a gradient flow on probability distributions equipped with a Wasserstein metric: the forward direction trivializes correlations, while the inverse direction suggests generation from a simple distribution. The paper relates the RG functional to a KL-like objective and a discretized Benamou–Brenier diffusion equation [Sheshmani et al. (2025), §§1–3](../../papers/sheshmani2025rgfot/paper.pdf#page=4).

This mathematical interpretation motivates but does not uniquely determine the image architecture. A benchmark should keep claims about the RG-gradient-flow derivation separate from claims about the performance of the chosen patching, transform, and neural denoiser.

## FDDM construction

The Frequency Domain Diffusion Model converts RGB images to YCbCr, divides them into patches, applies a DCT, and groups equal-frequency coefficients into channels. A momentum-dependent Fermi-style schedule adds noise from ultraviolet to infrared modes; a U-Net predicts clean frequency coefficients and inverse DCT reconstructs the image [Sheshmani et al. (2025), §§5.2–5.3](../../papers/sheshmani2025rgfot/paper.pdf#page=10).

On CelebA-64 with 1,000 inference steps, the reported 4×4- and 8×8-patch variants process steps about 2.7 and 8.5 times faster than the selected DDPM baseline. Their FID scores are 18.17 and 20.65 versus 3.26 for DDPM, exposing a substantial fine-detail cost for the speedup [Sheshmani et al. (2025), §5.4 and Table 1](../../papers/sheshmani2025rgfot/paper.pdf#page=14).

## Validation boundary

The experiments cover Fashion-MNIST and CelebA-64 and compare mainly to one image-domain diffusion baseline. Patch size, frequency schedule, architecture capacity, and downstream tolerance for missing detail are coupled choices. Strong evaluation therefore needs matched compute, parameter count, training steps, wall-clock measurements, multiple perceptual and task metrics, and ablations against non-RG frequency schedules.

## Benchmark hooks

- Derive and numerically verify the discrete Wasserstein gradient-flow step on a controlled Gaussian field.
- Reproduce the speed–FID frontier over patch size and noise temperature.
- Ablate momentum-dependent noise against scalar schedules with identical network and compute.
- Measure whether coarse semantic tasks retain accuracy despite degraded fine-detail FID.

## Related pages

- [[methods/machine-learning-renormalization-group|Machine-learning renormalization group]]
- [[topics/deep-learning-renormalization-and-holography|Deep learning, renormalization, and holography]]
- [[papers/sheshmani2025rgfot|Renormalization group flow, optimal transport and diffusion-based generative model]]
