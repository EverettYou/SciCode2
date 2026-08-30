---
title: Parametric random-matrix topology
page_type: model
status: provisional
updated: '2026-08-22'
source_refs:
- papers/lin2022focni/paper.pdf
idea_ids: []
topics:
- Topological Phases
---

# Parametric random-matrix topology

**Summary**: A momentum-parameterized random-matrix ensemble turns Weyl points into correlated signed events whose short-range pairing controls Chern-number fluctuations and their saturation.

**Sources**: [Lin et al. (2022)](../../papers/lin2022focni/paper.pdf)

**Last updated**: 2026-08-22

---

## Current synthesis

The model tracks band-touching Weyl points in a three-parameter GUE Hamiltonian and integrates their signed crossings to obtain changes in slice Chern numbers. Numerics find short-range correlations between opposite polarities, linear fluctuation growth over a limited parameter interval, and saturation set by the correlation range, with plateau scale depending on band count [Lin et al. (2022), §Abstract-and-Sec.6](../../papers/lin2022focni/paper.pdf#Abstract-and-Sec.6).

Perturbative estimates connect the Weyl-point correlation length to the fluctuation curve. The saturation is reported to persist across several tested short-range correlation shapes, while detailed finite-size constants remain ensemble-dependent [Lin et al. (2022), §Appendix-A](../../papers/lin2022focni/paper.pdf#Appendix-A).

## Benchmark opportunity

Compare independent Weyl-point tracking and lattice-Chern algorithms near avoided crossings, then test scaling under changed matrix rank and correlation kernels.

## Related pages

- [[papers/lin2022focni|Fluctuation of Chern numbers in a parametric random matrix model]]
- [[concepts/topological-responses-of-gauge-groups|Topological responses of gauge groups]]
