---
title: Twirled Petz recovery
page_type: method
status: provisional
updated: '2026-08-22'
source_refs:
- papers/liu2025mqdm/paper.pdf
idea_ids: []
topics:
- Quantum Information
---

# Twirled Petz recovery

**Summary**: A twirled Petz map reverses a known channel relative to before/after state priors by averaging rotated Petz maps; local restriction trades global access for a CMI-controlled approximation.

**Sources**: `paper:liu2025mqdm`

**Last updated**: 2026-08-22

---

## Construction

The infinitesimal map integrates rotated Petz maps over a modular-flow parameter with weight $f(\tau)=1/[2(\cosh(\pi\tau)+1)]$. Each integrand combines the adjoint forward channel with complex fractional powers of the prior states before and after a diffusion step [Liu et al. (2025), §Sec.IV.C.1-Eq.48](../../papers/liu2025mqdm/paper.pdf#Sec.IV.C.1-Eq.48).

The local construction substitutes reduced states and a restricted channel on $S_j=A\cup B$, then composes overlapping local maps in reverse schedule order [Liu et al. (2025), §Sec.IV.C.2](../../papers/liu2025mqdm/paper.pdf#Sec.IV.C.2). The recovery is data-constructed rather than learned, unlike the paper's trajectory-level controller [Liu et al. (2025), §p.9](../../papers/liu2025mqdm/paper.pdf#p.9).

## Numerical cautions

- Fractional inverse powers are support-sensitive for pure or nearly rank-deficient priors.
- Finite twirling quadrature, time discretization, and pseudoinverse thresholds can introduce errors distinct from locality error.
- A trustworthy implementation should report trace preservation, complete positivity, support loss, and convergence—not fidelity alone. This is wiki synthesis motivated by the formula, not a reproduced paper result.

## Related pages

- [[concepts/weak-measurement-quantum-diffusion|Weak-measurement quantum diffusion]]
- [[concepts/finite-markov-length|Finite Markov length]]
- [[comparisons/global-vs-local-petz|Global versus local Petz recovery]]
- [[comparisons/trajectory-vs-ensemble-recovery|Trajectory versus ensemble recovery]]
