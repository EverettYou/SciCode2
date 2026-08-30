---
title: Machine-learning renormalization group
page_type: method
status: provisional
updated: '2026-08-22'
source_refs:
- papers/hu2020mlhmb/paper.pdf
- papers/hu2022rahae/paper.pdf
- papers/hou2023mlrgf/paper.pdf
- papers/zhao2026aodnn/paper.pdf
- papers/sheshmani2023crlar/paper.pdf
idea_ids: []
topics:
- Machine Learning
---

# Machine-learning renormalization group

**Summary**: Hierarchical invertible generative models can learn information-preserving coarse-graining maps, separate scales, and infer RG flows, but physical interpretation depends on architectural constraints and information criteria.

**Sources**: [Hu et al. (2020)](../../papers/hu2020mlhmb/paper.pdf) [Hu et al. (2022)](../../papers/hu2022rahae/paper.pdf) [Hou et al. (2023)](../../papers/hou2023mlrgf/paper.pdf) [Zhao et al. (2026)](../../papers/zhao2026aodnn/paper.pdf) [Sheshmani et al. (2023)](../../papers/sheshmani2023crlar/paper.pdf)

**Last updated**: 2026-08-23

---

## Development path

Neural-network RG first uses a hierarchical flow to learn an exact-holographic-style map for an interacting field ensemble and extracts an emergent bulk distance from residual mutual information [Hu et al. (2020), §Conclusion](../../papers/hu2020mlhmb/paper.pdf#Conclusion). RG-Flow transfers the hierarchy to image modeling, using sparse priors and receptive fields to separate scale and position while retaining invertibility [Hu et al. (2022), §Sec.5](../../papers/hu2022rahae/paper.pdf#Sec.5).

MLRG returns to statistical physics with a teacher-student generative loop that explores symmetry-compatible lattice models, learns RG transformations and equations, and estimates phases, critical points, exponents, and scaling dimensions [Hou et al. (2023), §Abstract](../../papers/hou2023mlrgf/paper.pdf#Abstract).

For sequential data, the RG categorifier realizes each local disentangler and decimator as an invertible neural ODE, retains the decimated variables as a hierarchy of latent fields, and trains exact likelihood against independent Gaussian priors [Sheshmani et al. (2023), §§5.3–5.9](../../papers/sheshmani2023crlar/paper.pdf#page=14). Its influenza experiments show fitted one-site and length-4/16 embedding distributions and a ranking of 768 single mutations in one 32-residue test sequence [Sheshmani et al. (2023), §6](../../papers/sheshmani2023crlar/paper.pdf#page=22).

RGFlow specializes this idea to continuum scalar field theories discretized on a lattice. A bijective RealNVP map sends each fine field to a coarse field plus independent Gaussian irrelevant variables; minimizing Fisher divergence avoids explicit partition functions while enforcing the minimal-bulk-mutual-information criterion [Zhao et al. (2026), §§II.B–II.C](../../papers/zhao2026aodnn/paper.pdf#page=4). The method reproduces analytic decimation for a one-dimensional Gaussian theory and, on a minimal \(2\times2\) two-dimensional \(\phi^4\) system, finds a projected fixed point \((u^*,r^*)=(2.13\pm0.13,-1.97\pm0.12)\) and \(\nu=0.885\pm0.015\), about 10% from the exact value [Zhao et al. (2026), §§III–IV](../../papers/zhao2026aodnn/paper.pdf#page=6).

## Validation boundary

Invertibility preserves information but does not by itself identify the physically correct relevant variables. Benchmarks should test learned flows against known fixed points, operator spectra, monotonic quantities, and perturbations outside the training family, while checking sensitivity to architecture and latent prior.

For RGFlow, the reported two-coupling flow is only a projection of the full theory space; finite blocking factor, the tiny lattice, and omitted \(\phi^6\) and higher interactions can shift the critical line and exponent. The authors also report that detached samples make the ordinary PyTorch gradient with respect to learned couplings formally biased. Finite differences reach the same local minimum in their two-dimensional test, but stability in other dimensions is unknown; a policy-gradient correction is proposed [Zhao et al. (2026), §V and note added](../../papers/zhao2026aodnn/paper.pdf#page=10). This creates a useful validation ladder: analytic Gaussian recovery, finite-size scaling, enlarged coupling bases, corrected-gradient ablations, and transfer across dimension or symmetry class.

For the sequence model, visual t-SNE overlap and training likelihood do not establish that latent depth corresponds to biological scale or that generated sequences are viable. The reported escape task has no broad architecture baseline, uses only single mutations in a short fixed window, and evaluates known labels rather than prospective viral escape. These are representation-learning results, not experimental virology evidence [Sheshmani et al. (2023), §§6.2–6.4](../../papers/sheshmani2023crlar/paper.pdf#page=23).

## Related pages

- [[methods/data-driven-self-similar-dynamics|Data-driven self-similar dynamics]]
- [[methods/frequency-domain-diffusion-models|Frequency-domain diffusion models]]
- [[papers/hu2020mlhmb|Machine learning holographic mapping by neural network renormalization group]]
- [[papers/hu2022rahae|RG-Flow]]
- [[papers/hou2023mlrgf|Machine learning renormalization group for statistical physics]]
- [[papers/zhao2026aodnn|Application of deep neural networks for computing the renormalization group flow of the two-dimensional phi4 field theory]]
- [[papers/sheshmani2023crlar|Categorical representation learning and RG flow operators for algorithmic classifiers]]
