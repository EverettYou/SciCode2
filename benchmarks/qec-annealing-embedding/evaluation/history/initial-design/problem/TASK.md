# SciCode 2: Quantum Error-Correction Decoding on D-Wave

**Scientific objective.** Given a quantum-code check matrix and measured syndromes, discover an efficient, faithful translation into a quadratic annealing model and an embedding on D-Wave Advantage2 connectivity. Determine the useful tradeoffs between formulation, physical resource use, and hardware compatibility. The central challenge is scientific judgment about the representation and the graph it creates.

## Background and motivation

The supplied proposal [P] motivates quantum annealing for syndrome decoding. Roffe et al. [4] already relate quantum decoding to Ising hardware; Fujisaki et al. [5] and Takeuchi et al. [6] study Ising-based decoders on classical annealing systems. The new task focuses on check-matrix-to-hardware compilation and the evidence needed to justify an embedding before QPU access.

## Why this is unresolved

A parity-check matrix does not directly specify the quadratic graph programmed on an annealer. Auxiliary variables, equivalent constraints, and the choice of decoding representation can change its connectivity and coefficient scales. Embedding this graph introduces additional physical qubits and couplings. Reducing variable count can increase routing cost or suppress the useful energy scale after hardware rescaling. Periodic code boundaries and unavailable couplers complicate that tradeoff. Neither one automatic embedding nor good performance on a classical annealer establishes a good Advantage2 mapping. Offline analysis can establish correctness, graph feasibility and resource tradeoffs, but cannot determine the best physical annealing performance.

## Research question

Construct and validate resource-efficient quadratic encodings and minor embeddings of check-matrix-defined quantum decoding problems on D-Wave Advantage2 connectivity, and determine which formulation and embedding choices remain favorable under hardware constraints.

## Objective

Produce a reusable construction from code and noise specifications to a quadratic model, a valid embedding, and a justified comparison of alternatives. Seek a favorable resource-quality frontier within a stated classical search budget. A proof of global embedding optimality is not required; reserve “optimal” for a specified objective with a certificate.

## Mathematical problem and inputs

Use binary arithmetic over $\mathbb F_2$ for code relations. The required core is one error sector of a CSS stabilizer code. Supply $H_X\in\mathbb F_2^{m_X\times n}$ and $H_Z\in\mathbb F_2^{m_Z\times n}$ satisfying $H_XH_Z^T=0$. For X-error decoding set $H=H_Z$ and $G=H_X$; exchange them for Z errors. $\operatorname{row}(G)$ describes stabilizer-equivalent corrections. A lone $H$ defines syndrome constraints, but is insufficient to identify quantum logical equivalence without $G$ or equivalent code information.

Each decoding instance supplies a syndrome $s\in\operatorname{im}(H)$ and positive weights $w_i$. The reference optimization is

$$C^*(H,s,w)=\min_{e\in\{0,1\}^n}\sum_i w_i e_i\quad\text{subject to}\quad He=s\pmod 2.$$

For independent errors with $0<p_i<1/2$, $w_i=\log[(1-p_i)/p_i]$; uniform weights define minimum-weight decoding. State the noise model and tie rule. The decoder receives no true error or true logical class.

Supply or derive a logical-label map $L$ that is complete on $\ker H$, with $\ker(L|_{\ker H})=\operatorname{row}(G)$. If a hidden error is $e_{\rm true}$, a correction succeeds precisely when

$$H\hat e=s,\qquad \hat e\oplus e_{\rm true}\in\operatorname{row}(G).$$

Equivalently, for a syndrome-valid correction, require $L(\hat e\oplus e_{\rm true})=0$. Count an invalid correction or a missing output as a decoding failure. Exact error-string agreement is not the logical success criterion. Minimum-weight or most-likely-error decoding differs from degenerate maximum-likelihood decoding, which sums probability within logical classes; the latter is an optional extension, not an automatic property of QUBO minimization.

## Hardware and embedding contract

The target is a supplied graph $G_T=(V_T,E_T)$ and its documented programming limits. Advantage2 uses Zephyr; previous Advantage systems use Pegasus [1]. A generated ideal Zephyr graph, a synthetic graph with deleted nodes/edges, and an exported device working graph must be labeled separately. Save topology parameters, node and edge lists, software versions, provenance, and hashes. A concrete device claim requires its solver ID, graph ID or equivalent revision, and applicable coefficient and coupling-group limits [2]. No particular live QPU is assumed available.

Construct a quadratic model

$$Q(y)=c+\sum_u a_u y_u+\sum_{u<v}b_{uv}y_uy_v,\qquad y_u\in\{0,1\},$$

with a documented projection $\pi(y)=e$. Prove that projecting its ground states gives exactly the minimum-cost feasible corrections, allowing auxiliary degeneracy. Include any penalty conditions and recoverable offsets and scale factors. A higher-order parity expression is not itself the required QUBO. Auxiliary variables and all nonzero interactions count toward the model cost.

Embed the actual quadratic interaction graph. Each variable maps to a nonempty connected, pairwise-disjoint branch set in $G_T$; every logical interaction must have a physical coupler between its branch sets. Include isolated variables. Report physical biases, couplings, chain constraints and the conversion to the programmed Ising convention. For consistent branch sets, the physical energy must reproduce the logical energy up to a known positive scale and constant. Justify any stronger claim about physical ground-state equivalence. Coefficients must obey the supplied hardware limits after all penalties and chain couplings are included. If limits are unavailable, report conditional feasibility and a parameterized scale analysis.

