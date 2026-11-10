# A system-size-independent local-observable quantum remainder

This result applies to the same physical forward Hamiltonian and |+> initialization as QUANTUM_MOMENT_THEORY.md. It is separate from terminal equilibrium and the global original-optimum event. It gives a concrete finite-T guarantee for local observables, not just a formal Taylor coefficient.

Let O have support size s and operator norm at most1. At normalized time u, the sum of Hamiltonian-term norms incident on any one site is bounded by

    g(u)=1−u+u gE,
    gE=max_q(|h_q|+Σ_r|J_qr|).

Expand every nested Heisenberg commutator termwise over the one/two-site Hamiltonian terms. A nonzero next term must touch the current term's support; it adds at most one site. The incident-norm sum is at most(s+j)g(u) at step j, and ||[A,B]||≤2||A||||B||. Therefore the sum of norms of all order-k terms before time integration is at most

    2^k (s)_k Π_j g(u_j),
    (s)_k=s(s+1)...(s+k−1).

This argument tracks each nested LOCAL-TERM commutator, not the support of their sum. Internal-edge double counting is conservative. The scalar product Πg(u_j) is symmetric, so its ordered-simplex integral is (∫_0^1 g(u)du)^k/k!. With x=2|T|∫g=(1+gE)|T|, the absolute order-k expectation coefficient is bounded by(s)_k x^k/k!.

For real K(u), real initial density and real diagonal O, complex conjugation gives U(−T)=conj U(T), hence the real expectation is even in T. Its remainder after the exact T^4 coefficients is, for x<1, bounded by the positive even negative-binomial tail

    R_s(x)=[(1−x)^(−s)+(1+x)^(−s)]/2
                    −1−binom(s+1,2)x²−binom(s+3,4)x⁴.

For s=1, R_1=x^6/(1−x²). This bound depends on local incident strength, observable support and duration, not total physical spin count. It does not justify the same size-independent guarantee for a global feasible-optimum event.

## Actual unconditional original-cost certificate

Root-decoded cost is C_out=Σ_i w_i(1+Z_root_i)/2. Its constant cancels between programs. Uniform physical-spin averaging extracts the single-root Walsh coefficient of q2 and q4+q2²/2, giving exact coefficients c2,c4 for E[C_out]. For two actual binary64 programs A,B, treated as exact rational coefficients, a lower bound on mean-cost improvement of B is

    (c2_A−c2_B)T²+(c4_A−c4_B)T⁴
                  −(Σ_i|w_i|/2)[R_1(x_A)+R_1(x_B)].

Every spin is physical, including branch and auxiliary dynamics. No additional rounding correction is needed because the coefficient calculation uses Fraction(actual binary64) throughout. The optimum is never computed. local_forward.py evaluates the inequalities with exact rational arithmetic and returns inconclusive outside x<1 or without a positive lower bound.

For all48 ordinary fixed-coupling pairs, this certifies actual unconditional mean-cost improvement at a duration from the predeclared menu. The largest certified duration is.0125 or.025 (median.025); median calculation cost is174ms. These are substantially less restrictive durations than the global original-optimum norm bound. They certify a DIFFERENT observable. A lower unconstrained mean cost can occur by producing infeasible corrections, so it does not imply higher decoding success or solve the original issue.

Expected syndrome violations can likewise be written as a sum of parity Walsh observables of support equal to each row degree. The same R_s applies, but high check weight weakens the bound and feasibility of all rows is a joint event. This extension does not claim a cheap joint-decoding certificate from those local sums.

The parent and research child independently reviewed the commutator/time-order constants and observable scope. independent/local_forward_checks.py validates the coefficient/remainder relation against a separate adaptive ODE integrator on the already declared small physical anchors, including all negative/inconclusive comparisons.
