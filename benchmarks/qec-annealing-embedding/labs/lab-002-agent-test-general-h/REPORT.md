# Exploratory agent test: provisional scientific success

The autonomous scientific solve completed in 56.85 minutes of the original two-hour allowance (41.28 minutes in the scientific solver session). The evidence supports a **provisional pass in the prompt's permitted conditional regime**. This is a full exploratory solve, not formal difficulty calibration.

## Scientific outcome

The solver produced a reusable general sparse-matrix compiler, a deterministic ideal-Zephyr embedding construction in a stated sufficient size regime, faithful physical coefficient allocation, exact/rounding certificates, and a reusable CLI. Its conditional finite-time quantum hold theorem supplies a strict repair comparison and an initial-state reversal.

The [scientific report](RESEARCH_REPORT.md) contains all proofs, assumptions, costs, limitations and reproduction commands. [THEORY_CERTIFICATE.md](THEORY_CERTIFICATE.md) gives the full dynamical proof; [TARGET_NOTES.md](TARGET_NOTES.md) gives construction and programming details.

## Evidence-based acceptance review

| Criterion | Exploratory assessment | Main evidence |
|---|---|---|
| General compiler/embedding, fidelity, complexity and reuse/updates | Provisional pass | Exact penalty/ground-state proofs; rational backend; explicit Zephyr sufficient regime; physical allocation and scaling; charged update costs. |
| Efficient evaluation and substantive theoretical comparison | Provisional pass in a conditional hold regime | Full finite-time proof, rigorous evaluator, strict native/chained repair ordering and reversal for retention. |
| Reproducible code/report, witnesses, diverse inputs and automatic reference | Provisional pass | Five structural matrix examples, 25 final mappings, three seeded minorminer references per example, source, pinned versions and independent readers. |

This judgment uses mathematical review and saved evidence, not process exit or the solver's self-assessment. Details are in [score.json](score.json) and [the coordinator review](results/reviewer-assessment.md). No frozen external gold answer was loaded.

The solver's checks include 38 primary compiler cases, 32 syndrome updates, 100 chained updates, 1,024 pruning graphs, 24 small quantum models, exact extreme-weight cases and CLI overflow fallback. The coordinator independently checked 50 decoding instances and all 25 final hardware witnesses, including 800 consistent physical assignments. The maximum scaled energy discrepancy in this latter floating check was about 1.25e-13; the scientific witnesses separately include exact coefficient/rounding proofs. All 79 core scientific artifact hashes matched at closeout.

## Findings and limits

All alternatives use the same ideal Zephyr g=6,t=4 target (1,248 nodes, 11,400 edges) and common parametric programming limits. Final pruned placement plus validation took 2.50--3.92 ms, versus automatic per-case median 72.26--299.23 ms, after 25.53 ms target-template preprocessing. The pruned template uses 126--475 qubits versus automatic outputs using 50--101. Allocation/certification adds 74.66--92.45 ms. These are local placement/resource observations, not universal end-to-end latency superiority.

For the stated closed-system pause, native repair success is about 0.499997 and the chained alternative has certified success at most 0.016477. Starting from an optimal state reverses the preference: chained retention is at least 0.983523, versus native retention about 0.500003. The theorem includes tied optima and a specified recovery event. It assumes the stated initial encoded state at the pause, with preparation/ramps and noise excluded. **All 25 broad ordinary-strength example dynamics certificates are inconclusive.** No full-anneal speedup or actual-device performance was established.

## Actual trial conditions

- Exact current revision 0.3-general-H and the existing autonomous prompt were snapshotted byte-identically; no scientific question change was made. No external input dataset was supplied; matrix generators/inputs and seeds are saved.
- Original start: 2026-10-07 12:55:30.405 PDT. Scientific solver launch: 13:11:04.521 PDT. Scientific finish: 13:52:21.174756 PDT. Original deadline: 14:55:30.405 PDT; never extended.
- Scientific solver and both scientific assistants were independently verified as GPT-6 Astra/Ultra from their live rollout metadata. The procedural parent/preflight used GPT-6.1 Sol/Ultra; the user later declared a parent switch. The actual scientific solve was delegated with fork none. This setup is recorded, without claiming an independently user-opened child window or a single-model parent conversation.
- Visible parent context had repository procedures and the test request, with no author scientific history. Scientific context was the selected prompt, public resources and this attempt's new artifacts. No sibling reports, author solution, evaluation answers, wiki or prior trial was read. Shared filesystem access is not isolation. Human messages were procedural continuation/model selection, with no scientific correction.
- Codex Desktop 26.928.31416, embedded runtime 0.159.2; Python 3.13.2. Browsing worked; shell networking was restricted. The installed legacy dwave_networkx Zephyr generator was used, with exact graph/version saved. No QPU was used.

Two native g=1 preprocessing calls stalled/exited137; explicit construction replaced them. Autonomous reviews corrected floating arithmetic, gap-sign, CLI fallback and complexity-accounting issues. These recovered events are preserved and are not terminal scientific failures. No scientific jobs remain active.

## Evidence preservation and revision feedback

[run.json](run.json) records actual settings, context, timings, resource observations and file hashes. [scientific_completion.json](results/scientific_completion.json) records terminal scientific status. [scientific_artifact_manifest.json](results/scientific_artifact_manifest.json) binds 79 core deliverables. The lab manifest covers the final local record.

Raw original JSONL from only the exact root, procedural child and three scientific sessions is saved in transcripts/, with hashes, line locators, capture times and completion flags. The root remains active during export, so its snapshot excludes subsequent closeout events and this turn's final response. Child transcripts include terminal completion records. This limit is explicit; no bounded summary replaces the raw evidence. Re-export with `python3 scripts/export_transcripts.py` when a later root snapshot is needed.

The result demonstrates a legitimate narrow solution allowed by the current wording. The next scientific scope decision is whether a conditional hold certificate is the intended target, or whether usefulness across broader compiled instances should become a new objective. Such a change belongs to question revision and a new test; it must not retroactively invalidate this successful conditional result. The question remains unchanged. This run does not establish a failure-based difficulty claim; formal frozen A/B calibration and organizer acceptance remain unassessed.
