# Theory and fairness audit: two surface-code Ising encodings

This is supervised research following the user's comparison request, not a fresh autonomous benchmark test. The derivations below are specific to the ideal-measurement, independent-error, single-CSS-sector model in this lab. They do not assume access to the true error. Mathematical claims labelled as proved are derived here; experimental performance claims belong to the lab's numerical reports.

## Scope and notation

The common optimization problem is

\[
\min_{e\in\{0,1\}^n}C(e)=\sum_a w_a e_a,
\qquad He=s\pmod2.
\]

Positive weights describe independent errors with probabilities below one half through \(w_a=\log[(1-p_a)/p_a]\). The mapping and repair proof also work with signed finite weights when absolute weights are used in the repair bound. Minimum-cost error-pattern decoding is the score. It is not maximum-probability logical-class decoding, which sums probabilities over stabilizer-equivalent errors.

The rectangular unrotated patch has width \(w\ge2\), height \(h\ge2\), and rough boundaries on the left and right. Error edges are horizontal \((x,y)\), \(0\le x<w,0\le y<h\), and vertical \((x,y)\), \(1\le x<w,0\le y<h-1\). Checks are the \((w-1)h\) interior-column vertices. Relative face boundaries generate the syndrome-preserving stabilizers; let their incidence matrix be \(B\). There are \(r=w(h-1)\) faces. A horizontal boundary-to-boundary string is \(L\).

The matrices obey

\[
HB=0,\quad HL=0,\quad
\operatorname{rank}H=(w-1)h,\quad
\operatorname{rank}B=w(h-1),\quad
\ker H=\operatorname{im}B\oplus\langle L\rangle.
\]

Here \(n=wh+(w-1)(h-1)\). Thus every valid error has a **unique** representation

\[
e=e^{(0)}\oplus Bx\oplus\ell L,
\qquad x\in\{0,1\}^{r},\quad\ell\in\{0,1\},
\]

for any fixed syndrome-compatible reference \(e^{(0)}\). The lack of a redundant face generator is useful: this lab has no unremoved gauge degeneracy in \(x\).

## Encoding A: error bits and sequential XOR auxiliaries

For an intermediate XOR use a parity bit \(p\), a carry bit \(t\), and

\[
\Lambda(a+b-p-2t)^2.
\]

For the final two-input parity use

\[
\Lambda\left[s+(1-2s)(a+b-2ab)\right].
\]

Each check of degree \(d\ge2\) uses \(2(d-2)\) auxiliary bits and \(6(d-2)+1\) interaction edges. The constructed energy is

\[
Q_A(e,u)=C(e)+\Lambda V(e,u),\qquad V\in\mathbb Z_{\ge0}.
\]

**Exact auxiliary minimization.** For every original error vector,

\[
\min_u V(e,u)=|He\oplus s|.
\]

Proof: if an original check has the wrong parity, at least one of its XOR or final-parity relations must fail, contributing at least one integer penalty. Summing over checks gives the lower bound. Choosing all prefixes and carries to compute the actual parities makes only the mismatched final checks fail, attaining the bound. When \(He=s\), the zero-penalty extension is unique.

The previous lab used the generic sufficient condition \(\Lambda>\sum_a|w_a|\). It is valid but unnecessarily conservative for this surface-code geometry. This lab includes both that baseline and the following tighter condition.

### A geometry-aware penalty theorem

Form the decoding graph with a vertex for every check and one collapsed rough-boundary vertex. Error columns of weight one connect a check to the boundary; columns of weight two connect their two checks. Give each edge length \(|w_a|\), and define

\[
R=\max_v\min_{\gamma:v\to\partial_{\rm rough}}
\sum_{a\in\gamma}|w_a|.
\]

**Theorem.** If \(\Lambda>R\), every ground state of \(Q_A\) has valid syndrome and its projected error minimizes \(C\) among valid errors.

Proof: let \(q=He\oplus s\). For each violated check, take a shortest path to a rough boundary and add these paths modulo two, obtaining a repair vector \(r_q\) with \(Hr_q=q\). Their combined absolute weight is at most \(R|q|\), even when overlapping edges cancel. Therefore

\[
C(e\oplus r_q)-C(e)\le R|q|.
\]

The repaired error has a zero-penalty auxiliary completion. For any state with \(|q|>0\), its energy is at least \(C(e)+\Lambda|q|\), strictly larger than that repaired state's energy. For \(q=0\), incorrect auxiliaries can be corrected without changing \(e\), strictly decreasing the energy. Valid states with their unique correct auxiliaries have precisely \(C(e)\), completing the proof.

