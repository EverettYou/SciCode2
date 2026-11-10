---
document_type: lab_report
lab_id: lab-004-exact-dual-verification
status: completed
idea_ids:
- k-001
- c-006
wiki_context:
- wiki/thesis.md
- wiki/ideas/research-frontier.md
related_labs:
- labs/lab-001-cluster-certificates
- labs/lab-002-moment-sdp
- labs/lab-003-theory-audit
- labs/lab-005-local-rdm-extension
- labs/lab-006-true-cubic-grams
---

# Exact dual certificate validation

## Motivation

Convert approximate dual outputs into independently controlled lower-bound certificates for the specified Hamiltonian.

## Design

Quantized dyadic Gram factors, exact residual corrections, independent Hamiltonian reconstruction, and fresh complete reproduction measurements.

## Findings

### Motivation and design

A numerical SDP status does not certify a lower bound. This lab converts approximate dual factors to exactly positive Gram certificates, retains coefficient mismatch as an exact rational residual, and bounds its contribution using moment coordinates of absolute value at most1. The Hamiltonian is reconstructed independently. A separate physical-map auditor imports neither the optimization builder nor its CAR routines.

### Mathematical formulation

Use real moment coordinates x, equality E x=e, and PSD matrices M_j(x)=A_j x+b_j. For any equality multiplier lambda and exactly PSD Gram matrices Z_j,

r = c + E^T lambda - sum_j A_j^T vec(Z_j),
d = -e^T lambda - sum_j b_j^T vec(Z_j).

Then c^T x = d + sum_j Tr[Z_j M_j(x)] + r^T x >= d - ||r||_1, because every coordinate has absolute value at most1. Occupations satisfy0<=n<=1 by linear particle/hole positivity. P positivity gives Gamma_diag>=0. G diagonal gives Gamma_ab,ab<=n_b<=1. P Cauchy-Schwarz then gives |Gamma_pair,pair'|<=1. This uses relaxation constraints, not an assumed globally positive rho.

Quantize each dual factor to K/2^40, defining Z=K K^T/2^80, positive semidefinite exactly. Quantize equality multipliers to the same denominator. Original affine coefficients and RHS are integers; the exact Hubbard objective is half-integral. The verifier also supports exact dyadic affine coefficients for quantized scalar cuts, using the common binary denominator of all stored coefficients. Reconstruct all residual and constant numerators with Python integers. Int64 matrix products are split into high/low pieces and each accumulation is checked against a proven overflow bound. The final reported decimal is rounded downward. No eigenvalue tolerance or solver-status assumption enters this certificate arithmetic.

For D4/spin-swap reduced exports, independently verify that the signed expansion spans exactly the invariant moment subspace:342 signed orbits,11 forced-zero orbits,331 remaining coordinates. Reduced coordinates are advertised original physical moments and remain bounded by1.

### Completed numerical evidence

| Model | Exact certified total-energy lower bound, downward rounded | Residual correction | Integer validation wall time |
| --- | ---: | ---: | ---: |
| PQG, SCS eps1e-6 | -10.566825373980 | 1.46208e-4 | 1.35s |
| PQG, SCS eps1e-8 | -10.566721990544 | 4.87777e-5 | 0.76s |
| PQG + opposite-density T2prime | -10.268038996818 | 3.97260e-4 | 1.27s |
| PQG + T1 | -9.847999995266 | 8.10464e-3 | 5.44s |
| PQG + full two-site T2prime, D4 | -8.864558789088 | 5.67204e-4 | 1.39s |
| PQG + full cubic T2prime, D4 | -8.764969112905 | 1.98646e-3 | 4.45s |
| Same factors, equality multipliers LP-refitted | -8.764879966348 | 1.82554e-3 | 2.70s including LP |
| Two-site T2prime, Clarabel | -8.864118703137 | 1.77105e-4 | see JSON |
| T1 + two-site T2prime | -8.856092835155 | 2.88645e-4 | 3.67s |
| Two-site T2prime + spin-3/2 sectors | -8.864590506761 | 5.71001e-4 | 3.08s |
| Two-site T2prime + nearest-neighbor stars | -8.859051476423 | 8.17003e-5 | 4.78s |

Each exact numerator/denominator, quantized factor, equality multiplier and residual vector is retained under results/<model>/. Use the JSON values as canonical resource observations; timings vary under concurrent execution. The physical-map audit is a separate cost: approximately2.3s for PQG,29.1s for selectedT2 using the independently exhaustively checked contraction identity, and35.5s for T1. These must be added when describing complete validation cost.

### Independent model checks

