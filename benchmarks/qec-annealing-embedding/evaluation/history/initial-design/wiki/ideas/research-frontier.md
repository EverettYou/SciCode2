---
title: Formulation and embedding idea frontier
page_type: ideas
status: active
updated: '2026-10-07'
source_refs:
- problem/USER_REQUEST.md
- problem/LITERATURE_REVIEW.md
idea_ids:
- x-001
- c-001
- k-001
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

## Search decisions

Keep a construction only when it is independently correct and improves a meaningful part of the resource frontier or clarifies a limitation. Prune incorrect, dominated or unaffordable branches with retained witnesses and budgets. Cross representation and placement branches when their interaction changes a testable prediction. Distill only validated stable code to src and evidence-backed synthesis to note. No branch is tested, pruned or distilled yet.

## Related pages

[Thesis](../thesis.md); [index](../index.md).
