# Research review: decoding formulations and Advantage2 embedding

Reviewed 7 October 2026. This public-source literature and design memo accompanies the method-open [task](TASK.md). It contains no implemented decoder, measured embedding or QPU result. The task itself is standalone and does not depend on this memo.

## Research context

The application is syndrome-constrained quantum decoding; the central question is the joint cost of a faithful quadratic representation and its hardware embedding. Public Ising-decoding work supplies precedents, while the benchmark directly states its mathematical objective and inputs. No unpublished proposal or earlier private solver run is evidence for the task's claims. Later neural distillation and learning loops are outside the required scope.

## Hardware architecture and the graph to target

| Generation | Topology | Nominal maximum degree | Relevance |
| --- | --- | ---: | --- |
| D-Wave 2000Q | Chimera | 6 | Historical reference |
| Advantage | Pegasus | 15 | Prior-generation comparison |
| Advantage2 | Zephyr | 20 | Required target family |

D-Wave's [topology documentation](https://docs.dwavequantum.com/en/latest/quantum_research/topologies.html) identifies these generations. A bulk Zephyr qubit has 16 orthogonal internal connections, two collinear external connections and two odd connections; boundary degrees are smaller. Native K4 and K8,8 subgraphs do not imply arbitrary dense connectivity. A drawing is only an aid: node IDs and allowed edges define the embedding target. The device working graph excludes unusable components and can change with calibration.

