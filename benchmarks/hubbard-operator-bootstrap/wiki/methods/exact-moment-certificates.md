---
title: Exact Hubbard moment certificates
page_type: method
status: active
updated: '2026-10-07'
source_refs:
- labs/lab-004-exact-dual-verification/REPORT.md
- labs/lab-001-cluster-certificates/REPORT.md
idea_ids:
- k-001
- c-006
topics:
- Correlated Systems
---

# Exact Hubbard moment certificates

**Summary**: Exact Gram arithmetic, physical-map auditing, and declared operator closure jointly certify the reference bound.

**Sources**: [lab-004-exact-dual-verification evidence](../../labs/lab-004-exact-dual-verification/REPORT.md); [lab-001-cluster-certificates evidence](../../labs/lab-001-cluster-certificates/REPORT.md)

**Last updated**: 2026-10-07

For M_j=A_j x+b_j PSD and E x=e, choose exact PSD Z_j=K_j K_j^T/2^80. Define r=c+E^T lambda-sum A_j^T vec(Z_j), and d=-e^T lambda-sum b_j^T vec(Z_j). Occupation, particle-hole and pair Gram positivity imply |x_i|<=1, so d-||r||_1 is a rigorous lower bound. The [validation proof](../../labs/lab-004-exact-dual-verification/REPORT.md#mathematical-formulation) supplies explicit residual SOS terms in the degree-two core.

The verifier reconstructs the exact Hubbard objective rather than trusting exported cosine evaluations. It handles integer and exact dyadic affine coefficients; the selected q20 projections have forty affine fractional bits and yield a common certificate denominator 2^120. No solver status or numerical eigenvalue tolerance enters the final Gram positivity claim.

The [independent auditor](../../labs/lab-001-cluster-certificates/scripts/audit_moment_maps.py) rebuilds CAR, geometry, every affine map, sector equality, and symmetry action without importing the builder. It checks 4000 Fock actions and all 46,656 relative-order/equality patterns of its optimized T2 contraction identity. Exact coefficient validation and physical-map validation are separate stages.

A reduced dual direction is not an operator-space dimension. Sixteen active directions close to 88 cubic polynomials under D4/spin transformations; adjoints and the 2081-dimensional core give [dimension 2257](../../labs/lab-001-cluster-certificates/distilled/dual-16-pqg-q20/operator_space.json). Exact span relations and matching modular rank establish the count. Group twirling lifts reduced witnesses to this literal selected space.

T1/T2 anticommutator constraints eliminate sextic moments and form a weaker optimization than full cubic Gram positivity. Their dual squares belong to the declared cubic space, so the computed certificate is valid for its literal Eq(2) minimum. No equality between the two SDP optima is asserted.

## Related pages

- [Research map](../index.md)
- [Research frontier](../ideas/research-frontier.md)
