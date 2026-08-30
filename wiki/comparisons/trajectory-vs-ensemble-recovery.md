---
title: Trajectory versus ensemble recovery
page_type: comparison
status: provisional
updated: '2026-08-22'
source_refs:
- papers/liu2025mqdm/paper.pdf
- papers/liu2025mqdm/repo
idea_ids: []
topics:
- Quantum Information
---

# Trajectory versus ensemble recovery

**Summary**: Trajectory recovery learns record-conditioned unitaries for pure states; ensemble recovery reconstructs or applies recovery channels to an averaged mixed state. The companion repo currently addresses the former, not the local Petz branch.

**Sources**: `paper:liu2025mqdm`; `repository:liu2025mqdm `repository:liu2025mqdm

**Last updated**: 2026-08-22

---

## Two recovery targets

The paper's trajectory target is a distribution of conditioned pure states and uses a classical decoder plus learned control Hamiltonian/unitary generators. Its ensemble target is the averaged density matrix and uses classical-shadow reconstruction or Petz recovery [Liu et al. (2025), §p.3-Fig.1-and-Sec.III-IV](../../papers/liu2025mqdm/paper.pdf#p.3-Fig.1-and-Sec.III-IV).

The companion repository tokenizes future measurement records, passes them through a small Llama-style transformer, projects to a complex matrix, and obtains a unitary by QR decomposition [Liu quantum-diffusion repository, doc/design.md · policy-model-transformer-with-full-trajectory-conditioning-and-qr-unitary](../../papers/liu2025mqdm/repo/doc/design.md#policy-model-transformer-with-full-trajectory-conditioning-and-qr-unitary). Its loss trains that unitary against products of trajectory Kraus operators [Liu quantum-diffusion repository, src/model.py · QuantumDiffusionLoss](../../papers/liu2025mqdm/repo/src/model.py#QuantumDiffusionLoss).

## Paper–code boundary

No inspected repository module constructs density-matrix Petz maps, modular-flow quadrature, CMI, or the ten-qubit local-Petz experiment. Therefore the code snapshot is relevant to the paper's trajectory-level branch and cannot be cited as an implementation of its ensemble-level local recovery result [Liu quantum-diffusion repository, src/__init__.py](../../papers/liu2025mqdm/repo/src/__init__.py). This conclusion is from static inspection; runtime tests were not executed.

## Related pages

- [[papers/liu2025mqdm|Measurement-based quantum diffusion models]]
- [[concepts/weak-measurement-quantum-diffusion|Weak-measurement quantum diffusion]]
- [[methods/twirled-petz-recovery|Twirled Petz recovery]]
- [[implementations/liu-quantum-diffusion-companion|Companion quantum-diffusion implementation]]
