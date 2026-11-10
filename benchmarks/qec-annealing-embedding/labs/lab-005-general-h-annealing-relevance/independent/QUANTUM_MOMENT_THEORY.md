# Sparse quantum-forward readout moments for general H

## Scope and convention

Use exactly the full physical closed-system Hamiltonian K(u)=−(1−u)ΣX+uE(Z), u∈[0,1], total dimensionless duration T, and initial |+> on every physical spin. Computational bit b has z=2b−1. The readout is the declared original-variable roots; every other spin is unobserved, including other branch sites and reduction auxiliaries. E contains the actual programmed fields/couplings; its additive constant can be dropped. This is a quantum dynamical expansion, not a thermal model.

The coefficients below are exact algebraic results. Binary64 evaluation of them is a fast numerical implementation; it is not an interval proof. Their T^4 truncation has no useful moderate-time remainder certificate in this work. Parent FORWARD_THEORY.md gives a separate, conservative finite-time remainder for a different comparison.

## Linked expansion and local formula

Write ψ_z(u)=2^(−N/2)exp[iTN∫_0^u(1−v)dv+φ_z(u)]. The exact log-amplitude equation, on the analytic branch near T=0, is

    ∂u φ=−iTuE+iT(1−u)Σ_q(exp[Δ_qφ]−1),
    Δ_qf(z)=f(z^q)−f(z).

Let L=Σ_qΔ_q, B=Σ_q(Δ_qE)^2, C=Σ_qΔ_qE Δ_qLE, D=Σ_q(Δ_qE)^3. Expanding φ=ΣT^kφ_k gives

    φ1=−iE u²/2,
    φ2=LE(u³/6−u⁴/8),
    φ3=i[L²E(u⁴/24−7u⁵/120+u⁶/48)−B(u⁵/40−u⁶/48)].

The fourth derivative integrates

    φ4'=−(1−u)[L³E(u⁴/24−7u⁵/120+u⁶/48)
                         −LB(u⁵/40−u⁶/48)
                         −C(u⁵/12−u⁶/16)+D u⁶/48].

At u=1, real probability has only even powers, since changing T to−T complex conjugates the real-Hamiltonian evolution. Thus

    |ψ_z(1)|² / 2^(−N) = 1+q2(z)T²+[q4(z)+q2(z)²/2]T⁴+O(T⁶),
    q2=LE/12,
    q4=−L³E/1344+LB/2240+C/576−D/1344.

For pairwise E=Σh_q z_q+ΣJ_qr z_qz_r, q4 is a Walsh polynomial involving at most four spins within one physical star. The explicit star coefficients are implemented in forward_moments.expansion. Enumerating all stars costs O(N+|J|+Σ_q degree(q)^3), which is linear in physical program size for bounded-degree target hardware. The number of polynomial terms is of the same order. This counts arithmetic/hash operations: the current integer masks have O(N+n) bit lengths, so bit complexity and storage are not literally linear on unbounded targets. This is not exponential in physical Hilbert-space size.

fourth_order_checks.py independently obtains all time-polynomial Dyson coefficients of each small state amplitude by exact rational integration, then compares both probability coefficients on every basis state. It does not reuse the log-amplitude recursion. All24 arbitrary physical Ising models,278 total basis states, pass, including normalization through T^4.

## General-H affine averaging

For feasible H e=s, Gaussian elimination supplies e=e0+Vy over GF(2), with y uniform on the kernel parameters. An original root spin is z_i=(2e0_i−1)χ_{v_i}(y), where χ_a(y)=(−1)^(a·y). Each unobserved physical spin is an independent uniform character. A physical Walsh monomial therefore has a key (unobserved-spin mask, kernel character) and a sign. Group equal keys; the uniform-feasible expectation is exactly the coefficient at(0,0), and the expectation of the square is the sum of all grouped coefficients squared. No minimum-weight correction is computed.

Let a2=〈q2〉_F, a4=〈q4+q2²/2〉_F, μ=〈w·e〉_F. Then

    P_T(H e_out=s)=2^(−rank H)[1+a2T²+a4T⁴+O(T⁶)],
    E_T[w·e_out | H e_out=s]=μ+c2T²+c4T⁴+O(T⁶),
    c2=Cov_F(w·e,q2),
    c4=Cov_F(w·e,q4+q2²/2)−a2 c2.

The covariance with cost is evaluated by XOR shifts of grouped character keys. Additional cost is O(nP) hash operations for P polynomial groups, plus GF2 elimination; exact bitset operation cost depends on matrix dimensions. The implementation does not enumerate2^nullity feasible errors. Sparsity alone does not promise near-linear Gaussian elimination or a strong low-order prediction.

## Objective amplification: a universal coefficient comparison

Consider two programs with identical active spins, roots, driver, couplers and nonobjective fields, and objective field change Δη w_i/2 at each original root. Their exact q2 difference is

    δq2=Δη[Σ_i w_i−2(w·e_out)]/12.

Consequently

    δa2=Δη[Σ_i w_i−2μ]/12,
    δc2=−Δη Var_F(w·e)/6≤0.

Conditional optimum probability has relative T² coefficient improvement Δη(μ−C*)/6≥0. This latter identity contains the unknown optimum C*; the conditional-cost coefficient uses a variance computable by affine characters. Signed weights, zero weights, tied optima, dependent checks, irregular degrees and fixed coordinates are allowed. If Var_F(cost)>0 and Δη>0, analyticity implies strict conditional mean-cost improvement for sufficiently small positive T in the ideal exact coefficient model. If variance is zero the order is inconclusive. A conditional mean-cost improvement is not an unconditional original-optimum probability ordering.

In particular, a compiler whose nonobjective root-only parity terms are constant on F has c2=−α Var_F(cost)/6, if parity interactions on root-only subsets are constant on F and all other factors average to zero. This covers the balanced compiler used here. The48 matched ordinary-input program pairs verify the amplification identity to8.33e−17 numerical error; the23 balanced programs verify the latter identity to6.94e−18.

## Measured cost, anchors and limitations

quantum_moment_summary.json covers47 child main programs plus48 matched baseline/amplified pairs. Median moment evaluation is10–14ms, maximum118ms, with maximum15,719 q4 monomials. Times include affine moments and Python hash operations, exclude embedding search, and are measurements on this host rather than complexity guarantees.

forward_ode_audit.json independently integrates four representative n6 anchors, both programs, five durations(.05,.25,1,4,16). Adaptive DOP853 and the separate Strang backend agree on original-optimum probability within2.50e−6. Feasibility and conditional-cost predictions, including loss of accuracy/unphysical polynomial values, are retained. Agreement at a few anchors does not certify the expansion for larger H.

Low-order local dynamics can be blind to high-weight parity relations: if a root-only Walsh term is not in the row span of H its feasible expectation vanishes, and nonroot factors average to zero. T^4 cannot universally expose a high-order decoding constraint or control later coherent interference. A local-in-time formula is therefore a usable computational primitive, not the requested final practical finite-annealing criterion. The exploratory compactness-constrained mapping study explicitly labels its T^4 choices as heuristics pending useful remainder/transfer control.
