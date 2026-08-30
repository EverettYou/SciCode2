---
title: Clifford-algebra CRT classification
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/wan2023cffam/paper.pdf
- papers/li2026cfifh/paper.pdf
idea_ids: []
topics:
- Topological Phases
- Correlated Systems
---

# Clifford-algebra CRT classification

**Summary**: Real and complex Clifford representations organize fermion fields, internal symmetries, CRT extensions, admissible mass manifolds, and their dimensional reduction in a periodic classification.

**Sources**: [Wan et al. (2023)](../../papers/wan2023cffam/paper.pdf) [Li et al. (2026)](../../papers/li2026cfifh/paper.pdf)

**Last updated**: 2026-08-23

---

## Classification workflow

The first-quantized Hamiltonian approach begins from a real Clifford representation for Majorana fields or a complex Clifford representation for Dirac fields. It then identifies internal transformations commuting with the kinetic Clifford generators and combines those transformations with charge conjugation, spatial reflections, and time reversal into a generally nontrivial extension of the bosonic-looking CRT quotient [Li et al. (2026), §II.A-B and III.A-B](../../papers/li2026cfifh/paper.pdf#Sec.II.A-B-and-III.A-B).

Mass terms are treated as Clifford extensions. When several normalized masses exist, they form a mass manifold on which CRT-internal symmetries may act nontrivially. A mass domain wall selects the subgroup preserved by the wall and relates the symmetry data in adjacent spatial dimensions [Li et al. (2026), §II.C-D and III.C-D](../../papers/li2026cfifh/paper.pdf#Sec.II.C-D-and-III.C-D).

Ordinary Majorana fields cease to have half the real dimension of a Dirac field in spacetime dimensions (5,6,7\pmod 8). The classification therefore introduces symplectic Majorana fields, represented by a pair of Dirac fields with trivial charge conjugation, and embeds both Majorana types in real vector spaces. This produces the expected 8-fold Bott organization without forcing a quaternionic basis [Li et al. (2026), §I-II.A and Apps.A-C](../../papers/li2026cfifh/paper.pdf#Sec.I-II.A-and-Apps.A-C).

## Interpretation boundary

The periodic tables classify kinematic representation and symmetry data. They do not by themselves establish anomaly cancellation, construct an interacting lattice gapping path, or determine the universality class of a symmetric-mass transition. Those require the many-body and dynamical layers summarized in [[concepts/crt-fractionalization|CRT fractionalization]] and [[concepts/symmetric-mass-generation|symmetric mass generation]].

## Benchmark opportunities

- Generate Clifford representations across dimensions and reproduce invariant-group and CRT-extension tables.
- Verify mass-manifold dimensions and symmetry actions from explicit matrix realizations.
- Automate domain-wall reduction and test its mod-8 consistency.
- Cross-check basis-independent group presentations against explicit Majorana, symplectic-Majorana, and Dirac bases.

## Related pages

- [[concepts/crt-fractionalization|CRT fractionalization]]
- [[concepts/symmetric-mass-generation|Symmetric mass generation]]
- [[methods/systematic-fermion-symmetry-analysis|Systematic fermion symmetry analysis]]
- [[papers/li2026cfifh|CRT fractionalization in first-quantized Hamiltonian theory]]
- [[papers/wan2023cffam|CRT fractionalization, fermions, and mod 8 periodicity]]
