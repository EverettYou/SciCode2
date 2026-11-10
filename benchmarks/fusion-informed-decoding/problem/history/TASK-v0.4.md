# Decoding SU(N) Fusion Records with Hidden Pair Orientation

Exact inference, statistical mechanics, and N-dependent decoding phases on a honeycomb patch

## 1. Scientific objective

An error on an edge creates a pair: the fundamental representation $V$ of SU(N) at one endpoint and its conjugate $\bar V$ at the other. Which endpoint receives $V$ is random and is never observed. Each detector measures the total SU(N) irrep of what has arrived there. Determine how much logical information these fusion records carry, and how optimal logical recovery depends on $N$.

The task has definite answers. Section 5 lists five required results, R1 to R5. Each is checked against an independent reference: exact values, a proof, or numerical phase assignments with stated tolerances. Report every final answer in the machine-readable file described in Section 7.

The model below is a stipulated classical noise-and-observation channel motivated by SU(N) fusion. Conditional independence of the local readouts, given the microscopic configuration, is part of the definition. Deriving a microscopic joint quantum measurement is outside this task.

## 2. Geometry and logical recovery

For integer $L\geq2$, the vertices are $(i,j)$ with $0\leq i\leq2L-1$ and $0\leq j\leq L$. Retain the horizontal edge $((i,j),(i+1,j))$ for $0\leq i\leq2L-2$ and $1\leq j\leq L-1$. Retain the vertical edge $((i,j),(i,j+1))$ exactly when $0\leq j\leq L-1$ and $i+j$ is even. Discard vertices with no retained edge. This is a brick-wall honeycomb patch.

The rows $j=0$ and $j=L$ are the two open (rough) boundaries. Each of their $L$ remaining vertices has degree one and is not measured. All vertices with $1\leq j\leq L-1$ are measured detectors. The columns $i=0$ and $i=2L-1$ are closed (smooth) boundaries made of measured detectors.

There are $3L^2-3L+1$ retained edges and $2L(L-1)$ detectors. Exactly $2(L-1)$ detectors, those on the closed boundaries, have degree two; all others have degree three. The shortest path between the two open boundaries has $2L-1$ edges.

Let $H$ be the detector-edge incidence matrix over $\mathbb F_2$. Let $\Gamma_T$ contain exactly the edges meeting the top open boundary $j=L$. For any binary edge vector $z$, define

$$\ell(z)=\bigoplus_{e\in\Gamma_T} z_e.$$

A decoder returns a binary correction $c$ on the retained edges. On error vector $x$, it succeeds exactly when $Hc=Hx$ and $\ell(x\oplus c)=0$. Exact reconstruction of $x$ or of any orientation is unnecessary. Array ordering is your choice, but must be documented and exposed by the callable interface.

## 3. Noise and complete fusion readout

Independently on each retained edge, draw $x_e\sim\mathrm{Bernoulli}(p)$ with $0\leq p\leq1$. For each active edge, independently choose one of its two endpoints with probability $1/2$ each; that endpoint receives $V$ and the other receives $\bar V$. Write $\sigma$ for these hidden choices. At each detector $v$, let $a_v$ be the number of $V$ and $b_v$ the number of $\bar V$ it receives, and $s_v=(a_v+b_v)\ \mathrm{mod}\ 2$.

The local readout $R_v$ is an irreducible representation of SU(N), drawn independently across detectors conditional on $(x,\sigma)$, with

$$P(R_v=R\mid x,\sigma)=\frac{m_R(a_v,b_v)\,\mathrm{dim}\,R}{N^{a_v+b_v}},$$

where $m_R(a,b)$ is the multiplicity of $R$ in $V^{\otimes a}\otimes\bar V^{\otimes b}$. Readout labels are isomorphism classes of SU(N) irreps, including coincidences that occur only at small $N$.

Two checks fix conventions. For every $N$, $(a,b)=(1,1)$ gives the trivial irrep with probability $1/N^2$ and the adjoint otherwise, while $(a,b)=(2,0)$ gives the symmetric square with probability $(N+1)/(2N)$ and the antisymmetric square otherwise. At $N=2$ the readout depends only on $n_v=a_v+b_v$: total spin $J=0$ or $1$ with probabilities $1/4$ and $3/4$ when $n_v=2$, and $J=1/2$ or $3/2$ with probability $1/2$ each when $n_v=3$.

The decoder is told $(G_L,p,N)$, the syndrome $s$ and the complete record $R=(R_v)$. It receives no $x$, $\sigma$, $a_v$, $b_v$, fusion histories, or any information at the open boundaries. There is one observation round, with no syndrome or readout errors.

## 4. Logical-sector posterior and the physical average

For a supported record $(s,R)$, define the absolute sector weights

