# Original-error thermal readout for general sparse-H quadratizations

## Scope and advance beyond Lab004

Lab004 controlled chain defects and conditioned full-QUBO-ground mass. Here the
readout event is explicitly a MINIMUM-COST FEASIBLE ORIGINAL ERROR, including
states with excited compiler auxiliaries. The declared dynamics/readout model is
terminal Gibbs equilibrium. No schedule/runtime/initial-state assumption is
asserted to imply that equilibrium, and no real-QPU or finite-time quantum
annealing comparison follows. The new objective is original-error distribution
fidelity under this explicit readout model, not another chain-consistency bound.

The methods accept any sparse binary H, finite signed additive weights and a
feasible syndrome; no named code family, rank assumption, geometry or maximum
column degree is required. Bounded row degree is needed only for the inexpensive
ordinary-compiler entropy audit; balanced-factor formulas have no such bound.
Compilation does not solve decoding. Exact reference enumeration is kept separate.

## 1. Why auxiliary entropy matters

For a standard intermediate XOR factor

    M(x+y-p-2a)^2,

valid triples x xor y xor p=0 have auxiliary energies{0,4M}. Invalid triples have
{M,9M} for001 and{M,M} for the other three odd triples. Thus valid local triples
are thermally balanced, but invalid triples are not. In a check chain, different
invalid-prefix paths can end at the same original parity; summing them can give
different auxiliary partition factors for original inputs of equal parity.
Therefore conditioning on the original syndrome does NOT in general produce
exact cost Gibbs sampling, even though all zero-temperature minima are faithful.
This explains why full-QUBO-ground and minimum-cost-original-error events differ.

For fixed original row bits b, sum the auxiliary spins by a two-state prefix
transfer. A transition from previous parity v to prefix p, consuming current bit
x, has factor

    T_x(v,p)=sum_{a=0,1} exp[-t M(v+x-p-2a)^2].

The first prefix is fixed by the first original bit. Multiply transitions for
all intermediate stages, then final factor exp[-tM(v xor x xor s)]. This gives
A_r(b;t) exactly in O(row degree) work for a given row assignment. The original
error Gibbs marginal is

    P(e) proportional exp[-t w·e] product_r A_r(e[row r];t),

where t=beta*alpha for exact uniform physical rescaling. This includes ALL
compiler excited states. Enumerating e costs2^n and is reference-only; auditing
all row factors costs sum_r O(d_r 2^d_r), inexpensive on bounded-row-degree H.

## 2. A thermally balanced quadratic XOR gadget

Let G be the four even flips of a three-bit tuple. Define

    B_M(x,y,p,a_G) = (M/4) sum_{g in G}
       [(x xor g1)+(y xor g2)-(p xor g3)-2a_g]^2.

Every term is quadratic because XOR with a fixed bit is affine. The four hidden
variables are independent. Visible-visible couplings and visible fields cancel
under the even-flip group average. The actual intermediate interaction graph
is K_(3,4), with hidden fields and no visible-visible edge; unused structural
square-expansion edges are not embedded.

For a valid visible triple, every copy has a unique zero-energy hidden choice,
so B=0 has a unique hidden extension. For an invalid triple, every copy has
minimum square residual1, so its minimum total energy is M. For a valid triple
with any wrong hidden variable, that copy costs M. Hence every nonzero whole
factor costs at least M. The construction is faithful with the SAME global
M>sum|w| penalty as the ordinary compiler; no gain is attributed to a stronger
unnormalized parity gap.

The group acts transitively on each parity class. Relabeling independent hidden
copies under that action proves the hidden partition factor depends only on
visible parity at EVERY t, not just at zero temperature. Explicitly, with
r=exp(-tM), its valid/invalid factors are

    a=(1+r)^4,       b=8r(1+r^2).

For valid triples all four hidden excitations have energy M. For invalid triples
three hidden bits are free and one excitation costs2M, with base energy M.
Importantly, the invalid factor has an entropy8. Thermal balance is not free:
it can weaken effective parity suppression and adds three hidden bits per
intermediate gate. No novelty/priority claim is made for gauge symmetrization
or parity representation; the contribution is its rigorous integration and
resource-accounted evaluation in this decoding pipeline.

A degree-d>=2 check uses d-2 intermediate gadgets and the ordinary final parity
factor. Summing prefix/hidden variables gives two row factors(V,I), initialized
at(1,r) for the final factor, and updated d-2 times by

    (V,I) <- (aV+bI, aI+bV).

