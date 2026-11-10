---
title: Formulation and embedding idea frontier
page_type: ideas
status: active
updated: '2026-10-16'
source_refs:
- problem/USER_REQUEST.md
- problem/LITERATURE_REVIEW.md
- problem/DESIGN_REVISION.md
- labs/lab-005-general-h-annealing-relevance/REPORT.md
idea_ids:
- x-001
- c-001
- k-001
- c-002
- c-003
- k-002
- x-002
- k-003
- c-004
---

# Formulation and embedding idea frontier

**Summary**: Preserve the original open directions and record completed research decisions without treating endpoint equilibrium as a finite-time QA solution.

**Sources**: [Request](../../problem/USER_REQUEST.md), [review](../../problem/LITERATURE_REVIEW.md), metadata.idea_sources[0].

**Last updated**: 2026-10-16.

## x-001: joint representation and hardware cost

Track: cross. Status: frontier. Parents: none. Origin: metadata.idea_sources[0] and metadata.idea_sources[1]. Determine which faithful representation/embedding tradeoffs are useful on the declared target. Next action: future [audit](../../labs/lab-001-formulation-embedding-audit/PLAN.md). Evidence: literature only. Stable artifacts: none.

## c-001: explore source-graph and placement alternatives

Track: code. Status: frontier. Parent: x-001. Consider auxiliary/locality tradeoffs, hardware-aware placement or reusable embeddings. No method has been selected. Next action: choose and validate discriminating candidates within a declared budget after authorization. Evidence: [review deductions](../../problem/LITERATURE_REVIEW.md). Stable artifacts: none.

## k-001: exact objective, topology and scaling contract

Track: knowledge. Status: frontier. Parent: x-001. Determine what mathematical and static-hardware evidence can justify a recommendation before QPU runs. Next action: exact small-case proofs, sector and seam audit, and transparent scale accounting in the prospective lab. Evidence: [task](../../problem/TASK.md). Stable artifacts: none.

## c-002: sparse local reduction versus compact reduction

