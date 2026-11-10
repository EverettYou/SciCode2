# Candidate proposal: quantum decoding formulation and Advantage2 embedding

Status: design revised; exact A/B texts prepared as drafts; reference-pending; no difficulty claim. The central objective is inherited from [TASK.md](../problem/TASK.md), not redesigned here.

## Objective and motivation

Given CSS check matrices, consistent syndromes and independent-error weights, construct a faithful quadratic decoding formulation and a valid Zephyr embedding. Determine resource tradeoffs through controlled comparisons of representations and placements. The user's proposal and D-Wave discussion motivate studying this static compilation problem before spending unavailable QPU resources.

## Consequential scientific judgments

The investigator must decide which equivalent decoding representation preserves logical-sector coverage while keeping both source connectivity and physical scaling favorable; which routing resource matters when chain length and coefficient scale disagree; how to distinguish representation effects from placement effects; and what offline evidence supports a recommendation for later hardware review. Merely invoking a graph-minor library does not resolve these judgments. Whether models actually fail at them remains untested.

## Source and intervention provenance

The [request record](../problem/USER_REQUEST.md) and unchanged [proposal](../problem/references/DWaveProposal.pdf) are hashed in metadata. The [review](../problem/LITERATURE_REVIEW.md) links primary literature. The current audit request is recorded in [T-0007](../../../talk/threads/T-0007-audit-qec-benchmark-against-updated-creation-requirements.md), M-001. It authorizes requirements review and repair; it is a task-design request, not an observed scientific correction in a decoding trial. The initial user message clarified objective/scope and reported a historical CQM observation. No trial transcript, exact solver input, outputs or expert scientific-correction event has been supplied for that observation. Initial agent-authored cautions are not human intervention evidence.

## Non-searchable extension and rejection risks

Existing Ising/QUBO decoding and graph-minor search are known starting points. The proposed extension is their joint, code- and scale-dependent resource evaluation on Zephyr, including coefficient scaling, periodic boundaries and amortized compilation. Novelty of a future algorithm is not established.

A single slack-variable parity reduction does not determine a good source graph or physical placement, but a strong autonomous model may still combine standard tools successfully. A generic wrapper could plausibly meet a weak rubric. The revised task consequently requires decision-relevant controlled comparisons, independent witnesses and complete cost accounting. This is a design safeguard, not evidence of difficulty. Scientific conventions are supplied rather than withheld to manufacture niche-knowledge difficulty. The methods and parameters are not fixed as a complete recipe.

## Feasibility and reference plan

The two provided matrix fixtures are finite sanity examples, not a validated research-scale reference. Small algebra and graph invariants can be checked without a QPU. No decoder, reduction, embedding experiment, capacity result or end-to-end reference solution has been produced. Reference development must establish exact overlapping cases and a nontrivial achievable scale study; then revise or freeze budgets and the comparison suite. Workstation feasibility and active-time estimates remain uncertain. See the [evaluation plan](evaluation-plan.md).

## Prompt and input boundary

[prompt.md](prompt.md) is exact Prompt A, and [prompt-b.md](prompt-b.md) is the identical A followed by a substantial expert brief. C is omitted because no hindsight execution evidence exists. Only those texts and the explicitly enumerated [input files](inputs/README.md) may enter a future solver workspace. The proposal, TASK, review, PDF, wiki, labs, repository instructions, skill files, audit, history, rubric and any reference solution remain author-only. A later run needs an isolated fresh session, not just a folder inside this repository.

## Readiness and uncertainties

[task-version.json](task-version.json) identifies a hashed draft, not a frozen scored test. Example bank comparison is pending-access: the project record reports Drive 403 on 7 October 2026, and this audit's web reads of both example tabs were inaccessible. Full organizer template contents are unverified. No A/B model run, score or acceptance result exists. Author-side packaging is prepared only to the current reference-pending boundary.
