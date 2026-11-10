# Validated implementation entry points

Canonical experimental source remains versioned with its evidence under labs; no duplicate library copy is maintained here.

- [General sparse-H constructor](../labs/lab-004-general-h-evaluation-embedding-loop/scripts/construct.py): sparse rows, syndrome and weights → faithful QUBO → automatic Zephyr embedding candidates → terminal-Gibbs-certified physical program. Optional target/group/range manifests are explicit. No code-family label or decoding solution is required.
- [Tree-load evaluator](../labs/lab-004-general-h-evaluation-embedding-loop/scripts/evaluator.py) and [Contact allocation LP](../labs/lab-004-general-h-evaluation-embedding-loop/scripts/lp_allocator.py) implement the new evaluation-guided programming loop.
- [Independent saved-witness audit](../labs/lab-004-general-h-evaluation-embedding-loop/independent/audit_programs.py) checks actual coefficients and embeddings without importing the scientific compiler/evaluator.
- [General compiler](../labs/lab-002-agent-test-general-h/scripts/compiler.py) and [target/embedding adapter](../labs/lab-002-agent-test-general-h/scripts/embedding.py) are reused read-only with recorded dependency hashes.

The guarantee covers static fidelity and declared terminal equilibrium. Heuristic search can fail; a certificate may be inconclusive. No general finite-time QA performance or changing-window latency guarantee is provided. See the [stable takeaway](../note/general-h-tree-gibbs.md) and [Lab 004 report](../labs/lab-004-general-h-evaluation-embedding-loop/REPORT.md).

## New general-H readout and quantum-forward primitives

[Lab005](../labs/lab-005-general-h-annealing-relevance/REPORT.md) supplies validated additional entry points, kept with their primary evidence:

- [Weighted repair witness](../labs/lab-005-general-h-annealing-relevance/independent/penalty_bound.py): sparseH/weights → exact GF2 right-inverse witness, repair loads and sufficient penalty. No minimum-weight decoding is performed.
- [Balanced compiler](../labs/lab-005-general-h-annealing-relevance/scripts/models.py) and [endpoint evaluator](../labs/lab-005-general-h-annealing-relevance/scripts/thermal.py): general-H faithful construction and soft-parity readout certificates, with explicit extra hardware cost.
- [Sparse quantum moments](../labs/lab-005-general-h-annealing-relevance/independent/forward_moments.py): physical program and original-root affine characters → T²/T⁴ feasibility/conditional-cost coefficients without state-vector simulation.
- [Actual finite-forward optimum comparison](../labs/lab-005-general-h-annealing-relevance/independent/forward_certificate.py): conservative exact-rational short-time theorem for fixed-coupler amplification. It often certifies only tiny durations.
- [Local-observable finite-time certificate](../labs/lab-005-general-h-annealing-relevance/independent/local_forward.py): exact-rational unconditional original-cost comparison using local strength; this is a different observable from decoding success.
- [Compact mapping selector](../labs/lab-005-general-h-annealing-relevance/independent/moment_selection.py): concrete T^4-guided selection under a baseline qubit cap. Finite-time joint-event quality remains heuristic.

All interfaces preserve their scientific scope and may return inconclusive. See the [readout/forward synthesis](../note/general-h-readout-and-forward.md); no practical general finite-time decoding or live-QPU performance guarantee is claimed.

- [Certified cross-mapping event evaluator/selector](../labs/lab-005-general-h-annealing-relevance/independent/certified_mapping.py): exact projected T²/T⁴ and scalar word-tail bounds → actual original-optimum event comparison across different physical embeddings, with no decoding oracle. The implemented ordinary-input loop is useful only in the declared early-time mathematical regime; standard-compiler coverage is inconclusive.

- [Necessary-optimality LP](../labs/lab-005-general-h-annealing-relevance/standard_extension/scripts/optimality_lp.py) tightens the actual-event bound with exact dual witnesses; [feasible upper-witness control](../labs/lab-005-general-h-annealing-relevance/standard_extension/scripts/witness_followup.py) separates zero-search particular cost from charged bounded classical search. The resulting standard-compiler gains cover only3/24 inputs, all at n16; larger cases remain inconclusive.
