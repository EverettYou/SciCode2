---
title: Research frontier
page_type: ideas
status: provisional
updated: '2026-10-26'
source_refs:
- wiki/papers/chang2023fssmg.md
- problem/TASK.md
idea_ids:
- x-001
- k-001
- k-002
- k-003
- k-004
- c-001
- c-002
- c-003
- k-005
---

# Research frontier

**Summary**: The solver sees Lab 002 spectra, a two-sheet repeat, and a high-temperature band, then writes a model and predicts the low-temperature photoemission at 0.75 electrons per site.

**Sources**: [Chang et al. synthesis](../../../../wiki/papers/chang2023fssmg.md); [benchmark task](../../problem/TASK.md)

**Last updated**: 2026-10-26

---

## Active ideas

- **x-001 · cross · active** — Give the solver the tunneling, local magnetic, and resistivity curves plus fourfold sheet symmetry, and require a model plus an ARPES prediction. Do not name the lattice or the inferred gaps.
  - Parents: none. Origin: `metadata.idea_sources[0]`.
  - Why it has budget: this is the modeling task. Naming the Hamiltonian would collapse it into recall.
  - Next action: Lab 001 extracts the text of `problem/prompt.pdf` and writes the mechanism table.
  - Evidence: none yet.
- **k-001 · knowledge · frontier** — After those three facts, more than one mechanism remains, including a band insulator, a spin-gapped magnet, an exciton insulator, and a symmetric interaction-generated gap.
  - Parent: `x-001`. Origin: `metadata.idea_sources[2]`.
  - Why it has budget: if one fact already selects a unique phase, ARPES is not a real prediction.
  - Next action: the mechanism table in Lab 001 must show, fact by fact, which alternatives survive.
  - Evidence: none yet.
- **k-002 · knowledge · frontier** — Score ARPES by folding, quasiparticle coherence, and Green's-function poles versus zeros. A prediction that only says "gapped" fails.
  - Parent: `x-001`.
  - Why it has budget: the source spectra differ in exactly these features, and STM does not see them.
  - Next action: write those features into the author column of the mechanism table before any spectrum is computed.
  - Evidence: none yet.

## Kept alternatives

- **k-003 · knowledge · kept** — Density dependence is public through the high-temperature band at three densities. The eight-site removal ladder is not in the prompt, because its gap does not match the tunneling edge.
  - Parent: `x-001`.
  - Why it has budget: the motion of the chemical potential with density is part of the band the solver has to fit.
  - Next action: score that contrast in the Lab 001 mechanism table.
  - Evidence: [Lab 004 report](../../labs/lab-004-stm-greens-function/REPORT.md).
- **c-003 · code · kept** — Compute the public spectra on a bilayer plaquette at $J=8t$, and take high-temperature peak positions from the infinite nearest-neighbor band.
  - Parent: `c-001`.
  - Why it has budget: hand-drawn curves were not a band, a bilayer structure factor, or a doping ladder.
  - Next action: none for this parameter set. A second $J/t$ is a new lab, not a silent edit of these numbers.
  - Evidence: [Lab 002 report](../../labs/lab-002-cluster-spectra/REPORT.md).
- **k-005 · knowledge · frontier** — With $t_2=0.2t_1$, the low-temperature occupied peaks measured from the tunneling zero are $-10D$, $-7.2D$, and $-6D$ at $(0,0)$, $(1/2,0)$, and $(1/2,1/2)$. The high-temperature peak at $(0,0)$ is $-5.28D$ from the chemical potential. A nesting gap that leaves the band bottom near its high-temperature position does not fit.
  - Parent: `k-001`.
  - Why it has budget: this is the computed contrast with an interlayer exciton.
  - Next action: put that contrast in the Lab 001 mechanism table without naming it in the prompt.
  - Evidence: [Lab 004 report](../../labs/lab-004-stm-greens-function/REPORT.md).
- **k-006 · knowledge · frontier** — Next-nearest hopping $t_2=0.2t_1$ moves the saddle off the band center. In the tunneling curve the peaks sit at $-7.2D$ and $+8.8D$, not at the middle of the intervals $[-10D,-6D]$ and $[6D,10D]$. Recovering both hoppings from that offset is part of the solver's task. The prompt does not name the hoppings.
  - Parent: `k-001`.
  - Why it has budget: a nearest-neighbor-only band puts both peaks in the middle of those intervals.
  - Next action: keep the public curve dense enough that the offset is visible, and do not state the ratio.
  - Evidence: [Lab 004 report](../../labs/lab-004-stm-greens-function/REPORT.md).
- **c-001 · code · frontier** — Check the author key on a small cluster or a precomputed spectrum. Do not make large-scale Monte Carlo the solver's task or the first author task.
  - Parent: `k-002`. Origin: `metadata.idea_sources[1]`.
  - Why it has budget: the source study is sign-problem free and still too expensive to be the benchmark workload.
  - Next action: after Lab 001, choose the smallest system on which a symmetric gap and one ordered gap disagree in the single-particle spectrum.
  - Evidence: none yet.
- **k-004 · knowledge · frontier** — In a mixed-dimensional bilayer, interlayer exchange dominant is an interlayer-singlet product, while intralayer coupling dominant is a nearly decoupled Hubbard antiferromagnet. The public magnetic fact is the momentum sum of the leading strong-coupling spin excitation at the same $t_1$, $t_2$, and $J$ as the tunneling curve. That intensity is zero up to $4.69t_1$. A soft mode anywhere in the zone would put weight at zero energy in the sum, so one resolved momentum is not the evidence. The antiferromagnetic reading is the one that should fail.
  - Parent: `k-001`.
  - Why it has budget: a solver that writes a single-layer Hubbard model lands in the intralayer antiferromagnet. The public text must not say so.
  - Next action: add that row contrast to the Lab 001 mechanism table, with the local magnetic intensity as the column that separates them.
  - Evidence: [Lab 003 report](../../labs/lab-003-local-spin-dos/REPORT.md). Bohrdt et al., arXiv:2108.04118, for the mixed-dimensional definition and DMRG setting. The SMG-versus-AFM wording is the author reading, not a label in that paper's figures.
- **c-002 · code · frontier** — Add a text scan that fails the solver prompt if it contains hopping amplitudes, exchange constants, Hubbard interactions, orbital names, filling, a named target phase, or the inferred words square lattice, charge gap, spin gap, and superconductivity.
  - Parent: `x-001`.
  - Why it has budget: the failure mode of this benchmark is leaking the Hamiltonian into the prompt.
  - Next action: implement the scan in Lab 001 against the extracted prompt, not against this whole task file.
  - Evidence: none yet.

## Decision rules

- Keep a mechanism on the author table when it can satisfy all three public facts. Do not delete it for being less interesting.
- Prune a mechanism only when a public fact or a computed spectrum rules it out, and write that reason here.
- Do not distill code into `src/` or prose into `note/` from the prompt draft alone.
- Do not put Green's-function zeros, band folding, interlayer coupling, or a phase name into the public prompt.

## Related pages

- [Current synthesis](../thesis.md)
- [ARPES prediction target](../questions/arpes-prediction.md)
- [Lab 001 report](../../labs/lab-001-phenomenon-card/REPORT.md)
- [Lab 002 report](../../labs/lab-002-cluster-spectra/REPORT.md)
