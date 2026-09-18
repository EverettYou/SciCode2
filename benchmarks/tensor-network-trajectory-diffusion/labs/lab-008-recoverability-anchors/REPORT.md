---
document_type: lab_report
lab_id: lab-008
status: completed
idea_ids:
  - k-003
wiki_context:
  - ../../wiki/thesis.md
  - ../../wiki/ideas/recoverability-candidate.md
related_labs:
  - lab-007-paper-hamiltonian-score-matching
---

# Exact recovery anchors and evidence audit

## Motivation

The user requested a benchmark about a physical optimum with verifiable solutions.
The [candidate](../../problem/recoverability/README.md) must distinguish numerical
infrastructure from actual optimal-recovery evidence.

## Design

Use an unencoded logical qubit, inaccessible Bell reference and one positive weak
Z measurement of strength g. Erase its outcome with probability 1-eta. This is an
analytic specialization, not the candidate's nontrivial encoded chain.

## Methods and analytic reference solution

Write K_+=diag(a,b), K_-=diag(b,a), where a=sqrt((1+g)/2), b=sqrt((1-g)/2).
Identity recovery achieves

    sum_s |Tr K_s|^2/4 = (a+b)^2/2 = (1+sqrt(1-g^2))/2.

Erasure only partitions these Kraus terms into classical record blocks, so this
achievable fidelity is independent of eta. For each record block, let its positive
diagonal Kraus entries be x_h,y_h, including sqrt(eta) or sqrt(1-eta). Its objective
C has a nonzero block on |00>,|11>:

    C = (1/4) sum_h [[x_h^2, x_h*y_h], [x_h*y_h, y_h^2]].

Choose diagonal dual Y with

    Y_00 = (1/4) sum_h x_h*(x_h+y_h),
    Y_11 = (1/4) sum_h y_h*(x_h+y_h).

The supported block of I_2 tensor Y-C is
(sum_h x_h*y_h/4)*[[1,-1],[-1,1]], hence positive semidefinite; its other diagonal
entries are nonnegative. Summing Tr Y over records equals the achieved fidelity.
Weak duality proves optimality for all g,eta in [0,1].

The verifier rebuilds C and checks PSD, Hermiticity and trace preservation.
Independent tests evolve a Bell density matrix directly and check a complex,
non-symmetric unitary channel with its inverse recovery.

## Findings

The bounded checks passed on 2026-09-07.

- [Anchor results](results/anchors-v1.json): 15 pairs, g in {0,.2,.5,.8,1},
  eta in {0,.75,1}; zero computed primal/dual gap at recorded precision; agreement
  with the exact expression within 1e-10.
- [Seven tests](scripts/test_anchors.py): analytic family, explicit Bell channel,
  complex conventions, reset fidelity, and rejection of invalid trace preservation,
  false upper bounds and nonfinite certificates.
- Input-erasing reset gives entanglement fidelity 0.25 despite preparing its own
  fixed target perfectly. The observable distinguishes these tasks.
- [Historical audit](scripts/audit_existing.py): all 12 Lab 007 summary hashes and
  selected saved statistics pass. This does not rerun historical experiments.

## Reproduction and environment

Commands are in [candidate README](../../problem/recoverability/README.md).
Anchor output refuses overwrite. Use a fresh path. The result records Python,
NumPy and anchor source SHA-256. Runtime is ambient /usr/bin/python, not a locked
release environment. No packages were installed. Tests ran with that same Python.

## Limitations

No encoded-chain optimum, record advantage for that family, large-N feasibility,
phase transition, critical exponent or AI difficulty is established. Floating-point
residual checks are supported by the exact anchor derivation; they are not a general
rigorous numerical certificate engine. The one-qubit record advantage is exactly
zero, so a useful many-body effect must be demonstrated, not imposed as an answer.

## Search decision and next action

Keep k-003 as a candidate. Next construct the encoded channel and close small-system
primal/dual bounds before scaling. Prune/revise if the intended regime is trivial,
unverifiable on a workstation, or shows no useful record effect. This bounded lab
is complete; the proposed benchmark is still an author draft.

## Wiki ingest handoff

The [candidate idea](../../wiki/ideas/recoverability-candidate.md) links this raw
evidence and the next experiment. No historical fidelity is reinterpreted as an
optimal recovery result. No code is promoted to root src or note.
