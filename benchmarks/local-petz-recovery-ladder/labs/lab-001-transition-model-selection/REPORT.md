---
document_type: lab_report
lab_id: lab-001
status: designed
idea_ids:
  - x-003
  - k-004
  - c-003
  - k-005
wiki_context:
  - ../../wiki/thesis.md
  - ../../wiki/questions/recovery-locality-boundary.md
  - ../../wiki/ideas/research-frontier.md
related_labs: []
---

# Lab 001: Transition model selection and exact Petz-gap pilot

## Motivation

Before scaling local Petz recovery, establish that the chosen mixed-state family actually has a diverging CMI length. This lab prevents a pure-state critical point or endpoint singularity from being mislabeled as a mixed-state transition, then validates the smallest computational representation of the Petz gap.

## Design

Stage A qualifies 1D candidates. For transfer-matrix or MPDO families, compute CMI versus buffer radius and size across the interior parameter range. For a GHZ or repetition control under local decoherence, determine whether any apparent divergence occurs at a finite interior parameter or only at an endpoint or constraint. Reassess the weakly diffused 1D TFIM only under the same criterion.

Stage B activates if no 1D model qualifies. Use the smallest periodic toric-code lattices under independent Pauli noise. Construct dense global and radius-restricted Petz maps, derive the commuting Bayesian reverse formulation, and compare recovered outputs, CMI, normalization, and logical sectors exactly.

## Methods and execution

Prospective only. Record model definitions, boundary conditions, parameter grids, transfer or stabilizer representations, exact commands, seeds, numerical precision, and artifact hashes after execution.

## Findings

No benchmark experiment has been run. Literature evidence currently qualifies the decohered toric code and does not qualify the original 1D TFIM assumption.

## Analysis and limitations

The 1D audit may not prove impossibility for all 1D models; it decides whether an explicit, source-supported, workstation-feasible candidate is available. The 2D pilot is too small for critical exponents and validates only representation and observable definitions.

## Search decision

After Stage A, keep or prune `k-004`. After Stage B, keep `c-003` only if dense and commuting Petz agree; then activate `k-005` and `c-004`.

## Wiki ingest handoff

Ingest model qualification, endpoint results, equivalence tests, negative controls, and the selected primary model. Do not ingest prospective expectations as findings.
