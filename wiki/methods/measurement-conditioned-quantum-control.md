---
title: Measurement-conditioned quantum control
page_type: method
status: provisional
updated: '2026-08-22'
source_refs:
- papers/wang2025mlfgs/paper.pdf
- papers/liu2025mqdm/paper.pdf
- papers/hou2025mlteo/paper.pdf
idea_ids: []
topics:
- Machine Learning
- Quantum Information
---

# Measurement-conditioned quantum control

**Summary**: Mid-circuit outcomes can be compressed into a classical policy or state estimate that selects later quantum operations, turning measurements from passive readout into adaptive state preparation and recovery resources.

**Sources**: [Wang et al. (2025)](../../papers/wang2025mlfgs/paper.pdf) [Liu et al. (2025)](../../papers/liu2025mqdm/paper.pdf) [Hou et al. (2025)](../../papers/hou2025mlteo/paper.pdf)

**Last updated**: 2026-08-22

---

## Current synthesis

A recurrent policy can condition later circuit actions on accumulated mid-circuit outcomes and learn Hamiltonian-specific ground-state preparation protocols [Wang et al. (2025), §Abstract](../../papers/wang2025mlfgs/paper.pdf#Abstract). The reported policy repeatedly steers different initial states toward an intermediate state before approaching the target, while performance improves with a larger measured-ancilla fraction; noise was not included in the studied model [Wang et al. (2025), §Discussion](../../papers/wang2025mlfgs/paper.pdf#Discussion).

Measurement-based quantum diffusion similarly conditions reverse unitaries on a measurement record, but targets reversal of a stochastic trajectory rather than direct variational ground-state preparation [Liu et al. (2025), §Sec.III.A](../../papers/liu2025mqdm/paper.pdf#Sec.III.A). Learned post-measurement models can also act as observers rather than controllers, revealing conditional entanglement without choosing feedback actions [Hou et al. (2025), §Abstract](../../papers/hou2025mlteo/paper.pdf#Abstract).

## Benchmark variables

- information available to the policy and its latency;
- measured ancilla fraction and circuit depth;
- robustness to initial-state, Hamiltonian, and noise shifts;
- energy, fidelity, and success probability at fixed measurement cost;
- whether a learned intermediate strategy is reproducible across random seeds.

## Related pages

- [[concepts/learned-quantum-state-models|Learned quantum-state models]]
- [[concepts/weak-measurement-quantum-diffusion|Weak-measurement quantum diffusion]]
- [[papers/wang2025mlfgs|Machine learning for ground-state preparation via measurement and feedback]]
