# How Much Symmetry Knowledge Does Decoding Need?

Syndrome, Z(N) charge and SU(N) irrep records on a honeycomb patch

## 1. Objective

An error on an edge creates a fundamental $V$ of SU(N) at one endpoint and its conjugate $\bar V$ at the other. Which endpoint receives $V$ is random. Detectors may reveal three levels of information about what has arrived: only the parity, also the $\mathbb Z_N$ charge, or the full SU(N) irrep. Determine how optimal logical recovery depends on the level of information and on $N$.

The principal result is a phase diagram with $p\in[0,1]$ on the horizontal axis and $N=2,\ldots,8$ on the vertical axis, showing the boundary between decodable and non-decodable regions separately for each of the three records. Section 5 states the required results; each will be checked independently.

The model below is a stipulated classical noise-and-observation channel. Conditional independence of the local readouts, given the microscopic configuration, is part of the definition.

## 2. Geometry and logical recovery

For integer $L\geq2$, consider points $(i,j)$ with $0\leq i\leq2L-1$ and $0\leq j\leq L$. The edges are:

- horizontal edges $((i,j),(i+1,j))$ for $0\leq i\leq2L-2$, only in the rows $1\leq j\leq L-1$ (rows $j=0$ and $j=L$ have no horizontal edges);
- vertical edges $((i,j),(i,j+1))$ for $0\leq j\leq L-1$, present exactly when $i+j$ is even.

The vertices are the endpoints of these edges; points of rows $0$ and $L$ that meet no edge are not vertices. Every vertex with $1\leq j\leq L-1$ has exactly one vertical edge, so the graph is a brick-wall drawing of a honeycomb patch whose interior faces are hexagons. Figure 1 shows $L=3$.

The rows $j=0$ and $j=L$ are the two open (rough) boundaries. Each contains $L$ vertices of degree one, which are not measured. All vertices with $1\leq j\leq L-1$ are measured detectors; they have degree three, except the $2(L-1)$ detectors in the columns $i=0$ and $i=2L-1$, which form the closed (smooth) boundaries and have degree two. There are $3L^2-3L+1$ edges and $2L(L-1)$ detectors, and the shortest path between the two open boundaries has $2L-1$ edges.

![Figure 1. The patch for $L=3$. (a) In the integer coordinates of the text. (b) The same graph drawn with hexagonal faces. Filled circles are detectors, open circles are unmeasured open-boundary vertices, and red edges form $\Gamma_T$.](figures/geometry-L3.png)

Let $H$ be the detector-edge incidence matrix over $\mathbb F_2$, and let $\Gamma_T$ be the $L$ vertical edges that meet the top row $j=L$. For a binary edge vector $z$, define

$$\ell(z)=\bigoplus_{e\in\Gamma_T} z_e.$$

A decoder returns a binary correction $c$. On error vector $x$, it succeeds exactly when $Hc=Hx$ and $\ell(x\oplus c)=0$.

## 3. Noise and the three records

Independently on each edge, draw $x_e\sim\mathrm{Bernoulli}(p)$. For each active edge, independently choose one endpoint with probability $1/2$; it receives $V$ and the other endpoint receives $\bar V$. At detector $v$, let $a_v$ and $b_v$ be the numbers of $V$ and $\bar V$ received, and $s_v=(a_v+b_v)\ \mathrm{mod}\ 2$.

Conditional on the microscopic configuration, each detector independently yields an irrep $R_v$ of SU(N) with

$$P(R_v=R)=\frac{m_R(a_v,b_v)\,\mathrm{dim}\,R}{N^{a_v+b_v}},$$

where $m_R(a,b)$ is the multiplicity of $R$ in $V^{\otimes a}\otimes\bar V^{\otimes b}$. Labels are isomorphism classes of SU(N) irreps. For example, $(a,b)=(1,1)$ gives the trivial irrep with probability $1/N^2$; at $N=2$, $n_v=2$ gives total spin $0$ or $1$ with probabilities $1/4$ and $3/4$.

The three records, all given together with $(G_L,p,N)$, are:

| Record | Decoder-visible information |
| --- | --- |
| $O_0$ | syndrome $s$ |
| $O_1$ | $s$ and the charges $k_v=(a_v-b_v)\ \mathrm{mod}\ N$ |
| $O_2$ | $s$ and the irreps $R_v$ |

No decoder receives $x$, the orientations, $a_v$, $b_v$, or anything at the open boundaries. There is one round and no measurement error.

## 4. Optimal recovery

For record type $O_r$ and an observed record $o$, let $Z_\lambda(o)$ be the total probability of all microscopic configurations, including orientations and readout outcomes, that produce $o$ and have $\ell(x)=\lambda$. The optimal decoder chooses the larger of $Z_0,Z_1$. Its unconditional logical error rate is

$$R_{r,L}^*(p,N)=\mathbb E_o\left[\frac{\min(Z_0,Z_1)}{Z_0+Z_1}\right],$$

averaged over the physical record law. For a fixed record type and $N$, a value of $p$ is decodable if $R_{r,L}^*(p,N)\to0$ as $L\to\infty$, and non-decodable if it stays bounded away from zero.

## 5. Required results

**R1. Phase diagram.** For each record $O_0$, $O_1$, $O_2$ and each $N\in\{2,\ldots,8\}$, give the decodable set in $p\in[0,1]$ as a union of intervals. Give each interior endpoint with its uncertainty, or mark it unresolved with the bound you can support. Draw the three boundaries on one $(p,N)$ diagram.

**R2. Exact structure.** State and prove every exact property of the three records that your phase diagram relies on, such as exact solvability, orderings or equivalences.

**R3. Large N.** For $O_2$, give an explicit integer $N_0$ with a proof that every $p\in[0,1]$ is decodable for all $N\geq N_0$, or prove that no such $N_0$ exists. A smaller valid $N_0$ is better.

**R4. Exact posterior.** For $O_1$ and $O_2$, provide a routine that returns $Z_0/(Z_0+Z_1)$ for any record of positive probability, exact up to floating-point rounding or with certified bounds. It will be tested on held-out records with $L\leq4$ and $N\leq8$, with tolerance $10^{-9}$.

## 6. Evidence

Phase assignments must rest on size dependence across increasing two-dimensional patches, not on one crossing or one low failure count. Validate every inference method against an independent enumeration on small patches. Keep every attempted trial in the unconditional denominator; an exception or invalid correction is a failure. Separate statistical, finite-size and approximation uncertainty, and show that approximation error cannot change any R1 answer.

## 7. Deliverables and resources

Submit `answers.json` of the form `{"R1": {"O0": {"2": [[a, da, b, db], ...], ...}, "O1": {...}, "O2": {...}}, "R3_N0": n}`. Each decodable interval $[a,b]$ is listed with endpoint uncertainties `da`, `db` (`0` at $p=0$ or $p=1$); an unresolved entry is `{"unresolved": true, "bounds": "..."}`; `R3_N0` is an integer or `null`. Submit a concise report with the phase diagram, the proofs for R2 and R3, the evidence, and the limitations, together with source, data, an environment specification, and commands that reproduce every number and figure.

Provide the callables `posterior(L, p, N, record_type, record)` for R4, returning $Z_0/(Z_0+Z_1)$, and `decode(L, p, N, record_type, record, rng=None)`, returning a correction. Use these conventions. `record_type` is `"O0"`, `"O1"` or `"O2"`. A detector is its coordinate tuple `(i, j)`. A record is a dict from every detector to `s` for $O_0$, to `(s, k)` for $O_1$, and to `(s, w)` for $O_2$, where `w` is the tuple of $N-1$ Dynkin labels of $R_v$ (for $N=2$, `(2J,)`). An edge is the pair of its endpoint tuples in increasing lexicographic order, and a correction is the set of edges with $c_e=1$.

Use one workstation with at most 8 CPU cores and 32 GiB RAM; no GPU. Report resources, seeds and stopping rules. Internet access and standard scientific libraries are allowed. No method is prescribed.