Equivalently, V/I is determined by the product of binary parity transmission
ratios. Since a-b=(1-r)^4>=0, V>=I and the effective soft-syndrome penalty
kappa_r=log(V/I)>=0. Degree-one rows have(V,I)=(1,r); empty feasible rows cost0.
The balanced original-error marginal is EXACTLY

    P_bal(e) proportional exp[-t w·e-sum_r kappa_r 1{(He)_r!=s_r}].

Conditioning on He=s therefore yields exactly exp(-t w·e) on the affine feasible
set, independent of row dependence, row order, column degree or syndrome values.
The possible degeneracy of minimum-cost errors is fully retained. In particular,
if g_F(t) is their probability in the intended feasible cost Gibbs law, then

    g_F'(t)=g_F(t)(<w·e>_feasible-C*)>=0.

This is an actual ORIGINAL-ERROR conditional decoding ordering. It differs from
Lab004's ordering of full-QUBO-ground mass. It still does not order unconditional
readout unless feasibility/chain-defect contributions are also controlled.

Compiler size: ordinary intermediates use one prefix plus one carry; balanced
intermediates use one prefix plus four hidden variables. Total variables are
n+2 sum_r(d_r-2)_+ versus n+5 sum_r(d_r-2)_+. Actual edges per intermediate are
6 versus12, with shared endpoint interactions/cancellations accounted in the
saved graph. Both construction times and output sizes are O(n+m+nnz(H)).

## 3. General-H syndrome repair and a probability bound

This subsection reuses the parent agent's independently developed verified
right-inverse implementation, saved in independent/penalty_bound.py and hashed
in source provenance. It is scientific collaboration, not a blind agent test.
Choose independent original rows R and columns B so H[R,B] is invertible.
Let Delta_j be column j of that inverse, lifted to original coordinates B.
Then H[R,:]Delta_j is the unit vector j and, because R spans the row space,
H Delta(v)=v for every residual v in imH, where
Delta(v)=xor_{j in R:v_j=1} Delta_j. This identity is checked exactly over GF(2).
Let L_j=sum_{i in Delta_j}|w_i|. For any error e, repair it to

    e*=e xor Delta(He xor s).

It is feasible and its cost increase is at most sum_{j:v_j=1} L_j. The mapping
(e*,v_R)↔e is bijective between the feasible affine space times2^rank(H)
residuals and all original errors. This does not require a decoding optimum.

For a soft-parity Gibbs law with nonnegative kappa_r, the weight ratio of e to
its repaired e* is at most

    exp[sum_{j in R:v_j=1}(t L_j-kappa_j)],

because nonbasis row penalties are nonnegative and can be discarded. Summing
the bijection gives the cheap original-syndrome certificate

    P(He=s) >= product_{j in R}[1+exp(t L_j-kappa_j)]^(-1).

The bound uses independent original rows, not fictitious independent detector
statistics. It remains valid with dependent rows and arbitrary signed weights.
For balanced compilation, kappas come from the closed recurrence above. The
calculation is O(rankH) after the GF2 repair witness; its usefulness is explicitly
measured rather than inferred from positivity.

## 4. Ordinary-compiler entropy envelope

For each nonempty row, compute min/max of logA over valid assignments and max
logA over invalid assignments. Let

    R_r=max_valid logA-min_valid logA,
    kappa_r=max_valid logA-max_invalid logA,      R=sum_r R_r.

Conditioned on the original syndrome, log auxiliary weight varies by at most R.
A positive likelihood multiplier whose log range is R changes an arbitrary base
probability law in TV by at most tanh(R/4). To prove it, bound the absolute
centered multiplier by its endpoint chord, then maximize over its mean; the
maximum occurs at the geometric mean of its two endpoint values and equals
(sqrt(b)-sqrt(a))/(sqrt(b)+sqrt(a)). Therefore the ordinary conditional feasible
original-error law is within delta_aux=tanh(R/4) of intended cost Gibbs.

For any e and its repaired e*, the auxiliary weight ratio is bounded by
exp[R-sum_r kappa_r v_r]. Dropping a negative nonbasis kappa adds the conservative
constant N=sum_{r notinR} max(0,-kappa_r). Excluding the zero residual before
summing yields

    Z/Z_feasible <= 1+exp(R+N)
       {product_{j in R}[1+exp(t L_j-kappa_j)]-1}.

Its reciprocal lower-bounds syndrome feasibility. It reduces to the balanced
product bound when R=N=0. Negative kappa or high entropy can make the certificate
inconclusive; this is reported, not hidden. Empty feasible rows are omitted.

## 5. From physical consistency to actual original-error readout

