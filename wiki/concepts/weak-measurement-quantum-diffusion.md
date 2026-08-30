---
title: Weak-measurement quantum diffusion
page_type: concept
status: provisional
updated: '2026-08-22'
source_refs:
- papers/liu2025mqdm/paper.pdf
- papers/liu2025mqdm/repo
idea_ids: []
topics:
- Quantum Information
---

# Weak-measurement quantum diffusion

**Summary**: Random weak Pauli measurements generate pure conditioned trajectories while their outcome average evolves as a mixed, depolarizing channel; these two descriptions require different reverse processes.

**Sources**: `paper:liu2025mqdm`; `repository:liu2025mqdm

**Last updated**: 2026-08-22

---

## Current synthesis

At trajectory level, each normalized conditional state remains pure and is driven stochastically by its measurement record. Averaging over records removes that conditioning and produces a mixed-state channel that damps Pauli components toward the maximally mixed state [Liu et al. (2025), §Sec.II.A-II.C](../../papers/liu2025mqdm/paper.pdf#Sec.II.A-II.C). This is not a cosmetic distinction: trajectory reversal learns record-conditioned unitary control, whereas ensemble reversal reconstructs or recovers an average density matrix [Liu et al. (2025), §p.3-Fig.1](../../papers/liu2025mqdm/paper.pdf#p.3-Fig.1).

The companion code discretizes local weak measurements with six single-qubit Kraus outcomes and tensors them across qubits [Liu quantum-diffusion repository, doc/design.md · weak-measurement](../../papers/liu2025mqdm/repo/doc/design.md#weak-measurement). Its forward API stores the evolving state internally and returns measurement sequences [Liu quantum-diffusion repository, src/diffusion.py · ForwardDiffusion](../../papers/liu2025mqdm/repo/src/diffusion.py#ForwardDiffusion).

## Boundaries

- Comparing a trajectory-level recovered pure state directly with an ensemble-level Petz output conflates different targets.
- A finite-step schedule can differ from the continuous stochastic equation; numerical work must state its measurement order and step convention.
- Static code inspection does not verify normalization, sampling, or convergence in execution.

## Related pages

- [[papers/liu2025mqdm|Measurement-based quantum diffusion models]]
- [[methods/twirled-petz-recovery|Twirled Petz recovery]]
- [[comparisons/trajectory-vs-ensemble-recovery|Trajectory versus ensemble recovery]]
- [[implementations/liu-quantum-diffusion-companion|Companion quantum-diffusion implementation]]
