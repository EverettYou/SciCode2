---
title: Output-space model evaluation
page_type: method
status: provisional
updated: '2026-08-23'
source_refs:
- papers/liu2023eohpd/paper.pdf
- papers/liu2023gwaan/paper.pdf
idea_ids: []
topics:
- Machine Learning
---

# Output-space model evaluation

**Summary**: When an input space cannot be enumerated, model-guided sampling over outputs can estimate where human judgments and model predictions differ, with estimator quality depending critically on proposal coverage and annotation assumptions.

**Sources**: [Liu et al. (2023a)](../../papers/liu2023eohpd/paper.pdf) [Liu et al. (2023b)](../../papers/liu2023gwaan/paper.pdf)

**Last updated**: 2026-08-23

---

## Current synthesis

OmniInput reframes precision/recall evaluation over an internet-scale discrete input domain by sampling regions through the model's output distribution and requesting human labels for selected inputs [Liu et al. (2023), §Abstract](../../papers/liu2023eohpd/paper.pdf#Abstract). Its conclusion emphasizes that output-distribution sampling reveals input-output behavior missed by a fixed dataset, while acknowledging dependence on sampler quality, human gold-standard ambiguity, and difficulty aligning samples across models [Liu et al. (2023), §Conclusions-and-Sec.6](../../papers/liu2023eohpd/paper.pdf#Conclusions-and-Sec.6).

Gradient-based Wang–Landau (GWL) supplies one physics-inspired sampler for a finite discrete domain. It treats a scalar network output as an energy, estimates the log density of states over output bins, and replaces random pixel proposals with a differentiable Gibbs-with-gradients proposal aimed at underexplored bins [Liu et al. (2023), §§3.1–3.4](../../papers/liu2023gwaan/paper.pdf#page=3). On a 5×5 binary-image domain, its normalized histogram nearly matches exhaustive enumeration; on 28×28 MNIST models it explores a much wider logit range than random-proposal Wang–Landau under the reported compute budget [Liu et al. (2023), §§5.2–5.3](../../papers/liu2023gwaan/paper.pdf#page=6).

The empirical network interpretation is weaker than the sampler demonstration. The combined GWL update has no convergence proof, ResNet sampling remained unfinished, and claims about recognizable or semantic images rely on limited manual inspection [Liu et al. (2023), §6](../../papers/liu2023gwaan/paper.pdf#page=9). Output coverage, estimator convergence, and human labeling therefore need separate validation.

## Benchmark opportunity

An enumerable synthetic domain with controllable rare modes can measure estimator bias directly. Compare random, stratified, and model-guided proposals under equal labeling budgets, including adversarially low-probability disagreement regions.

## Related pages

- [[concepts/repetitive-task-accuracy-cliffs|Repetitive-task accuracy cliffs]]
- [[papers/liu2023eohpd|Evaluation of human-model prediction difference on the Internet scale of data]]
- [[papers/liu2023gwaan|Gradient-based Wang–Landau algorithm]]
