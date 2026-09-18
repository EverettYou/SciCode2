---
title: Certified recoverability benchmark candidate
page_type: ideas
status: provisional
updated: '2026-09-08'
source_refs:
  - labs/lab-008-recoverability-anchors/REPORT.md
  - labs/lab-009-encoded-recoverability/REPORT.md
  - labs/lab-007-paper-hamiltonian-score-matching/REPORT.md
idea_ids:
  - k-003
---

# Certified recoverability candidate

**Summary**: A user-requested candidate separates measured decoder performance
from the optimum of a fixed physical channel. It is a new branch alongside the
reviewed trajectory-controller task.

**Sources**: [Lab 008](../../labs/lab-008-recoverability-anchors/REPORT.md),
[Lab 007](../../labs/lab-007-paper-hamiltonian-score-matching/REPORT.md),
[candidate](../../problem/recoverability/README.md).

**Last updated**: 2026-09-08.

## k-003 — knowledge — frontier

- **Parents:** x-001, k-001 from [the existing frontier](research-frontier.md).
- **Origin:** user discussion on 2026-09-07; reviewed MQDM physical-validity and
  trajectory/ensemble pitfalls, via [global synthesis](../../../../wiki/papers/liu2025mqdm.md).
- **Statement:** Recover unknown encoded information with an inaccessible reference;
  bound optimal entanglement fidelity using independently verifiable certificates.
- **Rationale:** The physical optimum is unchanged when a better decoder is invented.
- **Evidence:** [Lab 009](../../labs/lab-009-encoded-recoverability/REPORT.md) supports verified N=2,4 optima and an N=6 pilot with width 1.51e-5. Lab 008 supplies analytic anchors.
  Lab 007 supports numerical infrastructure, not optimal recovery for this task.
- **Next action:** Calibrate N=8,g=.5,.8 at width 1e-4, including verification cost.
  The old .02 gate is retired because a standard no-training baseline passes it.
  Freeze a validated grid before conducting blind AI trials.
- **Keep:** Useful physical effect, independent bounds and workstation reference.
- **Prune/revise:** A trivial exact solution over the intended regime, unresolved
  effect, or infeasible verification. Preserve outcomes as evidence.
- **Decision:** Keep the physical-optimum candidate on measured evidence. N=2,4
  and one N=6 reference exist; N=8, AI difficulty and transitions remain unverified.
- **Stable artifacts:** None.

## Related pages

- [Research frontier](research-frontier.md)
- [Current synthesis](../thesis.md)
- [Candidate problem](../../problem/recoverability/README.md)
