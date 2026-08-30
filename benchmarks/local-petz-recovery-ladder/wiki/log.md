# Wiki log

<!-- Append entries; never rewrite prior entries. Format: ## [YYYY-MM-DD] operation | subject -->

## [2026-08-22] ingest | liu2025mqdm paper

- Raw source: `wiki/papers/liu2025mqdm.md`
- Registry entry: `paper:liu2025mqdm`
- Pages created: `concepts/weak-measurement-diffusion.md`, `concepts/finite-markov-length.md`, `methods/twirled-petz-recovery.md`, `comparisons/global-vs-local-petz.md`, `questions/recovery-locality-boundary.md`
- Pages updated: `index.md`, `thesis.md`
- Summary: Compiled the ensemble-level recovery formalism, CMI locality condition, reported numerical demonstration, limitations, and exact-to-local calibration gap without treating source-reported results as benchmark evidence.

## [2026-08-22] ingest | global paper citation migration

- Raw source: `wiki/papers/liu2025mqdm.md`
- Registry entry: `global:paper:liu2025mqdm`
- Pages created: `ideas/research-frontier.md`
- Pages updated: `index.md`, `thesis.md`, and local synthesis pages
- Summary: Retired benchmark-local source copies and the standalone idea YAML graph; retained the research history as a local idea page and cited the global paper entry.

## [2026-08-22] ingest | promote reusable liu2025mqdm knowledge globally

- Promoted weak-measurement diffusion, finite Markov length, twirled Petz recovery, and global-versus-local comparison to the root wiki.
- Removed the four duplicate local topic pages and replaced them with cross-scope links.
- Retained the benchmark thesis, recovery-locality question, exact calibration strategy, and research frontier locally.
- Cleared the local source registry because the canonical paper and companion repository are registered globally; future completed lab reports remain benchmark-local evidence.

## [2026-08-22] query | Petz gap as a transition diagnostic

- Human direction: `talk/threads/T-0002-refocus-petz-gap-on-mixed-state-transition.md`.
- Sources consulted: the global `liu2025mqdm` synthesis and its cited Sang--Hsieh finite-Markov-length result.
- Pages updated: `index.md`, `thesis.md`, `questions/recovery-locality-boundary.md`, and `ideas/research-frontier.md`.
- Lab redesigned: `labs/lab-001-transition-model-selection/`.
- Summary: Replaced the method-centered 1D TFIM calibration with a model-selection gate and a primary observable based on local-global Petz gap versus recovery radius. Preserved the original branches as kept or pruned history. The 2D decohered toric-code transition is the qualified default; 1D families are candidates only if independent CMI scaling supports an interior transition.

## [2026-08-22] query | scalable trajectory-level tensor-network learning

- Human direction: `talk/threads/T-0003-refocus-benchmark-on-scalable-trajectory-learning.md`.
- Sources consulted: the global `liu2025mqdm` synthesis and the companion implementation's design, diffusion, model, and operator modules.
- Pages updated: `index.md`, `thesis.md`, `questions/scalable-trajectory-reversal.md`, and `ideas/research-frontier.md`.
- Lab redesigned: `labs/lab-001-mps-trajectory-baseline/`.
- Summary: Replaced the local/global Petz criticality project with a trajectory-level MPS/MPO algorithm. The benchmark now requires a canonical MPS weak-measurement engine, a translation-equivariant finite-range controller, oracle-versus-record ablations, and frozen train-short-test-long evaluation. Prior Petz branches remain recorded as pruned history.

## [2026-08-22] query | correction: preserve Petz benchmark scope

- Human correction: the trajectory-level tensor-network idea was intended as a new benchmark, not a rewrite of this benchmark.
- Restoration: returned this benchmark's metadata, task, wiki, lab, source boundary, note, index entry, and provenance paths to the Petz/CMI criticality design.
- Separation: created `benchmarks/tensor-network-trajectory-diffusion/` for the new algorithmic direction.
- Summary: The preceding trajectory-redesign entry records an incorrect intermediate action and is superseded by this correction; no trajectory-learning content remains active in this benchmark.
