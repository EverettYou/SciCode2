# Can an Extra Measurement Improve Logical Recovery?

The logical value and noise robustness of an adaptive action in a finite D4 projector instrument

## 1. Research objective

Determine the logical value of a second measurement in the finite instrument below, and whether choosing an intervening action from the first public record gives a useful advantage over the best fixed action. Quantify how this comparison changes with second-readout noise, construct an executable adaptive policy, and explain which first-record features predict when adaptation matters.

The target is the original red-error chain's two binary homology labels under the full physical prior. A supported zero advantage or informative bound is acceptable. All strategies use the same finite geometry, initial state, action menu and two measurement stages. A compact treatment of this fixed instrument is needed; full Hilbert-space enumeration is not a required method.

## 2. Why this is unresolved

A second record can reveal private-error distinctions that do not change the most probable logical class. An action can also alter the second measurement law through the postmeasurement quantum state. A useful comparison must therefore combine the sequential Born law, full-prior logical inference and action selection, while distinguishing the information attainable in principle from the losses of a chosen policy and decoder. An information ordering or a selected private-error example does not quantify that comparison.

## 3. Fixed geometry and supplied input

The file `inputs/d4-instrument-v1.json`, also embedded as a PDF attachment, specifies one periodic finite geometry: 108 physical qubits, 36 star operators, 24 measured blue/green sites, and 36 red edges forming a connected honeycomb torus. Qubits and red edges have distinct explicit IDs. Binary arithmetic below is over $\mathbb F_2$ unless otherwise stated.

Each red edge lists its two measured endpoints. Their incidence matrix is $H\in\mathbb F_2^{24\times36}$. Twelve lists of face-edge IDs define the contractible face cycles. The input also supplies two noncontractible cycles $\gamma_1,\gamma_2$ and two logical masks $\Lambda_1,\Lambda_2$. The masks annihilate every face cycle and satisfy $\Lambda_i\cdot\gamma_j=\delta_{ij}$. Their exact labeling convention is fixed by the file.

For any red-edge vector $z$, define its two logical labels by

$$\ell(z)=(\Lambda_1\cdot z,\Lambda_2\cdot z).$$

For chains with the same boundary, these labels distinguish their four homology classes. A fixed extension to open chains is used only to label the inference target; recovery depends on the difference of chains.



## 4. Operators and initial state

For every star $u$, the input lists a six-qubit X support $F_u$ and six controlled-Z pairs $C_u$. Define the Hermitian involution

$$A_u=\left(\prod_{q\in F_u}X_q\right)\left(\prod_{(q,r)\in C_u}\mathrm{CZ}_{qr}\right).$$

The two supports in this product are disjoint. Each listed triangle $t$ has operator $B_t=\prod_{q\in t}Z_q$. The physical geometry includes all three star colors, even though only blue/green star outcomes are publicly measured.

The initial state is fixed, rather than left as a choice of ground sector. Let $u_1,\ldots,u_{33}$ be the ordered independent-star list in the input. Set

$$|\psi_0\rangle=2^{-33/2}\sum_{b\in\{0,1\}^{33}} A_{u_1}^{b_1}\cdots A_{u_{33}}^{b_{33}}|0\rangle^{\otimes108}.$$

The listed flip masks are independent. The orbit terms have distinct computational-basis supports; the state is normalized. All listed $A_u$ and $B_t$ stabilize this chosen state with eigenvalue $+1$. Star operators need not commute on arbitrary fluxful states. This compact state specification does not require materializing a $2^{108}$ state vector.

Independently on each red edge draw $E_e\sim\operatorname{Bernoulli}(p)$. Let $X(E)$ be the product of physical Pauli X operators at the corresponding red qubit IDs. The private premeasurement state is $X(E)|\psi_0\rangle$. There are no other physical faults or newly injected errors between the two stages. The physical prior is the full IID law on all 36 red edges, not a prior conditioned on a selected pair, low weight, or first record.

## 5. First public record

The exact flux syndrome is $s=HE$. At a measured site $v$ with $s_v=0$, measure $A_v$ projectively and record its eigenvalue $(-1)^{z_v}$. At a site with $s_v=1$, no charge outcome is measured; encode $z_v=0$ there. This public mask is already determined by $s$ and is not additional information. Conditional on the fixed flux, the eligible projectors commute.

For a supported first record $o_1=(s,z)$, define

$$M_s(z)=\prod_{v:s_v=0}\frac{I+(-1)^{z_v}A_v}{2}.$$

The first likelihood given $E$ is $\|M_{HE}(z)X(E)|\psi_0\rangle\|^2$. Retain the corresponding postmeasurement state; the next stage is not a fresh independent draw from a static fusion law.



## 6. Public action and second record

