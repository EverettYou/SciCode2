# Can an Extra Measurement Improve Logical Recovery?

Action-conditioned readout in a finite D4 projector instrument

## 1. Scientific objective

A second measurement may distinguish private errors without distinguishing the logical classes that matter for recovery. A correction applied between measurements can also change which information becomes visible. Determine the logical value of the second public record in the finite D4-inspired quantum instrument specified below, and determine whether choosing the intervening action from the first record improves that value.

The target is inference of the original red-error chain's two binary homology labels. It is not reconstruction of every private fault, full encoded-state fidelity, a fault-tolerance threshold, or an unspecified repeated-round channel. All comparisons must use the same physical prior and the same two measurement stages. The supplied operator supports are part of the problem input; no other research files are needed.

## 2. Fixed geometry and allowed input

The file `inputs/d4-instrument-v1.json`, also embedded as a PDF attachment, specifies one periodic finite geometry: 108 physical qubits, 36 star operators, 24 measured blue/green sites, and 36 red edges forming a connected honeycomb torus. Qubits and red edges have distinct explicit IDs. Binary arithmetic below is over $\mathbb F_2$ unless otherwise stated.

Each red edge lists its two measured endpoints. Their incidence matrix is $H\in\mathbb F_2^{24\times36}$. Twelve lists of face-edge IDs define the contractible face cycles. The input also supplies two noncontractible cycles $\gamma_1,\gamma_2$ and two logical masks $\Lambda_1,\Lambda_2$. The masks annihilate every face cycle and satisfy $\Lambda_i\cdot\gamma_j=\delta_{ij}$. Their exact labeling convention is fixed by the file.

For any red-edge vector $z$, define its two logical labels by

$$\ell(z)=(\Lambda_1\cdot z,\Lambda_2\cdot z).$$

For chains with the same boundary, these labels distinguish their four homology classes. A fixed extension to open chains is used only to label the inference target; recovery depends on the difference of chains.

<!-- pagebreak -->

## 3. Operators and initial state

For every star $u$, the input lists a six-qubit X support $F_u$ and six controlled-Z pairs $C_u$. Define the Hermitian involution

$$A_u=\left(\prod_{q\in F_u}X_q\right)\left(\prod_{(q,r)\in C_u}\mathrm{CZ}_{qr}\right).$$

The two supports in this product are disjoint. Each listed triangle $t$ has operator $B_t=\prod_{q\in t}Z_q$. The physical geometry includes all three star colors, even though only blue/green star outcomes are publicly measured.

The initial state is fixed, rather than left as a choice of ground sector. Let $u_1,\ldots,u_{33}$ be the ordered independent-star list in the input. Set

$$|\psi_0\rangle=2^{-33/2}\sum_{b\in\{0,1\}^{33}} A_{u_1}^{b_1}\cdots A_{u_{33}}^{b_{33}}|0\rangle^{\otimes108}.$$

The listed flip masks are independent. The orbit terms have distinct computational-basis supports; the state is normalized. All listed $A_u$ and $B_t$ stabilize this chosen state with eigenvalue $+1$. Star operators need not commute on arbitrary fluxful states. This compact state specification does not require materializing a $2^{108}$ state vector.

Independently on each red edge draw $E_e\sim\operatorname{Bernoulli}(p)$. Let $X(E)$ be the product of physical Pauli X operators at the corresponding red qubit IDs. The private premeasurement state is $X(E)|\psi_0\rangle$. There are no other physical faults or newly injected errors between the two stages. The physical prior is the full IID law on all 36 red edges, not a prior conditioned on a selected pair, low weight, or first record.

## 4. First public record

The exact flux syndrome is $s=HE$. At a measured site $v$ with $s_v=0$, measure $A_v$ projectively and record its eigenvalue $(-1)^{z_v}$. At a site with $s_v=1$, no charge outcome is measured; encode $z_v=0$ there. This public mask is already determined by $s$ and is not additional information. Conditional on the fixed flux, the eligible projectors commute.

For a supported first record $o_1=(s,z)$, define

$$M_s(z)=\prod_{v:s_v=0}\frac{I+(-1)^{z_v}A_v}{2}.$$

The first likelihood given $E$ is $\|M_{HE}(z)X(E)|\psi_0\rangle\|^2$. Retain the corresponding postmeasurement state; the next stage is not a fresh independent draw from a static fusion law.

<!-- pagebreak -->

## 5. A public action and the second record

Construct a deterministic tree correction $c_T(s)$ using the input's ordered rooted spanning tree: process children before parents, placing a red-edge bit on the parent edge when the subtree syndrome parity is odd. All physical syndromes have even total parity, so $Hc_T(s)=s$.

Let $f_1,f_2$ be the two contractible cycles listed as `probe_cycles` in the input (face IDs 0 and 11). There are exactly four allowed actions, labeled $t=(t_1,t_2)\in\{0,1\}^2$:

$$a_t(s)=c_T(s)\oplus t_1f_1\oplus t_2f_2.$$

