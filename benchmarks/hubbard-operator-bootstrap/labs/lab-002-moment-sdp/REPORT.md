---
document_type: lab_report
lab_id: lab-002-moment-sdp
status: completed
idea_ids:
- c-002
- c-003
- c-006
wiki_context:
- wiki/thesis.md
- wiki/ideas/research-frontier.md
related_labs:
- labs/lab-001-cluster-certificates
- labs/lab-003-theory-audit
- labs/lab-004-exact-dual-verification
- labs/lab-005-local-rdm-extension
- labs/lab-006-true-cubic-grams
---

# Translation-reduced fermionic moment bootstrap

## Motivation

Find affordable global moment constraints and select the cubic directions that carry the energy certificate.

## Design

PQG and selected T2prime models, D4/spin reductions, solver comparisons, adaptive trials, and dual-guided compact replay.

## Findings

The final stable construction uses only 16 discovered cubic directions, closed under D4 and spin exchange and combined with the full quadratic CAR core. Its exact resolved operator dimension is 2257: 2081 quadratic/linear/identity directions plus 88 cubic directions and 88 adjoints. Six compact T2′ projections, including existing linear augmentation, give 54 PSD blocks, largest dimension 32, and 11446 entries in 331 real moment coordinates. Independent exact arithmetic verifies the total-energy lower bound **E >= -8.763353354793**.

The full T2 oracle was used for discovery and its cost is counted: construction and solving are recorded in lab-003. The selected dual witness has rank 16, spread across just six momentum/character blocks (ranks 3,3,3,3,2,2). The Clarabel solve call for the distilled problem took 13.82 seconds, with 361.9 MB peak RSS, after 0.589 seconds of selection/model loading; these pilot timings exclude result export; the self-contained portable algebraic reconstruction took 0.812 seconds. Exact dual validation took 0.278 seconds and 56.95 MB in the independent verifier. The solver flag was `optimal_inaccurate`; validity follows from the exact certificate and does not depend on that flag.

A blind adaptive search selected 120 most-violated primal eigenvector tests over 10 rounds, but improved the small model only to a floating candidate -8.859542438484 after 313.75 seconds. In contrast, sixteen dual directions recover essentially the full-T2 energy witness. This comparison shows that large positivity violations can concern correlations with little influence on the energy objective.

`promotion/` is the self-contained handoff: it builds the PQG core directly and constructs the six new blocks from bundled raw operator words and integer projections. It imports no lab module and needs no expensive oracle cache. All 54 affine blocks, objective coefficients and equalities were compared exactly with the validated experiment. Compressed exact rank proof data is included in its input directory.

The baseline uses the complete operator space of degree at most two: identity, every creation/annihilation operator, every pair creation/annihilation operator, and every number-conserving quadratic operator. Its full operator dimension is 2081. Fixed spin population makes distinct charge/spin blocks orthogonal; translation makes distinct momentum blocks orthogonal. The resulting optimization uses 3240 real variables and 208 PSD cones, with largest dimension 32 and 36480 entries before triangular packing.

### Mathematical representation

Modes 0–15 are spin up and 16–31 are spin down, with momentum index k=x+4y. Let n_a=<c†_a c_a> and Gamma_(ab,cd)=<c†_a c†_b c_d c_c>, with a<b and c<d. Translation enforces momentum conservation. Fixed spin populations enforce equal spin composition in both pairs. The Hamiltonian is real in this momentum Fock basis, as are all test operators, so averaging a candidate with its complex conjugate permits real symmetric moments without changing the optimum. No stationarity or ground-state-only equality is used.

P blocks equal Gamma. Q blocks equal Gamma+diag(1-n_a-n_b). Particle-hole G entries indexed by (a,b),(c,d) are delta_ac delta_bd n_b-Gamma_(bc,da), with canonical pair signs included. Occupation and hole positivity are explicit. Besides sum_a-in-spin n_a=8, impose each sector contraction sum_b-in-spin-tau Gamma_(ab,ab)=(8-delta_(spin(a),tau))n_a.

The objective is sum_a epsilon_a n_a+(8/16)sum_(k,p,q) Gamma_(up(k+q),down(p-q);up(k),down(p)). For L=4 the dispersions are exact integers; the code rounds their analytically integral trigonometric evaluation before construction. This is the distinct-nearest-neighbor bond convention in the supplied problem.

### Degree-three selection

`selected_t2.py` constructs A_(k,q,sigma)=sum_p c†_(k+q,sigma)c†_(p-q,opposite)c_(p,opposite), for q!=0, together with B=4c†_(k,sigma). The q=0 density mode is N_opposite c†_k and is redundant on the target sector. These are Fourier transforms of c†_(i,sigma)n_(j,opposite). Their addition increases the full test-space dimension from 2081 to 3041, while only adding 32 cones of dimension 16.

