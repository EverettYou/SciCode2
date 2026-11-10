# Decoding Transitions of SU(N) Fusion Records at Large N

Directed SU(N) pair errors on a honeycomb patch: statistical mechanics and decoding phases

## 1. Scientific objective

A local SU(N) fusion measurement can distinguish error configurations that have the same parity syndrome. How much it distinguishes depends on $N$. Determine how optimal logical recovery from complete fusion records depends on $N$, and construct the statistical-mechanics description of this recovery problem.

Your principal results must be:

(i) an exact statistical-mechanics model for the logical-sector weights of the channel below, with a determination of whether and how it admits a free-fermion (Pfaffian) representation, and of the symmetry class and nature of any decoding transition;

(ii) the large-$N$ limit of the observation law and of optimal recovery, together with the leading finite-$N$ corrections;

(iii) the optimal decoding phase diagram in $(p,N)$ over $0\leq p\leq1$ and $N=2,3,4,\ldots$, supported by increasing lattice sizes. Determine whether the non-decodable region disappears at a finite $N$ or only as $N\to\infty$, and how the phase boundaries approach their limiting behavior.

The model below is a stipulated classical noise-and-observation channel motivated by SU(N) fusion. Conditional independence of its local readouts is part of the definition. Deriving a microscopic joint quantum measurement is outside this task.

## 2. Geometry and logical recovery

For integer $L\geq2$, the vertices are $(i,j)$ with $0\leq i\leq2L-1$ and $0\leq j\leq L$. Retain the horizontal edge $((i,j),(i+1,j))$ for $0\leq i\leq2L-2$ and $1\leq j\leq L-1$. Retain the vertical edge $((i,j),(i,j+1))$ exactly when $0\leq j\leq L-1$ and $i+j$ is even. Discard vertices with no retained edge. This is a brick-wall honeycomb patch.

The rows $j=0$ and $j=L$ are the two open (rough) boundaries. Each of their $L$ remaining vertices has degree one and is not measured. All vertices with $1\leq j\leq L-1$ are measured detectors. The columns $i=0$ and $i=2L-1$ are closed (smooth) boundaries made of measured detectors.

There are $3L^2-3L+1$ retained edges and $2L(L-1)$ detectors. Exactly $2(L-1)$ detectors, those on the closed boundaries, have degree two; all others have degree three. The shortest path between the two open boundaries has $2L-1$ edges.

Let $H$ be the detector-edge incidence matrix over $\mathbb F_2$. Let $\Gamma_T$ contain exactly the edges meeting the top open boundary $j=L$. For any binary edge vector $z$, define

$$\ell(z)=\bigoplus_{e\in\Gamma_T} z_e.$$

A decoder returns a binary correction $c$ on the retained edges. On error vector $x$, it succeeds exactly when $Hc=Hx$ and $\ell(x\oplus c)=0$. Exact reconstruction of $x$ is unnecessary. Array ordering is your choice, but must be documented and exposed by the callable interface.

Orient the edges like field lines running from the bottom open boundary to the top one. Every vertical edge points toward increasing $j$. A horizontal edge points from its endpoint with $i+j$ odd to its endpoint with $i+j$ even. In the regular honeycomb embedding, every edge then has a positive component along the bottom-to-top direction, and there are no directed cycles. For a detector $v$, let $\mathrm{out}(v)$ and $\mathrm{in}(v)$ be the incident edges whose tail or head, respectively, is $v$. A degree-three detector with $i+j$ even has one outgoing and two incoming edges; with $i+j$ odd, two outgoing and one incoming. A degree-two detector has one of each. The orientation is fixed and known to the decoder.

## 3. Noise and complete fusion readout

Independently on each retained edge, draw $x_e\sim\mathrm{Bernoulli}(p)$ with $0\leq p\leq1$. An active edge creates a pair: the fundamental representation $V$ of SU(N) at its tail and the conjugate representation $\bar V$ at its head. At each detector define

$$a_v=\sum_{e\in\mathrm{out}(v)}x_e,\qquad b_v=\sum_{e\in\mathrm{in}(v)}x_e,\qquad s_v=(a_v+b_v)\ \mathrm{mod}\ 2.$$

The local readout $R_v$ is an irreducible representation of SU(N), drawn independently across detectors conditional on $x$, with

$$P(R_v=R\mid x)=\frac{m_R(a_v,b_v)\,\mathrm{dim}\,R}{N^{a_v+b_v}},$$

where $m_R(a,b)$ is the multiplicity of $R$ in $V^{\otimes a}\otimes\bar V^{\otimes b}$. This law is normalized. Readout labels are isomorphism classes of SU(N) irreps: different fusion channels that give the same irrep give the same label, including coincidences that occur only at small $N$.

Two checks fix conventions. For every $N$, $(a,b)=(1,1)$ gives the trivial irrep with probability $1/N^2$ and the adjoint otherwise, while $(a,b)=(2,0)$ gives the symmetric square with probability $(N+1)/(2N)$ and the antisymmetric square otherwise. At $N=2$ the law depends only on $n_v=a_v+b_v$: total spin $J=0$ or $1$ with probabilities $1/4$ and $3/4$ when $n_v=2$, and $J=1/2$ or $3/2$ with probability $1/2$ each when $n_v=3$.

