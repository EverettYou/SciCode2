# What Drives the Gain from Directional Noise?

Physical logical-risk contributions, directional bias, and inference error on growing square patches

## 1. Research objective

Determine whether, and through which population of public records, direction bias changes optimal logical recovery in the bounded-current channel below. At the common activity rate $p=0.30$, resolve how much of a risk difference comes from changes in typical logical-sector gaps and how much comes from the probability and severity of ambiguous records. Determine whether the proposed mechanism also explains the behavior of a practical charge-informed decoder.

The target is a controlled finite-size mechanism comparison with a prediction tested on reserved data. A mixed mechanism, a supported absence of improvement, or an informative unresolved crossover is acceptable. The question does not assume monotonic improvement with field: changing the field changes the physical prior, rather than adding information to the same experiment.

## 2. Why this is unresolved

A large median posterior gap can coexist with appreciable logical risk concentrated in a small set of ambiguous records. Approximate inference may further distort that tail or create an apparent field trend. The scientific challenge is to control the physical weighting of these records, separate intrinsic risk from decoder loss, and obtain an explanation that predicts a new size or field comparison. A gap fit or a statistical-mechanics analogy alone cannot establish that connection.

## 3. Geometry and logical recovery

For integer $L\geq3$, the vertices are $(i,j)$ with $0\leq i,j\leq L-1$. Retain all horizontal edges $((i,j),(i+1,j))$, and retain vertical edges $((i,j),(i,j+1))$ only for $1\leq i\leq L-2$. Edges are undirected for binary errors. The two rough boundaries are the columns $i=0$ and $i=L-1$. All other vertices are measured detectors. No observation is made at either rough boundary.

There are $2(L-1)^2$ retained edges and $L(L-2)$ detectors. Interior detectors have degree four; detectors on the top and bottom have degree three. No vertical boundary edge is an error variable. The shortest left-to-right logical path has $L-1$ edges.

Let $H$ be the detector-edge incidence matrix over $\mathbb F_2$. Let $\Gamma_R$ contain exactly the retained edges meeting the right rough boundary. For any binary edge vector $z$, define

$$\ell(z)=\bigoplus_{e\in\Gamma_R} z_e.$$

A decoder returns a binary correction $c$ on the retained edges. On binary activity vector $x$, it succeeds exactly when $Hc=Hx$ and $\ell(x\oplus c)=0$. Exact reconstruction of $x$ is unnecessary. Array ordering is your choice, but must be documented and exposed by the callable interface.



## 4. Physical prior and public record

Orient horizontal edges toward increasing $i$ and vertical edges toward increasing $j$. Independently on every retained edge, draw $j_e\in\{-1,0,+1\}$ with

$$\Pr(j_e=0)=1-p,\qquad \Pr(j_e=\pm1)=\frac{p e^{\pm h}}{2\cosh h}.$$

The link field satisfies $0\leq h<\infty$; at $h=\infty$ use probabilities $(1-p,p,0)$ for $(0,+1,-1)$. At $h=0$ the two nonzero currents are equally probable.

Define $x_e=\mathbf1\{j_e\ne0\}$. The physical edge-activity rate is $p$ at every field.

Let $D$ be the integer incidence matrix on measured detectors, with $-1$ at the tail and $+1$ at the head of an edge. The complete public record is the exact signed interior charge vector

$$Q=Dj,\qquad s=Q\bmod2=Hx.$$

No charge is measured at a rough boundary. The decoder is told $(G_L,p,h,Q)$ and receives no currents, activity bits, unmeasured boundary charges, or microscopic histories. The signs of $Q$ are part of the record. There is only one observation round and no charge readout error.

Compare $h=0$, at least two finite fields chosen to distinguish your proposed mechanisms, and $h=\infty$, all at $p=0.30$. For reference, $h=\tfrac12\log9$, $\tfrac12\log(47/3)$ and $\tfrac12\log(97/3)$ correspond to positive-current probabilities $0.90$, $0.94$ and $0.97$ conditional on activity; these are possible comparison points, not a required sweep. Include a lower-noise control at some $0<p\leq0.05$. Declare the selected fields and size coverage before interpreting the main results.

## 5. Logical-sector posterior and physical average

For a supported public record $Q$, define two absolute logical-sector weights

$$Z_\lambda(Q)=\sum_{j:Dj=Q,\ \ell(\mathbf1\{j\ne0\})=\lambda}\prod_e w_{p,h}(j_e),\qquad \lambda\in\{0,1\},$$

