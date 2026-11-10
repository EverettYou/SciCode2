---
title: Operator-space search frontier
page_type: ideas
status: active
updated: '2026-10-07'
source_refs:
- problem/TASK.md
- labs/lab-001-cluster-certificates/REPORT.md
- labs/lab-002-moment-sdp/REPORT.md
- labs/lab-004-exact-dual-verification/REPORT.md
idea_ids:
- x-001
- c-001
- c-002
- k-001
- c-003
- c-004
- c-005
- c-006
- k-002
---

# Operator-space search frontier

**Summary**: Preserved branching history culminates in a certified small cubic space.

**Sources**: [problem evidence](../../problem/TASK.md); [lab-001-cluster-certificates evidence](../../labs/lab-001-cluster-certificates/REPORT.md); [lab-002-moment-sdp evidence](../../labs/lab-002-moment-sdp/REPORT.md); [lab-004-exact-dual-verification evidence](../../labs/lab-004-exact-dual-verification/REPORT.md)

**Last updated**: 2026-10-07

The root x-001 derives from metadata.idea_sources[0], the supplied problem question. Branches below preserve their ancestry and measured decisions.

- **x-001** (cross, distilled): affordable certified bound for the specified instance. Supported output: [stable code](../../src/README.md) and [research note](../../note/main.tex). Outer global optimality is not claimed.
- **c-001** (code, kept; parent x-001): translated cluster Hamiltonian certificates. Best tested cylinder -14.25342470; retain as an independent baseline, prune further support growth at the measured cost. [Lab 001](../../labs/lab-001-cluster-certificates/REPORT.md).
- **c-002** (code, distilled; parent x-001): global PQG moment positivity. Exact certificate beats tested clusters; promoted core and verifier live in [src](../../src/README.md). [Lab 002](../../labs/lab-002-moment-sdp/REPORT.md).
- **k-001** (knowledge, distilled; parent x-001): exact CAR, fixed-sector identities, and error control. Promoted proof in [note](../../note/main.tex); [lab 004](../../labs/lab-004-exact-dual-verification/REPORT.md).
- **c-003** (code, kept; parents c-002,k-001): degree-three anticommutator positivity with eliminated sextic moments. Full cubic and two-site models establish the comparison hierarchy. T1, spin completion and star additions yielded marginal or unresolved benefit; [labs 002/003](../../labs/lab-003-theory-audit/REPORT.md).
- **c-004** (code, pruned; parents c-003,k-001): local four-site density extension. Five compatibility tests found no resolved violation; this is not a redundancy theorem. [Lab 005](../../labs/lab-005-local-rdm-extension/REPORT.md).
- **c-005** (code, pruned; parents c-003,k-001): shared sixth-degree moments for true cubic Grams. Fixed global moments already admit the tested extension; joint SCS residual overwhelms any energy gain. [Lab 006](../../labs/lab-006-true-cubic-grams/REPORT.md).
- **c-006** (code, distilled; parents c-003,k-001): dual-guided direction selection, symmetry closure, and compact replay. Six reduced blocks certify -8.763353354793 with literal O dimension2257. [Exact proof](../../labs/lab-004-exact-dual-verification/REPORT.md#final-selected-space-certificates); [operator rank](../../labs/lab-001-cluster-certificates/distilled/dual-16-pqg-q20/operator_space.json).
- **k-002** (knowledge, frontier; parent x-001): expert benchmark calibration. Next action: choose public target and resource accounting, considering prior published 4x4 PQGT studies. No human decision is needed to reproduce the reference certificate.

No failed branch is erased. Fixed-space replay costs and full discovery costs remain distinct and both are charged.

## Related pages

- [Research map](../index.md)
- [Research frontier](../ideas/research-frontier.md)
