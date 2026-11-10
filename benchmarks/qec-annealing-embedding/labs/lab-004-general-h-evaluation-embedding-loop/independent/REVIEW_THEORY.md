# Independent review: local quantum Gibbs correction

This review is a derivation and independent numerical check, not a claim about finite-time annealing or a QPU output distribution. It supports the researcher-selected terminal thermal model. It is not a replacement for routine-instance evaluation and guidance tests.

## Rooted-tree repair inequality

Consider a physical branch C with a ferromagnetic tree, root r, chain energy `-sum_e K_e Z_u Z_v`, and external absolute loads `a_q=|h_q|+sum_{s outside C}|J_qs|`. Root fields may be arbitrary. For every tree edge e oriented away from r let L_e be the sum of a_q in its descendant subtree. Put delta_e=K_e-L_e. Repair a classical branch configuration by setting every branch spin to its root value. Each external term changes by at most its absolute load times the spin difference. The triangle inequality along the root-to-q path gives

`H(z_C)-H(z_root-consistent) >= 2 sum_{wall edges e} delta_e * I`

as an operator inequality on the outside Hilbert space. Terms driving or coupling outside spins cancel; no outside classical-state assumption is needed. With all branch transverse drivers removed, its spin configurations label blocks of the Hamiltonian. Each root and tree-wall subset uniquely labels a branch configuration. By min-max eigenvalue ordering, the trace of the exponential of a wall block is at most `exp(-2 beta sum delta_e)` times that of its corresponding consistent block. This uses trace monotonicity, not an invalid assertion that the operator exponential is operator-monotone.

Consequently, for the Hamiltonian H0 with only this branch's driver removed,

`Pr_H0(branch broken) <= 1 - product_e (1+exp(-2 beta delta_e))^(-1)`.

Negative margins make this bound loose, not false. The static ground-consistency conclusion requires positive margins. The endpoint all-branch classical bound can be obtained by successive repairs, with uniform loads bounding each step. Its quantum version must be derived separately; it must not silently reuse the classical global product bound.

## Local transverse-field Gibbs perturbation

Write H=H0+V, where `V=-sum_{q in C} Gamma_q X_q` and `v=||V||=sum_q |Gamma_q|`. Let F be the broken-branch projector and `U=product_{q in C} Z_q`. H0 and F commute with U; UVU=-V. Therefore both `N(lambda)=Tr F exp[-beta(H0+lambda V)]` and `Z(lambda)=Tr exp[-beta(H0+lambda V)]` are even functions of lambda.

In the Dyson expansion, Schatten Holder bounds each integrated order-n numerator contribution by `Z(0)*(beta*v)^n/n!`. Odd orders vanish. Thus

`N(1) <= N(0) + Z(0)*(cosh(beta*v)-1)`.

The partition function is convex and even, so `Z(1)>=Z(0)`. It follows that

`Pr_H(F) <= Pr_H0(F) + cosh(beta*v)-1`.

This argument does not require commuting outside spins, a global spectral gap, a known logical optimum, or a special H. It assumes a Gibbs state at a declared beta. Capping at one is understood.

A separate linear bound follows from the Gibbs derivative

`rho'(lambda)=-beta integral_0^1 rho^s (V-<V>) rho^(1-s) ds`.

Holder gives `||rho'||_1<=2 beta*v`; because the derivative is traceless, any effect's expectation changes by at most `beta*v`. One can use the minimum of this correction and `cosh(beta*v)-1`. The researcher's independent Pinsker-based `sqrt(beta*v)` alternative is also safe, although weaker in some ranges. None of these bounds is an equilibration or finite-runtime theorem.

Applying the local bound to each branch and a union bound gives an upper bound on any chain defect. It need not equal the sharper global classical product bound plus corrections without an additional proof. A better upper bound does not by itself order two actual defect probabilities or decoded success rates.

## Independent dense validation

`quantum_gibbs_check.py` imports no research evaluator. It creates 30 frustrated 4–7-qubit physical Ising models, including paths/stars, nonzero signed fields/couplings, and nonzero drivers on outside spins. For 270 beta/local-driver cases, exact dense thermal diagonalization verifies the repaired-block bound, local cosh correction, linear correction, and nondecrease of the partition function. 222 upper bounds are below one. These are floating numerical cross-checks of the mathematical argument, not rigorous eigensolver error certificates or broad-instance performance evidence. The first execution passed the scientific assertions but failed JSON serialization of a NumPy integer; the integer conversion was corrected and the full script rerun successfully.

## Numerical and scientific cautions

A final implementation should audit the margins of the actual programmed coefficients, rather than ideal pre-rounding coefficients. Direct `cosh(x)-1` loses relative accuracy at small x and can become zero; a certified implementation needs an outward-safe enclosure. Subtree-load and physical-range arithmetic likewise need error control for numerical certificate claims.

The model must state its beta, energy normalization and remaining transverse field. It does not assume an actual annealer has thermalized at that beta, and no finite-time anneal or decoding improvement follows solely from its chain-consistency guarantee. Ordinary sparse-matrix and compactness tests, equal-budget controls, and cost accounting are still necessary to close the research loop.
