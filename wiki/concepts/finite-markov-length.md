---
title: Finite Markov length
page_type: concept
status: provisional
updated: '2026-08-22'
source_refs:
- papers/liu2025mqdm/paper.pdf
idea_ids: []
topics:
- Quantum Information
---

# Finite Markov length

**Summary**: Finite Markov length is a conditional-mutual-information locality condition that controls approximate recovery across an omitted boundary; it is stronger and more targeted than short two-point correlation length alone.

**Sources**: `paper:liu2025mqdm`

**Last updated**: 2026-08-22

---

## Current synthesis

For regions $A$, buffer $B$, and distant complement $C$, the paper assumes that $I(A:C\mid B)$ decays exponentially as the separation across $B$ grows. Under that assumption at every intermediate diffusion state, a recovery acting on $S=A\cup B$ can approximate the global reversal with error that decreases with buffer width [Liu et al. (2025), §Appendix-D.3-Eqs.D13-D24](../../papers/liu2025mqdm/paper.pdf#Appendix-D.3-Eqs.D13-D24).

The practical phrase “finite correlation length” is only a heuristic unless it is tied to this conditional-dependence criterion. Ordinary connected correlators can decay while multipartite conditional dependence remains relevant; the paper's theorem is stated in terms of CMI, not a fitted two-point length [Liu et al. (2025), §Sec.IV.C.2](../../papers/liu2025mqdm/paper.pdf#Sec.IV.C.2).

## Open questions

- Which efficiently measurable proxy best predicts a sufficient recovery buffer?
- How stable is the inferred Markov length across the intermediate states of a diffusion schedule?
- When does two-point correlation length rank candidate windows differently from CMI?

## Related pages

- [[papers/liu2025mqdm|Measurement-based quantum diffusion models]]
- [[methods/twirled-petz-recovery|Twirled Petz recovery]]
- [[comparisons/global-vs-local-petz|Global versus local Petz recovery]]
- [[benchmarks/local-petz-recovery-ladder/wiki/index|Local Petz recovery ladder]]
