---
title: Twisted lattice gauging
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/lu2024rtapb/paper.pdf
idea_ids: []
topics:
- Topological Phases
- Quantum Information
---

# Twisted lattice gauging

**Summary**: Discrete torsion can be built into lattice Gauss laws to generate exact nonlocal dualities, quantum-process realizations, and non-invertible triality or p-ality symmetries.

**Sources**: [Lu et al. (2024)](../../papers/lu2024rtapb/paper.pdf)

**Last updated**: 2026-08-23

---

## Lattice construction

For a finite symmetry group, twisted gauging inserts a nontrivial \(H^2(G,U(1))\) cocycle into the Gauss-law operator. On the lattice this is equivalent to first applying the associated SPT entangler and then performing ordinary gauging. Symmetric local operators map to local operators, while charged fields generally map to nonlocal strings [Lu et al. (2024), §§2, 4–5](../../papers/lu2024rtapb/paper.pdf#page=9).

Combining twisted and untwisted gauging with symmetry automorphisms gives order-three triality maps and, for prime \(p\), order-\(p\) p-ality maps on \(Z_p\times Z_p\)-symmetric Hamiltonians. Their action on gapped phases and invariant operators can be calculated algebraically as symplectic transformations of generalized Pauli operators [Lu et al. (2024), §§6–7](../../papers/lu2024rtapb/paper.pdf#page=30).

## Quantum-process realization

Gauging introduces ancillas, minimally couples them with sequential gates, measures Gauss constraints, and postselects the required outcomes. The resulting Kraus map is completely positive but generally neither trace preserving nor invertible. Triality and p-ality therefore have operational quantum-process implementations, not ordinary deterministic unitary circuits [Lu et al. (2024), §§2–5](../../papers/lu2024rtapb/paper.pdf#page=12).

## Non-invertible symmetry and phases

When a Hamiltonian is invariant under one of these nonlocal maps, the corresponding defect generates a non-invertible fusion-category symmetry. The map permutes gapped phases and constrains invariant multicritical theories. Compatibility with a unique symmetric gapped ground state is an anomaly/fiber-functor question; distinct compatible gapped phases can exist without a symmetry-preserving finite-depth entangler between them [Lu et al. (2024), §7](../../papers/lu2024rtapb/paper.pdf#page=34).

## Validation boundary

The detailed construction is one-dimensional and focuses on finite Abelian groups, with p-ality developed for prime \(p\). Full lattice classification of the compatible gapped phases, extraction of all fusion-category data, and non-Abelian, fermionic, higher-form, or higher-dimensional extensions remain open [Lu et al. (2024), §8](../../papers/lu2024rtapb/paper.pdf#page=40).

## Benchmark hooks

- Verify twisted Gauss-law commutation and the SPT-entangler factorization for finite chains and boundary conditions.
- Derive operator maps independently from Kraus circuits and symplectic Pauli algebra.
- Enumerate triality/p-ality phase orbits and invariant Hamiltonian terms.
- Measure postselection success and resource scaling, then test alternative trace-preserving realizations.

## Related pages

- [[concepts/self-duality-protected-multicriticality|Self-duality-protected multicriticality]]
- [[concepts/noninvertible-spt-diagnostics|Non-invertible SPT diagnostics]]
- [[methods/quantum-process-code-constructions|Quantum processes for code constructions]]
- [[topics/topological-phase-transitions|Topological phase transitions]]
- [[papers/lu2024rtapb|Realizing triality and p-ality by lattice twisted gauging in (1+1)d quantum spin systems]]
