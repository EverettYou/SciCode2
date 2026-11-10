# Autonomous general-H evaluation-guided embedding research

Conduct an actual scientific follow-up to the attached problem. The user requests a closed loop: a theoretically justified inexpensive quality evaluation useful on ordinary structurally diverse sparse matrices H, used to guide more compact hardware-valid embeddings. Select your own scientific methods, meaningful regime, algorithms, public references and instance suite. No specific proof or construction is prescribed. Do not complete the round solely with a special toy comparison or a named-code structure. Keep correctness, meaningful nonvacuous evaluation coverage, guidance benefit, compactness and total computation cost distinct; report failures and tradeoffs.

This is continuing research, not a clean model/difficulty test. Prior Lab 002/003 artifacts may be reused read-only with hashes and attribution. No QPU access is available. All scientific outputs are English. Preserve prior labs and the benchmark's original problem/prompt.

Two-hour elapsed budget starts at 2026-10-16T08:02:44Z and ends at 2026-10-16T10:02:44Z. Preflight counts; do not reset or extend it. Produce code, a full mathematical argument, reproducible experiments, independent-checkable witnesses, and an honest report. Continue through implementation and validation; planning alone is not completion. Declare the physical model and what the evaluation actually guarantees. A certified bound is not automatically an ordering of actual annealing success. Reserve time for independent review and final saved artifacts. If the central loop remains unmet at the limit, report partial results explicitly.

The unchanged scientific question follows.

# SciCode 2: General Decoding-to-Annealer Embedding

**Scientific objective.** Develop a practical algorithm that starts from a sparse binary check matrix $H$, compiles the associated decoding problem into a quadratic annealing model, and rapidly constructs a valid embedding on D-Wave connectivity. Develop an efficient way to evaluate these embeddings and establish theoretically justified comparisons within a clearly stated quantum-annealing framework. The goal is a reusable algorithm, not a mapping tailored to one named code.

## Background

Parity-constrained decoding occurs in quantum codes and circuit-level detector error models. Ising-decoding and minor-embedding literature provide starting points [4-7], but a standard graph-minor call alone does not settle how to compile a general decoding matrix efficiently or which resulting embedding is better for annealing. D-Wave Advantage2 provides a concrete sparse target architecture [1-3]. No QPU access is required.

## Why this is unresolved

Sparsity of $H$ does not determine the interaction graph after quadratic reduction. Auxiliary choices, penalties and routing can change physical size, usable energy scale and the annealing Hamiltonian. Repeated syndromes and changing decoding windows also make compilation and update costs important. A shorter chain or smaller embedding need not imply better annealing dynamics. Exact quantum simulation can itself be expensive, so evaluating every candidate by full simulation may defeat the purpose of finding mappings quickly. The open challenge is to connect an efficient general construction to efficiently assessable, theoretically defensible notions of embedding quality.

## Research question

Develop an efficient algorithm that maps a general sparse binary decoding check matrix to a faithful quadratic model and a hardware-valid annealing embedding, together with an efficient evaluation method and theoretically justified comparisons of embedding quality within a stated quantum-annealing model.

The construction should accept general sparse matrices without assuming a code family. Theory may establish stronger guarantees on explicitly identified regimes; distinguish those assumptions from the algorithm's input interface. Global optimality or a universal ordering of all embeddings is not required.

## Input and decoding conventions

Let $H\in\mathbb F_2^{m\times n}$ be a sparse binary matrix, supplied in a sparse representation. Each column denotes a candidate error mechanism, and each row a parity check or detector. For binary mechanism activations $e$, the observed syndrome is $s=He$ over $\mathbb F_2$. Rows may be dependent and columns may affect more than two detectors. Do not assume planarity, geometry, translation symmetry, CSS structure, or a graphlike model in which each error touches at most two checks. Geometry or other metadata may support optional fast paths but is not required input.

$H$ defines the constraints, not the likelihood of errors. A complete decoding instance also supplies $s\in\operatorname{im}(H)$ and finite weights $w\in\mathbb R^n$. The required optimization is

$$C^*(H,s,w)=\min_{e\in\{0,1\}^n}\sum_{i=1}^n w_i e_i\quad\text{subject to}\quad He=s\pmod 2.$$

For independent error mechanisms with $0<p_i<1$, $w_i=\log[(1-p_i)/p_i]$ gives maximum-likelihood error-pattern decoding, up to an additive constant. Zero or negative weights are allowed. A single mechanism may flip many detectors; this does not require independence of the detector outcomes. Statistical dependence between mechanisms requires an explicit joint likelihood and is an extension of this additive objective, not something to infer from $H$ alone.

