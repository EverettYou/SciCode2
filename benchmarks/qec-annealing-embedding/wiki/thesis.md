---
title: Current thesis and evidence boundary
page_type: thesis
status: active
updated: '2026-10-16'
source_refs:
- labs/lab-002-agent-test-general-h/REPORT.md
- labs/lab-003-surface-code-encoding-comparison/REPORT.md
- labs/lab-004-general-h-evaluation-embedding-loop/REPORT.md
- labs/lab-005-general-h-annealing-relevance/REPORT.md
idea_ids:
- x-001
- k-001
- c-001
- k-003
- c-004
---

# Current thesis and evidence boundary

**Summary**: General sparse-H construction and cheap theory now close endpoint and early-time actual original-optimum quantum mapping loops. The finite-time guarantees have tiny effects; useful moderate-time and larger standard-compiler coverage remain unresolved.

**Sources**: [Lab 002](../labs/lab-002-agent-test-general-h/REPORT.md), [Lab 003](../labs/lab-003-surface-code-encoding-comparison/REPORT.md), [Lab 004](../labs/lab-004-general-h-evaluation-embedding-loop/REPORT.md).

**Last updated**: 2026-10-16.

## Central question

Develop an efficient algorithm from a general sparse binary check matrix, syndrome and additive weights to a faithful quadratic model and hardware-valid annealing embedding, coupled to an inexpensive theoretically justified quality evaluation. CSS form, named codes and planar structure are not prerequisites. The [original task](../problem/TASK.md) remains unchanged.

## Supported progression