The augmented block has top-left <A_i†A_j+A_jA_i†>, cross <A_i†B>, and bottom-right <B†B>. It is the sum of Gram(A_i,B) and the complex conjugate of Gram(A_i†,0), hence PSD. CAR cancels all sextic terms in the top-left block, leaving the same quadratic/quartic moment variables. This is a sufficient degree-three SOS certificate, rather than a claim to solve the full unconstrained cubic Gram hierarchy.

The `--all-two-site` refinement adds same-spin density, onsite pair creation with opposite-spin annihilation elsewhere, and spin exchange between two sites. Each spin/momentum block then contains 60 cubic operators plus the linear augmentation, so its dimension is 61. The full unprojected test-space dimension is 5921; its unreduced induced optimization has 240 cones and 155552 matrix entries. Exact Gaussian elimination modulo the prime 1000003 proves that all 60 cubic operators are independent in each of the 32 spin/momentum blocks (`results/operator_rank.json`). All four families have support on at most two real-space sites, including arbitrary separations. Integer coefficients are retained to simplify independent exact verification.

### Numerical evidence and validation

The SCS baseline at tolerance 1e-6 produced primal -10.566677907992 and a projected-dual residual-corrected floating candidate -10.566825373995 in 41.25 seconds in the solve call, with 138.0 MB peak RSS. Independent exact arithmetic verification is recorded in lab-004. Tightening SCS to 1e-8 hit 30000 iterations, costing 314.17 seconds for a candidate -10.566721990573; this small improvement illustrates poor return on tighter tolerances.

The opposite-density refinement at tolerance 1e-6 produced primal -10.267642827072 and candidate -10.268038996856 in 46.84 seconds, using 189.9 MB peak RSS. It improves the bound by about 0.299 while adding only 8192 matrix entries. Exact signed D4/spin-exchange orbit elimination reduces 3240 moment coordinates to 331. Retaining momentum/spin representatives and splitting their reflection characters with integer congruence matrices reduces the full two-site model to 66 cones, largest dimension 45, with 22050 entries. It produced primal -8.864001438200 and candidate -8.864558788545 after 24450 SCS iterations and 278.21 seconds in the solve call, with 188.5 MB peak RSS; construction under concurrent load took 61.06 seconds. The unreduced model cost 911.56 seconds and 658 MB for a weaker residual-corrected candidate -8.885023369223. Clarabel re-solving the reduced exported model cost 64.06 seconds and 600.5 MB, yielding candidate -8.864118703509 in 19 iterations. The selected space captures most of the independently measured full T2' gain in lab-003 (candidate near-8.765), missing about 0.10 total energy while reducing matrix entries by about 19 times.

`selected_t2.py` compares its hand-coded anticommutator formula against exact CAR normal ordering on 1000 random mode tuples. All comparisons passed. A half-filled momentum Slater product has energy 8.0 in the interacting model, satisfies all sector equalities exactly, and yields PSD P/Q/G blocks up to floating diagonalization noise below 8e-16.

Each result directory exports the objective, equality matrix and RHS, primal coordinates, equality dual multipliers, all affine PSD maps, and dual factors. For M_b=A_b x+b_b and Ex=e, an exact PSD witness Z_b gives d=-e·lambda-sum_b b_b·Z_b and r=c+E^T lambda-sum_b A_b^T vec(Z_b). P/Q/G imply 0<=n<=1, 0<=Gamma_(ab,ab)<=1, and |Gamma_(ab,cd)|<=1 by Cauchy–Schwarz. Thus d-||r||_1 is a lower bound even for the indefinite-rho relaxation. Independent verification quantizes the Gram factors and evaluates this expression exactly, controlling all solver errors.

The pilot JSON fields distinguish model construction, CVXPY construction, the solve call (`solve_sec`, which excludes result export), solver-internal time, and process peak RSS. The promoted replay adds explicit export and complete construction/solve/export timing. Runtime comparisons can be affected by concurrent independent pilot runs; they are measured workstation observations, not performance guarantees.

Additional selected-space tests are recorded in `results/comparison.json`. Adding full T1 to the two-site model improved its floating candidate to -8.856092835008, but cost 569.24 seconds and 256 MB and hit 30000 SCS iterations. Adding only two-site spin-3/2 cubic sectors gave no resolved primal improvement at current precision (-8.864032626503), so this branch was pruned. Adding 24 real Fourier nearest-neighbor three-site star vectors per spin/momentum produced a rank-85 augmented space and a candidate -8.859051476570; construction took 2.36 seconds and Clarabel took 43.15 seconds, but peak memory rose to 1.475 GB. This small improvement does not justify the added memory when the full T2 comparison is already affordable. These negative and marginal results constrain the next selection decision: expand beyond degree-four moments for a substantive improvement beyond the full T2 hierarchy.


## Wiki ingest handoff

Ingest supported claims and their exact artifact paths into the benchmark thesis, method, comparison, and preserved frontier. Retain numerical diagnostics and unsuccessful attempts with their stated limitations; do not promote them to certified energy results.
