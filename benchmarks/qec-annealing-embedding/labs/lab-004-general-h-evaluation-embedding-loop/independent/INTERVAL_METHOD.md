# Independent Gibbs-mass interval validation

This validation is separate from candidate construction and selection. It imports neither the compiler nor the evaluator. It uses the declared dyadic weights and unchanged sequential-XOR model, not a named code geometry. It is exponential in the number of original error mechanisms and is not the low-cost evaluation algorithm.

## Partition function and events

Enumerate all original errors e. For each row and fixed original bits, sum every prefix/carry assignment using a two-state prefix-parity transfer matrix. A transition from a to p with next original bit b has weight `sum_{carry=0,1} exp[-t M(a+b-p-2 carry)^2]`. The final original bit applies the syndrome-parity penalty. Multiply the row partition factors, then the original objective weight. This sums ALL auxiliary excitations, not only their minimizing configurations.

Normalize original costs by their unconstrained minimum Cmin to keep exponential arguments nonpositive. For `t=beta*alpha`,

`Z'(t)=sum_e exp[-t(C(e)-Cmin)] product_rows Z_row(e,t)`.

Ground degeneracy g0 is counted among feasible original errors of minimum cost E0. Each has exactly one zero-penalty auxiliary completion, so the full-QUBO ground mass is `g0 exp[-t(E0-Cmin)]/Z'`. The optimal-original-error mass instead sums each optimal error's entire auxiliary partition factor. These events are distinct; the latter is not generally monotone in t.

## Numerical enclosure

Quarter-integer original costs are accumulated exactly in int64 within the declared bounded n16 inputs. For every exponential constant, the exact exponent is a Fraction formed from the actual binary64 alpha and integer beta, weights and penalties. A 70-digit Decimal enclosure with directed division and adjacent Decimal exponential values encloses the true real exponential; conversion to binary64 is also directed. Every positive transfer/product addition is rounded outward using the adjacent binary64 value. Positive final sums use a conservative gamma_N rounding envelope with N=65536 and machine epsilon (larger than the unit roundoff). Finally ratios are rounded outward.

A separate eight-bit full-state enumeration, evaluated with 60-digit Decimal arithmetic, checks both the QUBO-ground and decoded-error-optimum intervals. These enclosures rely on the standard correctly rounded elementary binary64 operations and Decimal's documented correctly rounded exponential; no empirically estimated integration tolerance is used.

## Physical comparisons

For each actual programmed candidate, the independent witness audit supplies an outward defect bound u and a nonconstant consistent-polynomial coefficient error rho relative to alpha times the intended logical model. The conditional Gibbs-law total-variation correction is bounded by beta*rho. Thus chain-consistent full-model optimum probability is enclosed by

`[(1-u)*max(0,g_lower-beta*rho), min(1,g_upper+beta*rho)]`.

If the guided candidate's lower bound exceeds the reference's upper bound, this is a strict terminal-equilibrium comparison for that event, not merely a better upper bound. Root-decoded original-error optimum uses its separately summed error-optimum mass; an upper bound must additionally include u for broken-chain outcomes. The initial validation implementation used the wrong ground/error event in that upper bound; it was corrected before interpretation and rerun. No root-decoded improvement is inferred from the strict ground-readout comparisons.

No logical ground truth is used during mapping selection. The large ordinary suite establishes construction/evaluator coverage; this smaller subset provides the more expensive probability-validation evidence. Neither comparison supplies an equilibration, finite-time forward-anneal or QPU-performance theorem.
