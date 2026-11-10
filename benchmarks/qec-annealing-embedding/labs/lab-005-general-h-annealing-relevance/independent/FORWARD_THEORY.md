# Parent branch: a standard-initial-state short-forward-anneal comparison

This branch addresses the finite-forward-model gap explicitly. The result is a rigorous but generally VERY SHORT time interval, not practical-time or adiabatic superiority. It is separate from the terminal-Gibbs claims.

## 1. General measurement expansion

Let H(u)=-(1-u)sum_q X_q+u E(Z) on N physical spins, start in |+>^N, and evolve for total dimensionless duration T. Fix any computational-basis readout event F. Time ordering gives, at basis state z,

    Pr_T(z) = 2^-N [1+(T²/12)sum_q(E(z^q)-E(z))]+O(T^4).

One direct derivation writes D=-sum X and integrates the second Dyson coefficient: integrals DD=EE=1/8, DE=1/24 and ED=5/24. The amplitude's first-order term is imaginary. Combining its modulus square with the second-order term leaves the neighbor-energy difference above. Odd probability coefficients vanish because every Hamiltonian matrix is real and changing T to -T conjugates the solution. This is the full forward anneal, not an encoded-state pause.

## 2. Matched physical programs with amplified original objective

Consider two physical programs with identical nonobjective fields, all couplings, active spins, branches and root readout, differing only by

    E_1(z)-E_0(z) = (eta_1-eta_0)/2 sum_i w_i z_(root i) + constant,
    eta_1>eta_0.

Let F be original-error feasibility AND minimum original cost C*, counting ALL auxiliary/chain states whose original roots decode to such an error. At T=0 its mass is P0=g*/2^n. Terms outside original roots cancel, and every optimal error has sum_i w_i z_i=2C*-sum_i w_i. Hence

    [Pr_1(F)-Pr_0(F)]/P0
      = (eta_1-eta_0)(sum_i w_i-2C*) T²/12 + O(T^4).

All hidden-variable, chain and penalty effects cancel from this difference at second order. The statement is family-independent, includes ties, and uses the standard |+> initialization. It does NOT prove monotonicity at longer T or for arbitrary changes of embedding/couplings.

The parent repair-penalty method supplies a natural matched change: preserve the physical penalty scale k and all chain/contact coefficients, while raise objective eta from k/(W+1) toward k/(C+1). Hardware field limits and actual static fidelity must be audited again. Reusing fixed roots matters; independently rerooting can change the scored event. This is a programming improvement on a fixed embedding, not a qubit-count gain.

## 3. Cheap bound on C* without decoding

Parameterize the affine feasible set by ANY GF2 particular solution plus a kernel basis. This is linear algebra, not weighted decoding. For uniform feasible errors, group coordinates by their nonzero kernel characters. A coordinate with zero character is fixed. Let mu be the uniform feasible mean of w·e. If a group has character a and reference signs z_i^0, its contribution to variance is

    Var = (1/4)sum_(nonzero characters a)(sum_(i:character_i=a) w_i z_i^0)^2.

Different nonzero GF2 characters are orthogonal under the uniform kernel parameter. A cost upper bound is U=sum_fixed w_i e_i^0+sum_varying max(0,w_i). Bhatia-Davis follows directly from (C-C*)(U-C)>=0 and gives

    C* <= mu-Var/(U-mu), when U>mu.

If U=mu the cost is constant and C*=mu. Therefore D_lower=sum_i w_i-2[mu-Var/(U-mu)] is a cheap lower bound on the short-time advantage coefficient. Signed/zero weights and fixed coordinates are handled explicitly. If D_lower<=0, return inconclusive rather than assuming every feasible set has mean sumw/2. If every coordinate varies, mu=sumw/2 and nonzero variance gives a positive bound.

Kernel characters come from the saved right inverse plus nonbasis columns; no minimum-cost error is computed during evaluation. Costs are bitset linear algebra plus rational group sums, polynomial in input size and precision.

## 4. Explicit finite-T and floating-program bounds

Drop global energy offsets. Let Lambda=(N+sum|h|+sum|J|)/2. The row-sum matrix norm bounds the time-integrated Hamiltonian. Every amplitude Dyson coefficient is bounded by 2^(-N/2)Lambda^k/k!, so the probability coefficient at order k is bounded by 2^-N(2Lambda)^k/k!. Summing over F and retaining even terms gives a relative remainder

    R(T) <= cosh(2Lambda T)-1-(2Lambda T)^2/2
         <= (2Lambda T)^4 / [24(1-(2Lambda T)^2/30)],

for (2Lambda T)^2<30. The last bound is a positive geometric bound on the even Taylor tail, avoiding cancellation.

An amplified rational ideal field may need binary64 rounding. If its nonconstant coefficient L1 error is rho, an infinity-norm Duhamel bound from the uniform initial amplitudes gives event probability error at most

    P0 * T rho exp(2Lambda_max T)
       <= P0 * T rho/(1-2Lambda_max T),

for 2Lambda_max T<1. Here the perturbation ramps as u*deltaE, so its integrated row norm is T*rho/2; the factor2 in the probability difference cancels that half. A generic constant perturbation would require an extra factor2. This relative bound avoids losing the rare-event factor P0. Consequently a strictly positive rational lower bound

    Delta_eta*D_lower*T²/12 - R_0(T)-R_1(T)
       - T*rho/(1-2Lambda_max*T) > 0

certifies the ACTUAL rounded amplified program's original-error success exceeds the baseline at that finite T. Lambda_max covers ideal and rounded programs. The computation does not need P0, C*, a state vector or a global spectral gap.

The resulting interval is expected to be extremely conservative and can be operationally negligible for large programs. Positive curvature or a tiny certified T is not evidence of a useful moderate-time decision rule. The numerical extension below tests wider times and retains reversals.
