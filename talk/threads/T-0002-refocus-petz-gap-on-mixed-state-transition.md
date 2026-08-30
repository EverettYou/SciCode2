---
id: T-0002
title: Refocus Petz gap on mixed-state transition
status: closed
priority: high
category: scientific
created: '2026-08-23T01:29:17Z'
updated: '2026-08-23T05:36:06Z'
context: ''
benchmark_ids:
- local-petz-recovery-ladder
related:
- benchmarks/local-petz-recovery-ladder/metadata.yml
- benchmarks/local-petz-recovery-ladder/problem/TASK.md
- benchmarks/local-petz-recovery-ladder/wiki/thesis.md
- benchmarks/local-petz-recovery-ladder/wiki/ideas/research-frontier.md
---

# Refocus Petz gap on mixed-state transition

## M-001 · user · advice · 2026-08-23T01:29:17Z

The current local-petz-recovery-ladder overcomplicates the task. Refocus the central question on using the local-versus-global Petz recovery gap to characterize a mixed-state phase transition where the CMI or Markov length diverges. First determine whether a suitable one-dimensional transition exists, then choose a system and numerical methods that can verify it.

## M-002 · agent · acknowledgment · 2026-08-23T01:29:17Z

I will make the Petz gap the primary transition diagnostic, treat numerical invariants as controls, and add a model-selection gate. The literature check distinguishes a canonical 2D toric-code decodability transition from 1D GHZ/short-range-chain examples, which do not by themselves establish a generic finite-noise CMI-length divergence. I will revise the benchmark around that distinction and select methods by model geometry.

## M-003 · agent · resolution · 2026-08-23T01:37:19Z

Refocused the benchmark around the operational gap Δ_R(r,g,L) and recovery length r_ε. Added an explicit 1D model-qualification gate; pruned the unsupported use of the pure TFIM point Bx=1 as a mixed-state critical anchor; retained 1D GHZ and finite-range chains as endpoint or negative controls; selected the decohered 2D toric-code decodability transition as the qualified default. Replaced generic MPS scaling with dense overlap checks, commuting Petz-to-Bayesian validation, stabilizer/error-class enumeration, random-bond-Ising tensor contraction, and Monte Carlo finite-size scaling. Updated metadata, task, thesis, research frontier, question page, Lab 001, index, note boundary, and dashboard. Benchmark validation passes and wiki lint reports zero errors and zero warnings.

## M-004 · user · decision · 2026-08-23T05:36:06Z

Closed by user.
