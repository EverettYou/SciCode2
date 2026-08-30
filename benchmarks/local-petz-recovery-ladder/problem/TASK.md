# Petz Recovery Gap at Mixed-State Criticality

## Background and motivation

Local Petz recovery is controlled by conditional mutual information: when $I(A:C|B_r)$ decays with buffer radius $r$, a recovery map supported on $A\cup B_r$ can approximate the global reverse map. Sang and Hsieh proposed the corresponding decay length as a mixed-state Markov length and showed that it diverges at the decohered toric-code decodability transition. Liu et al. use the same finite-Markov logic to motivate local reverse diffusion.

This suggests a direct scientific diagnostic: instead of treating local-global recovery disagreement as an implementation nuisance, measure how much recovery radius is required to reproduce global Petz recovery. That radius should remain finite in a finite-Markov phase and grow near a mixed-state transition.

## Knowledge gap

It is not established that the local-global Petz recovery gap itself has useful finite-size scaling at a mixed-state transition. The earlier benchmark draft also conflated the pure-state critical point of a 1D transverse-field Ising Hamiltonian with a possible transition of the decohered mixed state. Those are different claims: the latter requires CMI or Markov-length evidence.

The first task is model qualification. Generic finite-range 1D Gibbs or primitive matrix-product density operators normally have finite correlation and Markov lengths at interior parameters. A 1D GHZ chain can exhibit long-range CMI and local irrecoverability, but this is an endpoint or constrained example rather than automatic evidence of a finite-noise bulk transition. If no source-supported 1D candidate passes the qualification tests, the benchmark uses the 2D toric code under independent Pauli noise, where the finite transition is established.

## Research question

Can the finite-window local-versus-global Petz recovery gap locate and characterize a mixed-state phase transition by tracking the divergence of the conditional-mutual-information Markov length?

## Primary observable

For system size $L$, control parameter $g$, and recovery radius $r$, define

$$
\Delta_R(r,g,L)=D(\mathcal R_{\mathrm{global}}\mathcal E_g(\rho_0),\mathcal R_r\mathcal E_g(\rho_0)).
$$

Here $D$ is trace distance for dense validation and total-variation or logical-channel distance for an exactly equivalent commuting representation. Define

$$
r_\varepsilon(g,L)=\min\{r:\Delta_R(r,g,L)\leq\varepsilon\}.
$$

The benchmark tests whether $r_\varepsilon$ scales with the independently fitted Markov length $\xi_M$ from $I(A:C|B_r)$, and whether both exhibit a common finite-size critical point.

## Model-selection gate

### 1D candidates

- A finite-range 1D mixed-state family represented by a transfer matrix or MPDO qualifies only if increasing-$L$ CMI supports a finite interior $g_c$ where the transfer or Markov length grows without saturation.
- A 1D GHZ or repetition-code family under tunable local decoherence is an endpoint long-range-CMI control, not automatic evidence of a generic finite-noise transition.
- The weakly diffused 1D TFIM remains a negative control unless it independently passes the same CMI finite-size criteria. Its pure-state point $B_x=1$ is not evidence by itself.

### Default primary model

If no 1D model qualifies, use the toric-code state on an $L\times L$ torus under independent bit-flip or phase-flip noise. This model has a source-supported decodability transition where the Markov length diverges and CMI maps to a random-bond-Ising free-energy cost.

Because the state and channel commute or are Pauli diagonal in the relevant representation, the twirled Petz map reduces to the ordinary Petz map and then to a Bayesian reverse channel on error classes. This reduction must be proved for the chosen conventions and checked against dense matrices on the smallest lattice.

## Hypotheses

- Away from $p_c$, $\Delta_R(r,p,L)$ decays exponentially once $r$ exceeds order $\xi_M$, and $r_\varepsilon$ saturates with $L$.
- Near $p_c$, both $\xi_M$ and $r_\varepsilon$ grow with $L$; a dimensionless scaled gap or $r_\varepsilon/L$ should show a crossing or collapse.
- A 1D short-range negative control should show no stable interior crossing.
- The Petz gap may have different corrections to scaling from CMI, but inferred critical parameters should agree within uncertainty if it is a valid diagnostic.

## Numerical methods

1. **Dense exact validation:** exact density matrices and superoperators for the smallest 1D systems and $L=2$ toric-code instances; verify Petz or Bayesian reduction, full-radius equality, positivity, and normalization.
2. **1D qualification:** transfer-matrix or MPDO/MPO contraction for CMI and local recovery as $L$ and buffer size grow.
3. **2D commuting calculation:** stabilizer and Pauli-error-class representation, exact enumeration for small lattices, then tensor-network contraction of random-bond-Ising partition functions.
4. **Large-size scaling:** Monte Carlo on the Nishimori-line statistical model when contraction becomes limiting, with autocorrelation and bootstrap uncertainties.
5. **Finite-size inference:** jointly fit CMI and Petz-gap scaling and test stability to omitted sizes, threshold $\varepsilon$, geometry, and numerical precision.

## Deliverables

- A model-qualification table covering dimension, parameter, evidence for an interior transition, CMI behavior, and numerical representation.
- Machine-readable $(L,g,r)$ sweeps of CMI, $\Delta_R$, $r_\varepsilon$, logical error, residuals, runtime, and uncertainty.
- A proof note and tests for the commuting Petz-to-Bayesian reduction.
- Scaling plots and fitted $g_c$ and $\nu$, or a documented negative result when sizes do not support exponent extraction.
- Stable code under `src/` only after dense and small-lattice agreement; the final supported interpretation belongs in `note/`.

## Evidence and stop conditions

- A transition claim requires an independently growing $\xi_M$, joint size scaling, and stability across analysis choices.
- Full-radius local recovery must reproduce the global map, and the commuting representation must reproduce dense Petz recovery on overlapping cases.
- Stop the 1D branch if all interior candidates have a transfer-matrix gap bounded away from zero and $r_\varepsilon$ saturates with $L$; retain this negative result and proceed to 2D.
- Stop exponent fitting if accessible sizes do not show a stable crossing or collapse; report bounds or pseudocritical drift instead.
- Numerical controls do not replace the physics question.

## Reproducibility interface

Scripts accept declarative model, size, control parameter, radius, seed, and output arguments. Every run writes configuration and environment hashes plus tidy results. Figures regenerate from tables. The workstation target is 16 GB RAM, at most 24 CPU-hours for the primary grid, with an optional longer Monte Carlo campaign only after the small-size qualification gate succeeds.