Both compilers are embedded on the same target with all reduction/chain
coefficients and signed coupling-group ranges charged. Reuse Lab004's physical
tree-repair certificate. Let epsilon_chain bound any broken branch. Conditioned
on consistency, the logical Gibbs law is exact up to the final rationally audited
coefficient perturbation. Compose distributions as follows: root decode to
original e, condition on He=s, then compare with intended feasible cost Gibbs.
The total variation is at most

    min(1, epsilon_chain+epsilon_syndrome+delta_aux+delta_rounding).

For balanced compilation delta_aux=0 identically. Also, minimum-cost feasible
ORIGINAL-ERROR readout probability is at least

    (1-epsilon_chain) P_feasible_lower max(0,g_F(t)-delta_aux),

again with the explicitly audited rounding correction. g_F may be expensive to
compute; the certificate exposes a monotone reference family rather than
pretending to solve decoding. On tractable original n, exact enumeration gives
g_F and the actual projected readout reference. The multiplicative bound is
preferred when additive TV is too weak for a rare optimum event.

Numerical comparisons hold target, coefficient ranges and declared beta fixed.
Extra hidden variables, qubits, search failures and evaluation costs remain
separate. A balanced conditional law can be scientifically exact yet perform
worse unconditionally because it weakens feasibility or uses smaller alpha.
No finite-time annealing ordering follows from these endpoint statements.

## 6. Precision and limitations

Authoritative compiler coefficients are exact rationals for finite binary64
input weights/penalty. Balanced algebra uses M/4 exactly. Actual physical
binary64 programs receive Lab004's rational range/repair/ground-state audits;
terminal law comparisons allow their nonconstant coefficient L1 perturbation.
Stable log transfers avoid cancellation/underflow. Ordinary row enumeration
returns inconclusive above degree20 in this implementation. Saved floating
exponentials are numerical evaluations of proved formulas; independent review
owns outward/interval checks where strict probability comparisons are claimed.

Repair-witness preprocessing uses bitset Gaussian elimination and does not
solve decoding. Its column basis is selected greedily by |w| as a linear-matroid
minimum-weight basis, but minimizing the worst repair-column load is not claimed.
The certificate can remain conservative or vacuous, particularly at small beta,
large n, dense right inverses or large auxiliary entropy. Resource failures of
minorminer are search failures unless a separate count obstruction is given.

## 7. A limitation for late-hold local dynamics

Consider a DECLARED CLASSICAL model of a terminal Gamma=0 hold: random-scan
single-site heat-bath updates, selecting one of Nphysical sites uniformly per
attempt, at fixed beta. Its reversible stationary law is physical Gibbs.
This is not coherent quantum evolution and is not asserted to model a device's
bath. It tests the thermalization assumption needed by endpoint conclusions.

For any nonsingleton original-variable branch, let S be states with its root
spin+1 and let B be states where that branch breaks. Any root-flip transition
has at least one endpoint in B. Split directed S→S^c flow into transitions with
broken starts and transitions with consistent starts/broken ends. Reversibility
charges the latter to broken root− starts, disjoint from broken root+ starts.
Each state has at most1/N total root-update rate, so

    Q(S,S^c) <= P(B)/N.

The indicator test function in the Poincare variational formula gives

    gap <= Q(S,S^c)/[p(1-p)] <= epsilon_branch/[N p(1-p)].

No independence assumption is used. For the balanced compiler, choose a verified
kernel vector v with v_i=1. The map e→e xor v preserves every row parity, so all
soft-syndrome factors are unchanged. Its objective changes by at most
L(v)=sum_{j in v}|w_j|. Pairing states gives logical original-bit marginal bounds

    logistic(-t L(v)) <= p_i <= logistic(t L(v)).

Physical root marginal differs by at most the global chain/rounding TV bound.
If a=logistic(-tL(v))-epsilon_chain-delta_rounding>0, then
p(1-p)>=a(1-a) and

    gap <= g_upper=epsilon_branch/[N a(1-a)].

The algorithm uses verified fundamental kernel vectors from the saved repair
basis, choosing the lowest absolute-weight support among those containing i;
it does not solve minimum-weight-codeword optimization. Singleton branches,
fixed bits and nonpositive a return inconclusive.

Random-scan heat-bath is an average of conditional-expectation projections and
has spectrum in[0,1]. For a nonconstant eigenfunction, worst-case TV after k steps
is at least(1/2)(1-gap)^k. Thus if0<g_upper<1, its worst-case mixing time toTV1/4
is at least log2/[-log(1-g_upper)] attempted updates, divided by N for sweeps.
These are LOWER bounds on worst-case mixing time, not lower bounds on decoding
failure or comparisons of actual spectral gaps. An upper gap bound getting
weaker does not prove improved mixing. Coherent or collective updates can evade
this local-update obstruction and are outside the theorem.