where $w_{p,h}$ is the edge law in Section 4. Set $q_\lambda(Q)=Z_\lambda(Q)/(Z_0(Q)+Z_1(Q))$. A logical Bayes decoder selects the more probable sector and returns a correction of that sector with syndrome $s$. A correction need not reconstruct the signed current.

Define

$$\Delta F(Q)=\log\frac{Z_0(Q)}{Z_1(Q)},\qquad G(Q)=|\Delta F(Q)|.$$

If one sector has zero mass, set $G=\infty$ and its conditional Bayes risk to zero. Unsupported records do not enter a physical average. The optimal unconditional risk is

$$R_L^*(p,h)=\mathbb E_{Q\sim P_{L,p,h}}\left[\frac{1}{1+e^{G(Q)}}\right].$$

The expectation is under the record distribution generated by the experiment. Conditional records, uniform record counting, selected low-charge records, and squared record probabilities define different averages.

## 6. Required mechanism comparison

Construct a method for logical-sector probabilities or controlled intervals and validate it independently on small square patches. Investigate increasing square patches, including sizes beyond direct whole-current enumeration. A narrow strip can be a check but cannot substitute for the square-patch question. A valid exact reduction is acceptable and should be justified rather than excluded.

For each principal field, determine or informatively bound the unconditional Bayes risk and the distribution of $G$. Quantify both the frequency of ambiguous records and their contribution to risk. One way to make the distinction precise is to report, for declared finite gap cutoffs $g$,

$$P_L(g;p,h)=\Pr(G\leq g),\qquad C_L(g;p,h)=\mathbb E_Q\left[\frac{\mathbf1\{G\leq g\}}{1+e^G}\right].$$

Together with gap quantiles and total risk, these quantities distinguish the fraction of records in a tail from the risk that tail carries. You may use other justified diagnostics that make the same comparison testable. Explain what counts as typical and rare in your analysis and how that choice affects the conclusion. Do not force an exclusive typical-versus-tail answer when both contribute.

Compare at least one executable practical decoder with the controlled Bayes reference on the same public records. Its physical risk $R_{D,L}$ counts every invalid or missing correction as a failure. Report the algorithmic excess risk $R_{D,L}-R_L^*$, or bounds on it, separately from the directional change $R_L^*(p,0)-R_L^*(p,h)$. These quantities address different explanations of a practical decoding trend.

## 7. Prediction, uncertainty and verification

State plausible competing mechanisms and give a quantitative prediction that distinguishes them. Fix the principal inference and analysis choices before evaluating at least one reserved size or finite-field cohort. Report the result even if the prediction fails. An explanation should account for physical risk and record populations, not only fit a single risk curve.

Independently check the microscopic prior, incidence signs, logical sector sums and normalized conditional probabilities on tractable cases, including zero sector mass. Check any claimed mapping against the exact bounded-current channel and rough-boundary score. Methods sharing a numerical approximation do not automatically provide independent validation.

Account for physical sampling uncertainty, reference-inference error and finite-size interpretation separately. Rare-event sampling or conditioning is allowed if its weighting is derived and its error controlled. Numerical failures in a reference calculation must retain their physical probability mass as unresolved uncertainty; they are not Bayes failures and may not be silently discarded. Submitted decoder failures remain physical failures. Pointwise posterior convergence without control of its effect on the mean risk or lower tail is insufficient for a mechanism claim.

An unresolved asymptotic interpretation can be a useful result when supported by informative bounds or finite-size constraints and a discriminating prediction. A thermodynamic transition, critical exponent or universal scaling law is not required. Report which explanations the evidence excludes and which remain consistent with it.

## 8. Scope, resources and deliverables

The physical prior, public signed-charge record, square geometry and binary logical target above are fixed. You choose the inference method, sizes, finite fields, estimators, analytical bounds and diagnostics. Plan a study feasible on a scientific workstation, state the computational allowance and stopping rules before the main comparisons, and charge decoder tuning and reference calculations as well as final evaluation. Report actual time, memory and randomness.

Submit a concise English report with risks or informative intervals, gap-population contributions, practical-versus-intrinsic comparison, reserved prediction check and limitations. Supply source, environment, public input generation, seeds, data sufficient to recompute the physical averages, and reproduction commands.

Provide `decode(graph, p, h, Q, rng=None) -> correction` and a documented sector-posterior estimator or bound routine. Specify array ordering, orientation and incidence signs, supported-record conventions, zero-mass handling, and whether uncertainty is certified or empirical. Only the declared public graph, parameters and charge record may enter a decision routine; private currents and errors belong to generation and scoring. Internet and standard scientific libraries are allowed.
