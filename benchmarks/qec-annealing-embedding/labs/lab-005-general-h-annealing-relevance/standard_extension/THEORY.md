# Necessary-optimality bounds without an optimum oracle

The physical/event model is unchanged from the parent's certified mapping study:
standard-|+> initialization, K(u)=−(1−u)ΣX+uE(Z), final original-root readout, and
the event of a minimum-cost feasible ORIGINAL error (all ties; arbitrary compiler
and chain excitations). This extension only improves the lower bound on the
actual second-order event coefficient. It does not replace the event by cost.

## General feasible characters

For arbitrary binary H and feasible s, exact GF2 elimination gives

    e(y)=e0 xor Vy,    y in GF2^k.

Write each original spin as Z_i=(2e0_i−1)χ_{a_i}(y), where
χ_a(y)=(−1)^(a·y). Thus the original cost is

    C(y)=mu+Σ_{a≠0} c_a χ_a(y).

Fixed coordinates and signed/zero weights are included in mu and c. Let U* be
ANY proved upper bound on the unknown minimum C*: the parent's affine-moment
bound, the exact cost of e0, or the cost of a verified feasible witness. No
claim that a feasible witness is optimal is necessary or permitted.

For any two actual physical programs read to the same original variables,
uniform nonroot averaging gives the exact second-order difference polynomial

    f(y)=delta q2_F(y)=a0+Σ_{a≠0} a_a χ_a(y).

The root-only coefficients are extracted directly from actual binary64 fields
and root-root couplers as exact Fractions: −h_i Z_i/6 and −J_ij Z_i Z_j/3.
Unobserved branch/auxiliary terms average to zero at this order. Root labels,
branch sizes and total physical spin counts may differ. The final event's
initial mass P0 depends only on original optimal patterns and is the same.

## Necessary optimality inequalities

For any selected nonzero parameter move t, a global optimum obeys
C(y xor t)−C(y)≥0. Character multiplication therefore proves

    Σ_{a:a·t=1} c_a χ_a(y)≤0.

The implementation includes fundamental moves t=unit_j, then all parameter
pairs unit_i xor unit_j. These are polynomially many necessary conditions,
not a global optimization oracle. They apply to every tied optimum, even if a
separate feasible witness is not locally optimal or hits its search cap.

For any nonzero a,b,c=a xor b, characters obey χ_c=χ_aχ_b. The convex hull of
(χ_a,χ_b,χ_c) is described by the four valid inequalities

    −x_a−x_b−x_c≤1,
    −x_a+x_b+x_c≤1,
     x_a−x_b+x_c≤1,
     x_a+x_b−x_c≤1.

Only triples induced by original-coordinate character pairs whose XOR is already
present are included. There is no exponential character closure or claim that
these facets describe all feasible character vectors.

Together with Σc_a x_a≤U*−mu and −1≤x_a≤1, these inequalities define a relaxation
containing every unknown optimal error character vector and any mixture of ties.

## Exact dual lower certificate

Collect the selected necessary inequalities as A x≤b. For ANY nonnegative
multipliers nu, and every actual optimum,

    f(y)≥a0−nu·b−Σ_a |a_a+(nu^T A)_a| = L2(nu).

Indeed f+nu·(Ax−b)≤f, and minimizing the left expression over the box gives the
formula. This proof does not require the numerical LP to be optimal, its primal
solution to be feasible, or any near-zero residual to be ignored.

HiGHS proposes multipliers from the numerical LP's inequality marginals.
Nonnegative binary64 multipliers are converted to exact rational values; negative
proposals are clipped to zero. All remaining coefficients are charged in the
exact L1 box minimum. The saved witness identifies every nonzero multiplier by
constraint ID. Earlier valid bounds are retained by taking their maximum, so a
weak numerical proposal never invalidates a previously proved lower bound.

The parent's one-dimensional cost-only Lagrange bound is a special case. Exact
breakpoint maximization of it is retained as a mechanism control under both
improved upper witnesses.

## Composition with the actual event certificate

The parent's exact physical fourth-order polynomial supplies a pointwise
feasible lower bound L4. The proved relative word-majorant tails bound the
remainder beyond T4 separately for both programs. Hence

    [P_candidate(opt)−P_first(opt)]/P0
      ≥ L2 T²+L4 T⁴−R_candidate,>4−R_first,>4.

The extension reuses the parent's EXACT stored lower gaps and updates them by
(L2_new−L2_old)T². This changes no fourth coefficient, physical program, event,
duration, tail or resource condition. All ordinary decisions use exact rational
positivity. Candidate selection is smallest N≤FIRST among strict certificates,
then greatest exact proved lower gap, then original seed; fallback FIRST.

For an upper bound on actual second-order difference, apply the same relaxation
to −f and negate its lower bound. A nonnegative upper bound is inconclusive.
No adverse actual ordering was proved in this study.

## Feasible witnesses and computational scope

The zero-search witness is the already computed affine particular solution e0.
Its original error is directly checked against H/s and its cost summed exactly.
The searched witness uses 16 fixed feasible kernel starts, then best-improving
fundamental/pair kernel descent, capped at4n accepted moves per start. Every move
stays feasible. The best visited error is a valid cost upper witness regardless
of local termination; it is not asserted optimal. No ordinary reference optimum
or planted generator error is consulted.

The implementation forms exact Fraction values of finite signed binary64 weights
and scales them by the LCM of their denominators. This supports arbitrary finite
binary64 weights, not only quarters. Measured instances have small dyadic
weights; large denominator/numerator bit lengths can substantially increase
integer/rational work. Arbitrary-real exact weights and arbitrary-precision
input formats are not claimed by the JSON interface. LP proposals use floating
arithmetic, but the returned bound is checked algebraically in exact arithmetic.

Basis/pair move enumeration and selected triangle construction are polynomial;
GF2 preprocessing, numerical LP cost and exact bit complexity are not promised
linear in general H. The ordinary suite measures n16/32/64 and bounded target
hardware. Only the small validation suite enumerates optima, explicitly separated
from ordinary construction/selection.
