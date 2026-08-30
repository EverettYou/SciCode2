---
title: Repetitive-task accuracy cliffs
page_type: concept
status: provisional
updated: '2026-08-22'
source_refs:
- papers/hou2025hfala/paper.pdf
idea_ids: []
topics:
- Machine Learning
---

# Repetitive-task accuracy cliffs

**Summary**: Sequence accuracy on repeated deterministic operations can collapse more sharply than independent per-step errors predict, revealing correlated error accumulation and a characteristic reliability length.

**Sources**: [Hou et al. (2025)](../../papers/hou2025hfala/paper.pdf)

**Last updated**: 2026-08-22

---

## Current synthesis

The paper defines sequence accuracy rate over cyclic replacement, integer addition, and Pauli-string multiplication. Instead of simple exponential decay expected from independent operation errors, tested models show a sharper crossover fitted by a statistical-physics-inspired correlated-error model with intrinsic-error and accumulation parameters [Hou et al. (2025), §Abstract-and-Sec.6](../../papers/hou2025hfala/paper.pdf#Abstract-and-Sec.6).

The proposed spin-glass analogy is an explanatory model, not evidence that internal attention literally realizes that physical system. Its durable contribution is the controlled length-scaling protocol and fitted reliability parameters.

## Benchmark opportunity

Vary decomposition, self-verification, context layout, and output protocol while holding atomic operations fixed. Measure whether the inferred cliff shifts and whether a model calibrated on one operation predicts another.

## Related pages

- [[methods/output-space-model-evaluation|Output-space model evaluation]]
- [[papers/hou2025hfala|How focused are LLMs?]]
