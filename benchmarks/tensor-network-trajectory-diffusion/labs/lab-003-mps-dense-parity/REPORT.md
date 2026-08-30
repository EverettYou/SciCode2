---
document_type: lab_report
lab_id: lab-003
status: completed
idea_ids:
  - c-001
  - c-004
wiki_context:
  - ../../wiki/thesis.md
related_labs:
  - lab-001-local-controller-feasibility
---

# Lab 003: Small-system MPS/dense parity

## Narrow question

Does an untruncated MPS implementation execute the same conditioned weak-
measurement trajectories and frozen-policy reverse updates as the dense
reference at $N=1,2,3$?

## Scope

This lab verifies execution correctness on an exactly checkable overlap. It
does not train an MPS policy, test differentiable MPS optimization, introduce
truncation, or make a large-system scalability claim.

## Findings

The frozen execution-parity run passed at $N=1,2,3$ on eight validation
trajectories per size, with `cutoff=0` and no bond cap. The maximum selected
outcome-probability errors were $8.33\times10^{-17}$, $1.67\times10^{-16}$,
and $3.05\times10^{-16}$; maximum forward-state errors were
$2.29\times10^{-16}$, $2.29\times10^{-16}$, and $1.08\times10^{-15}$; and
maximum frozen-policy reverse-state errors were $5.12\times10^{-16}$,
$4.96\times10^{-16}$, and $5.98\times10^{-16}$, respectively. All are below
the $10^{-10}$ gate. The policy is frozen random dense QR, so its poor reversal
fidelity is expected and identical on both backends; this validates execution
semantics rather than recovery quality. Gradient/training and truncation
parity remain follow-on work.

## Motivation

Small-system parity makes the MPS path trustworthy before large-$N$ use.

## Design

Records, states, weights, and update order are fixed; only representation varies.

## Wiki ingest handoff

Ingest as execution correctness only, not learned-control scalability.
