---
title: Current Hubbard bootstrap thesis
page_type: thesis
status: active
updated: '2026-10-07'
source_refs:
- labs/lab-001-cluster-certificates/REPORT.md
- labs/lab-002-moment-sdp/REPORT.md
- labs/lab-004-exact-dual-verification/REPORT.md
idea_ids:
- x-001
- c-002
- c-003
- c-006
---

# Current Hubbard bootstrap thesis

**Summary**: A small dual-selected cubic space preserves the full hierarchy bound at much lower replay cost.

**Sources**: [lab-001-cluster-certificates evidence](../labs/lab-001-cluster-certificates/REPORT.md); [lab-002-moment-sdp evidence](../labs/lab-002-moment-sdp/REPORT.md); [lab-004-exact-dual-verification evidence](../labs/lab-004-exact-dual-verification/REPORT.md)

**Last updated**: 2026-10-07

The strongest promoted certificate is **E0 >= -8.763353354793**, for the original Nup=Ndown=8 relaxation, with no singlet assumption. A degree-two core plus 88 symmetry-closed cubic polynomials and their adjoints gives ambient operator dimension **2257**. The [exact certificate](../labs/lab-004-exact-dual-verification/results/dual-blocks-pqg/verification.json), [physical audit](../labs/lab-001-cluster-certificates/audit-dual-blocks-pqg.json), and [rank proof](../labs/lab-001-cluster-certificates/distilled/dual-16-pqg-q20/operator_space.json) support different parts of this claim.

The measured six-block replay has 331 variables, 54 PSD cones, maximum dimension 32, and 11446 entries. Existing-export selection/construction took 0.589 s, solving 13.82 s, physical audit 3.52 s, and exact validation 0.278 s; solver peak was 362 MB. Discovery used the full cubic model and costs an additional 50.88 s construction and 511.52 s solve. The [fresh complete portable run](../labs/lab-004-exact-dual-verification/results/portable-reproduction/reproduction.json) took 22.953 s including startup, export, validation and rank proof, with 404.5 MB largest process peak. See [cost comparisons](comparisons/operator-cost-frontier.md).

The supported inference is that selected global correlations and dual activity are more useful at this instance than enlarging local spectral support. This is empirical selection evidence, not proof of outer-search optimality. The anticommutator program certifies the declared literal operator space without asserting equality to its full cubic Gram optimum; [certificate scope](methods/exact-moment-certificates.md) explains the distinction.

Five local-density compatibility tests and the shared-sextic extension found no resolved new violation; these are numerical diagnostics, not exact feasibility theorems. [Negative branches](comparisons/operator-cost-frontier.md) preserve that limitation. A separate theorem-backed S0 experiment changes the original relaxation and is not used in the promoted bound.

The benchmark is solution-drafted with expert calibration pending. The source provides neither a public energy target nor a memory ceiling. The finite instance and standard PQGT hierarchy have prior literature; calibration should assess reproducibility and operator-cost discovery accordingly.

## Related pages

- [Research map](index.md)
- [Research frontier](ideas/research-frontier.md)
