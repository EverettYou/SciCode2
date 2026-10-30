---
title: ARPES prediction target
page_type: question
status: provisional
updated: '2026-10-26'
source_refs:
- wiki/papers/chang2023fssmg.md
- problem/TASK.md
idea_ids:
- k-002
---

# ARPES prediction target

**Summary**: ARPES is the withheld observable. A successful prediction has to say more than that a gap exists.

**Sources**: [Chang et al. synthesis](../../../../wiki/papers/chang2023fssmg.md); [benchmark task](../../problem/TASK.md)

**Last updated**: 2026-10-26

---

## Question

Which features of a predicted ARPES spectrum can separate a symmetric interaction-generated gap from a band insulator, a spin-gapped magnet, and an exciton or pairing state, given only square-lattice symmetry, an STM charge gap, a neutron spin gap, and no superconductivity in transport?

## Working standard

The prediction is useful when it commits to at least one of these: whether the occupied spectrum is folded by a finite ordering wavevector, whether the gap-edge weight is a coherent quasiparticle, and whether the Luttinger count is carried by poles or by Green's-function zeros. The source calculation uses the zero surface as a hallmark of its symmetric gapped regime and uses zone folding as a hallmark of its exciton regime [Chang et al. synthesis](../../../../wiki/papers/chang2023fssmg.md). Those are author-side targets. The solver is not told them.

STM dI/dV remains an input. It is not renamed ARPES.

## What would change the standard

If Lab 001 finds that every mechanism surviving the three facts predicts the same photoemission features, this question is too weak and the prompt needs another public fact or the doping prediction. If a small-cluster spectrum cannot express folding or a zero surface, the author key needs a different check before any large simulation.

## Related pages

- [Current synthesis](../thesis.md)
- [Research frontier](../ideas/research-frontier.md)
