# How Much Fusion Information Does Decoding Need?

Four-valent SU(2) readout, binary compression, and practical logical recovery

## 1. Scientific objective

A local symmetry measurement can distinguish error configurations that have the same parity syndrome. Recording its complete outcome costs more than recording one herald bit. Determine the logical-recovery cost of that compression on a square lattice, and determine how much of the available information a scalable decoder can actually use.

Your principal result must be a quantitative map of the difference between full-irrep and binary-herald recovery over $0\leq p\leq1$ and $0\leq\eta\leq1$, supported by increasing lattice sizes. Identify where compression is harmless within resolved accuracy, where it has a measurable cost, and what the finite-size evidence supports about recovery as the lattice grows. A demonstrated loss on a single special observation is not sufficient.

The model below is a stipulated classical noise-and-observation channel motivated by SU(2) fusion. Conditional independence of its local readouts is part of the definition. Deriving a microscopic joint quantum measurement is outside this task.

## 2. Geometry and logical recovery

For integer $L\geq3$, the vertices are $(i,j)$ with $0\leq i,j\leq L-1$. Retain all horizontal edges $((i,j),(i+1,j))$, and retain vertical edges $((i,j),(i,j+1))$ only for $1\leq i\leq L-2$. Edges are undirected for binary errors. The two rough boundaries are the columns $i=0$ and $i=L-1$. All other vertices are measured detectors. No observation is made at either rough boundary.

There are $2(L-1)^2$ retained edges and $L(L-2)$ detectors. Interior detectors have degree four; detectors on the top and bottom have degree three. No vertical boundary edge is an error variable. The shortest left-to-right logical path has $L-1$ edges.

Let $H$ be the detector-edge incidence matrix over $\mathbb F_2$. Let $\Gamma_R$ contain exactly the retained edges meeting the right rough boundary. For any binary edge vector $z$, define

$$\ell(z)=\bigoplus_{e\in\Gamma_R} z_e.$$

A decoder returns a binary correction $c$ on the retained edges. On error vector $x$, it succeeds exactly when $Hc=Hx$ and $\ell(x\oplus c)=0$. Exact reconstruction of $x$ is unnecessary. Array ordering is your choice, but must be documented and exposed by the callable interface.

<!-- pagebreak -->

## 3. Noise and complete local readout

Independently on each retained edge, draw $x_e\sim\operatorname{Bernoulli}(p)$. At each detector define $n_v=\sum_{e\ni v}x_e$ and measure the exact syndrome $s_v=n_v\bmod2$.

Every incident active edge contributes a spin one-half leaf. A local readout $J_v$ is drawn from the following normalized distribution, independently across detectors conditional on $x$:

| Incident count $n_v$ | Distribution of total spin $J_v$ |
| --- | --- |
| 0 | $J=0$ with probability $1$ |
| 1 | $J=1/2$ with probability $1$ |
| 2 | $J=0$ with probability $1/4$; $J=1$ with probability $3/4$ |
| 3 | $J=1/2$ with probability $1/2$; $J=3/2$ with probability $1/2$ |
| 4 | $J=0$ with probability $1/8$; $J=1$ with probability $9/16$; $J=2$ with probability $5/16$ |

Draw independent masks $a_v\sim\operatorname{Bernoulli}(\eta)$, independent of $x$ and of the readout randomness. If $a_v=0$, the irrep result is not retained. The observed mask is known to the decoder. An absent result is a known missing measurement, not a measured singlet or a negative herald. There are no false readouts, syndrome errors, or additional rounds.

## 4. Three records from the same experiment

Each trial supplies the following nested records. Compare them on matched physical errors, readout outcomes, and masks.

| Record | Decoder-visible information |
| --- | --- |
| $O_0$ | Exact syndrome $s$ only |
| $O_1$ | $s$, mask $a$, and retained bit $b_v=\mathbf1\{J_v>s_v/2\}$ |
| $O_2$ | $s$, mask $a$, and retained total-spin label $J_v$ |

