---
title: Trainable-POVM tensor-network Born machines
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/hou2025sloat/paper.pdf
idea_ids: []
topics:
- Machine Learning
---

# Trainable-POVM tensor-network Born machines

**Summary**: Encode discrete tokens as constrained trainable quantum measurements on an MPS Born machine, separating vocabulary size from physical dimension while retaining tractable likelihoods and arbitrary-order conditioning.

**Sources**: [Hou et al. (2025)](../../papers/hou2025sloat/paper.pdf)

**Last updated**: 2026-08-23

---

## Construction

A sequence \(x=(x_1,\ldots,x_n)\) is assigned probability \(p_{\theta,\gamma}(x)=\langle\Psi_\theta|\bigotimes_i M_\gamma(x_i)|\Psi_\theta\rangle\). The MPS is normalized and each token operator belongs to a POVM: it is positive semidefinite and the vocabulary sum is the identity. QR decomposition of a trainable rectangular parameter tensor produces operators satisfying these constraints, so the local physical dimension can vary independently of vocabulary size [Hou et al. (2025), §II](../../papers/hou2025sloat/paper.pdf#page=2).

The normalized tensor network gives exact likelihood gradients and efficient marginals. Conditioning can fix an arbitrary subset of sites rather than only a left-to-right prefix, supporting autoregressive, masked, and mixed-order sampling [Hou et al. (2025), §§II–III](../../papers/hou2025sloat/paper.pdf#page=3).

## Evidence and tradeoffs

On fixed-length 5S rRNA sequences, increasing POVM physical dimension lowers test negative log-likelihood and improves single-site probabilities and two-site correlations relative to one-hot embeddings. At roughly matched parameter count, the reported MPS model beats the selected GPT-2 configuration in NLL and is competitive for single-site statistics, but GPT-2 better captures the tested long-range pair correlations [Hou et al. (2025), §IV and Figs. 3–4](../../papers/hou2025sloat/paper.pdf#page=4).

This is a classically simulated quantum-inspired model. The paper proposes circuit transfer and generalized-measurement sampling as future hardware paths but does not demonstrate quantum advantage. The current architecture also assumes fixed-length one-dimensional discrete data and does not directly handle variable lengths, higher-dimensional structure, or continuous observations [Hou et al. (2025), §V](../../papers/hou2025sloat/paper.pdf#page=5).

## Benchmark hooks

- Verify POVM positivity, completeness, and normalized sequence probabilities under optimization.
- Reproduce arbitrary-mask conditional probabilities by direct tensor contraction and sampling.
- Map the NLL and correlation error surfaces over bond dimension and POVM physical dimension.
- Compare against autoregressive baselines under matched data splits, parameter budgets, and correlation-distance diagnostics.

## Related pages

- [[topics/machine-learning-and-physics|Machine learning and physics]]
- [[concepts/learned-quantum-state-models|Learned quantum-state models]]
- [[papers/hou2025sloat|Sequential learning on a Tensor Network Born machine with Trainable Token Embedding]]
