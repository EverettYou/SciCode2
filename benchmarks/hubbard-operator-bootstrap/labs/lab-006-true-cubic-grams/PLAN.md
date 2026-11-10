# Lab 006 — Shared degree-six moments in individual cubic Gram matrices

## Objective

Test whether shared sixth-degree moments strengthen the full T2prime candidate.

## Stable interfaces

Exploratory scripts and data stay in this lab. Supported final interfaces are documented in [the stable implementation](../../src/README.md); the promoted portable replay imports no lab module.

## Steps

This bounded pilot retains separate Gram positivity for every translated opposite-spin density-assisted creation and annihilation operator, rather than only their anticommutator. It starts from the validated full T2′ number-sector model.

Represent the new moments by `X(d,a,b)=<c†_(d,up)c_(0,up)n_(a,down)n_(b,down)>`, with `a != b` unordered. Translation leaves 1,920 raw moments; D4, spin swap, and real Hermiticity reduce them to 200. The `a=b` cases equal existing two-RDM moments. The operator basis uses 15 relative density locations plus a linear operator in each momentum/charge sector; the missing density location follows the exact opposite-spin number identity.

Enforce the shared tensor across all cubic Gram products, and exact contractions `sum_b X(d,a,b)=8<c†d c0 n_a>` and `sum_i X(0,a-i,b-i)=8<n_a n_b>`. This is not an arbitrary independent decomposition of an anticommutator matrix.

Use exact Gaussian-integer Fourier phases and scale all new cones/equalities by256, keeping affine maps integral for exact dual verification. Validate on a physical fixed-number diagonal state and direct finite-Fock identities. Retire the pilot if construction/solve cost or lack of improvement fails to justify refinement; initially aim for less than one hour.

Completed outcome: construction and independent Fock/Wick checks passed. The full-T2′ primal is compatible with the new moments to numerical tolerance, and the joint5,000-iteration pilot produced no stronger validated bound. The branch is retired; REPORT.md records resources, diagnostic errors, and the unsuccessful exact-equality attempt.


## Completion criteria

Record actual findings, resources, uncertainty, failed attempts, and evidence paths. A promoted lower bound requires both a valid physical/operator formulation and independent numerical error control. A negative branch completes when its discriminating experiment supports a documented prune decision.