The [Zephyr graph API](https://docs.dwavequantum.com/en/latest/ocean/api_ref_graphs/generated/dwave.graphs.zephyr_graph.html) specifies coordinates (u,w,k,j,z), with u in {0,1}, 0 <= w < 2m+1, 0 <= k < t, j in {0,1}, and 0 <= z < m. Counting these tuples gives 4tm(2m+1) nodes. With t=4, Z12 has 4,800 ideal nodes; this arithmetic is not a claim about a particular available QPU. The current public API is dwave.graphs.zephyr_graph(m, t=4); dwave-networkx is deprecated. Record the actual generator and package version. Use the authoritative generator or explicit edge list, not an AI-reconstructed lattice from a schematic.

The [QPU properties](https://docs.dwavequantum.com/en/latest/quantum_research/solver_properties_all.html) distinguish actual working qubits/couplers, topology, h and J ranges, and Advantage2 per-group coupling limits. Example values in documentation are not a device contract. A defensible device-specific analysis needs a timestamped solver/graph identity, node/edge export, field/coupler limits, coupling-group membership and limits, supported scale rules, and provenance. Chain penalties enter these limits too. With no export, the first benchmark can study reproducible ideal Zephyr sizes and explicitly synthetic defect models. Synthetic defects must not be described as measured device yield or a substitute for the future target export.

The [Stride documentation](https://docs.dwavequantum.com/en/latest/industrial_optimization/leap_hybrid.html) confirms that Stride is the hybrid nonlinear solver. CQM is a distinct [hybrid service](https://docs.dwavequantum.com/en/latest/industrial_optimization/dwave_hybrid.html). Direct QPU QUBO/Ising work exposes the connectivity question; hybrid-service performance by itself does not identify an explicit embedding to audit. No broad solver-superiority claim is needed for this benchmark.

## Literature map and what transfers

| Source | Relevant contribution | Boundary of evidence |
| --- | --- | --- |
| [Roffe et al., 2019](https://arxiv.org/html/1903.10254), especially Secs. II and IV | Ising representation of quantum decoding; inference and reusable problem structure | Its derivation and numerics do not certify an Advantage2 embedding |
| [Fujisaki et al., 2022](https://arxiv.org/abs/2203.15304) | Stabilizer decoding as QUBO and surface-code experiments | Fujitsu Digital Annealer is classical hardware, not a D-Wave QPU |
| [Takeuchi et al., 2023](https://arxiv.org/html/2311.07973v2), Secs. II and IV | Constrained and constraint-free representations; solver-dependent tradeoffs under depolarizing noise | Better behavior in SA or Digital Annealer does not predict quantum sampling |
| [Cai, Macready and Roy, 2014](https://arxiv.org/abs/1406.2741) | Practical heuristic graph-minor search | A heuristic success is a witness, a timeout is not a nonexistence proof |
| [Dennis et al., 2002](https://arxiv.org/abs/quant-ph/0110143) | Topological decoding, homology and periodic code structure | Its statistical-mechanics mapping does not choose a hardware embedding |
| [Vinci et al., 2015](https://arxiv.org/abs/1507.02658) | Chain/encoding penalties and energy-based sample recovery | Protecting an annealer's optimization is distinct from using an annealer to decode another quantum code |

Roffe et al. explicitly observe that a syndrome can change coefficients while leaving the interaction structure fixed. This motivates amortizing compilation over many syndromes, if the chosen formulation actually has that property. They also distinguish inference based on a single likely pattern from inference using a distribution. The present task consequently separates the required minimum-cost optimization objective from optional logical-class posterior inference.

Fujisaki et al. provide a concrete precedent for QUBO-based surface-code decoding. Their reported scaling and threshold belong to their chosen Digital Annealer setup, code and noise assumptions. They establish neither a general quantum advantage nor routing costs on Zephyr.

Takeuchi et al. compare soft-constraint error variables with a representation built around stabilizers and logical choices. Their results show that formulation affects accuracy and iteration count differently across classical solvers. The lesson for the new question is to compare full representations and their induced graphs, rather than tuning a single graph as though it were mathematically forced. Their correlated depolarizing setting must not be silently replaced by independent X/Z sectors when comparing results.

Ocean's [EmbeddingComposite](https://docs.dwavequantum.com/en/latest/ocean/api_ref_system/composites.html) defaults to minorminer.find_embedding and computes a new embedding on each sample call. Its fixed/lazy variants allow reuse. Record the actual installed implementation, parameters and randomness. An unspecified “Ocean default” from a prior run cannot establish either poor quality or optimality. The automatic path is a reproducible reference candidate, not a guaranteed optimum.

## Mathematical distinctions that shape the benchmark

These are design deductions, not measured findings.

1. **Check constraints and quantum equivalence need different information.** For one CSS sector, H determines valid syndrome patterns and G determines stabilizer equivalence. Their quotient ker(H)/row(G) supplies logical sectors. A logical-label map is useful for evaluation but the hidden true sector must never be decoder input. For a general non-CSS code, a symplectic check convention and a joint Pauli likelihood are required; a plain n-column binary syndrome problem is not sufficient.
2. **A parity penalty is generally higher order.** Under e_i=(1-z_i)/2, the violated-check indicator for row a is (1-(-1)^(s_a) product_{i:H_ai=1} z_i)/2. A check of weight r therefore has an r-spin term. The faithful quadratic construction and its ground-state proof are part of the research.
3. **Equivalent encodings can have opposite hardware tradeoffs.** A squared integer parity constraint can couple every pair in a check's support, whereas a factorized parity construction can trade additional variables for more local interactions. Binary versus unary auxiliary choices also change coefficient scales. A syndrome-satisfying parameterization can eliminate penalties but turn a sparse check description into a dense interaction model, and must cover every logical sector. These are candidate directions, not assigned algorithms or a recommended solution.
4. **The Tanner graph is not automatically the QUBO graph.** Quadratic reduction can introduce edges between error variables and auxiliaries, or eliminate original checks entirely. Embed every nonzero quadratic interaction and retain isolated variables. Comparing embeddings without fixing or recording the source graph confounds formulation with placement.
5. **Toric boundaries constrain correctness, not the visual layout.** On the standard d by d toric CSS code, n=2d^2 and each sector has two independent logical labels. Every periodic seam check belongs to H. Stabilizer-only variations of one representative generally omit other logical classes. Deleting seam couplings changes the code; cutting a visual drawing does not. The same matrix may be relabeled or transformed only with a reversible mapping back to the stated objective and logical labels.
6. **Smaller chains are a proxy, not a hardware-performance ordering.** Chain geometry, coupler allocation and required penalties interact with dynamic range. For a connected branch set of a physical qubits on a degree-Delta target, at least a-1 internal edges are necessary, leaving at most (Delta-2)a+2 outgoing edge incidences. Thus a variable of source degree d needs at least ceil((d-2)/(Delta-2)) physical qubits, or one if that bound is smaller. This elementary necessary bound can support tiny-case certificates, but says nothing about collective routing sufficiency or QPU success.
7. **Static energy faithfulness has a precise limit.** On consistent chains, a positive affine relation between embedded and logical energy can be checked. Preventing broken-chain physical ground states requires an additional justified penalty condition. Classical or synthetic low-energy samples cannot establish the population, effective temperature or excitation structure of a real QPU.

## How to study “best embedding” without QPU access

The practical offline object is a Pareto set of correct constructions under a measured search budget: physical qubits, chain tails, required coefficient scale, construction/reuse time, and graph-defect sensitivity. This is an inference from the representation and hardware constraints above, not an assertion that these metrics predict a unique physical winner. First establish exact small-case correctness and export verifiable witnesses. Then compare a fixed formulation under different embeddings, and compare formulations under comparable embedding budgets. Test fixed-code embedding reuse separately from per-syndrome reconstruction. Report unsuccessful searches, auxiliary and chain penalties, all classical post-processing, and conditional feasibility when device limits are missing.

The revised goal prioritizes a reusable efficient algorithm and theoretical quality comparison; any later lab should support that goal rather than make synthetic sampling the principal objective. A good technical-review package for D-Wave would include representative H/G matrices and weights, the logical interaction graph, all variable-to-chain maps, physical coupler assignment, scale/penalty reasoning, periodic-seam treatment, resource distributions across independent seeds, and the exact target manifest. That package can make a concrete recommendation reviewable even before hardware sampling.

Questions to take to D-Wave after the offline study: Which timestamped Advantage2 graph and coupling limits should be used? Are there preferred Zephyr placement or chain-allocation practices for these graph families? Are apparently favorable chain/scale tradeoffs known to behave poorly on this device? Which chain recovery and local-improvement procedures are suitable controls once real samples are available? These are future review questions; no external message is authorized or sent.

## Current evidence and limits

The literature establishes prior Ising/QUBO decoding work and public topology/API contracts. Novelty of a specific future algorithm is not established by this initial review. No code family size has been shown to fit, no chain distribution has been measured, and no embedding is claimed optimal. The current interface is a general sparse binary H, with syndrome and additive mechanism weights; no CSS or graphlike structure is required. An observable map is optional for logical evaluation. Windowed detector matrices are intended applications; correlated-mechanism likelihoods and full real-time integration need explicitly richer specifications. Public scored-test targets, instance counts and numerical budgets remain uncalibrated until a later pilot.

## General-H and theory-first refinement

Revision 0.3-general-H supersedes the earlier CSS-specific framing in illustrative deductions above. [Stim's public detector-model semantics](https://github.com/quantumlib/Stim/blob/main/doc/file_format_dem_detector_error_model.md) define independent mechanisms by detector and observable flips, motivating an H/s/weights/optional-O interface. Columns can represent multi-detector events; a matching-graph assumption is unnecessary.

[Choi's parameter-setting work](https://arxiv.org/abs/0804.4884) and [Fang and Warburton's minor-embedding energy study](https://arxiv.org/abs/1905.03291) provide relevant analytical precedents. They do not supply a universal embedding ranking for the present task. [D-Wave's annealing Hamiltonian](https://docs.dwavequantum.com/en/latest/quantum_research/annealing.html) supplies a concrete physical comparison framework. The research must choose and justify its own efficient criterion and specify whether its guarantee concerns static robustness, a controlled effective model, or dynamics. These are formulation deductions, not new scientific findings.
