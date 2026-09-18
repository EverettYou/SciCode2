# How much quantum information survives partially observed weak measurements?

> Draft solver contract. N=2,4 reference bounds are now validated numerically.
> Larger targets remain pilot proposals; see the author evidence inventory.
> Author notes and reference solutions are distributed separately at release.

## Background

A weak measurement can leave a pure conditional trajectory while removing quantum
information about an unknown input. Reconstructing a known target state does not
measure preservation of that information. Here, recovery is assessed by whether a
logical qubit remains entangled with an inaccessible reference system.

## Why this is unresolved

For a specified encoding and measurement instrument, an individual decoder gives
an achievable fidelity but does not establish the optimum. Missing measurement
outcomes create mixtures even conditional on the available record. The question
is how much this loss of classical information changes optimal quantum recovery,
and whether that change grows or shrinks with code size. Existing fixed-target
trajectory-control results do not answer this question. This task asks for bounds
on a decoder-independent observable of a constructed finite-size system. It does
not assume a phase transition or that a neural decoder is necessary.

## Scientific objective

Determine the optimal entanglement recovery fidelity for the family below, as a
function of system size N, measurement strength g, and record retention eta.
Quantify the advantage of retaining all outcomes over retaining three quarters of
them. Establish numerical uncertainty sufficiently tightly to resolve that effect
where it exceeds the stated resolution.

## Physical system and conventions

All quantities are dimensionless. Qubits have open-chain order 0,...,N-1; qubit 0
is the most significant bit in dense basis indexing. The one logical input L is
placed at site q=floor(N/2), with all other sites in |0>. Define the encoding
isometry V_N by the following fixed circuit. This specifies the physical code,
not the recovery algorithm.

There are d=ceil(N/2) layers numbered ell=0,...,d-1. Within each layer:

1. On every site j, apply R_y(alpha[j,ell]), then R_z(beta[j,ell]), where
   alpha=pi*(2+((j+2*ell) mod 5))/11 and
   beta=pi*(1+((2*j+ell) mod 7))/13.
2. Apply CNOT(j -> j+1) on disjoint bonds with j mod 2 = ell mod 2.

Here R_a(theta)=exp(-i theta sigma_a/2). The circuit acts once before the noise.
The decoder knows the full circuit and may use any representation of it.

Each site is measured once, with measurement observable

    P_j = cos(theta_j) Z + sin(theta_j) X,
    theta_j = pi*(1+(j mod 3))/10.

For outcome s in {-1,+1}, the Kraus operator is

    K[j,s] = sqrt((I + s*g*P_j)/2),     0 <= g <= 1,

with the positive matrix square root. Outcomes follow the Born rule. Measurements
on different sites commute. There is no numerical time step or hidden conversion
between g and a continuous measurement rate in this task.

Independently of the input, outcomes, and other sites, each outcome is retained
with probability eta. The receiver sees c_j=s if retained and c_j=? otherwise.
The receiver always knows the site and measurement axis. Conditional *unnormalized*
local maps are

    M_s(rho) = eta K_s rho K_s^dagger,
    M_?(rho) = (1-eta) sum_s K_s rho K_s^dagger.

The full channel includes the classical record:

    N(rho) = sum_c (tensor_j M[c_j])(rho) tensor |c><c|.

Sum over records, including their physical probabilities; do not average normalized
conditional fidelities uniformly or give the decoder erased outcomes.

## Observable and allowed recovery

Prepare |Phi>_RL=(|00>+|11>)/sqrt(2), encode L with V_N, apply N to the N physical
qubits B, then apply a recovery channel R:BC -> L'. The reference R is inaccessible.

    F_opt(N,g,eta) = sup_R <Phi| (id_R tensor R o N o V_N)
                              (|Phi><Phi|) |Phi>.

V_N denotes its associated isometric channel in this expression. Fidelity is the
overlap above, without a square root. The supremum ranges over all deterministic
completely positive trace-preserving recovery channels. The recovery may depend
on the public instance and observed record. It may use fresh uncorrelated ancillas
and global operations, and must be independent of the unknown logical input.
It cannot access the reference, erased outcomes, or a classical description of the
unknown input. No postselection is allowed. A state-dependent numerical update
must be shown to implement one allowed channel before it counts as a recovery.

The physical optimum does not constrain decoder circuit depth. The workstation
budget constrains the algorithm used to compute/certify that optimum. Do not
substitute a resource-constrained decoder optimum without explicitly bounding
the unrestricted quantity above.

## Scope and approach

Use any scientifically justified computational or analytical method. Provide an
achievable lower bound and an independently checkable upper bound on the optimum.
Methods may differ between sizes. Quantify approximation, optimization, and
sampling errors separately. Study finite sizes; neither exponential decay nor a
thermodynamic transition is assumed. A negative finding about size trends is a
valid result if supported by the required numerical evidence. No neural network,
tensor network, training procedure, or particular optimizer is prescribed.

## Pilot instance grid and resources

- Validated small reference grid: N in {2,4}, g in {0.2,0.5,0.8}, eta in {0.75,1}.
  Target interval width U-L <= 1e-8, including reported numerical error accounting.
- Larger reference pilot: N=6,g=0.5,eta=0.75 has attained width below 1e-4.
- Next proposed calibration: N=8,g in {0.5,0.8}, eta in {0.75,1}. Its reference
  and verification costs still need measurement. N=12,16 are deferred.
- Proposed larger-case width: U-L <= 1e-4, including numerical error budgets and
  any sampling uncertainty. This remains to be calibrated before release.
- The original width 0.02 is retired: a no-training, no-SDP baseline already
  reaches it on all tested N=4,6 cells. It also exceeds the measured record effect.
- Propagate intervals into the record advantage; precision alone does not authorize
  claiming an effect smaller than the resulting uncertainty.
- Pilot execution envelope: 16 CPU cores, 64 GiB RAM, 24 elapsed compute hours;
  no accelerator required. Count preprocessing and training in the total.
- Intended active scientist work: 10–20 hours, excluding passive computation.

Authors must validate and freeze the required subset and these budgets before
release. The current draft does not require solving an unvalidated large-N grid.

## Deliverables

1. An executable entry point accepting an instance JSON (N,g,eta) and an output
   directory. Include an environment lock and deterministic seed control.
2. Machine-readable bounds, certificate files, and resource measurements. Each
   row identifies the instance, lower/upper bound, deterministic error budget,
   statistical confidence method if used, seeds, and source/environment hashes.
3. A recovery implementation or valid primal certificate achieving each lower
   bound, and a verifiable upper-bound certificate or derivation with executable
   numerical checks. Unsupported scalar assertions are not certificates.
4. The record advantage Delta_N(g)=F_opt(N,g,1)-F_opt(N,g,0.75), with propagated
   intervals, and a short account of the size dependence resolved by the data.
5. Checks of physical validity, exact limiting cases, and convergence. Include
   evidence supporting conclusions and identify unresolved trends.

Better algorithms and tighter valid bounds are accepted. Agreement with an
author's decoder architecture, learned weights, or scaling fit is not required.