Track: code. Status: frontier. Parent: c-001. Origin: [review, mathematical distinctions](../../problem/LITERATURE_REVIEW.md#mathematical-distinctions-that-shape-the-benchmark). Hypothesis: reducing auxiliary count may increase interaction density and routing or scaling cost. Next action: select defensible representatives and compare them with matched embedding budgets in the planned audit; do not implement before authorization. Evidence: a design deduction, not a measured result. Decision: retain as a discriminating alternative. Stable artifacts: none.

## c-003: topology-aware placement versus generic search

Track: code. Status: frontier. Parent: c-001. Origin: [review, best embedding without QPU access](../../problem/LITERATURE_REVIEW.md#how-to-study-best-embedding-without-qpu-access). Hypothesis: topology-aware placement may change chain tails or physical scale even when total qubit count is similar. Next action: freeze a source graph, compare independently validated embeddings with the generic reference, and charge search time. Evidence: untested hypothesis. Decision: retain without preferring a placement method. Stable artifacts: none.

## k-002: amortized reuse and pre-solving boundary

Track: knowledge. Status: frontier. Parent: k-001. Origin: [audit and evaluation plan](../../evaluation/evaluation-plan.md). Determine when graph reuse is valid and when preprocessing costs dominate the apparent embedding gain. Next action: document source-graph invariance conditions and initial/per-syndrome costs; identify classical answer encoding explicitly. Evidence: mathematical/accounting reasoning only. Decision: retain to make comparative claims identifiable. Stable artifacts: none.

## x-002: cross source locality with placement

Track: cross. Status: frontier. Parents: c-002 and c-003. Origin: [task](../../problem/TASK.md). Hypothesis: the favorable source formulation can change when placement strategy changes. Next action: design a crossed comparison of formulations and placements on shared targets, with correctness checks before resource ranking. Evidence: no lab findings. Decision: prospective, not selected as a preferred solution. Stable artifacts: none.

## k-003: theoretically defensible annealing comparison

Track: knowledge. Status: frontier. Parent: k-001. Origin: [user-directed revision](../../problem/DESIGN_REVISION.md). Find a meaningful conditional comparison, bound or certificate connecting an embedding to a declared annealing quantity, while distinguishing static correctness from dynamics. Next action: researcher-selected theory development after execution instruction. Evidence: public context and a research question only. Stable artifacts: none.

## c-004: efficient evaluator and changing-matrix interface

Track: code. Status: frontier. Parents: c-001 and k-003. Origin: [general-H question](../../problem/TASK.md). Develop a reusable sparse-input construction and an evaluator cheap enough to guide mapping, including preprocessing, per-syndrome and window-update costs. No CSS or named-family prerequisite. Next action: select a suitable regime and algorithm only in later research. Evidence: untested direction. Stable artifacts: none.

## Revision history

The initial root and broad children x-001, c-001 and k-001 are retained. The 7 October 2026 requirements audit adds explicit alternatives and a cross rather than overwriting the initial nodes. No unsuccessful numerical formulation has been observed, so no fabricated pruning decision is recorded. The original design is preserved in [history](../../evaluation/history/initial-design/README.md). Revision 0.3-general-H removes mandatory CSS/family choices and adds k-003/c-004 to reflect theoretical quality and evaluator efficiency. Existing alternatives are retained as possible directions, not an execution recipe. The superseded 0.2 formulation is preserved separately.

## Search decisions

Keep a construction only when it is independently correct and improves a meaningful part of the resource frontier or clarifies a limitation. Prune incorrect, dominated or unaffordable branches with retained witnesses and budgets. Cross representation and placement branches when their interaction changes a testable prediction. Distill only validated stable code to src and evidence-backed synthesis to note. That statement described the design phase; the completed research decisions below supersede it. Earlier frontier entries remain historical hypotheses, not current evidence summaries.

## Research decisions, 16 October 2026

### k-003 / c-004: useful evaluation on ordinary H

Status: partially supported in a declared terminal-equilibrium regime. [Lab 004](../../labs/lab-004-general-h-evaluation-embedding-loop/REPORT.md) establishes a cheap tree-load defect certificate, conditional compiled-model Gibbs comparison, a small-driver quantum-equilibrium correction and an implemented guidance loop. Ordinary-input compactness improves, and strict chain-consistent ground-readout orders are certified on some n=16 matrices. Retain this route as a useful endpoint baseline. Do not equate it with finite-time QA or original-error success ranking.

### c-003 / x-002: allocation-guided compact placement

Status: supported modestly within automatic candidate pools. Fixed-tree sparse LP allocation admits smaller candidates than uniform guided selection on 7/36 main inputs. A combined rule reduces qubits on 7/8 new inputs while preserving the quality floor. The constrained and unconstrained deletion trajectories coincide; preserve this null ablation rather than attributing pruning gains to the acceptance constraint. [LP and new-input evidence](../../labs/lab-004-general-h-evaluation-embedding-loop/REPORT.md#ordinary-instance-evidence).

### k-002: reuse boundary

Status: supported for fixed H and a fixed penalty envelope, open for matrix/window changes. [Lab 004 update audit](../../labs/lab-004-general-h-evaluation-embedding-loop/results/update_audit.json) validates 160 syndrome/weight updates without new minor search. New interactions still require routing/revalidation; no just-in-time latency guarantee follows.

### c-002: representation remains a separate lever

[Lab 003](../../labs/lab-003-surface-code-encoding-comparison/REPORT.md) supports a structured stabilizer encoding for its planar ideal-measurement family. This is evidence that representation can dominate routing resources, not a general-H solution. The new general-H loop keeps the inherited XOR model fixed and therefore does not settle alternative quadratization quality.

### Retained failures and next discriminating direction

The old ordinary pause bounds remain inconclusive in [Lab 002](../../labs/lab-002-agent-test-general-h/REPORT.md). Lab 004's fixed target fails one n=128 generator and all four n=256 searches. More useful finite-time theory or calibrated dynamical evidence, better large sparse-graph construction, and explicit changing-window interfaces could change the thesis. These are open directions, not newly authorized experiments or a prescribed next method. Stable synthesis: [note](../../note/general-h-tree-gibbs.md); reusable implementation: [entry points](../../src/README.md).

## Lab005 decisions: actual readout and early quantum guidance

### k-003 / c-004: a restricted finite-forward closed loop

Status: supported in an explicit early-time physical quantum regime. The [event theorem](../../labs/lab-005-general-h-annealing-relevance/independent/CERTIFIED_EVENT_THEORY.md) combines general-H affine optimal-set bounds, exact local-star coefficients and relative word tails. It proves actual optimum-event orders across different mappings, rather than substituting a full-QUBO-ground or mean-cost event. Retain this as a validated primitive; practical later-time predictions remain open. [Independent audits](../../labs/lab-005-general-h-annealing-relevance/results/independent_certified_mapping_audit.json).

### c-002 / x-002: representation enables theory but costs resources

Balanced parity factors remove feasible-sector auxiliary Gibbs bias and make early quantum root coefficients easier to control. Within this SAME compiler,15/23 ordinary mappings become smaller with a strict actual-event comparison, mean4.075% across23. Balanced physical size remains about2× standard, and one model exhausts its search budget. Do not promote a within-compiler reduction into an across-compiler win. [Main report](../../labs/lab-005-general-h-annealing-relevance/REPORT.md).

### c-004: ordinary standard coverage remains limited

The original cost-only certificate gives0/24 standard changes. Necessary kernel optimality and character facets strengthen bounds but need feasible upper witnesses: particular cost gives1/24 and charged bounded search gives3/24, all n16. Simpler evaluated controls stay0; all larger standard inputs remain inconclusive. This supports a small real advance and an unresolved coverage limit, not pruning all standard methods. [Extension/control evidence](../../labs/lab-005-general-h-annealing-relevance/standard_extension/RESEARCH_REPORT.md), [parent exact replay](../../labs/lab-005-general-h-annealing-relevance/results/independent_standard_extension_audit.json).

### Retain the useful-regime and benchmark questions

Finite-work classical ordering reverses endpoint ordering; numerical quantum anchors are positive but tractable. Tiny early-time probability guarantees do not establish practical decoding. The [new issue](../../problem/ISSUE-general-h-finite-annealing.md) is self-contained and methods-open; editorial pass-to-testing is separate from expert achievability, fair quantitative grading and clean model difficulty. Prior permissive conditional successes remain successes. Stable synthesis: [readout/forward note](../../note/general-h-readout-and-forward.md).

## Related pages

[Thesis](../thesis.md); [index](../index.md).