## Scope and approach

Work offline on code-capacity decoding with perfect syndrome measurements and independent binary noise in the required CSS sector. Include a toric-code family with periodic boundaries [8] and at least one non-toric CSS family supplied through the same matrix interface. Choose tractable sizes and extend them until the relevant resource limitation becomes visible. Use exact small cases and matched-budget alternatives to expose the formulation/embedding tradeoff. All encoding, preprocessing, embedding search, and sample-recovery methods are open choices. General stabilizer codes, correlated Pauli noise, noisy syndrome histories, and decomposition may be investigated as explicitly labeled extensions. No QPU run, hardware speedup, decoding threshold, real-time latency, or neural-decoder training is required in this phase.

## Evaluation and evidence requirements

- **Correctness:** independently check binary code relations, syndrome validity, logical equivalence, quadratic reduction and embedding validity. Use exact small-instance optimization or enumeration to verify the ground-state projection, including ties and auxiliary states. Uncertified larger cases remain labeled heuristic.
- **Embedding quality:** compare against a reproducible automatic Ocean/minorminer baseline [3,7] under a comparable offline search budget. Separate formulation changes from embedding changes through controlled comparisons. Report physical-qubit count, total/maximum/distribution of branch-set sizes, physical couplers, construction/search time, peak memory, achieved coefficient scale and failures. Explain tradeoffs; no single chain-length score defines universal quality.
- **Generalization:** preserve all toric wraparound checks and logical sectors. Report code family, matrix ranks, sizes, weights, random seeds and topology revision. Test independent syndrome sets and document whether the embedding is reused or recomputed, charging both initial and amortized costs. Geometry may help but is optional input; do not replace the matrix-defined code with a more convenient one.
- **Sample recovery:** specify how broken-chain or excited samples would become corrections. At minimum, audit the proposed rule on controlled offline samples and report results before and after recovery, including runtime and syndrome failures. Classical samples and artificial perturbations are diagnostic controls, not measurements of QPU error rates. A local minimum is not necessarily a global minimum or a successful correction.
- **Fair decoding comparison:** where decoding quality is assessed offline, compare identical syndromes, noise models, weights, information and budgets against an appropriate classical decoder and a classical optimizer on the same quadratic model. Report logical failure rate with uncertainty separately from optimization success, energy gap and syndrome feasibility. Charge post-processing and restarts.

The research may find a favorable construction, a tradeoff with no universal winner, or a reproducible capacity or robustness limitation. Any conclusion must be supported at the claimed scale. Failed embedding searches do not prove non-embeddability. No globally optimal embedding, quantum advantage, or QPU sampling distribution may be inferred from offline proxies.

## Deliverables and acceptance

1. A documented matrix-to-model construction, mathematical justification, and reusable code under `src/`, with reproducible instances and scripts.
2. Portable quadratic models, projections, embeddings, hardware manifests and independent validation results, including a boundary-correct toric example suitable for technical review with D-Wave.
3. Machine-readable resource and correctness comparisons, figures showing the resource-quality frontier, and an English research note explaining the main scientific choices and limitations.

Success means a reproducible, independently validated construction and evidence-supported tradeoff or limitation on the declared instance suite and budget. The organizer will freeze public numerical budgets and any performance target after a separate reference pilot; none is invented here. This is currently a research-design benchmark, not yet a calibrated scored test. This opening deliverable contains the specification and literature review only; implementation and numerical experiments await a subsequent user instruction.

## References

[P] Y.-Z. You and Y. Hu, *A quantum decoder for quantum error correction*, user-supplied proposal, draft v0.1, 9 September 2026, pp. 2-4. [Preserved PDF](references/DWaveProposal.pdf).

[1] D-Wave, [Topologies](https://docs.dwavequantum.com/en/latest/quantum_research/topologies.html), accessed 7 October 2026.

[2] D-Wave, [QPU Solver Properties](https://docs.dwavequantum.com/en/latest/quantum_research/solver_properties_all.html), accessed 7 October 2026.

[3] D-Wave, [Ocean embedding composites](https://docs.dwavequantum.com/en/latest/ocean/api_ref_system/composites.html), accessed 7 October 2026.

[4] J. Roffe et al., [Decoding quantum error correction with Ising model hardware](https://arxiv.org/abs/1903.10254), arXiv:1903.10254 (2019).

[5] J. Fujisaki et al., [A Practical and Scalable Decoder for Topological Quantum Error Correction with Digital Annealer](https://arxiv.org/abs/2203.15304), arXiv:2203.15304; Phys. Rev. Research **4**, 043086 (2022).

[6] Y. Takeuchi et al., [Comparative study of decoding the surface code using simulated annealing under depolarizing noise](https://arxiv.org/abs/2311.07973), arXiv:2311.07973v2 (2023).

[7] J. Cai, W. G. Macready and A. Roy, [A practical heuristic for finding graph minors](https://arxiv.org/abs/1406.2741), arXiv:1406.2741 (2014).

[8] E. Dennis et al., [Topological quantum memory](https://arxiv.org/abs/quant-ph/0110143), J. Math. Phys. **43**, 4452 (2002).
