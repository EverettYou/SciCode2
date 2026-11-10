# Affordable Hubbard Quantum Bootstrap Bounds

## Background and motivation

The user supplied [SciCode 2: Finding Affordable Quantum Bootstrap Bounds](references/scicode2-hubbard.pdf) and requested a new benchmark and an initially two-hour research attempt, subsequently extendable up to one day if needed. The question is operator-space discovery for a lower-bound relaxation, rather than merely estimating a ground-state energy.

For an operator space O, minimize Tr(rho H) over Hermitian trace-one rho supported in the target sector, with Tr(rho O^dagger O)>=0 for every O in the selected space. Global rho positivity is deliberately omitted. Every physical ground state is feasible, so a justified relaxation minimum lower-bounds E0. Operator spaces may contain operators changing particle number.

## Why this is unresolved

The original proposal leaves the public energy target and computation budget to private calibration. It does not prescribe an operator basis, moment representation or certificate. Full positivity in the 165,636,900-dimensional fixed-spin sector is prohibitive. Selected constraints must capture correlations cheaply enough to strengthen the bound, and a solver output alone does not establish that bound. This attempt must establish its own reproducible cost-versus-bound comparisons and controlled numerical validation; it cannot claim to pass an unspecified target or prove a globally optimal outer operator selection.

## Research question

Construct and validate an affordable operator subspace that gives a strong ground-state energy lower bound for the periodic 4x4 Hubbard model at t=1, U=8 and N_up=N_down=8, and quantify improvements against computational cost.

## Objective

Produce a reproducible, independently justified energy lower bound and assess which operator choices yield useful improvement per computational resource.

## Expected outcomes

- Local cluster algebras may offer inexpensive certificates with support-limited tightness.
- Global degree-two fermionic operator spaces may capture longer-range correlations at moderate SDP block size.
- Degree-three anticommutator constraints may improve the correlation description but increase construction and solving cost. These are hypotheses until tested.

## Scope and approach

Use only the specified finite 4x4 periodic square lattice with 16 sites, 32 distinct unordered nearest-neighbor bonds, t=1, U=8, N_up=N_down=8. Report total energy and optionally divide by16. Explore local support and global low-degree moment positivity, with exact CAR and fixed-sector identities. Symmetry reductions must preserve the Hamiltonian, physical sector and chosen relaxation. Validate the bound by an explicit SOS/dual identity or an equally controlled construction, including numerical residual corrections. Record unsuccessful refinements and full resource costs. The initial two-hour checkpoint is2026-10-07T09:36:39Z; the user subsequently relaxed the time threshold and authorized up to one day if necessary. Continue while measured scientific gains justify the cost. No numerical energy target or memory ceiling was supplied, so neither is invented.

## Project specification

Inputs: immutable supplied PDF; canonical lattice/sector above. Outputs: reproducible operator construction, code and formulation; bound and independent validation evidence; resource measurements; comparison of support, degree and correlation choices. Preserve separate discovery and verification outputs. One primal feasible state establishes only an upper bound on a minimization, not the desired lower bound. A literature energy may provide context but never a substitute certificate. An exact solution or a globally optimal operator set is not required by the proposal.

## Evidence requirements

- Audit geometry, normalization, CAR signs and sector constraints.
- Check smaller exact cases or analytic limits where practical.
- Export certificate data independent of solver status and subtract explicitly bounded numerical errors.
- Measure representation, construction, solve and validation stages and peak resident memory.
- Compare refinements on the same Hamiltonian and energy convention.

## Source and authorization

The source is a user-provided problem specification, not a reviewed paper follow-up. Its provenance is recorded directly, with empty paper_ids, rather than inventing a reviewed assessment. The user's direct request authorizes experiment execution within the user-authorized research scope; expert_review remains pending for later benchmark calibration. Han, arXiv:2006.06002, is background only and must be independently read before its scientific details support a claim.
