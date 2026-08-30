---
title: Systematic fermion symmetry analysis
page_type: method
status: provisional
updated: '2026-08-22'
source_refs:
- papers/he2026csaas/paper.pdf
- papers/he2026smgia/paper.pdf
idea_ids: []
topics:
- Correlated Systems
---

# Systematic fermion symmetry analysis

**Summary**: Mapping interacting fermion Hamiltonians to Majorana space turns continuous-symmetry discovery into a commuting Lie-algebra problem and candidate-order enumeration into representation decomposition.

**Sources**: [He et al. (2026)](../../papers/he2026csaas/paper.pdf) [He et al. (2026)](../../papers/he2026smgia/paper.pdf)

**Last updated**: 2026-08-22

---

## Method

The framework finds the subalgebra of $\mathfrak{so}(2N_f)$ commuting with a Majorana-form Hamiltonian, identifies its semisimple structure through Cartan subalgebras, roots, and Dynkin data, then determines the faithful group from the center's action [He et al. (2026), §Sec.IV-Conclusion](../../papers/he2026csaas/paper.pdf#Sec.IV-Conclusion). Exterior-power representations and intertwiners enumerate fermion operators, while lattice symmetries refine which order sectors are physically distinct.

Applied to benchmark models, it recovers Hubbard-model $SO(4)$ and classifies bilinear candidates; for a bilayer model it identifies $Spin(5)\times U(1)/\mathbb Z_2$ and 18 bilinear sectors [He et al. (2026), §Conclusion](../../papers/he2026csaas/paper.pdf#Conclusion). An exhaustive order-parameter search is then used as evidence against hidden symmetry breaking in SMG simulations [He et al. (2026), §Abstract](../../papers/he2026smgia/paper.pdf#Abstract).

## Benchmark opportunity

Independent symbolic and numerical implementations can be compared on randomly generated interaction tensors with known planted symmetry, checking algebra dimension, commutators, Dynkin identification, center quotient, and completeness of order sectors.

## Related pages

- [[concepts/symmetric-mass-generation|Symmetric mass generation]]
- [[concepts/crt-fractionalization|CRT fractionalization]]
- [[papers/he2026csaas|Continuous symmetry analysis and systematic identification of candidate order parameters]]