$$Z_\lambda(s,R)=\sum_{x:\,Hx=s,\ \ell(x)=\lambda}\ \sum_\sigma\ \prod_e p^{x_e}(1-p)^{1-x_e}\,2^{-x_e}\prod_v P(R_v\mid a_v,b_v),\qquad \lambda\in\{0,1\},$$

where $\sigma$ runs over the orientations of the active edges of $x$, and $q_\lambda=Z_\lambda/(Z_0+Z_1)$. A logical Bayes decoder selects the more probable sector and returns a correction of that sector with syndrome $s$. Its conditional risk is $\min(q_0,q_1)$. The optimal unconditional risk is

$$R_L^*(p,N)=\mathbb E_{(s,R)}\left[\min(q_0,q_1)\right],$$

with the expectation taken under the physical record law of Section 3. For fixed $N$, a value of $p$ is decodable if $R_L^*(p,N)\to0$ as $L\to\infty$ and non-decodable if $R_L^*(p,N)$ stays bounded away from zero.

## 5. Required results

**R1. Exact local law.** For every $(a,b)$ with $a+b\leq3$, give $P(R\mid a,b)$ in closed form as a function of $N$, listing each irrep by its highest weight or Young-diagram pair. State separately every coincidence of labels that occurs at $N=2$ and $N=3$. Verify each entry by two independent methods.

**R2. Exact sector posterior.** Provide a routine that returns $q_0(s,R)$ for any supported record. It must be exact up to floating-point rounding, or return certified bounds. It will be tested on held-out records with $L\leq4$, $N\in\{2,3,4,6\}$ and several $p\in(0,1)$, with tolerance $10^{-9}$ in $q_0$.

**R3. Statistical-mechanics model.** Write $Z_\lambda$ as an explicit classical statistical-mechanics model with quenched disorder supplied by the record. Prove that at $N=2$ the hidden orientation can be summed exactly, and that the resulting model on this geometry has an exact planar free-fermion (Pfaffian) representation. For $N\geq3$, identify every exact local constraint that the record imposes on $(x,\sigma)$, and state and justify the $N\to\infty$ limit of the record law and of the sector posterior.

**R4. A rigorous large-N statement.** Give an explicit integer $N_0$ and a proof that every $p\in[0,1]$ is decodable for all $N\geq N_0$. Any valid proof is accepted; a smaller valid $N_0$ is better.

**R5. Phase answers.** Using controlled exact or certified inference on increasing two-dimensional sizes:

(a) for $N=2$ and $N=3$, give the decodable set in $p\in[0,1]$ as a union of intervals, with each interior endpoint to within $\pm0.01$ and its uncertainty;

(b) for each $N\in\{2,3,4,5,6\}$, state whether $p=1/2$ is decodable;

(c) give $N^*$, the smallest $N\in\{2,\ldots,8\}$ for which every $p\in[0,1]$ is decodable, or state that none is.

Each phase assignment must rest on size dependence, not on one crossing or one low failure count. If your evidence cannot settle an item, mark it unresolved and give the constraint you can support; do not guess.

## 6. Evidence and trustworthiness

Validate the geometry, logical sectors, decoder input boundary and the local law for every $N$ used. On small patches, compare sector probabilities from an independent whole-configuration enumeration over $(x,\sigma)$ with the production inference, and show how the two implementations differ. Check $p=0$, $p=1$, and the $N=2$ reduction.

Retain every attempted trial in its unconditional denominator. An exception, missing output or invalid correction is a failure. Report numerical failures and truncation diagnostics separately; do not postselect on records or on successful inference. Separate sampling uncertainty, finite-size uncertainty and inference approximation, and show that inference approximation is small enough not to change any R5 answer.

## 7. Deliverables and resources

Submit `answers.json` with the keys `R1_table` (all entries of R1), `R4_N0`, `R5a` (for each of $N=2,3$: list of intervals with endpoint uncertainties), `R5b` (for each $N$: `true`, `false` or `"unresolved"`), and `R5c` (integer, `null`, or `"unresolved"`). Also submit a concise scientific report with the R3 derivations, the R4 proof, the R5 evidence and limitations, together with raw or sufficient data, source, an environment specification, and commands that reproduce every reported number and figure.

Provide documented callables: a graph constructor with array conventions; `local_law(N, a, b)`; `sector_posterior(graph, p, N, s, R)` returning $q_0$ or certified bounds (R2); and `decode(graph, p, N, s, R, rng=None) -> correction`. Randomness must be explicit and reproducible.

Use a single workstation with at most 8 CPU cores and 32 GiB RAM; no GPU is required. Report actual resources, seeds and stopping rules. Internet access and standard scientific libraries are allowed; essential model information is contained in this statement. No particular algorithm is required.
