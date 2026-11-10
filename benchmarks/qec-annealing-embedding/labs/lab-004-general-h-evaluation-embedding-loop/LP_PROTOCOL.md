# Supplemental contact-allocation LP, frozen 2026-10-16T08:31Z

Reuse exactly the saved eight-candidate pools of the36 main instances; no new
embedding generation and no changes to initial outcomes. For each fixed
embedding, use the same spanning tree and root selected by the uniform evaluator.
Optimize physical contact magnitudes, chain strengths and alpha with a sparse
linear program. Contact signs remain the logical coupling sign; contact totals
are alpha|J_ij|. Each F_e must exceed its descendant contact load by the same
main-protocol thermal margin d. Include every coefficient and signed coupling
group constraint. Maximize alpha; the uniform allocation is an ideal feasible
point, but this only establishes fixed-tree/root allocator optimality.

Choose the minimum-qubit LP-programmed candidate satisfying the original
first-valid UNIFORM alpha floor and defect budget. Compare with uniform guided
selection, unconstrained size selection and the original first mapping. Save
all LP statuses, actual timings and numerical violations. Add1e-8 margin reserve
and back off returned alpha by1e-8 before actual-program validation; count any
backoff-induced lost comparison honestly. No refinement or extra candidates are
added to this supplemental selection experiment. Treat HiGHS status as heuristic
numeric output until actual binary64 coefficients pass rational auditing.
