# Word-majorant proof clarification: union support

Final independent parent review identified an overstrong phrase in the frozen theory_extensions/THEORY.md, section3: a diagonal pair commutator was said to add at most one new *function-dependence* site. That wording is false if a flip-displacement site is absent from the diagonal function. For example, f=1,v={q} representsX_q; [Z_qZ_r,X_q] creates a diagonal factor proportional toz_qz_r and therefore adds two function-dependence sites.

The proved bound and all recurrence coefficients/certificates remain valid by tracking the correct support of EACH local-term branch:

    S = deps(f) union supp(v),   for f(Z)X^v.

1. A nonzero driver commutator atq requires q∈deps(f)⊆S. Translation adds no dependence site; togglingv atq adds no union-support site. Thus a driver insertion does not enlargeS.
2. A nonzero diagonal one/two-site term must touchsupp(v)⊆S. Its diagonal multiplication may add both Pauli sites todeps(f), but at most one lies outsideS; v is unchanged. Thus it adds at most one UNION-support site.

Starting from an event on n original roots, afterd driver andm energy commutators,

    |S|≤n+m,    |deps(f)|≤n+m,    |v|≤d.

These are precisely the inequalities used by the word-majorant factors2(n+m)(1−u) and2d gE u. The recurrence, time-order integration, even tail, exact inequalities, computational results and all probability comparisons therefore change by zero. The generic n+j local-support bound is also unaffected.

The scientific child independently confirmed this correction. Preserve the frozen main/extension manifests and original text as evidence; this clarification supplies the precise proof rather than silently rewriting its provenance. No new numerical experiment is needed. It is an AI parent/child proof review, not a human expert intervention or fresh-agent failure.
