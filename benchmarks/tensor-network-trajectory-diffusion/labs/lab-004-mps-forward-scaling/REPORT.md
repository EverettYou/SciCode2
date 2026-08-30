---
document_type: lab_report
lab_id: lab-004
status: completed
idea_ids:
  - c-001
  - k-001
wiki_context:
  - ../../wiki/thesis.md
related_labs:
  - lab-003-mps-dense-parity
---

# Lab 004: MPS forward-trajectory resource sweep

## Narrow question

Can the parity-validated MPS forward weak-measurement path run larger product-
state chains with controlled norm and bond dimension, without dense vectors?

## Scope

This is a forward-backend resource experiment only. A global dense QR reverse
policy cannot be evaluated at these sizes and is deliberately excluded.

## Findings

The prescribed eight-trajectory, six-step sweep completed with no effective
truncation and a realized maximum bond dimension of one at every size. Wall
times were 0.116, 0.391, 1.305, 2.659, and 4.997 seconds at $N=4,8,16,24,32$.
For scale context only, one dense complex128 state would require 256 B, 4 KiB,
1 MiB, 256 MiB, and 64 GiB at those sizes. The fixed-record product regime is
intentionally low-entanglement; it establishes forward-backend feasibility,
not a general MPS scaling law or reverse-controller result.

## Motivation

After parity, this checks whether local forward updates operate beyond dense sizes.

## Design

Seeded product trajectories isolate no-truncation MPS local-update cost.

## Wiki ingest handoff

Ingest as low-entanglement forward-backend evidence only.
