---
id: T-0003
title: Refocus benchmark on scalable trajectory learning
status: closed
priority: high
category: scope
created: '2026-08-23T01:40:13Z'
updated: '2026-08-23T05:36:16Z'
context: ''
benchmark_ids:
- local-petz-recovery-ladder
related: []
---

# Refocus benchmark on scalable trajectory learning

## M-001 · user · decision · 2026-08-23T01:40:13Z

The intended follow-up is to generalize the paper trajectory-level diffusion model to larger systems and demonstrate learning scalability with tensor-network methods. This direction should target a new algorithm; local Petz recovery is theoretically understood and should not remain the benchmark core.

## M-002 · agent · acknowledgment · 2026-08-23T01:45:16Z

Accepted. The benchmark core is now trajectory-level tensor-network learning: canonical MPS weak-measurement trajectories, a translation-equivariant local generator or MPO controller, oracle-versus-record ablations, and frozen train-short-test-long evaluation. Petz/CMI criticality is preserved only as pruned history.

## M-003 · agent · resolution · 2026-08-23T01:45:16Z

Redesign completed: metadata, task, wiki synthesis/frontier/question/index, Lab 001, stable-source boundary, note title, benchmark index, and global paper routing now point to scalable trajectory-level MPS/MPO learning. Validation and wiki lint are being run next.

## M-004 · agent · resolution · 2026-08-23T02:22:24Z

Correction: the user did not authorize changing local-petz-recovery-ladder. That benchmark has been restored to its Petz/CMI criticality design. The trajectory-level MPS/MPO direction has been moved into a separate benchmark, tensor-network-trajectory-diffusion; the earlier redesign messages describe a reverted intermediate state.

## M-005 · user · decision · 2026-08-23T05:36:16Z

Closed by user.
