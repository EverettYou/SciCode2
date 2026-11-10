# Create-benchmark design audit — 7 October 2026

## Verdict and authorized scope

The original workspace passed structural checks but its question was not fully self-contained: it cited an unpublished proposal and left code/target inputs partly implicit. These design defects are repaired in revision **0.2-design**. The result satisfies the applicable question-design and workspace-revision requirements; it is not a difficulty-calibrated benchmark or completed submission. Expert review remains pending.

The audit applies the repository's updated `skills/create-benchmark/SKILL.md`, its workspace and requested proposal references, and `docs/scicode2/requirements.md`. The user explicitly limited this phase to writing an effective independent question and deferred empirical screening. Under the skill's “Produce the requested subset of files” rule, no active guidance ladder, reference pilot or model trial is required to finish this requested design revision. The user clarification takes precedence over the general screening workflow.

## Requirement-by-requirement result

| Applicable requirement | Finding and repair | Current state |
|---|---|---|
| One central research objective | Retained joint decoding-to-QUBO formulation and Advantage2 embedding cost; no competing task or implementation added. TASK and metadata agree. | Satisfied for design |
| Self-contained solver document | Removed the private citation. Defined CSS matrices, objective, noise/weights, ties, stabilizer/logical success, toric indexing/check supports and explicit Steane matrices. Named the public Zephyr generator. | Repaired |
| Public scientific references and available inputs | All ten statement references are public primary literature or official documentation. No companion file, private proposal, credentials or repository history is needed. Optional JSON fixtures duplicate stated definitions. | Repaired |
| Current architecture/API | Distinguished Zephyr from Pegasus, ideal from device working graphs, and code periodicity from hardware edges. Replaced an obsolete dwave-networkx URL with the current dwave.graphs API. | Repaired |
| Fair correctness contract | Requires sound projected ground states and attained optimum, without demanding every tied minimizer. Defines logical equivalence separately from exact error agreement. | Repaired |
| Open scientific choices | Encoding, reduction, penalties, placement, reuse, recovery and file layout remain open. Explicit inputs and correctness invariants are problem definitions, not an embedding recipe. | Satisfied for design |
| Meaningful outputs and evidence | Portable models/embeddings, independent checks, controlled comparisons and full resource accounting; all preprocessing is charged. Supported negative conclusions allowed. | Repaired/clarified |
| Facts, hypotheses and findings separated | Expected outcomes are hypotheses; public-source facts have citations. No new algorithm, fit scale, resource improvement or difficulty result is claimed. | Satisfied |
| Workspace continuity | Reused the existing benchmark; preserved problem-opened/expert_review pending, original drafts and private source hashes; retained prospective lab and frontier branches. | Satisfied |
| Provenance and user handoff | Original private material is author provenance only. T-0007 records the actual audit request and scope clarification; DESIGN_REVISION records their effect. | Satisfied |
| Requested solver text and versioning | Complete standalone prompt mirrors TASK; version manifest records hashes and deferred reference status. No experimental freeze is claimed. Superseded A/B drafts are archived. | Satisfied for requested subset |
| Example bank comparison | Full organizer document was inaccessible; no examples or acceptance thresholds were invented. | Pending access; disclosed |
| Achievability, difficulty, A/B outcomes | No empirical work requested or performed. These cannot be established by this document audit. | Deferred by user |

## Design checks performed

The final checks cover workspace validation, wiki structure/provenance, statement/prompt equality, public-link accessibility, optional fixture consistency and commutation, source hashes, and LaTeX/PDF compilation and visual layout. These are document/input integrity checks, not formulation, decoding, embedding, reference or model-screening experiments. Final command outcomes are recorded in task-version.json.

## What to distribute

Distribute the problem PDF or complete prompt.md. Optional fixtures may accompany it but are not required. Do not require the private proposal, author history, wiki, lab plans, audit or evaluator records. Every scientific dependency in the question is either defined directly or publicly retrievable.

## Later work

The user will conduct screening and decide revisions from its results. A later scored submission would need the applicable reference, public numerical budgets, guidance variants and independent evidence. Their absence is disclosed, not treated as a reason to withhold the current question or launch experiments now.
