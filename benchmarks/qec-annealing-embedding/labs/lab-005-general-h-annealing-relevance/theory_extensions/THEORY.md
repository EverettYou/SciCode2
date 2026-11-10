# Relative original-error events in local finite-forward quantum dynamics

## Scope and outcome

This extension preserves the actual event F: the original roots decode to a
minimum-cost feasible error, counting all ties and allowing arbitrary compiler
auxiliary and branch excitations. It gives a rare-event-relative remainder for
ANY original-root event, then an inexpensive sufficient comparison for matched
objective amplification. It does not replace decoding success by expected cost.

The physical model remains K(u)=−(1−u)Σ_q X_q+uE(Z), u in [0,1], dimensionless
duration T, initial |+> on every active physical spin, and final computational
root readout. E has actual programmed one-site fields and pair couplers. Offsets
commute and are omitted. Arbitrary sparse binary H, dependent rows, finite signed
weights, feasible syndromes and tied optima are allowed. This is not a thermal
model, QPU estimate, adiabatic theorem or comparison between arbitrary mappings.

## 1. A uniform-diagonal norm that retains rare-event mass

Every operator on N physical spins has a unique displacement representation

    A = Σ_v f_v(Z) X^v,
    A[z,z xor v] = f_v(z).

Define the norm

    ||A||_U = Σ_v 2^(−N) Σ_z |f_v(z)|.

Triangle inequality follows componentwise. It is not asserted to be an operator
norm or invariant under arbitrary unitaries. The only properties needed are:

1. |<+|A|+>| ≤ ||A||_U, because X^v|+>=|+>.
2. Translations f(z)→f(z xor q) preserve its uniform L1 norm.
3. Multiplication by a diagonal Pauli character preserves that norm.

For a diagonal event projector P_F supported on n original roots,
||P_F||_U=P0=|F|/2^n. The ratio uses root patterns, not full physical ground states.
P0 is positive when a finite-cost feasible optimum exists; it need not be known
or computed by the evaluator.

For a single Hamiltonian Pauli term cP, each commutator obeys

    ||[cP,f(Z)X^v]||_U ≤ 2|c| E_uniform|f|.

For P=X_q this is the translated difference f(z xor q)−f(z). For diagonal
P=Z_a or Z_a Z_b, it is f(z)[P(z)−P(z xor v)]X^v. These elementary formulas prove
the bound directly, without an invalid multiplication/operator-norm argument.

## 2. Support-relative time-ordered remainder

Track EACH LOCAL-TERM BRANCH before summing. Initially f depends on the n roots
and v=0. A nonzero next local term must touch the current operator support; a
pair term adds at most one physical site. After j commutators its support is at
most n+j. Merging all terms first would destroy this support bound and is not
part of the proof.

Let gE=max_q(|h_q|+Σ_r|J_qr|), and g(u)=1−u+u gE. Summing incident Pauli-term
norms over a support S is at most |S|g(u); internal-edge double counting is
conservative. Hence the norm sum of order-k nested terms is at most

    P0 2^k (n)_k Π_j g(u_j),
    (n)_k=n(n+1)...(n+k−1).

The ordered-simplex integral of the positive symmetric scalar product is
(∫g)^k/k!. Therefore the absolute kth coefficient of Pr_T(F)/P0 is at most

    binom(n+k−1,k) (1+gE)^k.

For real K, real |+><+| and real diagonal P_F, U(−T)=conj U(T), so Pr_T(F) is
even. This remains true under time ordering; conjugation reverses no product.
For x=(1+gE)|T|<1, the relative remainder after T² is bounded by

    R_n,2(x)=[(1−x)^(−n)+(1+x)^(−n)]/2
                 −1−binom(n+1,2)x².

The denominator P0 cancels exactly. An operator-norm observable bound divided by
P0 would lose this property and be useless for rare decoding events. The present
bound depends on original readout support n rather than total N, but it is still
not size independent.

## 3. Sharper driver/diagonal word counts

The special form of K yields stronger low-order majorants. In a local-term
branch after d driver and m diagonal-energy commutators:

- |v|≤d, because only a driver term changes the flip displacement.
- f depends on at most n+m sites. A nonzero diagonal pair term touches v, hence
  an existing support site, and adds at most one new dependence site.
- A driver commutator is nonzero only where f depends on that site. Its total
  norm multiplier is at most 2(n+m)(1−u).
- A diagonal commutator only uses terms incident on v, so its multiplier is at
  most 2d gE u, rather than the whole functional support.

These are termwise counts, not support claims for a sum. Let B[d,m](u) majorize
the norm of all inner-later words at times in [u,1], divided by P0. Set B[0,0]=1
and out-of-range indices zero. Then

    B[d,m](u)=∫_u^1 {
       2(n+m)(1−v) B[d−1,m](v)
       +2d gE v B[d,m−1](v)} dv.

In the Heisenberg Dyson series, the inner Hamiltonians are later in time and
outer ones earlier. Thus the [u,1] orientation is essential. All integrands have
nonnegative scalar majorants. The implementation factors out gE^m and integrates
exact rational polynomials.

Any outermost driver commutator has zero |+> expectation, since each X_q has |+>
as an eigenstate. Only words with an outer diagonal term need remain. Their
relative kth expectation coefficient is bounded by

    C_k(n,gE)=Σ_{d+m=k,m≥1} ∫_0^1 2d gE u B[d,m−1](u) du.

