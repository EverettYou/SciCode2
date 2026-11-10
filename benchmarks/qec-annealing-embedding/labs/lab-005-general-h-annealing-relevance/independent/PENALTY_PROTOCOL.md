# Parent-independent general-H penalty study

Frozen before numerical outcomes, 2026-10-16. This is a separate reference-research branch; it does not prescribe the scientific child's method.

## Scientific question

Can a cheap code-independent linear-algebra repair bound reduce the global XOR penalty while preserving the projected decoding optima, and does the physically rescaled program improve an actual original-error readout event in the terminal model? This branch does not claim finite-time QA relevance from scale alone.

## Proposed theorem and method

Let B be a minimum-total-|w|-weight basis of columns of H, selected by binary matroid greedy elimination. Choose independent original rows R so H[R,B] is invertible. A right-inverse repair for a residual syndrome d in image(H) is x_B=H[R,B]^{-1}d_R. Let c_j be the |w|-weighted support cost of its jth column and C=max_j c_j (C=0 if rank0). Repair cost is at most C|d_R| <= C|d|. Thus a uniform per-violated-check penalty M>C preserves all feasible original-cost optima; every positive-penalty auxiliary excitation also remains nonoptimal. C<=sum_{i in B}|w_i|<=sum_i|w_i|. This is a sufficient bound, not the globally smallest penalty and not a decoding solver.

Check the complete right-inverse identity H[:,B] H[R,B]^{-1} H[R,:]=H exactly over GF(2), including dependent rows. Do not assume full row rank. Signed and zero weights use absolute flip-cost bounds. The proof requires a feasible syndrome, as in the original task. Matrix basis construction uses only H and weights, never the syndrome solution or planted error.

## Frozen comparisons

1. Reuse all 36 Lab004 main inputs and their first-valid/guided-pruned mappings read-only. Recompute three penalties with the SAME additive margin1: global W+1, basis-total W_B+1, and right-inverse C+1. Recompute physical programs on the exact same target, trees/contact policy, beta20 and epsilon.05. All auxiliaries remain included; no embedding search gain is claimed.
2. Validate the repair witness and actual coefficient ground-fidelity certificate independently. Check the nonzero source graph remains realized by the saved mappings. Charge basis construction, compilation, physical evaluation and final audits separately.
3. For all 12 ordinary n16 inputs, compute outward-enclosed terminal original-error-optimal mass, summing all auxiliary excitations. Compare conservative unconditional root-decoded success intervals after chain-defect and coefficient-rounding corrections. A larger alpha across DIFFERENT penalties is not itself a probability theorem. Count strict separated intervals and all inconclusive/reversed outcomes.
4. Generate 12 new inputs using unchanged Lab004 four generators at n16/32/64 with new seed8809. Use first valid automatic embedding from seeds11/29/47,5-second timeout,2tries, same fixed target and constraints. Evaluate all three penalties on the same mapping. Fresh n16 cases receive the same interval probability checks. Do not tune method/slack after outcomes.

## Acceptance and boundaries

A useful result is a universally valid general-H bound with modest cost and real parameter improvements, plus honestly classified actual readout orders or limitations. There is no arbitrary required percentage gain and no demand for universal ordering. Small exact enumeration checks validate the proof; ordinary datasets support coverage claims. No quantum runtime, QPU or Gibbs-equilibration claim follows. All code/results are parent-owned under independent/ with filenames prefixed penalty_.
