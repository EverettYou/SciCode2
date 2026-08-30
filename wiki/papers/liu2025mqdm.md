---
title: Measurement-based quantum diffusion models
page_type: paper
status: ingested
updated: '2026-08-22'
source_refs:
- papers/liu2025mqdm/paper.pdf
- papers/liu2025mqdm/repo
idea_ids: []
---

# Measurement-based quantum diffusion models

**Summary**: Routing page for Liu et al.'s paper bundle: the paper develops trajectory- and ensemble-level reversal, while the companion code currently implements the trainable trajectory-level branch.

**Sources**: `paper:liu2025mqdm`; `repository:liu2025mqdm

**Last updated**: 2026-08-22

---

## Source bundle

- Paper: [paper.pdf](../../papers/liu2025mqdm/paper.pdf), arXiv:2508.08799, 36 pages.
- Source archive: [source.tar](../../papers/liu2025mqdm/source.tar).
- Companion code snapshot: [repo entry point](../../papers/liu2025mqdm/repo/src/__init__.py) inspected statically; no repository commit metadata is present.

The paper separates pure-state trajectory recovery from mixed-state ensemble-average recovery [Liu et al. (2025), §p.1](../../papers/liu2025mqdm/paper.pdf#p.1). The repository must therefore be read through the paper–code boundary below, rather than assumed to implement the local Petz experiment.

## Compiled knowledge

- [[concepts/weak-measurement-quantum-diffusion|Weak-measurement quantum diffusion]]
- [[concepts/finite-markov-length|Finite Markov length]]
- [[methods/twirled-petz-recovery|Twirled Petz recovery]]
- [[comparisons/global-vs-local-petz|Global versus local Petz recovery]]
- [[comparisons/trajectory-vs-ensemble-recovery|Trajectory versus ensemble recovery]]
- [[implementations/liu-quantum-diffusion-companion|Companion quantum-diffusion implementation]]

## Benchmark use

- [[benchmarks/local-petz-recovery-ladder/wiki/index|Petz recovery gap at mixed-state criticality]] uses the ensemble-level Petz branch to test recovery radius as a mixed-state transition diagnostic.
- [[benchmarks/tensor-network-trajectory-diffusion/wiki/index|Scalable tensor-network quantum trajectory diffusion]] uses the trajectory-level branch and companion code as the dense baseline for a size-transferable MPS/MPO learning algorithm.

## Related pages

- [[papers/index|Papers]]
- [[benchmarks/index|Benchmarks]]
