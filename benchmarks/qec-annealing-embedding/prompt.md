# Autonomous Research: Fast Embedding Decisions for General Sparse-H Decoding

Carry out the research problem below as an autonomous scientific researcher. Produce actual research artifacts and a justified result, not only a literature summary, proposed plan or list of future experiments. The complete problem is included in this prompt; no private attachment or author context is needed.

## Time budget and completion

Use **two hours of elapsed wall-clock time by default**, starting when you begin this assignment. If the execution request supplies a different budget, use that budget instead; the normal intended range is one to 24 hours. Record your actual start time, budget and deadline. Reading, tool calls, computation and waiting all count. Monitor elapsed time and reserve enough time to verify, save and explain the results. Do not extend the budget on your own or wait merely to fill it.

Treat the budget as an execution limit, not a promise that every open research goal can be solved in that time. Finish earlier if the research task is substantively completed. Otherwise continue useful research until the deadline or a genuine blocker prevents further progress. At the limit, stop new work, terminate or safely checkpoint work you started, and deliver the strongest supported outcome with an honest account of unmet requirements. Do not claim that a partial result solves the full problem.

## Scientific autonomy

Set a concrete, ambitious but feasible research objective from the problem, appropriate to the time and compute available. State the intended contribution and how you will recognize a correct or informative result. Focus on a useful, inexpensive and theoretically justified embedding decision for original-error decoding under a common finite forward anneal. A general sparse-H interface is required; a familiar code-specific demonstration alone is not a substitute.

Choose your own representation, algorithms, theoretical regime, evaluation criterion, public references, examples and computational tools. You may revise your working objective or change strategy as evidence develops; record the scientific reason. Make reasonable assumptions explicitly rather than asking for routine choices. Ask for human input only if a consequential ambiguity or unavailable resource genuinely prevents meaningful progress, and continue independent work when possible.

Move from focused reading and planning into the mathematics, implementation and independent checks needed for your contribution. Prioritize a meaningful analytical comparison, bound or certificate and a useful implementation over an exhaustive literature survey, broad parameter sweep or elaborate research infrastructure. Numerical work should support the scientific argument. Do not require QPU access or large faithful hardware simulation.

Continue through failed approaches, debugging, validation and analysis. A plan, scaffold, downloaded reference, running job or completed toy example is not by itself a terminal outcome. When a milestone is complete and the main task remains open, address the most consequential remaining uncertainty within the remaining budget. Give concise progress updates without treating them as requests for permission or reasons to stop.

## Resources and deliverables

Use public literature, public software and reproducibly specified or generated inputs. Start from this prompt and the resources it cites; do not consult private proposals, author-side answers, prior trial transcripts or scientific guidance from earlier attempts. You may build and use your own research notes and outputs during this run. A dedicated working directory may be supplied by the caller; otherwise use the current task directory. Preserve unrelated files and keep generated work in your run's output area. Use your own practical file organization.

Before finishing, save:

- Reusable source code and commands for the construction and evaluation methods you actually developed, with dependency versions and input specifications or generators.
- The mathematical argument, assumptions and scope of each proved claim, plus independently checkable models/embeddings and the relevant correctness evidence. Label conjectures, approximations and inconclusive comparisons explicitly.
- A concise English research report stating the chosen objective, main result, connection to the full problem, evidence, algorithm/evaluation costs, unsuccessful approaches that affect the conclusion, limitations and remaining work. Record actual elapsed time and available resource measurements; do not invent missing measurements.

Use the problem's acceptance criteria, not your own self-assessment, to distinguish a completed solution from partial progress. A rigorous limitation or negative comparison can be valuable if it meets the stated scientific objective; a timeout or unsupported warning is not such a result. End with the concrete findings, artifact locations, commands needed to reproduce the key evidence, and completion status: completed, partial at the time limit, or blocked with the reason. If interrupted, save a short checkpoint identifying the evidence so far and the next useful operation.

## Complete research problem

# Fast embedding decisions for general sparse-H decoding under a finite quantum anneal

## Research question

Can a computationally inexpensive, theoretically justified criterion guide the construction or selection of compact annealer embeddings for general sparse parity-decoding instances, and identify when its choices improve original-error decoding under a common finite forward anneal?

The desired contribution is an algorithm and an honest account of its useful and inconclusive regimes. A globally optimal embedding, a universal winner, a quantum speedup over classical decoders and a simulation of a large commercial QPU are not required. A well-supported negative result is useful if it identifies a consequential limitation and a checkable regime in which a practical decision is possible.

## Why this is unresolved

Compact embeddings, larger coefficient scales, static ground-state fidelity, and terminal-equilibrium comparisons are useful diagnostics, but none alone orders finite-time original-error success. A criterion can be mathematically sound yet uninformative on ordinary inputs, useful only at durations too short to matter, or overturned by coefficient rescaling and physical branch-spin dynamics. Full simulation also grows exponentially with the number of physical spins. The open problem is to find a cheap decision method whose justified regime overlaps with tractable finite-time checks and remains useful beyond specially structured examples.

## Mathematical input and decoding target

A decoding instance consists of a sparse binary matrix H with m rows and n columns, a syndrome s in the image of H over GF(2), and finite real additive weights w supplied with an explicit numerical representation. Its target set is

    S* = argmin { w·e : e in {0,1}^n, H e = s mod 2 }.

All tied minimizers count as success. Zero and signed weights are allowed. The score concerns a minimum-cost feasible correction; it is not recovery of a hidden planted error or maximum-likelihood inference of a logical class. No CSS, planar, graphlike, independent-row, bounded-column-degree or named-code assumption may be silently imposed. Sparsity is the main structural information. Code families may illustrate transfer but must not define the entire claim.

