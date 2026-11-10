# Pre-result protocol (2026-10-16)

The method is a rooted-tree repair bound for all chain defects, followed by coefficient allocation and evaluation-guided qubit deletion. No decoding solutions are used to construct embeddings.

Models: sparse parity matrices with (1) uniform random degree-four rows, (2) irregular degree 2–7 rows and hub columns, (3) banded degree-four rows with long-range rewiring, (4) graph incidence augmented with degree 3–6 hyperchecks and dependent rows. Main original-variable sizes 16, 32, 64; m approximately n/2. Each family/size has development seed 1101 and held-out seeds 2203,3307. Development and held-out labels are frozen before running. All weights are dyadic in [-0.5,1.5], with injected zero and negative weights; syndromes are generated from a random error vector. No named code geometry is required.

Target: same ideal Zephyr g=6,t=4 for every run; no extra edges or QPU. Main parametric programming bounds h in [-4,4], J in [-1,1], signed coupling-group sums in [-13,10], with actual Ocean ideal-Zephyr groups saved. These are an illustrative declared model, not device-export properties. Sensitivity β=5,10,20,40; main β=20 in units where problem Hamiltonian equals programmed Ising energy. Allowed chain-defect probability ε=0.05. A small separate validation grid will enumerate arbitrary frustrated physical models and quantum thermal matrices.

Candidate budget: eight automatic minorminer seeds per instance, timeout 5 seconds per seed, tries=2. Controls use exactly the same proposal pool. Reference: first valid automatic embedding; size-only: smallest pool candidate; random: first valid (seed order fixed). Guided selection minimizes physical qubits subject to the certified effective scale meeting at least the first-valid scale; if no smaller candidate qualifies retain first valid. A second Pareto summary retains all qubit/scale tradeoffs. All candidates use the same proposed improved allocator so selection gains are distinct from allocator gains. Standard total-load chains are a separately labeled physical-allocation baseline.

Refinement: propose one-qubit deletions in each branch, requiring connectivity and every logical contact to survive. Evaluate candidates using the certificate; accept deletions retaining the frozen first-valid certified scale floor. Size-only pruning accepts every graph-valid deletion. Deterministic deletion order and one pass are frozen. Report both compactness versus already compact automatic embedding and changes in scale versus unconstrained pruning. Equal proposal-count controls will choose between the same graph-valid deletion proposals; extra validity/evaluation cost is charged.

Success requires valid compilation/embeddings, nonvacuous certificate at β=20 on at least 75% of successful routine instances, and some compactness improvement over first-valid automatic mapping without sacrificing the reference scale or 95% consistency certificate. Stronger claims require held-out gains, the unconstrained size-only comparison and actual total timings. A bound does not order actual chain-break probability, decoding success or finite-time quantum dynamics.

The model guarantees concern terminal thermal equilibrium and static robustness. No initial state/runtime assumption is claimed to imply thermalization; that assumption is explicit and conditional. The full transverse-field Gibbs state receives a separate trace-distance perturbation correction, possibly inconclusive. Finite-time annealing superiority is outside the guarantee.

## Recorded implementation clarification (2026-10-16T08:21Z)

The main eight-seed common proposal-pool comparison is exactly matched. Adaptive
pruning paths can differ after an acceptance differs; their candidate counts and
traces are therefore charged separately, and no exact equal-proposal causal
claim is made for those trajectories. To retain the intended stricter control,
add a frozen common ONE-STEP deletion pool enumerated from each unchanged guided
pool winner. Both rules inspect exactly the same graph-valid deletion candidates.
This supplementary control does not replace or retune the predeclared suite.
