---
title: Symmetry-protected topological ensembles
page_type: concept
status: provisional
updated: 2026-08-23
source_refs:
- papers/lee2025sptpu/paper.pdf
idea_ids: []
topics:
- Topological Phases
- Quantum Information
---

# Symmetry-protected topological ensembles

**Summary**: Mixed states can retain symmetry-protected topological information after decoherence, with experimentally accessible and globally encoded remnants separated by two strange correlators.

**Sources**: [Lee et al. (2025)](../../papers/lee2025sptpu/paper.pdf)

**Last updated**: 2026-08-23

---

## Doubled-space definition

The Choi–Jamiołkowski isomorphism maps a density matrix to a pure state in a doubled Hilbert space: a pure input becomes two decoupled layers, while decoherence couples them. A symmetry-protected topological ensemble is then identified through the symmetry and anomaly structure of this doubled state, subject to Hermiticity and positivity constraints inherited from the density matrix [Lee et al. (2025), §§1 and 4](../../papers/lee2025sptpu/paper.pdf#page=2).

## Two information layers

- A type-I strange correlator probes charged operators in one layer. Its marginalized form is experimentally accessible and bounds what topological information or measurement-assisted long-range order can be decoded with feasible sample complexity.
- A type-II strange correlator probes the full doubled system. It can retain the complete mixed topological response after type-I correlations become short-ranged, recording that the pre-decoherence state was topological even when that information is difficult to extract from ordinary bulk measurements [Lee et al. (2025), §§2, 4, and 5](../../papers/lee2025sptpu/paper.pdf#page=5).

This gives three information regimes as noise increases: decodable topology when type I is nontrivial, scrambled but still encoded topology when only type II remains nontrivial, and loss of the diagnosed SPT label when both are trivial [Lee et al. (2025), Fig. 1](../../papers/lee2025sptpu/paper.pdf#page=3).

## Evidence and limits

Exact stabilizer calculations, nonlinear-sigma-model arguments, and DMRG away from an exactly solvable cluster-state point show type-I decay or transitions under selective decoherence while type II can remain long-ranged [Lee et al. (2025), §§2–3](../../papers/lee2025sptpu/paper.pdf#page=6). The persistence is not unconditional: correlated or less symmetric noise can change the type-II magnitude or trivialize both diagnostics. The information-theoretic theorem constrains the existence of efficient diagnosis and measurement-assisted preparation but does not supply a general optimal decoder [Lee et al. (2025), §§2.6, 5.4, and 6](../../papers/lee2025sptpu/paper.pdf#page=8).

## Benchmark hooks

- Compute both correlators for solvable cluster-state channels and locate distinct noise thresholds.
- Test the doubled-state symmetry under strong, weak, and symmetry-breaking channels.
- Compare exact, tensor-network, and Monte Carlo estimators for marginalized type-I observables.
- Search for efficient decoders below the type-I threshold and certify failure bounds above it.

## Related pages

- [[topics/topological-phases|Topological phases]]
- [[topics/quantum-information-dynamics|Quantum information dynamics]]
- [[methods/measurement-conditioned-quantum-control|Measurement-conditioned quantum control]]
- [[papers/lee2025sptpu|Symmetry protected topological phases under decoherence]]
