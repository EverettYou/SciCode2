# A computable original-optimum quantum certificate across embeddings

## Event and assumptions

Use the exact full physical forward model and original-root readout defined in the report. The event F is e_out∈S*, the minimum-cost FEASIBLE original-error set, including ties. Every other physical spin is unobserved; excited auxiliaries and broken branches are included whenever the roots decode correctly. Two programs may have different physical size, couplers, roots or embeddings. Their uniform initial event mass P0=|S*|/2^n is identical. It is not computed during selection.

The [relative-event theorem](../theory_extensions/THEORY.md), with the [union-support proof clarification](PROOF_CLARIFICATION.md), bounds each program's normalized event probability remainder using a translation-invariant uniform-diagonal L1 norm. It retains P0, so no rare-event division is lost. The schedule-aware driver/energy word recurrence bounds even orders6..12; the proved generic local-support tail bounds higher orders. This work adds physical-program-specific T²/T⁴ event coefficients and a low-cost mapping decision.

## Exact projected fourth coefficient without finding S*

For each actual program, calculate exact rational q2 and log-probability q4. The fourth density coefficient is p4=q4+q2²/2. An affine parametrization of H e=s maps each original root spin to a signed GF2 kernel character. Each unobserved spin has its independent uniform physical character. Group the q2 polynomial by(unobserved mask, kernel character), yielding polynomials g2_u in the kernel variables; group q4 similarly.

Uniformly averaging ALL unobserved spins leaves

    p4_F = g4_0 + (1/2)Σ_u(g2_u ⋆ g2_u),

where⋆ is XOR convolution of GF2 characters. This is a pointwise polynomial in feasible original errors, not just a feasible average. For candidate-minus-baseline difference δp4_F=b0+Σ_{k≠0}bkχk, define

    L4=b0−Σ_{k≠0}|bk|.

Every feasible error has δp4_F(e)≥L4, hence so does the uniform mixture over the UNKNOWN optimum set. No minimum-weight decoding or optimal-error enumeration is required. Exact grouping must preserve fractions; the earlier floating-point grouped() routine is not used here.

The polynomial construction uses local-star algebra, GF2 elimination and groupwise convolution. Convolution can be quadratic in group size; it is not claimed universally linear. Wide integer character masks and rational bit lengths carry additional costs. On these physical sparse graphs the groups remain modest.

## Cost-constrained second-order lower bound

Likewise δq2_F=a0+Σakχk. Feasible cost is μ+Σckχk and a cheap affine-moment bound supplies C*≤U*. For anyλ≥0 and optimal error,

    δq2_F(e)≥δq2_F(e)+λ(cost(e)−U*)
             ≥a0+λ(μ−U*)−Σ_{k≠0}|ak+λck| = L2(λ).

The first inequality uses cost(e)=C*≤U*. The second bounds each character in[−1,1]. The right side is concave piecewise linear inλ. Its exact maximum is attained at0 or a nonnegative breakpoint−ak/ck. No maximum at infinity is omitted: its final slope isμ−U*−Σ|ck|≤0, because μ−Σ|ck|≤C*≤U*. A zero slope produces a flat tail reached at a finite breakpoint or0. Zero/signed weights, rank deficiency, dependent checks, fixed coordinates and tied optima are allowed.

For pure objective amplification this includesλ=Delta_eta/6 and reproduces the earlier second-order optimum bound. For different embeddings it additionally accounts for actual root-field and root-root-coupler differences. There is no need to pretend that logical scale alone determines q2.

## Finite-time certificate and algorithm

Let L2=maxλL2(λ), and let R_A,>4(T),R_B,>4(T) be the proved separate relative event tails beyondT4. Then

    [Pr_B(F)−Pr_A(F)]/P0
       ≥L2 T²+L4 T⁴−R_A,>4(T)−R_B,>4(T).

A positive exact rational value proves a strict actual original-optimum probability improvement at that common finite duration. It does not estimate the unknown absolute probability or claim a useful effect size. Static fidelity, graph validity and ranges are separate prerequisites.

Given H,s,w and a target/programming specification, compile a faithful model, search a fixed automatic candidate pool, construct actual physical programs, compute the affine witness and coefficient bounds, and select the smallest candidate within the baseline qubit cap whose finite-time comparison is positive. Otherwise return the baseline or inconclusive. Representation and candidate generation are separable from the certificate. The implementation accepts generalH and returns meaningful bounds only where its sufficient conditions permit.

## Independent checks and ordinary-input evidence

[event_projection_checks.py](event_projection_checks.py) independently integrates exact time-polynomial Dyson amplitudes on24 arbitrary small physical program pairs with different physical sizes/root locations. All2,688 basis states,352 projected coefficients and24 adaptive-ODE original-optimum event inequalities pass. Optima are enumerated ONLY for validation; the tested algorithm receives no answer. The child independently reviewed the grouping, convolution, Lagrange sign/breakpoint argument and cross-size event normalization. Explicit D/E-word enumeration independently agrees with all18 tested recurrence coefficients.

For48 fixed-coupler repaired-penalty pairs, the T4-specific event certificate proves45 strict orders, same3 inconclusive cases as the original curvature theorem. Largest certified dyadic duration is.00390625–.03125, median.0078125, median2048× larger than the original global-norm proof and8× larger than the word-only proof. Median evaluation is177ms, maximum766ms. This improves a proved time regime, not measured absolute success.

The mapping study preserves each compiler and its global penaltyM, and uses all375 successful candidates from47 main models:24 standard,23 balanced. One balanced model failed every search and another has seven successful candidates; both failures remain recorded. There is no new minor search or repaired-penalty amplification in this comparison.

At the predeclared primaryT=1/1024, the balanced model has17/23 certified mapping changes,15 strict qubit reductions and mean4.075% qubit reduction across all23. The standard model has0/24 certified changes over the entire declared duration menu. This is inconclusiveness, not proof that no standard mapping is better. The selected balanced relative advantage lower bounds range3.06e−12–6.18e−8, median2.62e−10. For unknownP0 as small as one optimal pattern/2^64, absolute guaranteed gains can be extraordinarily small.

AtT=1/64 there are4/23 balanced certified changes and3 smaller mappings; at1/256 there are14 changes and12 smaller mappings. The full common-duration frontier is retained. Total criterion work on375 candidates is34.67s, median0.608s per eight-search pool; programming adds5.90s, with standard saved reconstructions reused. Total45.32s includes serialization/audits. These are host measurements, not worst-case complexity guarantees.

## What is and is not closed

This establishes a genuine early-time theory-guided COMPACT MAPPING loop for ordinary generalH within the balanced compiler, with actual original-optimum event comparisons. It is stronger than comparing only equilibrium, mean cost or an unbounded Taylor proxy. It is not a practical general decoding solution: the balanced compiler costs about twice the physical qubits of the standard one, time is very early, bounds are tiny, standard-compiler selection is inconclusive, and no moderate-time/live-device transfer is established. The pools are reused exploratory data, not a new held-out confirmation or difficulty trial.

## Subsequent controls, preserved separately

The zero-search cost of the already computed feasible particular solution tightens47/48 programming upper bounds and certifies48/48 finite-event orders, median largest duration.015625. Earlier45/48 results remain frozen. The separate standard_extension/ necessary-optimality LP proves1/24 compact standard changes with this cheap upper witness and3/24 with charged bounded feasible search; all larger standard inputs remain inconclusive. These later controls do not overwrite the cost-only mapping study or change its early-time/tiny-effect interpretation.