For unit weights, \(R=\lfloor w/2\rfloor\). This order is unavoidable for a single uniform penalty across **all syndromes**: a single central defect has minimum feasible error cost \(R\), while \(e=0\), all auxiliaries zero, and one final parity violation have cost \(\Lambda\). If \(\Lambda<R\), an invalid state is below every valid state; at \(\Lambda=R\), a ground state can be invalid. Thus the geometry-aware worst-syndrome threshold is tight for unit weights. For individual syndromes and weight distributions a smaller penalty might suffice; this theorem does not optimize it.

### Exact resource counts before hardware embedding

There are \(2(w-1)\) degree-three checks and \((w-1)(h-2)\) degree-four checks. Consequently

\[
n_A=wh+5(w-1)(h-1),\qquad
a_A=4(w-1)(h-1),\qquad
m_A=(w-1)(13h-12).
\]

The edge count has no cross-check duplicate pairs in this construction: two vertex checks share at most one error edge, while their auxiliaries are distinct.

For a square patch \(w=h=d\), \(n_A=6d^2-10d+5\). This counts the particular sequential-XOR encoding, not the optimum possible error-variable encoding.

## Encoding B: stabilizer spins and two logical sectors

Fix \(\ell\), set \(\tau_a^{(\ell)}=(-1)^{e_a^{(0)}+\ell L_a}\), and use spins \(\sigma_f=(-1)^{x_f}\). An edge is incident to one or two retained face generators, so

\[
e_a=\frac{1-\tau_a^{(\ell)}\prod_{f:B_{af}=1}\sigma_f}{2}.
\]

The cost is exactly the two-local Ising energy

\[
Q_{B,\ell}(\sigma)=\frac12\sum_a w_a
-\frac12\sum_a w_a\tau_a^{(\ell)}
\prod_{f:B_{af}=1}\sigma_f.
\]

Two incident faces give coupling \(-w_a\tau_a^{(\ell)}/2\); a single incident face gives a longitudinal field of the same value. Contributions to the same field are summed. In the height-two patch, both top and bottom boundary terms can act on the same spin and either add or cancel. Every output is syndrome-valid, independently of whether it is a ground state.

Per logical sector the number of spins and structural interaction edges is

\[
n_B=w(h-1),\qquad
m_B=(w-1)(h-1)+w(h-2).
\]

The logical ground states of A and the union of the two B sectors project to the same minimum-cost errors. One sector alone is not equivalent to A. Finding a feasible reference by binary elimination or a fixed boundary tree does not solve the optimization problem or assume the correct logical class.

For square patches, \(n_B=d^2-d\). The asymptotic spin saving over sequential XOR is a factor of six per sector or three when both sectors are simultaneously instantiated. Sequential reuse needs only one sector's qubits but incurs two anneals/programs. All counts remain quadratic in code distance; the claim is a substantial constant-factor saving, not a change in big-O scaling.

### Canonical-reference invariance of ideal transverse-field QA

If another reference is \(e^{(1)}=e^{(0)}\oplus Bu\), then the variable change \(x\mapsto x\oplus u\) is a spin gauge transformation. Let \(U=\prod_{f:u_f=1}X_f\). It conjugates the two diagonal problem Hamiltonians, commutes with \(-\sum_fX_f\), and leaves the initial \(|+\rangle^{\otimes r}\) state unchanged. Consequently the complete forward-anneal spectra and decoded success probabilities are identical, with corresponding measurement relabeling. If the references differ additionally by \(L\), the sector labels are swapped.

This is an exact invariance for the ideal driver, initial state, gauge-independent scale, and readout used here. It means a clever initial canonical pairing cannot improve this ideal dual QA dynamics by itself. Broken calibration symmetry, nonuniform schedules, restricted reference-dependent postprocessing, or a classical initial-state heuristic can change that conclusion and are outside this experiment.

## The drivers are different algorithms on the error space

Under encoding B, a single \(X_f\) flips a whole relative face boundary in the decoded error. It directly connects two valid errors in the same logical class. This is a local move in face variables but a collective move in error variables.

For encoding A, let \(P\) project onto valid errors and their unique zero-penalty auxiliary completions. In this patch every original error column has at least one nonzero check incidence. Flipping one original error therefore changes syndrome; flipping one auxiliary destroys its unique correct completion. Hence

\[
P X_j P=0\quad\text{for every encoded bit }j,
\qquad P\left(-\Gamma\sum_jX_j\right)P=0.
\]