A fixed policy chooses one label $t$ for every first record. An adaptive policy chooses $t=\pi(o_1)$ using only the first public record and known model parameters. Apply the physical operator $X(a_t(s))$. Every allowed action clears the red flux and has the same homology label as the tree correction; the menu varies the local deformation of the probing correction. Measure all 24 blue/green stars, now with ideal second eigenvalue record $y\in\{0,1\}^{24}$ and projector

$$M_0(y)=\prod_v\frac{I+(-1)^{y_v}A_v}{2}.$$

The joint ideal record likelihood for the selected action is exactly

$$P(z,y\mid E,a)=\|M_0(y)X(a)M_{HE}(z)X(E)|\psi_0\rangle\|^2.$$

The known first flux is always $HE$. Unsupported records have zero probability. Different actions may define different conditional second laws; their raw outcomes must not be exchanged between action branches.

Only the second charge readout is noisy: independently flip each ideal second bit with probability $\nu$, and give the decoder $\widetilde y=y\oplus\xi$, where $\xi_v\sim\operatorname{Bernoulli}(\nu)$. This is a classical report channel after the ideal second measurement. The first record remains exact. Study $0\leq\nu\leq1/2$, with $\nu=1/2$ as a control. The decoder receives the chosen action label, the two public records, and true $(p,\nu)$, but no private state, error support, ideal noisy-readout bits, or hidden fusion distinctions.

<!-- pagebreak -->

## 6. Logical target and policy comparisons

The target is $\lambda=\ell(E)\in\{0,1\}^2$. A final output may be a label $\widehat\lambda$ or a total red-chain correction $c$ with $Hc=s$. In the latter convention success means $\ell(E\oplus c)=(0,0)$. If the probing action has already been applied, the remaining binary correction is $c\oplus a$, so these conventions have the same stipulated score. This is a red-chain homology inference score; no claim about full quantum recovery after measurement is implicit.

Let $R_1^*(p)$ be the Bayes failure probability using the first record only. For a specified action policy $\pi$, let $R_{2,\pi}^*(p,\nu)$ be the Bayes failure probability using both available records and the chosen action. Both are unconditional over the full IID physical prior and measurement outcomes. Missing, invalid, or exceptional outputs count as failures.

Determine the gain from the second record under each of the four fixed policies. Then determine, or tightly bound, the additional gain available from adapting the action to the first record. Construct at least one executable public-input adaptive policy and compare it with all four fixed policies at matched $(p,\nu)$ and resource settings. Distinguish a policy's actual decoder loss from the best attainable risk given its observations. A pointwise ideal-policy bound can be used as a reference if its computation and limitations are explicit.

The main physical rate is $p=0.05$, at second-readout noise $\nu=0,0.05,0.10$. Include $p=0.02$ and $p=0.10$ at $\nu=0$, plus $p=0$ and $\nu=1/2$ controls. You may add parameter values if they clarify where the advantage persists. Do not discard high-weight errors or difficult first records; if a controlled truncation is used, bound its effect under the full physical prior.

Explain whether useful extra information separates different homology classes or only errors inside one class. Relate the noise sensitivity and action dependence to measurable features of the first record. A positive private-error mutual information, or a difference between two selected conditional laws, alone does not answer this recovery question.

<!-- pagebreak -->

## 7. Validation and scientific evidence

Verify the supplied graph, face space, logical masks, and spanning-tree action convention. Independently check operator algebra, state normalization or its compact proof, and normalization of the joint record law on controlled cases. Verify no-action/repeated-measurement limits wherever used. Show that the first-record distribution is independent of a subsequently selected action and that public decision routines cannot read private generation or scoring state.

Use exact or independently controlled conditional cases to check logical-sector probabilities and decisions, then justify how the aggregate risk calculation covers the physical prior. Explicitly separate physical-prior sampling error, error from likelihood or state approximation, and policy/decoder suboptimality. Rare record examples may explain a mechanism, but an unconditional gain needs physical weighting or a valid full-prior bound.

Retain joint charge correlations. If you compress the second record, define the compression and compare it with the full record under the same instrument. A product of single-site marginals is a different likelihood unless its validity has been established. Report whether evidence resolves a gain, constrains it to be small, or leaves it unresolved; unsupported numerical precision is not a positive result.

## 8. Deliverables and resources

Submit a concise scientific report containing the fixed-action and adaptive-policy risks or informative controlled intervals, the value of the second measurement, noise dependence, mechanism analysis, and limitations. Provide sufficient numerical data, source, environment, and commands to reproduce every reported result.

Expose separate public routines `choose_action(first_record, p, nu, rng=None) -> label` and `infer_logical(first_record, action_label, second_report, p, nu, rng=None) -> two_bits`. Document any posterior or bound interface supporting the conclusions. A simulator may hold private state, but the two decision routines must accept only public inputs. State all ordering conventions and explicit randomness.

Design a study feasible on a scientific workstation. Justify the accuracy and policy-development cost against the available computational resources. Internet and standard scientific libraries are allowed. Report time, memory, seeds, stopping rules, and all failure handling. No particular inference method, positive adaptive advantage, or numerical threshold is prescribed. Assessment concerns fidelity to the finite instrument, valid full-prior logical inference, an informative policy comparison, and reproducibility.


<!-- pagebreak -->

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
