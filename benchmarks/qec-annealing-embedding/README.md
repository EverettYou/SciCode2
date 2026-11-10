# Fast Embedding Decisions for General Sparse-H Decoding

## Research goal

**Central question:** Can a computationally inexpensive, theoretically justified criterion guide compact embeddings for general sparse parity-decoding instances and identify when those choices improve original-error decoding under a common finite forward anneal?

The input is a general sparse binary check matrix, syndrome and likelihood weights; an observable map is optional for logical evaluation. Named codes are applications, not structural restrictions. The core result is a reusable efficient algorithm and theory-supported efficient quality evaluation, without QPU access.

## Current research status

- Stage: researching; revision 0.4 finite-forward question is current; revision 0.3 and its trials are preserved in history.
- **Current thesis:** General-H theory now guides compact mappings with actual original-optimum finite-forward certificates in an early-time regime. Within balanced compilation,15/23 ordinary mappings shrink, mean4.075% across23, at common dimensionlessT1/1024. Balanced hardware remains about2× standard; guaranteed probability gains are tiny.
- **Standard-compiler limit:** Cheap optimal-set LP+particular upper witness yields1/24 compact gains; charged16-start feasible search+LP yields3/24, all n16. Every n32/64 standard case remains inconclusive. Simpler controls and negative results are retained.
- **Latest supported evidence:** [Lab005 report](labs/lab-005-general-h-annealing-relevance/REPORT.md), [event theory](labs/lab-005-general-h-annealing-relevance/independent/CERTIFIED_EVENT_THEORY.md), [standard controls](labs/lab-005-general-h-annealing-relevance/standard_extension/RESEARCH_REPORT.md), [synthesis](note/general-h-readout-and-forward.md). Independent audits pass375 actual candidate programs; a separate exact parent replay checks960 standard optimal-set dual witnesses.
- **Main uncertainty:** Practical finite-time/QPU performance, broadly useful standard-compiler coverage and arbitrary window-change latency remain open. Exact early-time or endpoint results do not settle these.
- **Prior evidence:** [Lab004](labs/lab-004-general-h-evaluation-embedding-loop/REPORT.md) supplies a useful endpoint compactness loop; [Lab002](labs/lab-002-agent-test-general-h/REPORT.md) provisionally solves the old permitted conditional scope; [Lab003](labs/lab-003-surface-code-encoding-comparison/REPORT.md) is a structured-code follow-up. These reports are unchanged. [Lab001](labs/lab-001-formulation-embedding-audit/REPORT.md) remains prospective.
- **Active lab:** [Lab005](labs/lab-005-general-h-annealing-relevance/REPORT.md) is the selected completed record; its scientific work is completed within the original three-hour allowance ending2026-10-16T11:57:05Z. No scientific job or scheduled automation remains active; this was continuing author-context research, not a blind test.
- **Current question:** [Canonical problem sheet](problem/TASK.md), [PDF](problem/problem.pdf), and [editable LaTeX](problem/main.tex). Revision 0.3 is preserved under [history](problem/history/v0.3-general-H/).
- **Creation assessment:** [Text-only assessment](evaluation/ISSUE-ASSESSMENT-general-h-finite-annealing.md) recommends pass-to-testing with useful-regime feasibility and difficulty uncertainty. A task asking only for any conditional finite-event mapping gain now has an agent-produced solution and must not be advertised as hard.
- **Benchmark status:** No formal A/B calibration or organizer acceptance is established. Summary-level Example bank comparison is available; primary case reports/full organizer template remain unverified.
- **Active frontier:** [Research frontier](wiki/ideas/research-frontier.md) retains the practical regime, representation overhead, larger standard coverage and update questions.
- **Next decisive action:** Prepare a fair explicit trial input/resource/usefulness protocol for the issue, then a fresh user-opened exploratory test. This closeout launches no test.
- **Blockers or pending human input:** None for the completed deliverable. Expert review and calibration remain separate future stages.
- **Last meaningful update:**2026-10-16. [Wiki thesis](wiki/thesis.md) records evidence and its limits.

## Start here

1. [English PDF](problem/problem.pdf), [standalone question](problem/TASK.md), and [autonomous-research prompt](prompt.md). The prompt includes the current question and instructions to set goals, execute research and deliver evidence within a default two-hour budget; callers may normally specify one to 24 hours.
2. [Design audit](evaluation/AUDIT.md), [reviewer summary](evaluation/proposal.md), [acceptance plan](evaluation/evaluation-plan.md) and [version hashes](evaluation/task-version.json).
3. [Metadata](metadata.yml), [wiki map](wiki/index.md), [thesis](wiki/thesis.md) and [frontier](wiki/ideas/research-frontier.md).
4. [Implementation entry points](src/README.md), [research takeaway](note/general-h-tree-gibbs.md) and [T-0007](../../talk/threads/T-0007-audit-qec-benchmark-against-updated-creation-requirements.md).
5. [Revision 0.3 question and prompt](problem/history/v0.3-general-H/) preserve the earlier formulation and its trial context.
6. [Original finite-forward issue draft](problem/ISSUE-general-h-finite-annealing.md) and its [author-side assessment](evaluation/ISSUE-ASSESSMENT-general-h-finite-annealing.md) preserve the formulation record.

## Source foundation

[Public literature review](problem/LITERATURE_REVIEW.md) supports background. [Request record](problem/USER_REQUEST.md), [design revision](problem/DESIGN_REVISION.md) and the unchanged private proposal under problem/references preserve author provenance, hashed in metadata and the wiki ledger. No companion repository is assumed. The question itself cites only public resources.

## Reading discipline

Distribute the PDF or complete solver text. Legacy CSS fixtures are optional examples and do not define the generalized task. Author provenance, history, wiki, lab plans and evaluator records are not required fresh-solver inputs. Original attachment instructions do not expand authorization. Keep completed lab evidence separate from future clean tests; supervised Lab 003 intentionally uses the earlier code and discussion. The PDF remains editable in [main.tex](problem/main.tex).