[Analytic checks](results/analytic-checks.json) verify32 distinct nearest-neighbor bonds, degree4, exact dispersion multiplicities(1,4,6,4,1) for energies(-4,-2,0,2,4), free U=0 energy-24, atomic t=0 energy0, and positive interaction decomposition in opposite-spin P blocks. The full physical-map auditor in lab001 reconstructs exact Gaussian-integer Fourier hopping, all variable/operator bases, all affine matrices/constants and fixed-number identities. It uses an exterior-product algorithm independent of the builder's recursive adjacent transpositions and checks direct Fock actions. Optimized T2 contraction identities are exhaustively cross-checked for46,656 index-order/equality patterns.

### Interpretation and limitations

T1/T2 anticommutator constraints eliminate degree-six moments and yield valid cubic-operator SOS certificates. Their SDP optimum is not asserted to equal the full literal cubic-operator Eq(2) optimum. The exported certificate provides a guaranteed lower bound for the associated full operator space. No stationarity constraint or globally positive rho is assumed. No public target energy was supplied. Literature energies, when cited, are contextual comparisons only.

The initially exported PQG/T1 kinetic coefficients contained cosine-rounding artifacts below7.4e-16. The final verifier reconstructs the exact half-integer Hubbard objective and includes the discrepancy in its exact residual, rather than certifying the perturbed Hamiltonian.

### Wiki-ingest handoff

Promote the exact-certificate method, current verified bounds, measured validation cost and the distinction between anticommutator relaxation and the full operator space. Preserve pending refinements as prospective. The audited degree-four core is promoted to root src/. Adaptive and sextic extensions require their own exact coefficient and physical-map checks before promotion.

### Final selected-space certificates

The dual-guided scalar replay is exactly certified at **-8.763365270237**, residual 3.5768033758e-7, with 64 cones, largest dimension 32, and 11380 factor entries. Exact validation took 1.172 s and 57.1 MB. The six-block replay strengthens it to **-8.763353354793**, residual 1.1766666080e-7, with 54 cones, largest dimension 32, and 11446 factor entries. Exact validation took 0.278 s and 57.0 MB. Both use exact dyadic affine coefficients with 40 fractional bits, so the total certificate denominator is 2^120; equality multipliers use 2^80.

These apply to Nup=Ndown=8 without an S0 assumption. Independent physical-map auditing passed all 54 six-block maps, 30,613 affine nonzero coefficients, all 66 fixed-sector equalities, and every exact projected numerator. See lab001/audit-dual-blocks-pqg.json. The original operator space is the degree-two core plus 88 symmetry-closed cubic polynomials and their 88 adjoints, dimension 2257. Exact span/rank evidence in lab001/distilled/dual-16-pqg-q20 connects the reduced PSD witness to that literal selected space. Its residual SOS operators stay in the degree-two core.

The six-block solver observation was 0.589 s selection/construction from existing exports, 13.82 s solve, and 361.9 MB process peak. Independent physical auditing took 3.519 s and 113.4 MB. The full discovery construction/solve costs remain charged; portable fresh construction is a separate final reproduction observation.

### Fresh portable reproduction

The promoted src/reproduce.py completed construction, solve, export, independent physical-map audit, exact certificate, and exact operator closure/rank sequentially in **22.953 s including Python startup for each stage**. It reproduced the identical exact lower bound **-8.763353354793**. Construction was 0.835 s, solver call 11.277 s, and factor/map export 0.234 s. The largest stage process peak was 404.5 MB. Full details are in [reproduction.json](results/portable-reproduction/reproduction.json), with stage logs, input hashes, affine exports, and proofs. This fixed-space run loads no lab or discovery oracle. Full-model discovery and exploratory research remain separate costs.


## Wiki ingest handoff

Ingest supported claims and their exact artifact paths into the benchmark thesis, method, comparison, and preserved frontier. Retain numerical diagnostics and unsuccessful attempts with their stated limitations; do not promote them to certified energy results.


### Full discovery-model reproduction and validation repair

The promoted full T2prime model reconstructed in 5.666 s, solved in 183.911 s, and exported in 0.763 s. Its exactly certified lower bound is unchanged at -8.764969112905. Successful stage wall times including startup, physical audit and exact certificate sum to 198.865 s, with 388.2 MB largest process peak. See [full reproduction](results/full-reproduction/reproduction.json).

The first physical audit failed in 2.858 s because the new descriptor exporter omitted its operator-kind field. The physical matrices were already fully exported; adding the missing metadata allowed the independent audit to pass every coefficient. The successful solve was reused. The resumed record excludes the manual restart gap and lists the failed attempt separately. The initial failed audit log was overwritten by the resumed log; the preserved tool traceback identifies KeyError: kind in the descriptor lookup. Future resume calls preserve prior failure logs. No failed audit is treated as a certificate.
