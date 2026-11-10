---
document_type: lab_report
lab_id: lab-001-cluster-certificates
status: completed
idea_ids:
- c-001
- k-001
- c-006
wiki_context:
- wiki/thesis.md
- wiki/ideas/research-frontier.md
related_labs:
- labs/lab-002-moment-sdp
- labs/lab-003-theory-audit
- labs/lab-004-exact-dual-verification
- labs/lab-005-local-rdm-extension
- labs/lab-006-true-cubic-grams
---

# Cluster bounds and independent physical-map auditing

## Motivation

Compare certified local-support bounds and independently validate the physical maps and selected operator space.

## Design

Translation-averaged cluster decompositions, complete spectral certificates, independent exterior-algebra audits, and exact symmetry-closure rank proofs.

## Findings

The strongest completed cluster certificate is **E0 >= -14.25342470**, for the
4x2 cylinder embedded in the 4x4 torus. This branch was pruned after the independent
PQG moment relaxation produced a substantially stronger bound at smaller cost.
The cluster bound remains a useful independently validated baseline.

| Cluster | Total-energy lower bound (rounded down) | Largest dense sector | Construction and validation | Peak resident memory |
| --- | ---: | ---: | ---: | ---: |
| 2x2 open | -16.821987868 | 36 | 0.040 s | 59.2 MB |
| 2x3 open, uniform weights | -15.373681304 | 400 | 0.203 s | 70.1 MB |
| 2x3 open, optimized weights | -14.670935399 | 400 | 0.294 s + 0.917 s optimization | 70.7 MB |
| 2x4 cylinder | -14.25342470 | 4,900 | 105.365 s | 978.4 MB |

The process timings above are the latest complete runs on the shared workstation;
optimization time is recorded separately in `weights-2x3.json`. Other agents ran
concurrently, so these are observed resource measurements rather than isolated
machine benchmarks. The first cylinder run took 107.210 s with 1,126.7 MB peak RSS.
All peak-RSS figures are macOS bytes divided by 10^6. Each complete run includes
matrix construction, all necessary sector diagonalizations, and numerical
validation. Per-sector times are in the result JSON files.

### Construction and operator interpretation

For a cluster C with n sites, distribute hopping coefficients so their sum is n
for each lattice direction, and onsite coefficients so their sum is 8n. Define

K_C = -sum_(ij,sigma) t_ij(c_i,sigma^dagger c_j,sigma + h.c.)
      + sum_i u_i(n_i,up - 1/2)(n_i,down - 1/2).

All stored coefficients are exact dyadic rationals and their translation-cover
sums are checked using Python `Fraction`, rather than rounded floating sums.
There are 16 physical translations. In the required Nup=Ndown=8 sector,

H = (1/n) sum_tau K_(tau C) + 32.

If lambda is a certified lower bound for every particle sector of K_C, then

H - [16 lambda/n + 32] I = (1/n) sum_tau [K_(tau C)-lambda I] >= 0.

An explicit permitted operator-space construction is the span of the 16
translated local spectral square roots O_tau = sqrt[(K_(tau C)-lambda I)/n].
Its positive diagonal tests alone establish the reported bound. The code defines
these roots by finite functional calculus on the explicitly constructed local
matrices; it need not materialize their dense expansions. Each operator has
support n sites, is even and number preserving, and has a normal-ordered fermion
expansion of degree at most 4n. This certificate is a guaranteed lower bound for
that operator space; we do not claim to have solved the entire literal relaxation
including every cross-Gram identity for these square roots.

The square-root count alone hides the computation: local Hilbert dimensions are
256, 4,096, and 65,536, with largest particle-number blocks 36, 400, and 4,900.
The complete number-preserving local algebra has sum_(a,b) dim(a,b)^2 =
C(2n,n)^2 matrix entries, namely 4,900, 853,776, and 165,636,900. We exploit its
block structure and certify only the sectors that cannot be excluded by a proven
kinetic-plus-interaction estimate. All representative sectors and their methods
are recorded, including those excluded without dense diagonalization.

The cylinder has hopping 1 along its periodic direction, hopping 2 across its
rungs, and onsite coupling 8. The optimized 2x3 cluster uses onsite coefficients
2.4287109375 on the four outer sites and 19.142578125 on the two center sites;
rung hoppings are 0.7646484375 on the two outer rungs and 4.470703125 on the center
rung, with longitudinal hopping 1.5. Redistributing interaction toward the
center improves the bound by 0.702746 total energy at almost unchanged solve cost.
A discovery-only optimized 2x4 open cluster reached about -14.3338321 and was not
certified, because it was already inferior to the cylinder and the moment SDP.
No unvalidated discovery number is used as a reported lower bound.

