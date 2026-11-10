---
title: Current thesis and evidence boundary
page_type: thesis
status: active
updated: '2026-10-07'
source_refs:
- problem/USER_REQUEST.md
- problem/LITERATURE_REVIEW.md
- problem/DESIGN_REVISION.md
idea_ids:
- x-001
- k-001
- c-001
---

# Current thesis and evidence boundary

**Summary**: Encoding and embedding should be evaluated together because each can alter the physical cost and usable coefficient scale; whether a particular choice is favorable remains untested.

**Sources**: [Task](../problem/TASK.md), [literature and design deductions](../problem/LITERATURE_REVIEW.md).

**Last updated**: 2026-10-07.

## Central question

Construct and validate resource-efficient quadratic encodings and minor embeddings of check-matrix-defined quantum decoding problems on D-Wave Advantage2 connectivity, and determine which formulation and embedding choices remain favorable under hardware constraints.

## Supported context

The review establishes prior Ising decoding work and public Advantage2 topology/property contracts. It does not establish a new algorithm, a measured embedding or a performance claim. The quantum success criterion needs stabilizer/logical data as well as syndrome checks. One CSS sector under code-capacity noise is the present mathematical core; exact small-case proofs and periodic boundaries are required.

## Alternatives and uncertainty

Representation-driven locality, topology-aware placement and embedding reuse are open directions, not selected solutions. Fewer variables or shorter chains need not give the best programmable scale. The required ideal graph is publicly constructible; an actual device graph is optional. Numerical budgets and scored-test targets are uncalibrated. There are no supported lab findings and no QPU resources.

## Question-design audit

The [design audit](../evaluation/AUDIT.md) repairs self-containment and preserves the research objective. The standalone statement includes toric/Steane inputs and a public Zephyr generator, with no private citation or required attachment. It charges preprocessing and permits justified tied-optimum rules. [The revision record](../problem/DESIGN_REVISION.md) captures the user's explicit boundary: question design now, empirical screening later. Draft guidance is archived; no reference or difficulty evidence is claimed.

## Next research transition

The [frontier](ideas/research-frontier.md) motivates the [planned audit](../labs/lab-001-formulation-embedding-audit/PLAN.md). Execution needs a later user instruction. Completed lab evidence should update this synthesis, branch or prune ideas, and only then support stable source or the final note.

## Related pages

[Index](index.md); [frontier](ideas/research-frontier.md).
