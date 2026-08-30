---
title: Global versus local Petz recovery
page_type: comparison
status: provisional
updated: '2026-08-22'
source_refs:
- papers/liu2025mqdm/paper.pdf
idea_ids: []
topics:
- Quantum Information
---

# Global versus local Petz recovery

**Summary**: Global Petz recovery supplies the full-system reference, while local Petz recovery uses overlapping reduced-state windows and relies on finite Markov length to control omitted conditional dependence.

**Sources**: `paper:liu2025mqdm`

**Last updated**: 2026-08-22

---

## Comparison

The global map acts on the full density matrix and is generally intractable at many-body scale. The local variant restricts each reverse step to $S_j=A\cup B$ and is justified when intermediate states exhibit exponentially decaying CMI across the buffer [Liu et al. (2025), §Sec.IV.C.1-IV.C.2](../../papers/liu2025mqdm/paper.pdf#Sec.IV.C.1-IV.C.2).

The paper reports a ten-qubit open Ising-chain demonstration using three-qubit windows, $T=10$, $dt=0.01$, and off-critical fields $B_x=1.5,2.0,5.0$, with final fidelities $0.911,0.963,0.989$ respectively [Liu et al. (2025), §p.10-Fig.5](../../papers/liu2025mqdm/paper.pdf#p.10-Fig.5). These are source-reported results, not reproduced evidence. The figure does not provide a matched global baseline, CMI-by-window curve, or numerical-error decomposition.

## Calibration principle

For a finite benchmark, a full-window implementation should agree with the global construction when schedule, priors, twirling quadrature, and support policy are identical. Only after that equality and numerical convergence hold should smaller-window disagreement be interpreted as locality error. This is benchmark-oriented synthesis.

## Related pages

- [[concepts/finite-markov-length|Finite Markov length]]
- [[methods/twirled-petz-recovery|Twirled Petz recovery]]
- [[benchmarks/local-petz-recovery-ladder/wiki/index|Local Petz recovery ladder]]
- [[benchmarks/local-petz-recovery-ladder/wiki/index|Local Petz recovery ladder]]