This establishes a concrete late-anneal structural disadvantage: a strictly projected single-spin driver cannot directly move between feasible A states, whereas the B driver can. In a perturbative regime where intermediate penalty states are spectrally separated, transitions between distinct A feasible states appear through virtual multibit paths; the first possible order is at least their Hamming distance in the complete error-plus-auxiliary register. A representative path contributes factors of the form \(\Gamma^k/\Delta^{k-1}\). This is conditional perturbation reasoning, **not** a bound on the full forward-anneal gap, the transition rate on an open device, or the actual time-to-solution. Early in the anneal the penalty subspace is not isolated, and beneficial paths may explore violations.

Hardware embedding adds another layer. A logical face flip represented by a physical chain can itself require collective motion. Thus the clean logical-driver difference does not transfer unchanged to a physical Zephyr driver. Logical-model dynamics and physical-embedding dynamics must be labelled separately.

## Energy scaling and the meaning of a fair comparison

Use \(H(t)=-(1-t/T)\sum X+(t/T)\alpha H_P\), \(\hbar=1\). The lab saturates the model coefficient limits \(|h|,|J|\le1\), allowing \(\alpha>1\) for small raw coefficients. All sectors of B share one common \(\alpha\). These are dimensionless model limits, not the calibrated asymmetric limits and coupling-group constraints of a particular D-Wave device.

On bounded-degree surface patches, A's maximum coefficient is of order \(\Lambda\), so after saturation the useful objective scale is of order \(1/\Lambda\). For unit weights the legacy global penalty scales as \(d^2\), while the tighter geometry-aware penalty scales as \(d\); the latter materially reduces this handicap. B has no syndrome penalty and its coefficients remain of constant order before any hardware chain penalties. This is a reason to expect B to use limited analog range more efficiently. It does not prove a larger spectral gap throughout the anneal.

The same transverse field per physical/model spin is a natural hardware-style restriction, but A and B then have different total driver operator norms because they use different numbers of spins. There is no unique normalization making Hilbert-space size, total energy, per-coupler range, run count, and elapsed time all equal at once. State the chosen resource comparison explicitly rather than calling it an all-purpose fair speed test.

For independent sector runs, define \(p_\ell(T)\) as the probability that sector \(\ell\) outputs a **globally** minimum-cost error; set it to zero if that sector has no global optimum. One sample from each sector succeeds with probability

\[
p_B(T)=1-(1-p_0(T))(1-p_1(T)).
\]

There is no requirement to find the minimum of a losing sector once a global optimum has already been sampled. At sequential anneal budget \(C\), compare B runs of length \(C/2\) each to A at length \(C\), and also to two independent A runs of length \(C/2\). The two-run A probability is \(1-(1-p_A(C/2))^2\). Programming and readout overhead require additional device measurements.

For A, the primary decoded score marginalizes **all auxiliary outputs** whose original error is valid and globally optimal. A wrong auxiliary bit does not invalidate a correction already recovered correctly. Strict programmed-ground probability is a separate diagnostic. Counting only A states with all auxiliaries correct would unfairly penalize its decoding score.

For independent repeated samples, success means at least one acceptable error was obtained. The corresponding operational selector discards syndrome-invalid raw outputs and chooses the minimum original error cost among the remainder. It must not select the minimum raw QUBO energy while ignoring validity. The lab additionally examines a deterministic, weight-independent syndrome repair defined by a fixed binary right inverse of \(H\). This maps every raw error to a valid one, and its cost is evaluated after repair. Its success is a separate algorithmic variant, not silently substituted for raw sampling.

There is also a non-dynamical sector-stratification advantage. At zero anneal time, let \(g_\ell\) be the number of global optima in sector \(\ell\), and put \(a=g_0/2^r\), \(b=g_1/2^r\). Dual sampling gives one independent uniform sample in each sector, succeeding with probability \(a+b-ab\). Uniform direct samples followed by the fixed linear syndrome repair are uniform over both sectors together. Two such repaired samples succeed with probability \(a+b-(a+b)^2/4\). The dual advantage is already \((a-b)^2/4\ge0\) without any evolution. Thus a short-anneal advantage must not automatically be attributed to tunnelling or a spectral gap. Improvement over each encoding's zero-time baseline helps distinguish dynamical improvement from this sampling allocation and automatic-feasibility advantage.

Degenerate ground states must all count. A zero endpoint gap to another state in the target manifold does not itself signal failure. Any spectral comparison must distinguish target-manifold splitting from the gap to states that count as errors.

## Limits, adverse cases, and alternatives

No universal runtime superiority follows from these mappings. B has a proven compact representation and no invalid decoded states; A covers both logical sectors in a single optimization and permits intermediate syndrome violations. B can have frustrated domain-wall rearrangements and slow collective relaxation despite fewer variables. Sector accounting can matter when either sector has tied optima, when the winning sector is easy, or when one anneal could otherwise be replaced by several independent A samples. An actual reversal under specified QA dynamics needs numerical or experimental evidence; it must not be inferred from these possibilities alone.

