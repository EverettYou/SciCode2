---
title: Self-organized error correction in monitored circuits
page_type: concept
status: provisional
updated: 2026-08-23
source_refs:
- papers/fan2021secir/paper.pdf
idea_ids: []
topics:
- Quantum Information
---

# Self-organized error correction in monitored circuits

**Summary**: The volume-law phase of a monitored scrambling circuit suppresses the information revealed by deep local measurements, behaving like a dynamically formed quantum error-correcting code.

**Sources**: [Fan et al. (2021)](../../papers/fan2021secir/paper.pdf)

**Last updated**: 2026-08-23

---

## Entanglement-feature description

All subsystem second-Rényi purities are assembled into an auxiliary Ising-spin “entanglement-feature state.” For locally basis-scrambled channel ensembles, its averaged evolution is approximated by a Markovian transfer matrix built from the entanglement features of unitary and measurement Kraus operators [Fan et al. (2021), §§Entanglement-Feature-Formalism and Mean-Field-Description](../../papers/fan2021secir/paper.pdf#page=2).

In the low-measurement volume-law phase, the associated imaginary-time Ising model gives
\[
S^{(2)}(A)=\kappa |A|+\tfrac32\log |A|+O(1),
\]
and the mutual information between a qudit at depth \(x\) in \(A\) and \(\bar A\) decays as \(x^{-3/2}\). Thus a measurement deep inside the encoded region reveals and destroys parametrically little boundary-crossing information [Fan et al. (2021), §§Mutual-Information and Universal-Log-Correction](../../papers/fan2021secir/paper.pdf#page=5).

## Coding interpretation

Modeling the steady state as a code encoding a Page state gives a capacity-style constraint on the critical measurement probability,
\[
p_c\log[(d^2-1)(p_c^{-1}-1)]\leq\log[(1-p_c)d],
\]
which is saturated at \(p_c\to1/2\) for large local dimension and gives \(p_c(d=2)\leq0.1893\) [Fan et al. (2021), §Error-Correction-Bound](../../papers/fan2021secir/paper.pdf#page=4).

## Evidence boundary

The transfer theory replaces an average of normalized purities by a ratio of averages and then makes an Ising-model approximation. It is intended for the stable volume-law phase and does not reproduce the true critical universality class. The analytic exponents apply to the locally scrambled ensemble and second Rényi entropy; Clifford numerics show a similar but not identical decay [Fan et al. (2021), main text and Appendices A–F](../../papers/fan2021secir/paper.pdf#page=6).

## Benchmark hooks

- Reproduce the transfer matrices and MPS steady state for several local dimensions.
- Compare ratio-of-averages predictions with trajectory-normalized Haar and Clifford simulations.
- Fit the \(3/2\) logarithmic term and \(x^{-3/2}\) information profile with finite-size corrections.
- Test whether the information-depth profile predicts explicit erasure-recovery fidelity.

## Related pages

- [[methods/entanglement-feature-dynamics|Entanglement-feature dynamics]]
- [[topics/random-quantum-circuits-and-measurements|Random quantum circuits and measurements]]
- [[topics/entanglement-structure-and-dynamics|Entanglement structure and dynamics]]
- [[methods/monte-carlo-operator-dynamics|Monte Carlo operator dynamics]]
- [[concepts/finite-markov-length|Finite Markov length]]
- [[papers/fan2021secir|Self-organized error correction in random unitary circuits with measurement]]
