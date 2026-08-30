---
title: Exact lattice duality constructions
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/jian2019lcodw/paper.pdf
idea_ids: []
topics:
- Topological Phases
---

# Exact lattice duality constructions

**Summary**: Non-Abelian Chern–Simons–matter dualities can be regularized as Euclidean lattice path integrals whose gauge and matter variables admit an exact local transformation to free fermions.

**Sources**: [Jian et al. (2019)](../../papers/jian2019lcodw/paper.pdf)

**Last updated**: 2026-08-23

---

## Construction

The lattice theory couples an (SO(3)) vector boson and Wilson Majorana fermions to link-valued (SO(3)) gauge fields. Integrating out an appropriately chosen massive fermion supplies the desired level-1 Chern–Simons response without writing a bare lattice Chern–Simons action [Jian et al. (2019), §II.A](../../papers/jian2019lcodw/paper.pdf#page=2).

A sitewise rotation decomposes the colored Majorana field into one component parallel to the boson and two orthogonal components. Gauge-link integration and exact elimination of the orthogonal fields leave a single free lattice Majorana theory, with explicit mappings for partition functions, correlators, and a seemingly mismatched global (mathbb Z_2) symmetry. Related (O(3)) and (mathbb Z_2)-extended constructions yield either a free Majorana or a free Majorana plus a decoupled gauge sector [Jian et al. (2019), §§II–III](../../papers/jian2019lcodw/paper.pdf#page=3).

## Exactness boundary

The finite-lattice path-integral identity is exact. The inference that its interacting side flows to a critical (SO(3)) vector boson coupled to (SO(3)_1) Chern–Simons theory is not: interaction-induced changes of the effective level and the infrared role of disconnected (O(3)) components remain unresolved [Jian et al. (2019), §IV](../../papers/jian2019lcodw/paper.pdf#page=7).

## Benchmark hooks

- Symbolically reproduce the one-link gauge integral and the fermion change of variables.
- Verify mapped correlators and global-symmetry actions on small periodic lattices.
- Compute effective topological responses across the Wilson-mass windows and interacting deformations.
- Test the proposed continuum limit with finite-size spectra or Monte Carlo observables while keeping lattice identity and IR conjecture separate.

## Related pages

- [[topics/topological-phase-transitions|Topological phase transitions]]
- [[concepts/grand-unified-deconfined-criticality|Grand-unified deconfined criticality]]
- [[papers/jian2019lcodw|Lattice construction of duality with non-Abelian gauge fields in 2+1D]]