This interface includes detector error models [4] without requiring $H_X,H_Z$ or a stabilizer presentation. If logical outcomes are assessed, supply an observable map $O\in\mathbb F_2^{k\times n}$: mechanism $i$ flips the observables in column $i$. For a hidden error $e_{\rm true}$, a successful correction satisfies $H\hat e=s$ and $O\hat e=Oe_{\rm true}$. Neither the hidden error nor its true observable outcome is decoder input. $H$ alone does not define logical failure. Minimum-cost pattern decoding is distinct from maximizing total probability of an observable class.

No private dataset is needed. Researchers choose public decoding instances or reproducible sparse-matrix generators, valid syndromes and weights, and document their conventions. Toric codes, quantum LDPC codes and spacetime detector models are motivating applications, not mandatory family-specific formulations. Include structurally different sparse inputs when supporting broad claims; do not make one chosen family's special structure a hidden prerequisite.

## Algorithmic goal: from matrix to embedding

Given $H$, the instance data and a target graph $T=(V_T,E_T)$, produce a quadratic binary model $Q(y)$, a decoding projection $\pi(y)=e$, a minor embedding of its actual interaction graph, and programmed Ising coefficients with explicit offsets and scales. The same interface should handle different matrices and sizes. Representation, reduction, placement, caching, decomposition and recovery are research choices.

Prove that projected ground states of $Q$ are minimum-cost feasible corrections and that the reference optimum is attained. State penalty conditions and tie handling; a valid deterministic tie rule need not retain every tied optimum. Any elimination or decomposition must preserve the stated objective or identify its approximation and scope. Solving the decoding instance classically and then encoding its answer is not by itself a useful embedding algorithm; charge all preprocessing.

A valid minor embedding assigns each model variable a nonempty connected branch set in $T$, with pairwise-disjoint branch sets and a physical coupler realizing every nonzero quadratic interaction. Include isolated variables. Provide the physical coefficient allocation and chain constraints, and establish the energy relation for consistent branch sets. State separately when penalties guarantee faithful physical ground states. A sparse check incidence graph is not automatically the quadratic interaction graph to embed.

Efficiency is part of the result. Analyze construction time, memory and output size in terms of $m$, $n$, $\operatorname{nnz}(H)$ and target size, including auxiliary and routing overhead. Separate one-time matrix/target preprocessing from syndrome-dependent work. Also address reuse or updates when a decoding window changes $H$, weights or boundary conditions. State the update model and what must be recomputed; a full just-in-time logical-operation system is not required. Any causal window claim must specify the boundary information available and may not use future detector outcomes.

A fixed finite target may not fit every input. Distinguish certified resource obstructions from heuristic search failures. Seek useful efficiency and justified guarantees in declared regimes; rapid global optimization is not required.

## Target architecture

Advantage2 uses Zephyr connectivity [1]. The credential-free starting point is an ideal target generated by `dwave.graphs.zephyr_graph(g, t=4)` for a reported positive integer $g$ [2]. Save generator version, parameters and node/edge lists. Other target graphs or synthetic defects may be studied, but distinguish them from an actual device working graph. Code periodicity does not authorize extra hardware edges.

The hardware model must include coefficient ranges and any applicable coupling-group limits [3]. Without a device export, analyze them parametrically. All reduction penalties and chain couplings enter the rescaling calculation. Compare alternatives on the same target and physical programming constraints; report increases in hardware size separately from mapping improvements.

## What makes an embedding better?

Develop the evaluation method as part of the research. It must be computationally useful for selecting or improving embeddings, with its own time and memory cost characterized. Separate validity, physical resource cost, and annealing-relevant quality; do not collapse them into an unexplained score. Physical qubits, chain geometry and coefficient scale are useful descriptors but are not by themselves a proof of quantum-annealing superiority.

Make the physical comparison model explicit. A starting framework is a transverse-field Ising anneal [8], using normalized anneal coordinate $u$:

$$\mathcal H_{\mathcal E}(u)=-\frac{A(u)}{2}\sum_{q\in V_{\mathcal E}}X_q+\frac{B(u)}{2}\left(\sum_q h_q Z_q+\sum_{(q,r)\in E_{\mathcal E}}J_{qr}Z_qZ_r\right).$$

Here $\mathcal E$ includes the embedding and its coefficient allocation, $X_q,Z_q$ are Pauli operators, and $A,B$ set the driver and problem energy scales. State the schedule, physical normalization, initial state, runtime and, where relevant, temperature/noise or bath assumptions needed by the claimed comparison. Alternative justified annealing models are allowed. Static final-energy equivalence alone does not establish equivalence of the full annealing path.