For $a_v=0$, write a missing marker in place of $b_v$ or $J_v$. All measured zeros are included. The binary compression rule is fixed by the definition above; optimizing a different compression rule is not required. Both enriched decoders are told the same true $p$ and $\eta$. No decoder receives $x$, $n_v$, unretained readouts, pairings, or fusion histories. Boundary counts and irreps remain unmeasured.

<!-- pagebreak -->

## 5. Required scientific investigation

For a stated decoder family $D_k$ using $O_k$, measure the unconditional logical error rate

$$R_{D_k}(L;p,\eta)=\Pr[Hc\ne s\ \mathrm{or}\ \ell(x\oplus c)=1].$$

Define $R_k^*(L;p,\eta)$ as the minimum possible rate among decoders restricted to $O_k$. The information cost of the specified compression is

$$\Delta_{\mathrm{comp}}(L;p,\eta)=R_1^*(L;p,\eta)-R_2^*(L;p,\eta).$$

The algorithmic cost for a chosen record is $R_{D_k}-R_k^*$. These quantities concern logical recovery, not accuracy of individual edge beliefs. The optimum selects a logical class, rather than necessarily the most probable complete error configuration.

Develop a computational approach that can distinguish the compression cost from decoder approximation. Establish independently checked optimal logical risks on small patches or another rigorously controlled subset. Extend to genuinely two-dimensional sizes beyond that exact-check regime with a reproducible decoder family. You may use exact inference, controlled contraction, sampling, hybrid methods, or another justified approach. Quantify the limits of any reference or approximation used to interpret the larger sizes.

Produce a two-dimensional summary in $(p,\eta)$ of full versus compressed recovery and its uncertainty, together with selected quantitative size-dependent sections. Resolve whether the available evidence indicates only a finite-size penalty, a persistent practical penalty, or different recovery boundaries; keep these conclusions distinct. A decodable phase means the stated family's logical error rate tends to zero as $L$ grows. Any transition estimate must be supported by size dependence, not one crossing or one low failure count. An unresolved boundary is an acceptable scientific conclusion when accompanied by informative constraints and a clear explanation of what remains unresolved.

Select sizes, parameter samples, reference checks, and resource allocation yourself. The supplied model does not prescribe a decoder or scaling ansatz. Explain why your design can detect the effect you report and why an apparent absence of an effect is informative at the achieved precision.

<!-- pagebreak -->

## 6. Evidence and trustworthiness

Validate geometry, logical sectors, normalized readout likelihoods, and the decoder's input boundary. Check $\eta=0$, $\eta=1$, $p=0$, and a syndrome-only baseline of the same geometry. On exact or controlled cases, verify both class probabilities and the returned logical decision. Show how the independent small-system check differs from the production inference implementation.

Retain every attempted trial in its unconditional denominator. An exception, missing output, or invalid correction is a failure. Report numerical failures and convergence diagnostics separately; do not postselect on readout patterns or successful inference. If approximate references cannot resolve $\Delta_{\mathrm{comp}}$, report a supported interval or bound rather than attributing all observed differences to measurement information.

Separate sampling uncertainty, finite-size uncertainty, and inference approximation. Changing the readout model, masking law, lattice geometry, or logical loss does not constitute a matched comparison. State the meaning of interpolated regions in every map.

## 7. Deliverables and resources

Submit a concise scientific report with the information-cost map, increasing-size evidence, interpretation, and limitations. Supply raw or sufficient numerical data, source, an environment specification, and commands reproducing every reported table and figure.

Provide documented callable decoders for all three records, of the form `decode(graph, p, eta, record, rng=None) -> correction`, together with a graph constructor and array conventions. If posterior estimates or risk bounds support a claim, expose a documented way to recompute them. Randomness must be explicit and reproducible.

Design a study feasible on a scientific workstation. Justify the chosen sizes and precision against the available computational resources. Report actual resources, seeds, and stopping rules. Internet access and standard scientific libraries are allowed; essential model information is contained in this statement. No particular numerical threshold or algorithm is required for success: assessment concerns model fidelity, inference validity, informative evidence about compression, practical logical recovery, and reproducibility.