Construct a deterministic tree correction $c_T(s)$ using the input's ordered rooted spanning tree: process children before parents, placing a red-edge bit on the parent edge when the subtree syndrome parity is odd. All physical syndromes have even total parity, so $Hc_T(s)=s$.

Let $f_1,f_2$ be the two contractible cycles listed as `probe_cycles` in the input (face IDs 0 and 11). There are exactly four allowed actions, labeled $t=(t_1,t_2)\in\{0,1\}^2$:

$$a_t(s)=c_T(s)\oplus t_1f_1\oplus t_2f_2.$$

A fixed policy uses the same label $t$ for all first records; its physical correction still depends on $s$ through $c_T(s)$. An adaptive policy chooses $t=\pi(o_1)$ using only the first public record and known model parameters. Apply the physical operator $X(a_t(s))$. Every allowed action clears the red flux and has the same homology label as the tree correction; the menu varies the local deformation of the probing correction. Measure all 24 blue/green stars, now with ideal second eigenvalue record $y\in\{0,1\}^{24}$ and projector

$$M_0(y)=\prod_v\frac{I+(-1)^{y_v}A_v}{2}.$$

The joint ideal record likelihood for the selected action is exactly

$$P(z,y\mid E,a)=\|M_0(y)X(a)M_{HE}(z)X(E)|\psi_0\rangle\|^2.$$

The known first flux is always $HE$. Unsupported records have zero probability. Different actions may define different conditional second laws; their raw outcomes must not be exchanged between action branches.

Only the second charge readout is noisy: independently flip each ideal second bit with probability $\nu$, and give the decoder $\widetilde y=y\oplus\xi$, where $\xi_v\sim\operatorname{Bernoulli}(\nu)$. This is a classical report channel after the ideal second measurement. The first record remains exact. Study $0\leq\nu\leq1/2$, with $\nu=1/2$ as a control. The decoder receives the chosen action label, the two public records, and true $(p,\nu)$, but no private state, error support, ideal noisy-readout bits, or hidden fusion distinctions.



## 7. Logical target and comparable risks

The target is $\lambda=\ell(E)\in\{0,1\}^2$. A final output may be a label $\widehat\lambda$ or a total red-chain correction $c$ with $Hc=s$. For a correction, success means $\ell(E\oplus c)=(0,0)$. If the probing action has already been applied, the remaining correction is $c\oplus a$. These conventions share the same stipulated homology score; full encoded-state fidelity after measurement is outside this task.

For a supported first record, let $q_{1,\lambda}(o_1)=P(\ell(E)=\lambda\mid o_1)$ and $b_1(o_1)=1-\max_\lambda q_{1,\lambda}(o_1)$. For every possible action label $t$, use the conditional experiment in which that action is applied after $o_1$, including actions that a particular policy would not select. Define the logical posterior from the actual second report and the expected conditional risk

$$q_{t,\lambda}(o_1,\widetilde y)=P(\ell(E)=\lambda\mid o_1,t,\widetilde y).$$

$$b_t(o_1)=\mathbb E_{\widetilde y\mid o_1,t}[1-\max_\lambda q_{t,\lambda}(o_1,\widetilde y)].$$

For deterministic policies, the relevant Bayes risks are

$$R_1^*=\mathbb E_{o_1}b_1(o_1),\qquad R_{2,t}^*=\mathbb E_{o_1}b_t(o_1).$$

$$R_{2,\pi}^*=\mathbb E_{o_1}b_{\pi(o_1)}(o_1),\qquad R_{2,\mathrm{ad}}^*=\mathbb E_{o_1}\min_t b_t(o_1).$$

Randomized policies average over their action probabilities. All expectations include the full IID error prior and the physical measurement law. Report the second-record gain for each fixed action, and the additional information gain attainable by adaptation,

$$\Delta_t=R_1^*-R_{2,t}^*,\qquad \Delta_{\rm ad}=\min_t R_{2,t}^*-R_{2,\mathrm{ad}}^*.$$

If $R_{D,\pi}$ is the actual failure probability of an implemented policy and inference routine, distinguish its inference loss $R_{D,\pi}-R_{2,\pi}^*$ from policy regret $R_{2,\pi}^*-R_{2,\mathrm{ad}}^*$. Controlled intervals are allowed when an optimal reference is not exact. The identities define the comparison; evaluating them informatively under the full instrument is part of the research.

## 8. Scientific investigation

Develop a tractable inference method and an adaptive action rule using only public inputs at decision time. Determine or informatively bound the risks above, then compare the executable adaptive strategy with all four fixed policies under matched physical parameters, inference accuracy and evaluation resources. Charge policy development and reference computation separately from online decision cost. Simulated private labels may be used during policy training, but the final decision routines must not access private generation or scoring state.

