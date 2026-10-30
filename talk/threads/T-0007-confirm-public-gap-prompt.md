---
id: T-0007
title: Confirm public gap prompt
status: open
priority: high
category: scientific
created: '2026-10-26T18:51:42Z'
updated: '2026-10-26T19:54:25Z'
context: 'Paper: chang2023fssmg

  Benchmark: lattice-gap-mechanism

  Follow-up: solver-facing prompt gives square-lattice symmetry, an STM charge gap, a neutron spin gap, and transport without superconductivity. The solver writes a model and predicts ARPES. Hoppings, orbitals, and the phase name stay hidden.'
benchmark_ids:
- lattice-gap-mechanism
related:
- benchmarks/lattice-gap-mechanism/problem/TASK.md
- benchmarks/lattice-gap-mechanism/wiki/thesis.md
- benchmarks/lattice-gap-mechanism/wiki/ideas/research-frontier.md
- benchmarks/lattice-gap-mechanism/labs/lab-001-phenomenon-card/REPORT.md
---

# Confirm public gap prompt

## M-001 · agent · question · 2026-10-26T18:51:42Z

What this is about: lattice-gap-mechanism asks a solver to invent a model from experimental facts and to predict ARPES. The microscopic Hamiltonian is withheld.

What we know:
- The draft public prompt is square-lattice symmetry, an STM dI/dV charge gap, a neutron spin gap, and transport with no superconductivity.
- Band folding, quasiparticle coherence, and Green's-function zeros are prediction targets, not inputs.
- Doping is held out of the first prompt.
- The Chang et al. bilayer study is author-side context. Those three facts are not a dataset reported by the paper.
- Lab 001 is designed to extract the prompt and a four-mechanism table. It has not been run.

What is unclear or blocked: Transport was specified only as the absence of superconductivity. Calling the bulk insulating would add a fact and change which mechanisms survive. The prompt should not be frozen until that sentence is chosen.

Options:
- A — Keep transport as "no superconductivity" only. STM already supplies the charge gap. Do not call the bulk an insulator.
- B — Also state that transport is insulating, so the charge gap is a bulk gap as well as a local tunneling gap.

**Suggested: A** — it matches the latest instruction, and it leaves the bulk charge response for the model to explain rather than restating the STM gap.

Decision requested: Please choose A or B, or rewrite the public sentences.

## M-002 · agent · update · 2026-10-26T19:38:22Z

What this is about: the public prompt for lattice-gap-mechanism now shows curves instead of naming the conclusions, and the author side has a mixed-dimensional coupling contrast.

What we know:
- The solver text gives a layered transition-metal oxide with a fourfold axis and two equal orthogonal in-plane metal-metal directions. It does not say square lattice.
- Tunneling conductance is suppressed around zero bias. Neutron intensity stays at background until a finite energy, with no elastic magnetic weight. Resistivity rises on cooling and never falls to zero. A superconducting trace would drop toward zero; that sentence is not in the prompt.
- The schematic is problem/public-data/schematic-observables.svg.
- lu2023sfdsm is a second hidden reference for filling and doping.
- Mixed-dimensional bilayers, in the sense of Bohrdt et al., arXiv:2108.04118, are two-dimensional layers with interlayer spin exchange and suppressed interlayer hopping. Their DMRG is mainly doped pairing. The author reading used here is: interlayer exchange dominant gives an interlayer-singlet product; intralayer coupling dominant gives a nearly decoupled Hubbard antiferromagnet. The neutron curve is what should reject the second reading.

What is unclear or blocked: nothing further is blocking the phenomenon card. The mixed-dimensional papers are not yet in the local catalog.

Options:
- A — Leave Bohrdt et al. as an external author-side citation and extract the curve prompt in Lab 001.
- B — Fetch that paper into the catalog before Lab 001 writes the mechanism table.

**Suggested: A** — the public curves do not depend on that PDF, and the singlet-versus-antiferromagnet contrast is already recorded as an author reading rather than as a plotted SMG label.

Decision requested: Please choose A or B. Lab 001 can still draft the table from the curves while that choice is open.

## M-003 · user · response · 2026-10-26T19:44:22Z

A

## M-004 · agent · update · 2026-10-26T19:54:07Z

What this is about: the solver handoff for lattice-gap-mechanism is now a compiled PDF.

What we know:
- The only document given to a solver is benchmarks/lattice-gap-mechanism/problem/prompt.pdf, built from prompt.tex.
- It contains the fourfold sheet symmetry, the tunneling, neutron, and resistivity tables, the three-panel figure, and a required answer: a model the solver writes, an account of each trace, and a momentum-resolved photoemission prediction.
- It does not name the lattice, a charge or spin gap, superconductivity, a Hamiltonian, a filling, or a phase.
- Author notes stay in problem/TASK.md. Lab 001 extracts the PDF text rather than a fenced paragraph.

What is unclear or blocked: fetching Bohrdt et al. into the catalog is still optional and does not change this PDF.

Options:
- A — Leave the mixed-dimensional paper as an external author-side citation.
- B — Fetch it into the catalog before Lab 001 writes the mechanism table.

**Suggested: A** — the PDF is already the solver document, and that paper is not part of it.

Decision requested: Please choose A or B only if you want the catalog changed. The PDF does not wait on that choice.

## M-005 · agent · update · 2026-10-26T19:54:25Z

What this is about: the earlier choice already settles the catalog question.

What we know:
- M-003 selected A. Bohrdt et al. stays an external author-side citation and is not fetched into the catalog.
- The solver document is benchmarks/lattice-gap-mechanism/problem/prompt.pdf. It does not depend on that paper.
- No further choice is requested on this thread.

What is unclear or blocked: nothing.

Options:
- A — Keep the PDF as the solver document and leave the paper outside the catalog.

**Suggested: A** — this is the choice already recorded in M-003.

Decision requested: None. This note only records that M-003 stands.