The first inner term must be a driver; the factor d already makes the all-E
words zero. In particular,

    C_2 = n gE/6,
    C_4 = n³ gE/56 + n(35n+17)gE²/1260 + n gE³/168.

For comparison, the generic fourth-order bound scales as n^4(1+gE)^4. The mixed
word bound retains the distinction between energy and driver insertions.
It does not exploit every cancellation or connected-cluster identity.

Fix K=12 before evaluating outcomes. The refined relative remainder is

    R_word(T) = Σ_{k=4,6,...,12}
        min[C_k T^k, binom(n+k−1,k)x^k]
       +{[(1−x)^(−n)+(1+x)^(−n)]/2
           −Σ_{k=0,2,...,12} binom(n+k−1,k)x^k}.

All coefficients inside the final braces are nonnegative. Exact rational
arithmetic avoids subtractive rounding in this tail. Higher orders use the
proved generic bound; no unproved mixed-word infinite-series convergence is
assumed. The two-program remainder is the sum of their separate remainders.

## 4. Actual rounded objective-amplification comparison

The matched programs have identical active sites, roots, driver, couplers and
nonobjective fields. Their actual root-field difference is

    delta h_i = Δη w_i/2 + epsilon_i,
    Δη>0, rho=Σ_i|epsilon_i|,

all interpreted as exact rationals for the saved binary64 values. The known
second-order density coefficient is q2=LE/12, L=Σ_q[f(z^q)−f(z)]. Consequently,
for the original optimum event,

    delta a2 = Δη(Σ_i w_i−2C*)/12
                    −Σ_i epsilon_i E[Z_i|F]/6
             ≥ Δη D_lower/12−rho/6 = A_actual.

D_lower≤Σw−2C* is obtained from the parent's exact affine mean/variance bound
without solving weighted decoding: C*≤mu−Var/(U−mu), with the constant-cost case
handled separately. This extension reuses that proved input and does not claim
its discovery. All tied optima have the same C*, so their uniform mixture obeys
the same bound.

Unlike a generic Duhamel rounding estimate, rounding here is charged directly
to the exact T² coefficient. All higher coefficients are already bounded for
ACTUAL rounded programs, and their odd coefficients remain zero. No separate
linear-in-T rounding penalty is necessary.

Thus

    [Pr_new(F)−Pr_base(F)]/P0
       ≥ A_actual T²−R_base(T)−R_new(T).

A positive exact rational right side certifies strict actual original-error
optimum probability improvement at that finite duration. The event, P0, C* and
optimal error patterns are never enumerated by the certificate. If A_actual≤0
or the remainder dominates, return inconclusive. A positive guarantee is not
universal over all H/s/w; e.g. forced costly feasible bits can oppose the short
forward bias. Static ground-fidelity and hardware-range audits remain separate
prerequisites for using the programs as decoding implementations.

## 5. Costs and limits

For fixed K=12, scalar polynomial majorants depend only on n and are cached;
program-specific work computes actual local strengths and evaluates exact
rational inequalities on a dyadic menu. There is no Hilbert-space or 2^nullity
enumeration. Bit lengths and rational arithmetic costs are charged; constants
in exact output fractions can be large. Hexadecimal numerator/denominator
strings make the saved exact witnesses portable across JSON integer limits.

This improves conservative finite-time ORIGINAL-OPTIMUM guarantees, rather than
only local mean-cost guarantees. It still covers very early evolution, says
nothing about moderate-time interference or practical annealing success, and
retains system-size dependence through n. An increased certified duration is
not an increased absolute success probability claim: P0 itself can be tiny.

## 6. Corollary for different embeddings

The remainder applies separately to any two physical programs reading the same
original variables, even if N, branch sizes, contact locations and root labels
differ. Initial event mass P0 is the same. After uniform nonroot averaging,

    q2_root(e)=−Σ_i h_root_i Z_i/6
                 −Σ_{i<j} J_root_i,root_j Z_i Z_j/3.

Choose Δη>0 and subtract Δη(Σw−2cost)/12 from the difference of these root-only
polynomials. Restrict the residual Q to the affine feasible set. Its GF2 Walsh
constant minus the L1 norm of its nonconstant coefficients gives a pointwise
lower bound L_Q on every feasible error. Then

    delta a2_on_optimum ≥ Δη D_lower/12+L_Q.

Together with separate event-relative tails, this is a sufficient actual
optimum-event comparison across mappings without an optimum oracle. All source
fidelity/range/graph checks remain necessary. For the balanced compiler with
row degrees at least three, no source original-original couplings remain and
original-root fields contain only the objective; with root-local field
programming this reduces to logical alpha differences plus actual rounding.
Degree-one/two rows require retaining their root-only parity terms explicitly.

This corollary is not evaluated/promoted in the present extension. It identifies
how a certified early-time mapping loop could be implemented; it does not assert
ordinary-instance compactness gains or useful moderate-time comparisons.

## Appendix: explicit fourth-order word integrals

Write D/E words in inner-to-outer order. Only D-D-D-E, D-D-E-E, D-E-D-E and
D-E-E-E contribute to the majorant. Their ordered schedule integrals are,
respectively, 1/2688, 1/4480, 17/40320 and 1/2688. Their norm factors are
48n³gE, 64n²gE², 32n(n+1)gE² and 16ngE³. Multiplying and summing gives the stated
C4 exactly. These scalar integrals integrate the actual factors (1−u) for D and
u for E in the outer-earlier simplex; no unordered-word factorial is inserted.