### Numerical certificate

For each dense sector, let Q be the complete computed eigenvector matrix, D the
computed diagonal eigenvalue matrix, R=AQ-QD, and eta >= ||Q^T Q-I||_2. If eta<1,

lambda_min(A) >= min(D) - ||R||_2 / sqrt(1-eta).

To prove this, take a normalized lowest left eigenvector x of symmetric A and
z=Q^T x. Then z^T(D-lambda)=-x^T R and
||z|| >= sqrt(1-eta). If lambda<min(D), the stated inequality follows directly.
Completeness of Q is essential; a single approximate Ritz vector would not prove
this result.

The implementation bounds the residual spectral norm by
sqrt(||R||_1 ||R||_infinity), the symmetric Gram error by its infinity norm,
and adds gamma_k = ku/(1-ku) dot-product error bounds, with binary64 unit
roundoff u=2^-53. Nonnegative sums and scalar bounds are rounded outward, with
additional conservative margins. Exact dyadic matrix coefficients avoid
Hamiltonian coefficient uncertainty. The cylinder ground block has eta about
1.60e-9 and residual spectral norm at most 5.79e-10; its final energy is rounded
further downward to -14.25342470.

This is a floating-arithmetic certificate under the stated IEEE754 and standard
BLAS dot-product model. The benchmark's preferred moment certificate additionally
uses exact integer Gram arithmetic, avoiding this assumption for its final bound.

Spin interchange and simultaneous particle-hole transformations reduce sectors;
the latter uses the bipartite sign (-1)^(x+y), valid for every induced subgraph of
the even 4x4 torus. We do not infer a cluster ground sector from residuals or
from a half-filling theorem: every symmetry-distinct sector is certified or
excluded using an independently certified lower bound.

### Reproduction

From the repository root, run the Python commands below with NumPy and SciPy:

```sh
python3 benchmarks/hubbard-operator-bootstrap/labs/lab-001-cluster-certificates/cluster_bound.py --w 4 --h 2 --periodic-x --certify --output /tmp/cylinder-result.json
python3 benchmarks/hubbard-operator-bootstrap/labs/lab-001-cluster-certificates/optimize_weights.py --shape 2x3 --output /tmp/weights-2x3.json
python3 benchmarks/hubbard-operator-bootstrap/labs/lab-001-cluster-certificates/cluster_bound.py --w 3 --h 2 --certify --weights /tmp/weights-2x3.json --output /tmp/optimized-result.json
```

### Independent physical-map audit

`scripts/audit_moment_maps.py` imports neither the optimization builder nor its
normal-ordering code. It independently rebuilds the 32 distinct physical bonds,
proves the Fourier hopping coefficients using exact Gaussian-integer phases,
reconstructs all variable and operator bases, and compares every sparse affine
map, constant, fixed-number equality, and right-hand side. Its normal-ordering
routine multiplies exterior monomials from left to right, whereas the builder
uses recursive adjacent transpositions. It also checks 4,000 direct Fock-action
identities and explicitly verifies cancellation of degree-six terms for T1/T2.

The PQG export passed every physical-map check. Its original objective contained
cosine-rounding artifacts of at most 7.35e-16; the final verifier independently
reconstructs and uses the exact half-integer Fourier objective. The affine maps
and equality data matched exactly. Audit results and timings are stored in
`audit-*.json` alongside their full block logs.


The completed independent audits have the following measured costs. These are
additional validation costs and must be included alongside solver and exact
integer-certificate timings.

| Export | Exact affine coefficients checked | Physical audit time | Peak RSS |
| --- | ---: | ---: | ---: |
| PQG eps6, initial exterior audit | 37,600 | 2.300 s | 55.8 MB |
| PQG + T1 | 219,232 | 35.544 s | 82.8 MB |
| PQG + density T2', full-word audit | 112,896 | 116.533 s | 97.2 MB |
| PQG + density T2', contracted audit | 112,896 | 29.061 s | 84.1 MB |

The faster T2 routine is derived by commuting the two annihilators in A_t^dagger
past the two creators in A_u, retaining all double and single contractions.
Its sextic cancellation and contraction signs are exhaustively compared with the
independent exterior implementation on all 6^6 = 46,656 assignments of six
indices to ranks 0,...,5. Any six indices among 32 modes have one of these
relative-order and equality patterns, so this validates the identity generally.
The exhaustive checks are included in each current audit's reported time.
The full-word and contracted selected-T2 audits independently agree on every
coefficient; both costs are retained in the experimental record.