Prioritize an analytical result that explains when one construction or embedding is preferable to another. This may be a comparison theorem, a rigorously justified bound or an efficiently checkable certificate linked to a stated annealing-relevant quantity. Its regime, assumptions and strength must be explicit. A conditional or partial ordering is sufficient; do not require one winner for every $H$. Identify whether a guarantee concerns static robustness, a low-energy effective description, or actual dynamics, and explain what supports the connection to annealing quality. Merely proving the usual minor-embedding validity conditions is insufficient for this part of the question.

The criterion and proof strategy remain open. If using spectral gaps, low-energy structure or transition bounds, account for degeneracy and the relevant subspace, and justify the inference to the claimed performance measure. A larger gap alone is not a general ordering of finite-time success. If an intuitive resource metric has no such ordering, a proved limitation or counterexample can help define a sounder criterion. The evaluation algorithm should expose uncertainty or return an inconclusive comparison when its conditions do not apply.

## Scope and approach

The core is general sparse binary decoding-to-annealer compilation and efficient, theory-supported evaluation. Methods and test instances are researcher-selected. No named code family, special geometry or full classical simulation of a large QPU is required. Public literature and software are allowed. There is no prescribed numerical target or fixed execution recipe. Windowed decoding motivates update efficiency; complete real-time integration and QPU measurements are later applications.

Numerical work may support or challenge theory on tractable cases. If using a classical simulation, specify what it models, its approximations and cost. Classical simulated annealing is not quantum dynamics; other simulation methods also require a justified interpretation. Large-scale faithful simulation of D-Wave hardware is not a prerequisite. Empirical search alone does not fulfill the theoretical comparison goal.

## Desired outputs and acceptance

1. A reusable matrix-to-model-to-embedding algorithm with mathematical fidelity guarantees, complexity analysis and a clear separation of preprocessing, per-syndrome and matrix-update costs.
2. An efficient embedding evaluation method, with a substantive theoretical comparison or certified limitation under a stated annealing model, and a clear account of what is and is not proved.
3. Reproducible source code and an English technical report. Supply independently checkable model/embedding witnesses and researcher-chosen examples supporting the claimed domain. Use public or fully specified inputs, dependency versions, commands and seeds. Compare with an appropriate automatic embedding reference when making algorithmic improvement claims [9].

A successful result connects a general matrix interface, a useful construction algorithm and theoretically supported quality evaluation. It need not prove global optimality, universal speedup or superiority on all inputs. Correctness checks and modest numerical illustrations support the result; they do not replace the algorithmic and theoretical contributions. No QPU run or hardware advantage claim is required.

## Expected outcomes

Sparsity-aware construction and reuse may reduce compilation cost without relying on a code-specific lattice. A cheap, certified quality criterion may guide mapping more effectively than raw chain length, while its limits may prevent a universal ordering. These are research hypotheses, not required positive findings or established results.

## Public references

[1] D-Wave, [Topologies](https://docs.dwavequantum.com/en/latest/quantum_research/topologies.html).

[2] D-Wave, [Zephyr graph generator](https://docs.dwavequantum.com/en/latest/ocean/api_ref_graphs/generated/dwave.graphs.zephyr_graph.html).

[3] D-Wave, [QPU Solver Properties](https://docs.dwavequantum.com/en/latest/quantum_research/solver_properties_all.html).

[4] Quantumlib, [Stim detector error model format and semantics](https://github.com/quantumlib/Stim/blob/main/doc/file_format_dem_detector_error_model.md).

[5] J. Roffe et al., [Decoding quantum error correction with Ising model hardware](https://arxiv.org/abs/1903.10254), arXiv:1903.10254 (2019).

[6] V. Choi, [Minor-Embedding in Adiabatic Quantum Computation: I. The Parameter Setting Problem](https://arxiv.org/abs/0804.4884), Quantum Inf. Process. **7**, 193-209 (2008).

[7] Y.-L. Fang and P. A. Warburton, [Minimizing minor embedding energy: an application in quantum annealing](https://arxiv.org/abs/1905.03291), arXiv:1905.03291 (2019).

[8] D-Wave, [Annealing Implementation and Controls](https://docs.dwavequantum.com/en/latest/quantum_research/annealing.html). Official documentation accessed 7 October 2026.

[9] J. Cai, W. G. Macready and A. Roy, [A practical heuristic for finding graph minors](https://arxiv.org/abs/1406.2741), arXiv:1406.2741 (2014).