Use $p=0.05$ at $\nu=0,0.05,0.10$ as the main noise comparison. Include $p=0$ and $\nu=1/2$ controls, and at least one additional physical rate to check the scope of the mechanism. Rates $p=0.02$ and $p=0.10$ are possible robustness points. These are finite-instrument comparisons, with no required positive advantage or threshold extrapolation.

Explain whether the extra information changes competition between homology classes or only distinguishes errors within a class. Identify public first-record features associated with an action preference or with the disappearance of an advantage as noise increases. Test a quantitative prediction on independently generated records or a parameter cohort reserved before tuning the policy and explanation. Report null and contradictory results. A policy that selects from noisy estimates must be evaluated independently of the data used to select it.

## 9. Verification and uncertainty

Check the supplied graph, face space, logical masks and tree convention. Establish controlled checks of the operator algebra, initial state, sequential likelihood normalization and logical-sector sums. The first-record law must be independent of an action chosen afterwards. The $\nu=1/2$ control makes the second reported bits independent of the ideal outcomes and supplies a check of the first-record-only Bayes limit.

Retain joint measurement correlations and the action-conditioned postmeasurement state. A product of single-site marginals or a fresh static fusion draw is valid only if its equivalence or approximation error is established. Second records from one action branch may not be reused as if drawn under a different action. Use independently controlled conditional cases to check the likelihood and logical posterior; then justify the full-prior weighting of the aggregate result.

Separate physical sampling uncertainty, likelihood/state approximation, policy regret and inference loss. If a controlled error-weight truncation is used, bound the omitted probability under the full IID prior. Every physical trial remains represented in an estimate or conservative interval. Failed reference calculations contribute unresolved mass, not invented Bayes errors. Missing or invalid outputs of an implemented decision routine count as actual failures.

An informative upper bound on a small advantage, a resolved gain, or a controlled unresolved comparison can each be valid. State what the evidence excludes and what would distinguish the remaining explanations. An isolated record, a formal information ordering or an unqualified numerical curve is insufficient.

## 10. Deliverables and resources

Submit a concise English report with the fixed-action and adaptive risks or informative intervals, noise dependence, policy and decoder losses, mechanism prediction and independent check, costs and limitations. Provide source, environment, seeds, stopping rules, sufficient data to reproduce the risk comparisons, and reproduction commands.

Expose `choose_action(first_record, p, nu, rng=None) -> label` and `infer_logical(first_record, action_label, second_report, p, nu, rng=None) -> two_bits`. Document ordering, randomness and any supporting posterior or bound interface. The geometry may be a public immutable model input; the routines otherwise accept only the specified public records and parameters.

Choose representations, state/likelihood methods, policy construction and uncertainty analysis appropriate to a scientific workstation. Declare a computational allowance before the principal comparisons, report actual memory and time, and explain whether the accuracy obtained supports the scientific conclusion. Internet and standard scientific libraries are allowed. No full state-vector computation, particular policy architecture or prescribed inference algorithm is required.

## Appendix. Supplied geometry file

The complete input `d4-instrument-v1.json` is embedded in this PDF as a file attachment and is supplied alongside the statement under `problem/inputs/`. Extract it with a PDF attachment tool, for example `pdfdetach -saveall problem.pdf`. The mathematical definitions in this statement and that file are the complete task specification. No private note or research repository is required.

All lists are ordered. Qubit IDs run from 0 to 107, measured-site IDs from 0 to 23, and red-edge IDs from 0 to 35. A vector bit is indexed by its corresponding ID. A list defining a mask or cycle contains the IDs of its nonzero bits.

| JSON field | Meaning |
| --- | --- |
| `measured_sites` | Site ID to star-center label mapping |
| `red_edges` | Red-edge ID, physical qubit ID, and the two measured endpoints |
| `stars` | Every star's center, color, X support, CZ pairs, and two Z-triangle supports |
| `independent_star_centers` | Ordered 33-star list in the initial-state definition |
| `face_cycles` | Twelve contractible red-edge cycles, indexed 0 through 11 |
| `logical_cycles` | The ordered noncontractible pair used to fix homology labels |
| `logical_masks` | The ordered pair of red-edge masks defining the target |
| `probe_cycles` | The ordered two face cycles defining the action labels |
| `tree` | Root, parent vertex and edge arrays, and ordered nonroot traversal |

In `tree`, the root is site 0 and its parent entries are null. Initialize a working parity array to $s$. For each vertex $v$ in `children_first_order`, put the current parity at $v$ on its parent edge and XOR it into the parent's working parity. All nontree edges receive zero. This defines the unique convention for $c_T(s)$; it is not a prescribed inference algorithm.

The file contains model definitions only: no likelihood tables, selected-error witnesses, reference decoder, policy, or numerical result. The specification uses a fixed finite instance rather than an unspecified scalable D4 lattice family.