The decoder is told $(G_L,p,N)$, the edge orientation, the syndrome $s$ and the complete record $R=(R_v)$. It receives no $x$, $a_v$, $b_v$, fusion histories, or any information at the open boundaries. There is one observation round, with no syndrome or readout errors. The syndrome-only record $s$ on the same geometry is the baseline.

<!-- pagebreak -->

## 4. Logical-sector posterior and the physical average

For a supported record $(s,R)$, define the absolute sector weights

$$Z_\lambda(s,R)=\sum_{x:\,Hx=s,\ \ell(x)=\lambda}\ \prod_e p^{x_e}(1-p)^{1-x_e}\prod_v P(R_v\mid a_v(x),b_v(x)),\qquad \lambda\in\{0,1\},$$

and $q_\lambda=Z_\lambda/(Z_0+Z_1)$. A logical Bayes decoder selects the more probable sector and returns a correction of that sector with syndrome $s$. Its conditional risk is $\min(q_0,q_1)$. The optimal unconditional risk is

$$R_L^*(p,N)=\mathbb E_{(s,R)}\left[\min(q_0,q_1)\right],$$

with the expectation taken under the physical record law of Section 3. Conditional, selected, or uniformly counted records define different averages. A decodable phase means $R_L^*(p,N)\to0$ as $L$ grows; a non-decodable phase keeps a positive limit.

## 5. Required scientific investigation

**Statistical mechanics.** Write the sector weights as an explicit classical statistical-mechanics model with quenched disorder supplied by the record. Determine whether this model has an exact free-fermion or Pfaffian representation on the stated geometry, for which $N$, and under which conditions; support the answer by proof or by explicit counterexample. Relate the model to the random-bond Ising model and its Nishimori line where such a relation exists. Identify the symmetry class of the disordered model and what it implies for possible transitions. Any mapping must keep the channel, open-boundary convention and binary logical target defined here.

**Large N.** Derive the $N\to\infty$ limit of the observation law and of the sector posterior. Identify the leading finite-$N$ corrections and the natural expansion parameter. If the weights allow $N$ or $1/N$ to be continued to non-integer values, state where the continued model remains a positive probability model, and use it only inside that domain.

**Phase diagram.** Estimate $R_L^*(p,N)$ for $N=2,3,4$, for several larger $N$, and in the limit, over the full range of $p$, with controlled exact or certified inference on increasing two-dimensional sizes. Determine the decodable region for each $N$, whether the non-decodable region vanishes at a finite $N$ or only as $N\to\infty$, and how the boundaries approach the limit, with uncertainties. A transition estimate must rest on size dependence, not on one crossing or one low failure count. An unresolved boundary is acceptable when accompanied by informative constraints. Reserve at least one value of $N$ or one size comparison as a check performed after the main analysis choices are fixed, and report it even if it contradicts the preferred conclusion.

**Practical decoding.** For $N=2$ and at least one larger $N$, compare one scalable practical decoder with the optimal reference on the same records. Keep algorithmic loss separate from intrinsic loss.

<!-- pagebreak -->

## 6. Evidence and trustworthiness

Validate the geometry, logical sectors, decoder input boundary, and the readout law for every $N$ used, with multiplicities and dimensions checked by two independent methods. Check $p=0$, $p=1$, the $N=2$ reduction, and the syndrome-only baseline. On small patches, compare sector probabilities and logical decisions from an independent whole-configuration enumeration with the production inference, and show how the two implementations differ.

Retain every attempted trial in its unconditional denominator. An exception, missing output or invalid correction is a failure. Report numerical failures and convergence diagnostics separately; do not postselect on records or on successful inference. Separate sampling uncertainty, finite-size uncertainty and inference approximation. Changing the readout law, orientation, geometry or logical loss does not give a matched comparison.

## 7. Optional extension

Not required for success: test whether the conclusions survive when the free-fermion structure may fail. One option is the square patch with vertices $(i,j)$, $0\leq i,j\leq L-1$, all horizontal edges, vertical edges only for $1\leq i\leq L-2$, and open columns $i=0$ and $i=L-1$. It has degree-four detectors. Orient horizontal edges from the left open boundary toward the right one, and vertical edges toward increasing $j$; take the logical bit from the edges meeting the right open boundary. Another is hidden orientation: each active edge independently places $V$ at either endpoint with probability $1/2$, and the decoder does not see this choice. State which parts of the statistical-mechanics model and of the large-$N$ conclusions change.

## 8. Deliverables and resources

Submit a concise scientific report with the statistical-mechanics model, the large-$N$ analysis, the $(p,N)$ phase diagram with increasing-size evidence, the reserved check, the practical-decoder comparison, and limitations. Supply raw or sufficient numerical data, source, an environment specification, and commands that reproduce every reported table and figure.

Provide a documented callable decoder `decode(graph, p, N, record, rng=None) -> correction`, a graph constructor with array conventions, a routine that returns the readout law $P(R\mid a,b)$ for given $N$, and a routine that returns sector probabilities or certified bounds for a record. Randomness must be explicit and reproducible.

Design a study feasible on a scientific workstation. Justify sizes, values of $N$ and precision against the available resources. Report actual resources, seeds and stopping rules. Internet access and standard scientific libraries are allowed; essential model information is contained in this statement. No particular algorithm, threshold value or universality class is required for success: assessment concerns model fidelity, correctness of the statistical-mechanics construction, inference validity, informative evidence about the $N$ dependence, and reproducibility.
