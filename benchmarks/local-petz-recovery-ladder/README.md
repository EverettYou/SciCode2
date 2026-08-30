# Petz Recovery Gap at Mixed-State Criticality

This README is the benchmark onboarding summary. Detailed claims and evidence live in the wiki and labs.

## Research goal

**Central question:** Can the finite-window local-versus-global Petz recovery gap locate and characterize a mixed-state phase transition by tracking the divergence of the CMI Markov length?

**Objective:** Measure how the Petz recovery gap closes with recovery radius and test whether the required radius scales with the independently extracted Markov length.

**Success means:** Identify a source-supported transition, show joint finite-size scaling of CMI and Petz gap, and distinguish it from 1D endpoints, pure-state criticality, or numerical artifacts.

**Scope boundary:** The transition diagnostic is primary. Channel invariants and convergence are controls. A generic 1D TFIM under weak depolarization is not presumed to have a mixed-state CMI transition; the canonical fallback is the 2D toric-code decodability transition.

## Current research status

- **Stage:** `problem-opened`; `expert_review: pending`.
- **Overall state:** The benchmark has been refocused from method calibration to mixed-state criticality; no experiment has been executed.
- **Current thesis:** The minimum Petz recovery radius should track Markov length, but a meaningful test requires a model with an independently established mixed-state transition; see [the synthesis](wiki/thesis.md).
- **Active frontier:** `k-004` decides whether a suitable 1D transition exists, `x-003` defines the Petz-gap observable, and `c-003` builds the commuting exact baseline; see [research frontier](wiki/ideas/research-frontier.md).
- **Active lab:** [Lab 001](labs/lab-001-transition-model-selection/REPORT.md) qualifies the model and runs the smallest exact Petz-gap pilot.
- **Latest supported evidence:** The cited literature supports Markov-length divergence at the decohered toric-code decodability transition, not equating the pure 1D TFIM critical point with a mixed-state CMI transition.
- **Main uncertainty:** Whether a genuinely finite-parameter, equal-time 1D model exists that is source-supported and computationally useful.
- **Next decisive action:** Complete Lab 001's 1D qualification gate, then validate the commuting Petz/Bayesian equivalence on a small toric code.
- **Blockers or pending human input:** None for model qualification; the refocus is recorded in [T-0002](../../talk/threads/T-0002-refocus-petz-gap-on-mixed-state-transition.md).
- **Last meaningful update:** 2026-08-22.

## Start here

1. [metadata.yml](metadata.yml)
2. [problem/TASK.md](problem/TASK.md)
3. [wiki/thesis.md](wiki/thesis.md)
4. [wiki/ideas/research-frontier.md](wiki/ideas/research-frontier.md)
5. [Lab 001 report](labs/lab-001-transition-model-selection/REPORT.md) and [plan](labs/lab-001-transition-model-selection/PLAN.md)
6. [src/](src/) and [note/](note/)

## Independent numerical environment

This benchmark has its own uv project and will acquire numerical dependencies only when its experiment implementation needs them. From this directory run `uv sync`; commit changes to `pyproject.toml` and `uv.lock`, while keeping `.venv` local. It does not inherit the repository-root environment.

## Source foundation

- `liu2025mqdm` — the local/global Petz construction and finite-Markov premise via its [global paper entry](../../wiki/papers/liu2025mqdm.md).
- Sang and Hsieh, *Stability of mixed-state quantum phases via finite Markov length* — the canonical transition model.
- The companion code implements the trajectory-level branch, not this mixed-state Petz-gap experiment.

## Reading discipline

- Do not call a pure-state Hamiltonian critical point a mixed-state transition without CMI finite-size evidence.
- Do not use Petz-gap growth alone to define the transition.
- Preserve negative 1D results because they establish the diagnostic boundary.
