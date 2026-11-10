---
document_type: lab_report
lab_id: lab-003-theory-audit
status: completed
idea_ids:
- k-001
- c-003
wiki_context:
- wiki/thesis.md
- wiki/ideas/research-frontier.md
related_labs:
- labs/lab-001-cluster-certificates
- labs/lab-002-moment-sdp
- labs/lab-004-exact-dual-verification
- labs/lab-005-local-rdm-extension
- labs/lab-006-true-cubic-grams
---

# Lab 003 — Cubic positivity and theory audit

## Motivation

Establish the exact algebraic scope of the cubic hierarchy and compare full and theorem-specific variants.

## Design

CAR-based T1/T2prime construction, exact symmetry reductions, primary-source checks, bounded solver refinements, and separate singlet experiments.

## Findings

The completed full T2′ experiment gives an exact verified total-energy lower bound of **−8.764969112905**, or −0.547810569557 per site. Its uncorrected SDP value is approximately −8.76290; the difference is a conservative coefficient-residual correction, not a statistical uncertainty. A separate exact equality-multiplier fit in lab004 improves the same factors to **−8.764879966348**. The smaller selected-operator solution in lab002/lab004 is the final benchmark recommendation; this lab supplies stronger full-space comparisons and independent algebra checks.

| Experiment | Certified total lower bound | Construction | Solve | Peak RSS |
|---|---:|---:|---:|---:|
| PQG + full T1, D4/spin reduction | −9.839898719195 | 6.89 s | 156.99 s | 192.2 MB |
| PQG + mixed-spin full T2′, D4/spin reduction | −8.790405273878 | 4.65 s | 559.20 s | 237.4 MB |
| PQG + full T2′, exact D4/spin reduction | −8.764969112905 | 50.88 s | 511.52 s | 265.6 MB |
| PQG + full T1 + full T2′ + singlet theorem | −8.763432534493 | 39.82 s | 1273.29 s | 330.7 MB |

Exact dyadic verification took 2.89 s/55.4 MB for compressed T1, 4.47 s/59.5 MB for mixed T2′, 3.39 s/74.5 MB for full T2′, and 4.09 s/76.0 MB for the singlet refinement. Reproducible exports use `outputs/pqgt1_sym`, `outputs/pqgt2prime_mixed_sym`, `outputs/pqgt2prime_sym`, and `outputs/pqgt1t2prime_sym_s0`; the matching `_exact` directories contain the exact rational certificate records. The singlet row changes the relaxed feasible set; Lieb's theorem makes this a valid bound on the physical ground energy, separately from the original number-sector relaxation.

### Mathematical construction

For each ordered triple T=(p<q<r), let A_T=a_r a_q a_p. The matrix
`T1[T,U] = <A_T† A_U + A_U A_T†>` is positive semidefinite. CAR cancels all degree-six terms, leaving only the one- and two-particle moments already used by PQG. Momentum and spin composition give 64 blocks of dimension 35 or 120. The cubic tests add 9,920 annihilation/creation operators to the 2,081-dimensional original PQG operator space, for 12,001 original-Hilbert-space operators before sector identities.

For T2, use `A_(a,b;c)=a†_a a†_b a_c` with a<b. Standard T2′ uses this anticommutator matrix as its cubic block, one-sided quartic cross terms `<A_i† a†_k>`, and lower-right `<a_k a†_k>=1−n_k`. This is the sum of a Gram matrix for `(A_i,a†_k)` and the transpose-conjugate Gram matrix for `(A_i†,0)`. Full T2′ together with PQG uses 33,825 original operators; adding T1 gives 43,745.

The anticommutator constraints relax separate full cubic Gram positivity. Therefore their optimum is not claimed to equal the literal minimum for the full cubic space in the PDF. A dual feasible certificate still proves a lower bound using sums of squares of operators in that space.

### Validation completed

The T1 algebra was compared with direct matrices in the six-mode Fock space: maximum elementwise CAR error was exactly zero. T2 and its standard linear augmentation were independently checked in five- and four-mode Fock spaces with zero matrix error. The exact certificate verifier replaces floating dual matrices by exact positive Gram factors and bounds every remaining affine coefficient using the PQG consequence `|n|, |Gamma| <= 1`.

The cluster-cover normalization and complete-eigenbasis residual lower-bound theorem were independently audited. Translation, D4, and spin-swap averaging preserve the specified number sector and the full chosen spaces. Stationarity constraints would require a separately labeled ground-state relaxation; none were added here.

### Completed comparisons and bounded attempts

The full T2′ pilot completed with exact D4/spin variable compression (3,240 to 331 moments), integer little-group cone projections, 244 total cones, maximum dimension 233, and 410,274 scalar matrix entries. Source operator words, sparse integer projection W matrices, and the signed symmetry expansion T are exported for independent map reconstruction. Exact affine-map checks establish zero cross-character entries. The cluster-bound agent independently reconstructed the full physical maps and projection congruences. The singlet refinement adds T1 cones for 280 total cones and 446,924 entries.

The initial uncompressed T1 attempt gave the weaker exact bound −9.847999995266 (35.60 s construction, 472.98 s solve, 390.5 MB peak). Two unreduced T2 pilots were retired after the equivalent symmetry-reduced construction succeeded; `abandoned_runs.json` records their consumed resources. A one-iteration SCS warm-start smoke check verified the canonical primal/dual map to2.50e−14; it is a software check, not an improved energy result. No further SCS refinement was run after the cheaper selected solution succeeded.

The full-T2′ Clarabel precision attempt terminated during its native solver call with exit137, before exporting a solution or witness. It had requested600-second/2-GB watchdog limits, but no watchdog record was written, so the termination cause and peak memory are not established. The attempt began08:20:44 UTC and termination was observed by08:30:34 UTC. `outputs/pqgt2prime_clarabel/attempt.json` and `clarabel_refine.log` preserve this unsuccessful attempt. No bound is claimed from it.

Lab006 retained 200 shared sixth-degree moments in separate cubic Gram matrices. The full-T2′ primal already admits that extension to numerical tolerance (2.36e−9 contraction mismatch, positive Gram margin2.15e−5). The joint pilot produced no stronger certificate and is not continued.

### Primary references and calibration

X. Han, *Quantum Many-body Bootstrap*, [arXiv:2006.06002](https://arxiv.org/abs/2006.06002), motivates local operator selection. Its thermodynamic-limit numbers are background, not certificates for this finite instance.

J. S. M. Anderson, M. Nakata, R. Igarashi, K. Fujisawa, and M. Yamashita, *The second-order reduced density matrix method and the two-dimensional Hubbard model*, [arXiv:1207.4847](https://arxiv.org/abs/1207.4847), Table IV reports the same lattice and coupling with an additional singlet restriction: ED −8.46888, PQG −10.5641, PQGT1 −9.77809, and PQGT1T2′ −8.76192. These published values are comparisons only.

E. H. Lieb, *Two theorems on the Hubbard model*, [Phys. Rev. Lett. 62, 1201 (1989)](https://doi.org/10.1103/PhysRevLett.62.1201), proves the half-filled repulsive bipartite ground-state spin `S=||A|−|B||/2`. The connected 4×4 torus has equal sublattices, real hopping, and constant U>0. The [erratum](https://doi.org/10.1103/PhysRevLett.62.1927.5) changes wording and an intermediate equation, not this conclusion.


## Wiki ingest handoff

Ingest supported claims and their exact artifact paths into the benchmark thesis, method, comparison, and preserved frontier. Retain numerical diagnostics and unsuccessful attempts with their stated limitations; do not promote them to certified energy results.
