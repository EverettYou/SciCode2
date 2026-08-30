---
title: SMG regimes and diagnostics
page_type: comparison
status: active
updated: '2026-08-23'
source_refs:
- papers/chang2023fssmg/paper.pdf
- papers/he2026smgia/paper.pdf
- papers/liu2024doare/paper.pdf
- papers/zeng2024ocism/paper.pdf
- papers/lu2023fssmg/paper.pdf
- papers/guo2023smgok/paper.pdf
- papers/hou2023vmcso/paper.pdf
- papers/lu2023gfzif/paper.pdf
idea_ids: []
topics:
- Correlated Systems
---

# SMG regimes and diagnostics

**Summary**: Dirac, Fermi-surface, and chiral-fermion SMG require different diagnostics; gaps and absent bilinear order are necessary, while critical scaling, Green-function zeros, entanglement, disorder operators, and response regularization test different parts of the claim.

**Sources**: [Chang et al. (2023)](../../papers/chang2023fssmg/paper.pdf) [He et al. (2026)](../../papers/he2026smgia/paper.pdf) [Liu et al. (2024)](../../papers/liu2024doare/paper.pdf) [Zeng et al. (2024)](../../papers/zeng2024ocism/paper.pdf) [Lu et al. (2023a)](../../papers/lu2023fssmg/paper.pdf) [Guo and You (2023)](../../papers/guo2023smgok/paper.pdf) [Hou and You (2023)](../../papers/hou2023vmcso/paper.pdf) [Lu et al. (2023b)](../../papers/lu2023gfzif/paper.pdf)

**Last updated**: 2026-08-23

---

## Diagnostic ladder

1. Establish single-particle and relevant bosonic gaps with finite-size and imaginary-time convergence.
2. Exhaust the symmetry-allowed bilinear order space rather than checking only familiar channels.
3. Locate the transition with RG-invariant ratios and test competing scaling windows.
4. Use Green-function zeros to distinguish interaction-generated spectral gaps from a simple band mass where applicable.
5. Test candidate CFT behavior with disorder-operator and Rényi-entanglement scaling [Liu et al. (2024), §Abstract](../../papers/liu2024doare/paper.pdf#Abstract).
6. Derive physical response operators from a bounded lattice regularization before interpreting continuum pole-zero substitutions. The optical-conductivity analysis shows that a naive duality argument can produce an unphysical negative response, while the regularized lattice model has no subgap optical conductivity [Zeng et al. (2024), §Abstract](../../papers/zeng2024ocism/paper.pdf#Abstract).

Fermi-surface SMG preserves a finite-volume loop-group structure and can exhibit Green-function-zero surfaces pinned to the original Fermi surface [Lu et al. (2023), §Abstract](../../papers/lu2023fssmg/paper.pdf#Abstract) [Chang et al. (2023), §Abstract](../../papers/chang2023fssmg/paper.pdf#Abstract). Bilayer-honeycomb DQMC emphasizes direct versus intervening excitonic phases and symmetry-sensitive fermion anomalous dimensions [He et al. (2026), §Conclusion](../../papers/he2026smgia/paper.pdf#Conclusion).

For the bilayer square lattice, Luttinger volume is carried by Green-function zeros in the SMG insulator. Strong-coupling cluster perturbation and weak-coupling fluctuating-order analyses agree on the low-energy zero surface, while the exact surface shape relies on extra lattice symmetries and the proposed ARPES test requires Kramers–Kronig reconstruction [Lu et al. (2023), §§II–IV](../../papers/lu2023gfzif/paper.pdf#page=3).

For the same bilayer-honeycomb Hamiltonian, parton-guided VMC and DQMC agree qualitatively on direct continuous SMG but disagree quantitatively on critical fermion scaling. VMC obtains \(\eta_\psi\simeq0.62\) from \(\Delta_c=1.31(4)\) on systems up to \(L=16\) and cannot reliably extrapolate \(\Delta_c\) to infinite size [Hou and You (2023), §III](../../papers/hou2023vmcso/paper.pdf#page=3). DQMC obtains \(\eta_\psi=0.071(1)\) through moving-window extrapolation [He et al. (2026), §Fermion-anomalous-dimension](../../papers/he2026smgia/paper.pdf#page=4). Possible explanations include variational bias and finite-size effects, but the compiled evidence does not yet determine the critical theory.

Kähler–Dirac SMG adds a constructive classification check: verify the cell-complex Dirac algebra, inversion symmetry, local unique-gapped spectrum, and then the extended-lattice gap rather than inferring all of them from anomaly cancellation alone [Guo and You (2023), §§IV–VI](../../papers/guo2023smgok/paper.pdf#page=5).

## Tension

The papers support several realizations but do not establish a universal critical exponent or a universal response signature across them. Comparisons must keep dimension, symmetry group, fermion content, lattice regularization, and transition path explicit.

## Related pages

- [[concepts/symmetric-mass-generation|Symmetric mass generation]]
- [[concepts/doped-smg-superconductivity|Doped SMG and superconductivity]]
- [[methods/systematic-fermion-symmetry-analysis|Systematic fermion symmetry analysis]]
- [[methods/parton-guided-variational-monte-carlo|Parton-guided variational Monte Carlo]]
- [[concepts/kahler-dirac-symmetric-mass-generation|Kähler–Dirac symmetric mass generation]]
- [[concepts/green-function-zero-surfaces|Green-function zero surfaces]]
- [[papers/he2026smgia|Symmetric mass generation in a bilayer honeycomb lattice]]
- [[papers/hou2023vmcso|Variational Monte Carlo study of symmetric mass generation in a bilayer honeycomb lattice model]]
