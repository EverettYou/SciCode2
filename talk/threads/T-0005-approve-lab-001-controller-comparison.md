---
id: T-0005
title: Approve Lab 001 controller comparison
status: closed
priority: blocking
category: checkpoint
created: '2026-08-23T04:12:00Z'
updated: '2026-08-23T05:34:18Z'
context: 'Benchmark: tensor-network-trajectory-diffusion

  Lab 001 is a controlled N=1,2 dense-vector comparison only. The companion trajectories, future-record encoder, loss, optimizer budget, dtype, and evaluation are fixed; only the dense QR unitary head is compared against local-Hamiltonian and direct local-gate heads. The benchmark metadata requires expert review before experimental execution. The plan explicitly forbids MPS scaling, truncation sweeps, N>2 training, and size transfer at this stage.'
benchmark_ids:
- tensor-network-trajectory-diffusion
related:
- benchmarks/tensor-network-trajectory-diffusion/metadata.yml
- benchmarks/tensor-network-trajectory-diffusion/labs/lab-001-local-controller-feasibility/PLAN.md
- benchmarks/tensor-network-trajectory-diffusion/labs/lab-001-local-controller-feasibility/REPORT.md
---

# Approve Lab 001 controller comparison

## M-001 · agent · question · 2026-08-23T04:12:00Z

The narrowly scoped Lab 001 plan is ready for execution. It will reproduce the companion dense-QR baseline, freeze its splits, validate QR refactoring, unitary/finite-difference/Quimb exact-circuit parity, then compare matched local heads at N=1,2 only. Recommendation: approve this controlled plan, or specify the smallest required design change; no MPS or scaling work will begin without a later go/no-go decision.

## M-002 · agent · acknowledgment · 2026-08-23T04:42:06Z

The user approved and requested kickoff in the active Codex task. Applied the approval to benchmark metadata and activated Lab 001 under the exact N=1,2 controller-comparison boundary. This thread remains open because only the user may close it; no further input is currently pending.

## M-003 · agent · resolution · 2026-08-23T05:31:18Z

Superseded the planned N=1,2 three-head comparison after the user clarified the controller definition in the active Codex task. A generic gate on any contiguous block of at most R sites remains parameterized by a dense complex matrix followed by QR; when N<=R, including N=1,2 with R>=N, that allowed block spans the full system and is not a distinct locality hypothesis. Lab 001 is now limited to companion dense-QR behavioral and encoder/interface qualification. Existing Hamiltonian/Euler prototype artifacts are retained as reframed branch history, but their training comparison is deprecated. Updated benchmarks/tensor-network-trajectory-diffusion/metadata.yml, problem/TASK.md, README.md, labs/lab-001-local-controller-feasibility/PLAN.md, REPORT.md, and the local wiki. A meaningful controller experiment requires N>R and a new reviewed dense-state plan; MPS scaling, truncation, N>2 training, and size transfer remain unauthorized.

## M-004 · user · response · 2026-08-23T05:34:16Z

yes, autoresearch has started, I will close this thread.

## M-005 · user · decision · 2026-08-23T05:34:18Z

Closed by user.
