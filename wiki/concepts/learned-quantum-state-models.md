---
title: Learned quantum-state models
page_type: concept
status: provisional
updated: '2026-08-22'
source_refs:
- papers/yao2024sltsq/paper.pdf
- papers/hou2025mlteo/paper.pdf
- papers/liu2025mqdm/paper.pdf
- papers/zhang2024oscwa/paper.pdf
idea_ids: []
topics:
- Machine Learning
- Quantum Information
---

# Learned quantum-state models

**Summary**: Classical models trained on randomized or post-measurement data can predict observables, generate measurement records, or reveal conditional correlations, but their success is limited by learnability, coverage, and validation against held-out quantum data.

**Sources**: [Yao et al. (2024)](../../papers/yao2024sltsq/paper.pdf) [Hou et al. (2025)](../../papers/hou2025mlteo/paper.pdf) [Liu et al. (2025)](../../papers/liu2025mqdm/paper.pdf) [Zhang and You (2024)](../../papers/zhang2024oscwa/paper.pdf)

**Last updated**: 2026-08-22

---

## Current synthesis

ShadowGPT treats Pauli bases, Hamiltonian parameters, and outcomes as a conditional sequence model, learning a distribution from which synthetic measurement records and observables can be estimated [Yao et al. (2024), §Fig.1-and-Conclusion](../../papers/yao2024sltsq/paper.pdf#Fig.1-and-Conclusion). Measurement-induced-entanglement experiments instead learn conditional post-measurement models and correlate their predictions with an independent dataset to bound properties of unmeasured qubits [Hou et al. (2025), §Outlook](../../papers/hou2025mlteo/paper.pdf#Outlook).

The measurement-based diffusion paper adds a third use: infer trajectory information from weak-measurement records to condition reverse control [Liu et al. (2025), §Sec.III.A](../../papers/liu2025mqdm/paper.pdf#Sec.III.A). These are related data interfaces but not interchangeable scientific tasks.

Generative accuracy can hide selective loss of quantum structure. In the GHZ shadow model, an information bottleneck retains low-variance classical \(Z\)-correlations after it discards high-variance global X/Y coherence; reconstructed states may also violate positivity [Zhang and You (2024), Discussion](../../papers/zhang2024oscwa/paper.pdf#page=9).

## Validation boundary

Interpolation across a Hamiltonian parameter grid is weaker than transfer to a new Hamiltonian family. A useful benchmark should separate held-out measurement samples, held-out parameters, shifted state families, and observables not used in training. Failure to model a distribution may indicate inadequate architecture or a genuine learnability transition; these explanations require controlled scaling to distinguish.

## Related pages

- [[concepts/classical-shadow-tomography|Classical shadow tomography]]
- [[methods/measurement-conditioned-quantum-control|Measurement-conditioned quantum control]]
- [[comparisons/trajectory-vs-ensemble-recovery|Trajectory versus ensemble recovery]]
- [[concepts/information-bottleneck-quantum-classicality|Information-bottleneck quantum classicality]]
- [[papers/yao2024sltsq|ShadowGPT]]
