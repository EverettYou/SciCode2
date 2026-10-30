---
document_type: lab_report
lab_id: lab-001
status: designed
idea_ids:
  - x-001
  - k-001
  - k-002
  - c-002
wiki_context:
  - benchmarks/lattice-gap-mechanism/wiki/thesis.md
  - benchmarks/lattice-gap-mechanism/problem/TASK.md
related_labs: []
---

# Lab 001: Phenomenon card

## Motivation

The benchmark is a modeling test only if the solver sees experiments rather than a Hamiltonian. This lab freezes that public statement and writes the author-side table of mechanisms that still fit. Computing a spectrum before the table exists cannot tell us which ARPES feature is worth scoring.

The decision it informs is whether band insulator, magnetic order, exciton or pairing order, and a symmetric interaction-generated gap all survive the three public facts. If they do, ARPES remains the prediction. If one fact already selects a unique mechanism, the prompt is too strong and should be revised before any solver run.

## Design

Inputs are `problem/prompt.pdf` and the author-side phase contrast from the reviewed bilayer study. The PDF text is extracted verbatim into `results/solver-prompt.md`. It is not paraphrased with extra microscopic facts.

The mechanism table in `results/mechanism-table.md` has one row for each of these candidates: a filled-band insulator, an intralayer Hubbard antiferromagnet, an exciton or interlayer pairing state, and an interlayer-singlet product. Columns are the tunneling curve, the local magnetic intensity, the resistivity curve, and the ARPES feature that would distinguish the row. The antiferromagnetic row should be marked in tension with the magnetic panel. That intensity is the momentum sum, and it stays at zero from zero energy up to a finite threshold. A soft mode at any momentum would put weight at zero in the sum. A cell may say that the curve is naturally satisfied, that it can be arranged, or that it is in tension. It may not cite a number that this lab did not compute.

Controls: the extracted prompt is scanned for hopping amplitudes, exchange constants, Hubbard interactions, orbital names, filling, layer number, a named target phase, and the inferred phrases square lattice, charge gap, spin gap, and superconductivity. A hit fails the lab even if the scientific table is interesting. The scan runs on `solver-prompt.md` only, because the task file is allowed to discuss the author-side Hamiltonian.

Keep the current prompt if at least two rows survive all three facts and disagree on ARPES. Branch the prompt if every survivor predicts the same photoemission features. Prune a row only by writing the fact that rules it out. Do not drop the magnetic or band-insulator rows merely because the source paper emphasizes a different phase.

Doping stays out of the extracted prompt.

## Methods and execution

Not run. No environment, command, or result file exists yet. The plan is `PLAN.md`.

## Findings

Not run. This report does not contain spectra, fitted gaps, or a completed mechanism table.

## Analysis and limitations

Nothing has been tested. The design assumes that a spin gap does not by itself remove an exciton insulator, and that a charge gap does not by itself remove a band insulator. Those assumptions are what the table is for. If the transport sentence is later changed to "bulk insulator," the table has to be rewritten before it is used.

## Search decision

Leave `x-001`, `k-001`, `k-002`, and `c-002` open until the prompt file and the table exist. Do not prune or distill from this design.

## Wiki ingest handoff

None until execution. After the two result files and the token scan exist, ingest the surviving-mechanism claim and the ARPES feature each survivor must predict. Do not ingest this design section as a finding.
