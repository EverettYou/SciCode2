---
title: Operator selection and measured cost
page_type: comparison
status: active
updated: '2026-10-07'
source_refs:
- labs/lab-001-cluster-certificates/REPORT.md
- labs/lab-002-moment-sdp/REPORT.md
- labs/lab-004-exact-dual-verification/REPORT.md
- labs/lab-003-theory-audit/REPORT.md
- labs/lab-005-local-rdm-extension/REPORT.md
- labs/lab-006-true-cubic-grams/REPORT.md
idea_ids:
- c-001
- c-002
- c-003
- c-004
- c-005
- c-006
topics:
- Correlated Systems
---

# Operator selection and measured cost

**Summary**: Dual-guided cubic directions improve the measured bound while shrinking the replay program.

**Sources**: [lab-001-cluster-certificates evidence](../../labs/lab-001-cluster-certificates/REPORT.md); [lab-002-moment-sdp evidence](../../labs/lab-002-moment-sdp/REPORT.md); [lab-004-exact-dual-verification evidence](../../labs/lab-004-exact-dual-verification/REPORT.md); [lab-003-theory-audit evidence](../../labs/lab-003-theory-audit/REPORT.md); [lab-005-local-rdm-extension evidence](../../labs/lab-005-local-rdm-extension/REPORT.md); [lab-006-true-cubic-grams evidence](../../labs/lab-006-true-cubic-grams/REPORT.md)

**Last updated**: 2026-10-07

All energies are total energies for the same finite Hamiltonian; larger lower bounds are stronger. Canonical stage timings and process peaks are in the [resource records](../../labs/lab-001-cluster-certificates/resource-summary.json). Concurrent pilot runs affect timing, and process peaks do not measure aggregate simultaneous memory.

| Space | Certified lower bound | Solve observation | Process peak |
| --- | ---: | ---: | ---: |
| 2x4 cylinder | -14.25342470 | 105.4 s | 978 MB |
| PQG | -10.566825373980 | 40.3 s | 138 MB |
| Opposite-density T2prime | -10.268038996818 | 46.8 s | 190 MB |
| Full two-site T2prime, Clarabel | -8.864118703137 | 64.1 s | 600 MB |
| Full cubic T2prime, SCS | -8.764969112905 | 511.5 s | 266 MB |
| Same factors, equality multiplier fit | -8.764879966348 | +2.7 s | see exact JSON |
| Dual-selected scalar tests | -8.763365270237 | 27.6 s | 263 MB |
| Dual-selected six blocks | -8.763353354793 | 13.8 s | 362 MB |

The six-block replay has 11446 matrix entries versus 410274 for full cubic T2prime, about 36 times fewer. Its original O dimension is 2257 versus 33825. These gains describe replay after discovery: the full model's 50.88 s construction and 511.52 s solve still count. Auditing and exact verification also count.

The [selected-space experiments](../../labs/lab-002-moment-sdp/REPORT.md) preserve marginal T1/star additions, unresolved spin-completion gain, and weak primal eigenvector cuts. Three-site stars consumed 1.475 GB for only a small gain over two-site constraints. Tighter baseline SCS tolerances cost 314 s for about 0.0001 improvement. The full-T2 Clarabel attempt ended with exit137 and no certificate; its cause and peak are unknown, so no OOM claim is made.

The [local RDM lab](../../labs/lab-005-local-rdm-extension/REPORT.md) found five four-site compatibility fits below 5e-10 mismatch. The [shared-sextic lab](../../labs/lab-006-true-cubic-grams/REPORT.md) found that the full-T2 primal already admits its 200-variable extension within about 2.36e-9. The joint sextic solver's large residual erased any apparent primal improvement. These branches were pruned based on numerical diagnostics; neither is proved universally redundant.

[Theorem-backed S0 results](../../labs/lab-003-theory-audit/REPORT.md) use a ground-singlet equality and are listed separately from the source's full N8/N8 relaxation.

The [fresh full-model reproduction](../../labs/lab-004-exact-dual-verification/results/full-reproduction/reproduction.json) totals 198.865 s across successful phases, after a separately recorded 2.858 s metadata-audit failure and restart. Solver output was reused after correcting the descriptor. Fresh portable total is 22.953 s. SCS/Clarabel and tolerances differ, so structural cone/operator counts are the direct comparison.


## Related pages

- [Research map](../index.md)
- [Research frontier](../ideas/research-frontier.md)
