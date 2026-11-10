# Affordable Hubbard Quantum Bootstrap Bounds

## Research goal

**Central question:** select an affordable operator space that certifies a strong lower bound for the half-filled periodic 4×4 Hubbard model, t=1 and U=8.

## Current research status

A symmetry-closed **2257-dimensional operator space** gives the independently audited, exact-arithmetic certificate **E₀ ≥ −8.763353354793** (total energy; no singlet assumption). Its reduced program has 331 variables, 54 PSD cones, largest cone 32, and 11446 full matrix entries. Fixed-space selection/construction took 0.589 s, solving 13.82 s, physical-map auditing 3.52 s, and exact certificate verification 0.278 s. Peak solver-process RSS was 362 MB. These recorded timings used existing discovery exports; fresh portable construction is measured separately in the stable reproduction record.

The space was found using a full T2prime anticommutator SDP: 50.88 s construction plus 511.52 s solving, 266 MB process peak. That discovery cost is charged separately. It has 33825 ambient operators and 410274 reduced matrix entries. A fresh full-model replay measured 198.865 s across successful stages, plus one separately recorded 2.858 s metadata-audit retry; see [full reproduction](labs/lab-004-exact-dual-verification/results/full-reproduction/reproduction.json). Runtime observations can be affected by concurrent research pilots; peaks are per process, not aggregate simultaneous memory. See the [environment](environment.json) and [resource evidence](labs/lab-001-cluster-certificates/resource-summary.json).

**Stage:** solution drafted, with a verified reference certificate. Expert calibration remains pending because the PDF supplies neither an energy threshold nor a memory ceiling. No globally optimal operator selection is claimed. The original two-hour allowance became a checkpoint when the user authorized up to one day if necessary.

## Start here

1. [Research question and exact conventions](problem/TASK.md), [metadata and source hash](metadata.yml).
2. [Stable implementation and reproduction commands](src/README.md).
3. [Research note with mathematical certificate](note/main.tex), opened in the native LaTeX editor.
4. [Exact certificate JSON](labs/lab-004-exact-dual-verification/results/dual-blocks-pqg/verification.json), [independent physical audit](labs/lab-001-cluster-certificates/audit-dual-blocks-pqg.json), and [operator-space dimension proof](labs/lab-001-cluster-certificates/distilled/dual-16-pqg-q20/operator_space.json).
5. [Evidence wiki](wiki/index.md), [preserved search frontier](wiki/ideas/research-frontier.md), and [six labs](labs/README.md).

## Source foundation

Dual-guided operator selection retained almost all full T2prime strength with about 36 times fewer matrix entries. Two-site cubic operators give a cheaper structural baseline; larger local clusters, spin completion, three-site stars, T1 additions, local density extensions, and shared sextic moments supplied useful negative or marginal comparisons. The reports distinguish exact lower certificates from numerical primal compatibility tests and theorem-specific singlet refinements.

The next benchmark-design decision is human calibration of a public energy target and resource budget, including how to account for previously published methods. There is no pending input needed to reproduce the reference certificate. The immutable [supplied PDF](problem/references/scicode2-hubbard.pdf) is a direct user-provided question; no reviewed-paper assessment or provenance is fabricated.

## Reading discipline

The [labs](labs/README.md), exported JSON data, and exact proof files own the scientific evidence. This README provides navigation and status. Reduced cone dimensions, active dual directions, and the full declared operator dimension are different quantities.

- **Current thesis:** dual-guided selection preserves the tested full T2prime anticommutator strength with a much smaller replay program.
- **Active frontier:** [expert calibration k-002](wiki/ideas/research-frontier.md); scientific branch history is preserved there.
- **Active lab:** [lab 004](labs/lab-004-exact-dual-verification/REPORT.md) has completed full discovery-cost reproduction; all six labs are complete.
- **Latest supported evidence:** [fresh complete selected-space reproduction](labs/lab-004-exact-dual-verification/results/portable-reproduction/reproduction.json) reproduces the exact bound and operator dimension.
- **Main uncertainty:** public target/resource calibration and global optimality of operator selection.
- **Next decisive action:** expert review of target energy, budget, and the role of prior published methods.
- **Blockers or pending human input:** none for the reference solution; benchmark calibration remains pending.
- **Last meaningful update:** 2026-10-07; initial start07:36:39UTC, later authorized up to one day if necessary.