Lab 002 supplies an exact/rounding-certified XOR compiler and general Zephyr construction, but its compactness is poor against automatic embedding and all 25 ordinary pause certificates are inconclusive. Its strict quantum comparison uses a narrow initial-state/pause regime and admits a preference reversal. [Lab 002 findings](../labs/lab-002-agent-test-general-h/REPORT.md#findings-and-limits).

Lab 003 favors stabilizer/dual variables for the tested ideal-measurement planar surface codes, with better resources up to distance 9 and numerical tiny-system forward-QA evidence. The geometry-specific encoding and penalty proof do not transfer unchanged to arbitrary H. [Lab 003 scope and limits](../labs/lab-003-surface-code-encoding-comparison/REPORT.md#advantages-of-a-and-limits).

Lab 004 proves a rooted-tree repair/terminal-Gibbs defect certificate without decoding or a partition function. Its effective scale guides compact mapping selection and fixed-tree contact allocation. On 36 ordinary sparse inputs, the uniform guided/pruned rule reduces physical qubits on 33/36, mean 6.57%, retaining reference scale and <5% classical equilibrium defect bounds. An adaptively developed LP/pruning rule improves 7/8 entirely new inputs, mean 5.53%. Independent actual-coefficient audits pass 313 saved selected programs. [Lab 004 outcomes](../labs/lab-004-general-h-evaluation-embedding-loop/REPORT.md#ordinary-instance-evidence), [independent audit](../labs/lab-004-general-h-evaluation-embedding-loop/results/independent_program_audit.json).

## Strongest comparison and its boundary

At fixed compiled model and beta, increasing alpha increases conditional full-QUBO ground probability. Separated intervals prove strict chain-consistent full-QUBO-ground readout improvement on 8/12 ordinary n=16 inputs for uniform-guided-pruned, and 11/12 for LP-selected. They prove no strict unconditional original-error-optimal order on those inputs. Auxiliary excitations distinguish these events. [Independent interval evidence](../labs/lab-004-general-h-evaluation-embedding-loop/results/independent_logical_gibbs_intervals.json).

A local transverse-driver correction yields a small-driver quantum **equilibrium** consistency bound. Lab004 gives no equilibration, mixing-time or finite-time QA theorem; the later Lab005 results below establish different, explicit early-time quantum guarantees. Identical defect certificates can accompany opposite changes in actual chain failures and decoded success; refinement quality constraints also have null effects in the sampled pruning trajectories. [Theory and limitations](../labs/lab-004-general-h-evaluation-embedding-loop/THEORY.md), [physical counterexample](../labs/lab-004-general-h-evaluation-embedding-loop/results/physical_gibbs_validation.json).

## Early-time original-error quantum loop

[Lab005](../labs/lab-005-general-h-annealing-relevance/REPORT.md) adds weighted GF2 repair penalties, an exact balanced thermal original-error law, sparse quantum readout polynomials and rare-event-relative commutator word bounds. A program-specific exact coefficient/optimal-set relaxation compares ACTUAL optimum-error probabilities across different mappings without enumerating the optimum or Hilbert space. [Final theorem](../labs/lab-005-general-h-annealing-relevance/independent/CERTIFIED_EVENT_THEORY.md), [relative-event proof](../labs/lab-005-general-h-annealing-relevance/theory_extensions/THEORY.md).

Within balanced compilation,15/23 ordinary mappings shrink, mean4.075% across23, with strict original-optimum probability improvement at commonT1/1024. Standard compilation needs stronger optimal-set facets and feasible-cost witnesses: zero-search particular cost gives1/24 smaller mappings; charged16-start search gives3/24, all n16. Every n32/64 standard case remains inconclusive. The balanced representation itself costs about twice standard, so this is not an across-compiler resource win. [Mapping results](../labs/lab-005-general-h-annealing-relevance/results/certified_mapping_summary.json), [standard controls](../labs/lab-005-general-h-annealing-relevance/standard_extension/RESEARCH_REPORT.md).

Same-mapping objective programming comparisons certify48/48 after an O(n) zero-search particular-cost upper control, at median largest dimensionlessT=.015625. Guaranteed relative/absolute gains can be extremely small. Tractable full physical forward anchors numerically favor amplification throughT128; they do not prove ordinary moderate-time performance. [Upper-control evidence](../labs/lab-005-general-h-annealing-relevance/results/particular_upper_summary.json), [quantum anchors](../labs/lab-005-general-h-annealing-relevance/results/long_forward_summary.json).

Endpoint improvement is also explicitly challenged: finite-work CLASSICAL annealing reverses the balanced-versus-standard terminal ranking, and a rigorous classical mixing obstruction identifies an equilibration risk. Neither classical result determines quantum ranking. [Dynamics and interpretation](../labs/lab-005-general-h-annealing-relevance/RESEARCH_REPORT.md). There is no contradiction between the scoped early quantum theorem and the retained endpoint/classical limitations.

## Remaining research gaps

Useful finite-time annealing regimes beyond the proved early-time loop, real-device parameter/precision/noise validation, broad larger standard-compiler or logical-observable success guarantees, large-instance routing coverage and general window-change latency remain unresolved. n=128 fits only 3/4 tested generators on the fixed target; all four n=256 searches fail their budgets. Fixed-H syndrome/weight reuse is demonstrated; arbitrary H changes are not. [Extension and updates](../labs/lab-004-general-h-evaluation-embedding-loop/REPORT.md#scaling-updates-and-retained-failures).

## Benchmark interpretation

Scientific evidence strengthens achievable conditional-regime solutions. It does not establish model difficulty, expert approval or organizer acceptance. Lab 002 is an exploratory solve; Labs 003/004 use continuing author context and scientific supervision. The old design-only/no-lab-result status in the append-only log is historical, now superseded by completed lab evidence. No earlier scientific report is rewritten or retroactively regraded. Lab005 supplies an agent-produced solution to an ANY-conditional finite-event mapping version; such correct early-time results cannot be discarded to manufacture difficulty. The new [finite-forward issue](../problem/ISSUE-general-h-finite-annealing.md) retains a useful-regime goal with explicit feasibility uncertainty and no calibrated failure claim.

## Related pages

[Index](index.md); [frontier](ideas/research-frontier.md); [implementation](implementations/general-h-embedding-loop.md).
