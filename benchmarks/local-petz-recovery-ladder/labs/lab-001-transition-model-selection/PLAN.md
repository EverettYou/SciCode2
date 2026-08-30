# Lab 001 execution plan

## Objective

Select a mixed-state model with an independently demonstrable Markov-length transition and validate the local-global Petz-gap observable on the smallest exact instance.

## Stable interfaces

Prototype `conditional_mutual_information`, `fit_markov_length`, `global_petz`, `local_petz`, `commuting_reverse`, and `recovery_gap`. No interface is stable until dense or commuting overlap passes.

## Steps

1. Write a model-qualification table: dimension, parameter, interior transition, CMI behavior, and scalable representation.
2. Implement analytic or transfer-matrix checks for a 1D endpoint control and one finite-range 1D mixed-state family.
3. Select 1D only if $\xi_M$ grows with $L$ at a stable interior parameter; otherwise instantiate periodic toric-code lattices.
4. For the smallest selected model, implement dense global and restricted Petz maps and a commuting Bayesian reverse channel.
5. Verify full-radius equality, dense/commuting agreement, invariants, and the qualitative relation between CMI and recovery gap.
6. If the toric-code pilot passes, design Lab 002 around exact enumeration, tensor contraction, Monte Carlo, and joint finite-size scaling.

## Completion criteria

- The 1D decision distinguishes an interior transition from endpoints or crossover.
- The selected primary model has independent support for a divergent CMI length.
- Dense Petz and commuting reverse agree within `1e-10`, and full-radius local equals global.
- Output records $L$, $g$, $r$, CMI, $\Delta_R$, $r_\varepsilon$, residuals, runtime, and uncertainty.
- The next scaling method is justified by model structure.

## Stop conditions

- Do not promote a 1D candidate from a single-size peak, pure-state gap closing, or endpoint divergence.
- Stop dense scaling after the smallest equivalence tests.
- Do not infer a critical exponent from pilot sizes.
- Redesign the observable if the commuting distance is not exactly linked to recovered-state or logical-channel distance.
