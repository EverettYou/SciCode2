---
id: T-0001
title: Review exact calibration scope
status: closed
priority: high
category: checkpoint
created: '2026-08-22T10:26:56Z'
updated: '2026-08-23T05:35:03Z'
context: 'Benchmark: local-petz-recovery-ladder'
benchmark_ids:
- local-petz-recovery-ladder
related:
- benchmarks/local-petz-recovery-ladder/metadata.yml
- benchmarks/local-petz-recovery-ladder/problem/TASK.md
- benchmarks/local-petz-recovery-ladder/ideas.yml
- benchmarks/local-petz-recovery-ladder/labs/lab-001-exact-local-calibration/REPORT.md
- benchmarks/local-petz-recovery-ladder/labs/lab-001-exact-local-calibration/PLAN.md
- benchmarks/local-petz-recovery-ladder/wiki/thesis.md
---

# Review exact calibration scope

## M-001 · agent · question · 2026-08-22T10:26:56Z

The proposed first lab calibrates global versus local twirled Petz recovery on exact open Ising chains ($N=3$--$8$). It includes near-critical fields $B_x=0.8,1.0,1.2$ alongside the paper's off-critical $B_x=1.5,2.0,5.0$ controls and requires CMI, global/local error metrics, Choi positivity, trace preservation, and numerical convergence before any MPS scale-up.

I recommend retaining this breadth because the near-critical points are the main discriminating stress test while the off-critical points anchor the source comparison. Should lab 001 retain this full field grid, or should the initial implementation target be narrowed before execution?

## M-002 · user · response · 2026-08-22T18:37:47Z

local recovery is expected to fail at the critical point as Markov length diverges. local recovery will match global recovery better away from the critical point. read the related papers cited in the reference paper about this. it is interesting to test both on and off critical to see the contrast.

## M-003 · agent · acknowledgment · 2026-08-22T19:36:39Z

[process-talk:working] I will retain both critical and off-critical comparisons, inspect the cited recovery literature and the linked calibration plan, then update the scoped artifacts with the expected contrast and verification criteria.

## M-004 · agent · resolution · 2026-08-22T19:38:28Z

[process-talk:done] Retained the full critical/off-critical grid and made the contrast a prospective matched test: $B_x=1.0$ is the finite-size critical anchor; compare it with off-critical controls $B_x\in\{1.5,2.0,5.0\}$ and crossover points $B_x\in\{0.8,1.2\}$. The plan requires matched settings, uncertainty/effect-size reporting, and preservation of null or reversed outcomes; it does not infer thermodynamic divergence from $N=3$--$8$. Added $k$-003 and updated the finite-Markov-length and thesis synthesis. I inspected the source paper cited work by Sang and Hsieh, *Stability of mixed-state quantum phases via finite Markov length* ([arXiv:2404.07251](https://arxiv.org/abs/2404.07251)); it motivates Markov-length divergence at a mixed-state transition but does not establish this finite-chain Petz outcome. Artifacts: [PLAN.md](benchmarks/local-petz-recovery-ladder/labs/lab-001-exact-local-calibration/PLAN.md), [REPORT.md](benchmarks/local-petz-recovery-ladder/labs/lab-001-exact-local-calibration/REPORT.md), [ideas.yml](benchmarks/local-petz-recovery-ladder/ideas.yml), [finite-markov-length.md](benchmarks/local-petz-recovery-ladder/wiki/concepts/finite-markov-length.md), and [thesis.md](benchmarks/local-petz-recovery-ladder/wiki/thesis.md). Checks performed: parsed YAML for ideas.yml and metadata.yml, verified k-003 linkage, and ran git diff --check.

## M-005 · user · decision · 2026-08-23T05:35:03Z

Closed by user.