The auditor also handles exact D4/spin variable expansion and little-group cone
congruences. It independently traverses signed variable orbits, checks all
claimed reflection eigenplanes, proves their complete orthogonal span by exact
integer Gram products, and verifies all cross-character affine maps vanish.
A projected cone remains physically valid even without completeness, but these
extra checks validate the claim that the projection preserves the entire cone.

A separately derived spin-singlet equation is exported in
`singlet-constraint.json`, with its independent direct Fock-action tests in
`scripts/singlet_constraint.py`. Its 152 coefficients represent S^-S^+=S² at
Sz=0. The test explicitly distinguishes a singlet from an Sz=0 triplet.
This equation is not an identity throughout the requested Nup=Ndown=8 sector;
using it requires the independently justified Lieb-theorem restriction to the
spin-singlet ground sector. It is a separate refinement, not silently included
in any of the original-sector cluster or moment audits above.


Later completed symmetry audits passed with these additional costs:

| Export | Exact affine coefficients checked | Physical audit time | Peak RSS |
| --- | ---: | ---: | ---: |
| Four-family two-site T2', D4/spin reduced | 335,781 | 34.387 s | 138.6 MB |
| Full monomial T2', D4/spin reduced | 174,132 | 20.909 s | 113.6 MB |

The first has 66 final cones and six independently reconstructed source cones;
the second has 244 final cones and 12 sources. Both use 331 reduced variables.
An additional combined T1 + four-family T2' construction audit took 33.533 s and
146.8 MB; it checked all 18 source cones before the solver finished exporting
its final maps. That construction audit is explicitly marked incomplete until
the stored final coefficient maps have also been compared.

`resource-summary.json` collects every completed lab resource record and flags
construction-only audits separately. These multiple validation runs are genuine
research costs, not hidden behind the final verifier's timing.

The final combined T1 + four-family T2' export also passed every physical map
check: 102 cones, 362,097 nonzero affine coefficients, 30.756 s and 132.9 MB.

### Compressing the discovered dual witness

The dual Gram factors suggest a compact subspace after the SDP search. Dropping
factor columns whose squared norm is at most 1e-10, then repeating exact integer
verification, retains essentially the same bound:

| Witness | Original factor columns | Retained nonzero columns | Factor entries | Exact total-energy lower bound |
| --- | ---: | ---: | ---: | ---: |
| Four-family two-site T2' | 942 | 83 | 2,346 | -8.864558789095 |
| Full monomial T2' | 5,062 | 62 | 6,870 | -8.764969112897 |

These are **dual witness ranks**, not dimensions of the complete literal
operator space. The positive square terms number 93 and 78, respectively, before
spatial/spin group closure and residual-coordinate SOS completion. That closure
and the degree-two residual operators remain necessary in a literal operator
subspace construction. No claim of a complete 83-dimensional or 62-dimensional
operator-space relaxation is made.

Compression took 0.501 s and 1.436 s, with exact reverification taking 0.638 s
and 1.313 s, respectively. The initial full SDP search cost is still charged to
the experiment. `scripts/compress_dual.py` creates a reproducible compressed
certificate using relative links to unchanged source maps and independent factor
files; `lab-004-exact-dual-verification/scripts/verify_exact.py` computes its
new exact lower bound. Empty factor spaces are represented by a single zero
column for compatibility with the verifier, and are excluded from the retained
nonzero-column counts.

This gives a useful operator-selection outcome: most cubic directions are
inactive at the discovered solution, and a small collection of optimized cubic
linear combinations carries the improved bound. It is a compact witness for the
affordable search already performed, rather than a claim that the search itself
had the cost of the compressed certificate.

The spin-complete two-site extension passed 84 cones and 372,286 affine
coefficients in 29.988 s with 159.9 MB peak RSS. The three-site-star Clarabel
export passed 66 cones and 856,739 affine coefficients in 11.952 s with 572.8 MB
peak RSS. Its larger validation memory is included in the comparison.

The star construction intentionally selects an 85-dimensional subspace of a
377-dimensional raw cubic source. The auditor reconstructs its 60 two-site
columns, 24 real cosine/sine Fourier star columns, and one linear column from
exact Gaussian-integer phases. It then proposes an integer change of basis using
a floating solve, validates the equation P*C=W with an exact integer residual,
and proves both ranks are 85 using modular elimination. Thus no floating solve
or sampled rank is trusted. The character projections preserve that selected
subspace; they do not preserve the full 377-dimensional source, and the audit
makes that distinction explicit.