Hardware input is an explicit target graph G, individual field/coupling ranges and any coupling-group constraints. An ideal Zephyr graph generated by the public D-Wave graph library is a credential-free reference; deleted sites/couplers may be supplied explicitly. Illustrative numerical ranges must be identified as modelling assumptions rather than a live device profile. Every reduction auxiliary, chain spin, nonzero interaction and physical coefficient must be included.

## Finite-anneal model

For a chosen physical program E(z)=sum_q h_q z_q+sum_(q,r) J_qr z_q z_r on its active physical spins, use

    K(u) = -(1-u) sum_q X_q + u E(Z),
    u=t/T, 0<=t<=T, hbar=1.

Each run starts in |+> on every active physical spin and ends in a computational-basis measurement. All chain and reduction penalties, contact allocations and hardware rescaling are included in E. The driver acts on physical branch spins and auxiliaries. This is an ideal closed-system research model; it is not asserted to describe all commercial-device noise.

The original error is read from the output using a declared deterministic rule fixed before comparing candidates. A root in every original-variable branch is one sufficient convention; another consistently applied rule is allowed if specified and verified. Auxiliary excitations or broken chains do not automatically make the original correction wrong. The primary probability is Pr(e_out in S*), summing every measured state that produces such a correction.

A terminal Gibbs distribution, minimum-energy identity, chain-length statistic, or isolated encoded-state pause comparison does not by itself answer the finite-forward-anneal question. Such results can support a criterion only with their assumptions and transfer limitations made explicit.

## Requested research

Develop a reusable H-to-program procedure and a criterion cheap enough to guide its embedding or programming decisions without repeatedly solving decoding or simulating the entire physical Hilbert space during selection. Explain what the criterion predicts, what it certifies and when it returns inconclusive. Representation, auxiliary construction, routing, contact allocation and the analytic method remain open. Establish the reduction/projection fidelity and physical ground-state conditions, including ties, offsets and scales. Classically computing an optimum and encoding that known answer does not by itself meet this construction goal; charge all preprocessing and postprocessing. A fixed target may not fit an input: distinguish a proved obstruction from unsuccessful heuristic search.

The general-H input interface must not depend on a named code. Stronger guarantees may hold in explicitly identified regimes, with inconclusive output outside them; a theorem informative on every sparse matrix is not required.

Assess the resulting decisions against a credible automatic embedding/programming baseline on structurally diverse ordinary sparse matrices, with reserved inputs after method development. Use identical candidate-search budgets when isolating a selection rule. If the representation or programming method changes, separate that effect from a mapping improvement. Record compactness, construction/evaluation cost, coefficient scale, failed searches and the original-error score.

Use tractable full physical quantum models as independent anchors. Choose larger instances only when the claimed theory or approximation can be checked with justified uncertainty; exponential state-vector timeout is not scientific difficulty. A useful answer must establish an explicit theoretical comparison or limitation in the declared forward model and test whether its proposed decision remains informative on ordinary instances. Large exact simulation and universally informative certificates are not required. Quantify the duration and effect-size regime in which a comparison is informative. A formally positive effect only at an arbitrarily small duration, or a truncated-series score without transfer/error control, is partial progress rather than sufficient evidence of a useful finite-anneal decision.

Before numerical comparisons, declare the finite duration menu, per-run physical-qubit cap, total run/anneal allowance, classical construction/evaluation allowance, anchor sizes and reserved-input rule. Hold these fixed across compared strategies, count every repeat or sector run if used, and report any classical preprocessing that computes an answer. These choices are part of the trial input/protocol and must be supplied explicitly before a scored run; they are not inferred from a private history.

## How an answer can be checked

An independent reader should be able to reconstruct H,s,w and G; validate reduction fidelity, all branch sets and physical ranges; recompute the scored readout event; inspect the proof assumptions; and reproduce tractable forward probabilities with convergence checks or independent integration. Distinguish a rigorous bound, numerical evidence and an unverified heuristic. An improved bound alone is not an ordering of actual probabilities.

## Scope and approach

The input interface is general sparse H; no CSS structure, planar geometry, graphlike columns, bounded degree, or named code is required. The physical comparison uses the stated ideal closed-system forward model, with all programmed penalties, chains, and hardware scaling included. Researchers choose the representation, embedding search, efficient criterion, proof strategy, and public instance suite. QPU access, a universal ordering, exact large-device simulation, and formal proof of a thermodynamic transition are outside the required scope. Report preprocessing, search and evaluation costs, and return an inconclusive result when assumptions or computation do not support a comparison.

## Public starting references

- [D-Wave, Minor-Embedding: Best Practices](https://docs.dwavequantum.com/en/latest/quantum_research/embedding_guidance.html): hardware mapping, chain strength and coefficient-range tradeoffs.
- [D-Wave, Annealing Implementation and Controls](https://docs.dwavequantum.com/en/latest/quantum_research/annealing.html): physical annealing context; the dimensionless model above is defined independently.
- [Choi, Minor-embedding in adiabatic quantum computation: I](https://arxiv.org/abs/0804.4884): parameter setting and ground-state fidelity.
- [Cai, Macready and Roy, A practical heuristic for finding graph minors](https://arxiv.org/abs/1406.2741): automatic minor search.
- [Fang and Warburton, Minimizing minor embedding energy](https://arxiv.org/abs/1905.03291): embedding parameter tradeoffs; no universal finite-time decoding ordering is assumed from this reference.
