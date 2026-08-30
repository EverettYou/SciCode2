---
title: Companion quantum-diffusion implementation
page_type: implementation
status: needs-validation
updated: '2026-08-22'
source_refs:
- papers/liu2025mqdm/repo
idea_ids: []
topics:
- Quantum Information
---

# Companion quantum-diffusion implementation

**Summary**: A small PyTorch/Transformers package for weak-measurement trajectories and transformer-conditioned unitary feedback; it is a static code snapshot requiring runtime validation and does not implement local Petz recovery.

**Sources**: `repository:liu2025mqdm

**Last updated**: 2026-08-22

---

## Architecture and interfaces

- `WeakMeasurement` builds and samples six local Pauli Kraus outcomes and tensors local operators across qubits [Liu quantum-diffusion repository, src/operator.py · WeakMeasurement](../../papers/liu2025mqdm/repo/src/operator.py#WeakMeasurement).
- `ForwardDiffusion` owns the state, advances it with weak measurements, and returns outcome trajectories [Liu quantum-diffusion repository, src/diffusion.py · ForwardDiffusion](../../papers/liu2025mqdm/repo/src/diffusion.py#ForwardDiffusion).
- `PolicyModel` converts a future outcome slice into a full $2^N\times2^N$ unitary through a Llama-style transformer and QR factorization [Liu quantum-diffusion repository, src/model.py · PolicyModel](../../papers/liu2025mqdm/repo/src/model.py#PolicyModel).
- `BackwardDiffusion` applies policy unitaries either with additional sampled weak measurements or through a separate trajectory-reversal path [Liu quantum-diffusion repository, src/diffusion.py · BackwardDiffusion](../../papers/liu2025mqdm/repo/src/diffusion.py#BackwardDiffusion).
- `DiffusionTrainer` collects trajectories and optimizes `QuantumDiffusionLoss` [Liu quantum-diffusion repository, src/model.py · DiffusionTrainer](../../papers/liu2025mqdm/repo/src/model.py#DiffusionTrainer).

The documented public experiment surface is `ForwardDiffusion` and `BackwardDiffusion`; direct `WeakMeasurement` calls are reserved for construction, tests, or custom pipelines [Liu quantum-diffusion repository, doc/usage.md · intended-api](../../papers/liu2025mqdm/repo/doc/usage.md#intended-api). Dependencies are PyTorch 2+ and Transformers 4.40+ [Liu quantum-diffusion repository, requirements.txt](../../papers/liu2025mqdm/repo/requirements.txt).

## Scale and validation boundary

States, operators, and predicted unitaries are dense in dimension $2^N$, so both memory and QR cost grow exponentially with qubit count [Liu quantum-diffusion repository, doc/design.md · pytorch-design](../../papers/liu2025mqdm/repo/doc/design.md#pytorch-design). The snapshot has notebook checks but no conventional automated test suite discovered. No code was executed during ingest; numerical correctness, training behavior, and notebook reproducibility remain unverified.

## Related pages

- [[papers/liu2025mqdm|Measurement-based quantum diffusion models]]
- [[concepts/weak-measurement-quantum-diffusion|Weak-measurement quantum diffusion]]
- [[comparisons/trajectory-vs-ensemble-recovery|Trajectory versus ensemble recovery]]
