---
title: Symmetric mass generation
page_type: concept
status: active
updated: '2026-08-23'
source_refs:
- papers/wang2022smg/paper.pdf
- papers/you2018sfmga/paper.pdf
- papers/zeng2022smgit/paper.pdf
- papers/he2026smgia/paper.pdf
- papers/lu2024dacof/paper.pdf
- papers/guo2023smgok/paper.pdf
- papers/hou2023vmcso/paper.pdf
idea_ids: []
topics:
- Correlated Systems
---

# Symmetric mass generation

**Summary**: Symmetric mass generation gaps interacting fermions without fermion-bilinear condensation, spontaneous symmetry breaking, or intrinsic topological order, subject to anomaly cancellation and sufficiently strong interactions.

**Sources**: [Wang et al. (2022)](../../papers/wang2022smg/paper.pdf) [You et al. (2018)](../../papers/you2018sfmga/paper.pdf) [Zeng et al. (2022)](../../papers/zeng2022smgit/paper.pdf) [He et al. (2026)](../../papers/he2026smgia/paper.pdf) [Lu et al. (2024)](../../papers/lu2024dacof/paper.pdf) [Guo and You (2023)](../../papers/guo2023smgok/paper.pdf) [Hou and You (2023)](../../papers/hou2023vmcso/paper.pdf)

**Last updated**: 2026-08-23

---

## Current synthesis

SMG is a gapping mechanism in interacting fermion systems, used to describe both the resulting gapped phase (the SMG phase) and the universality class of the gap-opening transition (the SMG transition). Its defining feature is a many-body interaction-driven gap openning in a gapless fermionic system with the absence of symmetry-breaking bilinear order and topological order; anomaly freedom determines whether a symmetric gapped endpoint is possible [Wang et al. (2022), §Sec.I-and-VI](../../papers/wang2022smg/paper.pdf#Sec.I-and-VI).

The SMG transition is a metal-insulator transition: the metallic phase can be a Fermi liquid or a Dirac semimetal, while the insulating phase is featureless, with no symmetry breaking or topological order. The nature of the SMG transition remains an open question; in some systems, it is a continuous phase transition. The fermionic deconfined quantum critical point (DQCP) is a proposed description using emergent gauge fields, fermionic partons, and critical Higgs fields, and predicts a Green-function zero-to-pole change [You et al. (2018), §Abstract](../../papers/you2018sfmga/paper.pdf#Abstract). In 1+1 dimensions, DMRG on the anomaly-free 3-4-5-0 construction instead finds an interaction-gapped mirror sector and a BKT transition while the desired chiral sector stays gapless [Zeng et al. (2022), §Conclusion](../../papers/zeng2022smgit/paper.pdf#Conclusion).

Parton-guided VMC on the bilayer honeycomb model reports \(J_c=3.48\), \(\nu=0.96(3)\), and \(\Delta_c=1.31(4)\), corresponding to \(\eta_\psi\simeq0.62\), and interprets the result as support for fermion fractionalization [Hou and You (2023), §§III–V](../../papers/hou2023vmcso/paper.pdf#page=3). Later DQMC on the same Hamiltonian reports a direct continuous transition but \(\eta_\psi=0.071(1)\), sharply different from both the VMC and large-\(N\) estimates [He et al. (2026), §Discussion-and-Conclusion](../../papers/he2026smgia/paper.pdf#page=4). The shared evidence supports direct SMG more strongly than any particular infrared gauge theory; the exponent discrepancy remains unresolved.

For finite Fermi surfaces, anomaly cancellation can be classified independently of a specific gapping interaction. A vanishing Fermi-surface anomaly permits a symmetric product-state endpoint; it becomes SMG only when symmetry forbids every bilinear gap and an interacting realization actually gaps the surface [Lu et al. (2024), §§IV–V](../../papers/lu2024dacof/paper.pdf#page=10).

Kähler–Dirac fermions provide a dimension-uniform constructive example: inversion protects a \(Z_2\) bosonic SPT boundary obstruction, so two copies can be trivialized by explicit four-fermion interactions in every dimension [Guo and You (2023), §§IV–VI](../../papers/guo2023smgok/paper.pdf#page=5).

## Related pages

- [[comparisons/smg-regimes-and-diagnostics|SMG regimes and diagnostics]]
- [[concepts/doped-smg-superconductivity|Doped SMG and superconductivity]]
- [[concepts/crt-fractionalization|CRT fractionalization]]
- [[concepts/fermi-surface-anomalies|Fermi-surface anomalies]]
- [[concepts/kahler-dirac-symmetric-mass-generation|Kähler–Dirac symmetric mass generation]]
- [[concepts/grand-unified-deconfined-criticality|Grand-unified deconfined criticality]]
- [[methods/parton-guided-variational-monte-carlo|Parton-guided variational Monte Carlo]]
- [[papers/hou2023vmcso|Variational Monte Carlo study of symmetric mass generation in a bilayer honeycomb lattice model]]
- [[papers/wang2022smg|Symmetric mass generation]]
