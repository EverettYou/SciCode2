---
document_type: lab_report
lab_id: lab-006-true-cubic-grams
status: completed
idea_ids:
- c-005
wiki_context:
- wiki/thesis.md
- wiki/ideas/research-frontier.md
related_labs:
- labs/lab-001-cluster-certificates
- labs/lab-002-moment-sdp
- labs/lab-003-theory-audit
- labs/lab-004-exact-dual-verification
- labs/lab-005-local-rdm-extension
---

# Lab 006 — Individual cubic Grams with shared sixth-degree moments

## Motivation

Test whether shared sixth-degree moments strengthen the full T2prime candidate.

## Design

Individual cubic Grams sharing a semantic X tensor, exact contractions, physical checks, and a fixed-moment compatibility diagnostic.

## Findings

This completed pilot tests whether retaining a small, shared set of sixth-degree moments strengthens the validated full T2′ bound. It begins with the faithful `N↑=N↓=8` model; no singlet restriction is added. **No validated improvement was found.** A separate extension solve shows that the existing full-T2′ primal point already admits these individual cubic Grams to numerical tolerance. The branch is therefore closed without a new best certificate.

The new tensor is `X(d,a,b)=<c†_(d,up)c_(0,up)n_(a,down)n_(b,down)>`, for distinct unordered density sites a,b. Exact translation reduction leaves 1,920 raw moments. D4, spin swap, and real Hermiticity reduce them to **200 new real variables**. Cases a=b reduce to the existing two-RDM moment `Y(d,a)=<c†d c0 n_a>`. Together with the full T2′ model this gives 531 variables.

The operator tests are every translated `c†_(i,up)n_(j,down)` and its adjoint, with the linear creation/annihilation operators. Fourier transformation produces individual Gram matrices. In each momentum sector, the opposite-spin number identity removes one density seed: `sum_r F_(k,r)=8 c†_k`. We retain 15 relative density locations and the linear seed. D4 and spin symmetry leave six representative momenta and two charges, giving **12 additional realified 32×32 cones**.

The same X tensor appears in every product. Thirty-nine distinct exact number contractions enforce `sum_b X(d,a,b)=8Y(d,a)` and `sum_i X(0,a−i,b−i)=8<n_a n_b>`. This differs from choosing unrelated matrices whose sum equals a T2 anticommutator.

All Fourier phases are Gaussian integers. Multiplication by256 makes the new affine cone and equality maps integral. `global_symmetry_expansion.npz`, `full_global_names.json`, `extra_moment_names.json`, and `extra_moment_reduction.json` separate the original moments from the new semantic tensor. Physical seed definitions and scaling are in `true_gram_descriptors.json`.

### Coordinate bounds for certificate correction

For each X, use annihilation seeds `B1=n_(a,down)c_(d,up)` and `B2=n_(b,down)c_(0,up)`. Then `X=<B1† B2>`. Positivity of their Gram matrix gives `|X|²<=<B1†B1><B2†B2>`. Each diagonal is a two-RDM occupation probability bounded by1 using PQG. Thus **|X|<=1** follows from the selected cubic Gram positivity and existing PQG constraints. The omitted Fourier density seed is recovered through the exact number contractions. Explicit redundant scalar bounds `1±X>=0` are also included to aid numerical stability.

An explicit SOS identity certifies each scalar bound for indefinite rho: if `p=<B1†B1>` and `q=<B2†B2>`, then `1±X = ½<(B1±B2)†(B1±B2)> + ½(1−p)+½(1−q)`. Each complement satisfies `1−<n_d↑n_a↓> = <c_d↑c_d↑†> + <(c_a↓†c_d↑)†(c_a↓†c_d↑)>`. These squares lie in the chosen cubic span and existing linear/quadratic span. The justification does not assume that rho is globally positive.

### Validation completed

Construction took5.12s. A physical density matrix uniform in each fixed-number spin sector satisfies all equalities to1.85e−13; the smallest new Gram eigenvalue is0.44788 after the scale factor256. An independent eight-mode direct Fock calculation, using a nontrivial translation-invariant mixture of Slater states and their complex conjugates, reproduces both Fourier Gram formulas with **exactly zero matrix error**. A second check uses a D4 mixture of nontrivial fixed-N8N8 momentum Slater determinants: every global Γ-to-Y/D Fourier map and every shared-X number contraction agrees with Wick's theorem with zero error. The new Gram minimum is−7.84e−14, consistent with floating eigensolver rounding at a PSD boundary. Results are saved in `fock_fourier_check.json` and `wick_map_check.json`.

### Outcome and resources

The joint SCS pilot used531 variables,656 cones (including400 redundant scalar boxes), maximum dimension233, and422,962 full matrix entries. It ran5,000 iterations in628.27s and used457.6MB peak RSS. The approximate primal energy was−8.76051804, but the coefficient-residual correction was1.90296; its corrected floating value−10.66319 is weaker than the original full-T2′ certificate. The solver returned `optimal_inaccurate`. This approximate primal value is not presented as a validated lower bound, and no exact verification of that weaker witness was needed.

The decisive compatibility check fixes the331 global moments to the full-T2′ primal and solves only for the200 extra moments in12 realified32×32 cones. To accommodate the original numerical equality error, it minimizes a common nonnegative cone/equality slack. Clarabel returns `optimal_inaccurate` with slack1.97e−9, contraction mismatch2.36e−9, and minimum unscaled Gram eigenvalue+2.15e−5. Cost was3.13s and278.2MB. This is numerical evidence of compatibility, not an exact feasibility theorem, but it supplies no reason to continue the expensive joint energy optimization. The initial exact-equality feasibility attempt hit a solver error; the softened diagnostic above records the actual conclusion.

All completed outputs, cached models, shared-moment semantics, and unsuccessful solver logs are preserved under `outputs/full_t2_plus_true_density` and `outputs/fixed_full_t2_extension`. No additional branch is planned.


## Wiki ingest handoff

Ingest supported claims and their exact artifact paths into the benchmark thesis, method, comparison, and preserved frontier. Retain numerical diagnostics and unsuccessful attempts with their stated limitations; do not promote them to certified energy results.