### A complete2257-dimensional operator selection

The full-T2 witness has16 active cubic factor directions. Their exact integer
coefficients, mapped back through the character projections, can be closed
under the16-element D4/spin group and supplemented by adjoints and the full
degree-two PQG core. Exact rational dependence certificates and matching
modular rank lower bounds establish the resulting dimensions. The q40 witness
initially gave96 independent closed cubics and a complete2273-dimensional O.
Quantizing the directions at q20 removed tiny numerical symmetry noise and
gave88 independent closed cubics,88 adjoints, and the2081-dimensional PQG core:
the complete declared polynomial span has dimension2257.

The16 q20 scalar directions were re-solved with the PQG core and then grouped
into six small matrix cones with existing one-body augmentation. Every first
column direction agrees exactly with the scalar replay, and every new last
column is exactly c-dagger_k already in the core. The six-cone replay therefore
has the same2257-dimensional O. Its exact total-energy certificate is
**-8.763353354793**, using54 final cones, maximum cone dimension32, and11446
factor entries. The solver took13.820 s with361.9 MB process peak RSS;
construction/build took0.589/0.018 s. This is the final replay cost after
discovering the directions through the more expensive full-T2 search.

The original six-block audit compared all30613 affine coefficients and took
3.519 s,113.4 MB. A second, self-contained audit reconstructs the raw377-word
CAR sources directly and contracts the portable integer R matrices. It uses no
discovery oracle, passed all54 maps and the Hamiltonian/equalities in3.147 s,
and reached188.0 MB. Independent direct-R operator distillation reproduced the
2257 count in0.365 s,67.4 MB. Exact integer SOS validation took0.278 s,57.0 MB.
The portable proof/data are in `distilled/portable-dual-blocks-q20`; the auditor
accepts `--operator-input` pointing to the six source descriptors and R files.

The literal operator relaxation additionally requires all Gram entries of O.
The small anticommutator/congruence SDP used to discover and replay this
certificate is an auxiliary relaxation. Its dual SOS proves the displayed
lower bound for the literal O without claiming that the auxiliary primal
optimum equals the full literal operator-space optimum.

`operator-count-audit.json` independently checks rank15 per density family,
rank60 per four-family two-site source, rank15 per extreme-spin source, and
rank84 cubic plus one linear per star source. It confirms5921 for two-site,
15841 for T1 plus two-site,7457 for stars, and33825 for full T2. These are
original full-Fock polynomial dimensions before further fixed-sector
identities. No count discrepancy was found; reduced cone dimensions, active
dual squares, and complete operator-space dimensions remain distinct.

`global-comparison.json` and `global-comparison.md` aggregate every completed
global and cluster branch, all adaptive checkpoints, validation invocations,
and explicitly retained abandoned runs. Per-process elapsed phases cannot be
summed into end-to-end wall time because the experiments ran concurrently.
Process peak RSS is also distinct from total simultaneous workstation memory.
Shared adaptive oracle loading is charged once rather than once per checkpoint.

The remaining completed comparison audits also passed: symmetric T1-only,
244 cones/63104 affine coefficients in4.949 s and91.0 MB; mixed-spin full T2',
226 cones/96552 coefficients in5.062 s and97.2 MB; and the final adaptive
checkpoint,186 cones/372326 coefficients with all120 exact dyadic cuts checked
in23.737 s and137.7 MB. The T1 and mixed-spin branches already have exact SOS
certificates. The weaker adaptive branch is explicitly retained as floating;
no additional exact verification was run. The S0 combined branch passed all
280 maps and the separately derived singlet equality in13.676 s,114.8 MB.

No further numerical validation or new scientific branch is planned in this
lab. The root task owns final portable pipeline timing and publication.

The root task's fresh portable reproduction subsequently completed the entire
sequential construction, solve, export, physical audit, exact SOS verification,
and operator-rank check in22.953 s including Python startup. It reproduced
exactly -8.763353354793 with O dimension2257. Its largest stage process peak
was404.5 MB; construction/solve/export took0.835/11.277/0.234 s. These fresh
measurements are included separately in the global comparison, rather than
replacing or hiding the preceding discovery and validation costs.


## Wiki ingest handoff

Ingest supported claims and their exact artifact paths into the benchmark thesis, method, comparison, and preserved frontier. Retain numerical diagnostics and unsuccessful attempts with their stated limitations; do not promote them to certified energy results.
