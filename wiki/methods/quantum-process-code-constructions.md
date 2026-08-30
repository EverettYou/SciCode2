---
title: Quantum processes for code constructions
page_type: method
status: provisional
updated: '2026-08-22'
source_refs:
- papers/zhang2026qprol/paper.pdf
idea_ids: []
topics:
- Quantum Information
---

# Quantum processes for code constructions

**Summary**: LDPC-code dualities and products can be represented as maps between Tanner-graph operator algebras and realized by ancilla initialization, local unitaries, projective measurements, and ZX-derived circuits.

**Sources**: [Zhang et al. (2026)](../../papers/zhang2026qprol/paper.pdf)

**Last updated**: 2026-08-22

---

## Current synthesis

The operator algebra associated with a classical LDPC Tanner graph is treated as the physical invariant, with code transformations inducing algebra maps and corresponding Hamiltonian/phase maps. The paper gives complementary ZX diagrams, extracted circuits, and phase interpretations for generalized Kramers-Wannier duality, tensor product, check product, and $(p,q)$ products [Zhang et al. (2026), §Abstract-and-Outlook](../../papers/zhang2026qprol/paper.pdf#Abstract-and-Outlook).

Kramers-Wannier duality becomes gauging; products become coupled-layer constructions with interlayer coupling and projection. Circuit extraction also exposes ancilla and measurement overhead tied to code symmetries and redundancies [Zhang et al. (2026), §Outlook](../../papers/zhang2026qprol/paper.pdf#Outlook).

## Benchmark opportunity

Given small parity-check matrices, independently construct the process, verify stabilizer/operator conjugation, logical action, postselection probability, ancilla count, and depth, then compare tensor and check products on the same component codes.

## Related pages

- [[methods/twisted-lattice-gauging|Twisted lattice gauging]]
- [[papers/zhang2026qprol|Quantum process realization of LDPC code dualities and product constructions]]
- [[concepts/noninvertible-spt-diagnostics|Non-invertible SPT diagnostics]]
