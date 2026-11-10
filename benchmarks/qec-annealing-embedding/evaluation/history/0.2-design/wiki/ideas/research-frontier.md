---
title: Formulation and embedding idea frontier
page_type: ideas
status: active
updated: '2026-10-07'
source_refs:
- problem/USER_REQUEST.md
- problem/LITERATURE_REVIEW.md
- problem/DESIGN_REVISION.md
idea_ids:
- x-001
- c-001
- k-001
- c-002
- c-003
- k-002
- x-002
---

# Formulation and embedding idea frontier

**Summary**: Preserve independent representation and placement directions without assigning an implementation recipe.

**Sources**: [Request](../../problem/USER_REQUEST.md), [review](../../problem/LITERATURE_REVIEW.md), metadata.idea_sources[0].

**Last updated**: 2026-10-07.

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

## Revision history

The initial root and broad children x-001, c-001 and k-001 are retained. The 7 October 2026 requirements audit adds explicit alternatives and a cross rather than overwriting the initial nodes. No unsuccessful numerical formulation has been observed, so no fabricated pruning decision is recorded. The original design is preserved in [history](../../evaluation/history/initial-design/README.md).

## Search decisions

Keep a construction only when it is independently correct and improves a meaningful part of the resource frontier or clarifies a limitation. Prune incorrect, dominated or unaffordable branches with retained witnesses and budgets. Cross representation and placement branches when their interaction changes a testable prediction. Distill only validated stable code to src and evidence-backed synthesis to note. No branch is tested, pruned or distilled yet.

## Related pages

[Thesis](../thesis.md); [index](../index.md).
