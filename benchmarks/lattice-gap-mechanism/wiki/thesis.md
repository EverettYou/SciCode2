---
title: Current synthesis
page_type: synthesis
status: provisional
updated: '2026-10-26'
source_refs:
- wiki/papers/chang2023fssmg.md
- problem/TASK.md
- wiki/papers/lu2023sfdsm.md
- labs/lab-002-cluster-spectra/REPORT.md
- labs/lab-003-local-spin-dos/REPORT.md
- labs/lab-004-stm-greens-function/REPORT.md
idea_ids:
- x-001
- k-001
- k-002
---

# Current synthesis

**Summary**: The solver sees curves, not the names of the lattice or the phases. An intralayer Hubbard antiferromagnet and an interlayer-singlet product are the hidden contrast those curves have to separate.

**Sources**: [Chang et al. synthesis](../../../wiki/papers/chang2023fssmg.md); [benchmark task](../problem/TASK.md)

**Last updated**: 2026-10-26

---

## Current synthesis

The source paper gives an existence proof that a square-lattice Fermi surface can be gapped by interaction without symmetry breaking, and that weak coupling on the same lattice prefers an exciton instability because of nesting [Chang et al. synthesis, scientific role](../../../wiki/papers/chang2023fssmg.md#scientific-role). Local tunneling does not resolve the momentum-space difference between a folded quasiparticle gap and a gap whose Luttinger volume is carried by Green's-function zeros. The benchmark therefore gives the solver schematic curves and a fourfold sheet symmetry, and asks for a model plus an ARPES prediction [Benchmark task, public prompt](../problem/TASK.md#public-prompt). A mixed-dimensional bilayer supplies the hidden coupling contrast: interlayer exchange dominant is an interlayer-singlet product, and intralayer coupling dominant is a nearly decoupled Hubbard antiferromagnet [Bohrdt et al., arXiv:2108.04118](https://arxiv.org/abs/2108.04118). The public spectra are one parameter set, $t_2=0.2t_1$ and $J=8t_1$ [Lab 004](../labs/lab-004-stm-greens-function/REPORT.md). Tunneling is the zone sum of the spectral function in Eq. (19) of Lu, Zeng, and You. Its inner edges are at $\pm 6t_1$, the resistivity is activated with that edge, and the occupied peaks lie on the same lower band. The local magnetic intensity is the momentum sum of the second-order triplon band of those same hoppings and is zero below $4.69t_1$. The eight-site ladder is not part of the prompt.

The three facts are compatible with more than one phase. A band insulator, a spin-gapped magnetic state, an exciton insulator, and a symmetric interaction-generated gap can all be arranged to show a charge gap, a spin gap, and no superconducting transport. The prompt is a modeling test because the interesting mechanisms are not separated until the ARPES prediction is specific.

## Strongest support

- The source calculation finds a single-particle gap on both sides of its transition, so a gap is not a phase label [Chang et al. synthesis](../../../wiki/papers/chang2023fssmg.md).
- In the symmetric gapped regime, the source spectrum is broad and the zero-frequency Green's-function zeros track the original Fermi surface. That is an ARPES-level statement, not an STM statement.
- Bilinear mean-field theory has an order parameter only for the symmetry-breaking side.

## Tensions and alternatives

- The public facts are a designed prompt. The source paper does not report this tunneling, local magnetic, and transport set as a measured dataset.
- An exciton insulator can also gap charge and spin while preserving spin rotation. A local intensity that is zero only below a finite energy does not by itself remove it. ARPES folding is the intended separator, and that claim is still a hypothesis.
- Transport "no superconductivity" does not say whether the bulk is insulating. Upgrading the sentence would change which mechanisms survive.
- Doping is a natural second prediction and is not part of the first prompt.

## Frontier

The next informative step is the phenomenon card in Lab 001: freeze the public sentences, and write the mechanism table that shows which ARPES feature each survivor must get wrong. Computing a spectrum before that table exists does not change the question.

## Related pages

- [Research frontier](ideas/research-frontier.md)
- [ARPES prediction target](questions/arpes-prediction.md)