The choice \(\Lambda=R+1\) is a transparent certified comparison point, not a dynamically optimized penalty. A penalty sweep above the validity threshold, anneal-schedule optimization, chain-strength tuning, and alternative postprocessing could alter the quantitative ranking. Such tuning must use comparable budgets and validation information for both encodings.

The comparison is also not a theorem against every error-variable formulation. For a degree-three or degree-four check, an alternative is

\[
\Lambda\left(\sum_{a\in r}e_a-s_r-2k_r\right)^2,
\]

with binary-encoded integer \(k_r\). Degree three needs one carry bit; degree four needs two for even syndrome, and one suffices for odd syndrome. This uses fewer auxiliaries than sequential XOR but creates denser local couplings and a different spectrum. It is an untested alternative in this lab.

Likewise, jointly modelling depolarizing X/Z correlations produces products involving both face-spin species and can introduce four-body terms requiring reduction. Repeated noisy syndrome measurements produce a spacetime decoding problem. The present two-local, penalty-free advantage is for one sector with perfect measurements; it cannot be silently extrapolated to those settings or to multiple holes with many logical sectors.

Finally, the logical-class likelihood is

\[
Z_\ell=\sum_x\exp[-C(e^{(0)}\oplus Bx\oplus\ell L)],
\]

up to a common noise normalization. Choosing its largest value differs from comparing \(\min_xC\) when class degeneracies matter. Neither ground-state encoding by itself computes \(Z_\ell\).

## Primary-source context

[Dennis, Kitaev, Landahl and Preskill, *Topological quantum memory*](https://arxiv.org/abs/quant-ph/0110143) establishes the statistical-mechanical relationship between topological-code errors, homology, and disordered spin/gauge models. It provides the conceptual context; the rectangular-patch counts, repair-radius theorem, and driver comparison above are derived explicitly in this lab.

[Takeuchi et al., *Comparative study of decoding the surface code using simulated annealing under depolarizing noise*](https://arxiv.org/abs/2311.07973), especially sections III and IV.3, directly distinguishes error-spin soft-constraint and stabilizer-spin constraint-free mappings. Its experiments use simulated annealing, a classical Digital Annealer, and CPLEX, not a D-Wave quantum annealer. It reports solver-dependent outcomes: constraint-free mapping helps its SA accuracy, whereas the Digital Annealer behaves differently and the constrained mapping can require fewer steps. This is useful evidence against inferring a universal solver-independent ordering, but supplies no QA performance verdict for our experiment.

[D-Wave, *Minor-Embedding: Best Practices*](https://docs.dwavequantum.com/en/latest/quantum_research/embedding_guidance.html) recommends short chains and balancing chain strength against problem range. Its guidance supports treating logical-variable savings, physical embedding cost, and coefficient scaling as separate quantities. A graph-fitting result is not a measured annealing speed or accuracy result.

## Independent executable audit

Run `python3 scripts/theory_checks.py` from this lab. It independently checks geometry/ranks and analytical counts, enumerates the smallest patch's full direct-model state spaces against residual-factor energies, verifies direct and dual ground projections against exhaustive original-error optimization, tests all reference gauges, and exhibits the insufficient-penalty counterexample. Results are saved in `results/theory_audit.json`. These checks validate mapping/proof identities, not large-code QA performance.

The completed audit passes 36 rectangular geometries, 16 full direct-energy cases containing 8,192 expanded assignments, and 128 reference-gauge comparisons. Repair-radius ground-fidelity checks cover every syndrome of four small geometries with positive and signed weights. The same script checks 96 saved physical programs across embedding seeds 11, 29, and 47 against the saved Zephyr graph, coefficient limits, signed coupling-group limits, and all physical ground states. This covers 57,728 consistent/full assignments and finds zero error in the raw consistent-state energy identities. It does not independently integrate the Schrödinger equation; the root experiment supplies its separate integration checks.

Review of the physical-dynamics implementation found no material correctness issue. The seed-11 embedding's only two-qubit chain contains an auxiliary parity variable, so its deterministic majority tie rule does not directly change the decoded error bits. Seeds 29 and 47 embed both models without chains, providing controls for the extra chain and its scaling cost. Three seeds improve the embedding comparison, but the physical test still uses only one tiny geometry and a sufficient, untuned chain strength where needed. Its dual model has just two spins per sector, so it cannot establish scaling or behavior of large frustrated domains.
