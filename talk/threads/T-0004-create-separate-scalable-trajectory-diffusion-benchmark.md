---
id: T-0004
title: Create separate scalable trajectory diffusion benchmark
status: closed
priority: high
category: scope
created: '2026-08-23T02:22:25Z'
updated: '2026-08-23T05:34:52Z'
context: ''
benchmark_ids:
- tensor-network-trajectory-diffusion
related: []
---

# Create separate scalable trajectory diffusion benchmark

## M-001 · user · decision · 2026-08-23T02:22:25Z

Preserve local-petz-recovery-ladder unchanged. Use the create-benchmark workflow to create a separate benchmark for generalizing trajectory-level diffusion to larger systems with tensor-network methods and demonstrating learning scalability.

## M-002 · agent · acknowledgment · 2026-08-23T02:22:25Z

Accepted. Created tensor-network-trajectory-diffusion as an independent benchmark and restored local-petz-recovery-ladder to its prior Petz/CMI scope. The two projects now have separate metadata, wiki, labs, and index entries.

## M-003 · agent · resolution · 2026-08-23T02:22:25Z

The new benchmark design is complete and awaiting validation: its core is MPS weak-measurement trajectories, a translation-equivariant local controller, oracle-versus-record ablations, and frozen train-short-test-long evaluation.

## M-004 · user · decision · 2026-08-23T04:00:00Z

Do not begin with the full many-body scaling problem. Use the repository's existing dense-vector single- or two-qubit experiment as the baseline, replace it with the extensible tensor-network or quantum-circuit architecture, and first test whether that architectural change works.

## M-005 · agent · resolution · 2026-08-23T04:00:00Z

Lab 001 is narrowed to a controlled one- and two-qubit head-replacement experiment. MPS scaling and short-to-long transfer are now gated later phases rather than Lab 001 deliverables.

## M-006 · user · decision · 2026-08-23T05:34:52Z

Closed by user.
