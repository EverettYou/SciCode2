---
title: Structured classical-shadow protocols
page_type: comparison
status: active
updated: '2026-08-22'
source_refs:
- papers/akhtar2023safcs/paper.pdf
- papers/akhtar2024dcst/paper.pdf
- papers/hu2022hstoq/paper.pdf
- papers/hu2022lstee/paper.pdf
- papers/hu2025dorae/paper.pdf
- papers/wu2025dstpb/paper.pdf
- papers/wu2026cuacs/paper.pdf
- papers/zhang2025hcst/paper.pdf
- papers/akhtar2024mcito/paper.pdf
idea_ids: []
topics:
- Quantum Information
---

# Structured classical-shadow protocols

**Summary**: Shallow circuits, tensor-network reconstruction, Hamiltonian evolution, dual-unitary dynamics, logical post-processing, and learned circuit design occupy different points in the measurement-depth, sample-efficiency, noise, and classical-cost trade space.

**Sources**: [Akhtar et al. (2023)](../../papers/akhtar2023safcs/paper.pdf) [Akhtar et al. (2024a)](../../papers/akhtar2024dcst/paper.pdf) [Akhtar et al. (2024b)](../../papers/akhtar2024mcito/paper.pdf) [Hu et al. (2022)](../../papers/hu2022hstoq/paper.pdf) [Hu et al. (2022)](../../papers/hu2022lstee/paper.pdf) [Hu et al. (2025)](../../papers/hu2025dorae/paper.pdf) [Wu et al. (2025)](../../papers/wu2025dstpb/paper.pdf) [Wu et al. (2026)](../../papers/wu2026cuacs/paper.pdf) [Zhang et al. (2025)](../../papers/zhang2025hcst/paper.pdf)

**Last updated**: 2026-08-22

---

## Protocol landscape

- Finite-depth local Clifford circuits interpolate between local Pauli and global Clifford regimes; tensor-network representations make the reconstruction map scalable when its coefficients remain low-bond-dimension [Akhtar et al. (2023), §Sec.5](../../papers/akhtar2023safcs/paper.pdf#Sec.5).
- Dual-unitary circuits expose analytically structured operator spreading and favorable behavior for nearly full-support observables, but exact dual unitarity is a special circuit constraint [Akhtar et al. (2024), §Abstract](../../papers/akhtar2024dcst/paper.pdf#Abstract).
- Hybrid circuits permit intermittent measurements and optimize contiguous-Pauli shadow scaling at a tuned measurement-induced critical point; moving into either phase worsens the asymptotic base [Akhtar et al. (2024), Fig. 4](../../papers/akhtar2024mcito/paper.pdf#page=4).
- Chaotic Hamiltonian evolution replaces a compiled random circuit by time evolution and yields an unbiased estimator across evolution times [Hu et al. (2022), §Abstract](../../papers/hu2022hstoq/paper.pdf#Abstract).
- Logical shadows apply nonlinear, codespace-aware post-processing to noisy logical states and subsume subspace expansion and virtual distillation as special cases [Hu et al. (2022), §Abstract](../../papers/hu2022lstee/paper.pdf#Abstract).
- Shallow-shadow experiments must distinguish statistical efficiency from bias caused by noisy randomizing circuits [Hu et al. (2025), §Abstract](../../papers/hu2025dorae/paper.pdf#Abstract).
- Learned circuit search can optimize a gate dictionary and sequence for a target shadow objective, but generalization outside the training distribution is an empirical question [Wu et al. (2025), §Abstract](../../papers/wu2025dstpb/paper.pdf#Abstract).
- Contractive-unitary designs mix deterministic global structure with local randomization to reduce sample complexity for separated local operators [Wu et al. (2026), §Abstract](../../papers/wu2026cuacs/paper.pdf#Abstract).
- Hierarchical tree and holographic circuits allocate measurements across scales and approach the optimal \(d^k\) exponent for contiguous Pauli support without target-specific depth tuning, while introducing alignment, ancilla, and post-processing costs [Zhang et al. (2025), §V](../../papers/zhang2025hcst/paper.pdf#page=10).

## Cross-paper benchmark opportunity

A fair comparison should hold the observable set, state family, shot budget, hardware noise, and total classical compute fixed. Report both variance and implementation bias; otherwise a deeper or learned protocol can appear superior by moving cost into calibration or post-processing. This is wiki synthesis.

## Related pages

- [[concepts/classical-shadow-tomography|Classical shadow tomography]]
- [[concepts/learned-quantum-state-models|Learned quantum-state models]]
- [[papers/akhtar2024dcst|Dual-unitary classical shadow tomography]]
- [[papers/wu2026cuacs|Contractive unitary and classical shadow tomography]]
- [[methods/holographic-classical-shadows|Holographic classical shadows]]
- [[methods/hybrid-circuit-classical-shadows|Hybrid-circuit classical shadows]]
- [[papers/zhang2025hcst|Holographic Classical Shadow Tomography]]
