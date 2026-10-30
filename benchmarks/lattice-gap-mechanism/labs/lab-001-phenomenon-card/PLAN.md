# Lab 001 execution plan

## Objective

Write the solver-facing prompt and the mechanism table, then reject the prompt if it leaks microscopic specifications.

## Stable interfaces

No function from `src/` exists yet. This lab does not add one. The only outputs are the two Markdown files below and a scan record. A later spectral lab may propose a stable interface after the table says which comparison matters.

## Steps

1. Extract the text of `problem/prompt.pdf` into `results/solver-prompt.md` without adding sentences. That PDF is the solver document.
2. Write `results/mechanism-table.md` with rows for a band insulator, an intralayer Hubbard antiferromagnet, an exciton or pairing state, and an interlayer-singlet product. For each row, mark the tunneling curve, the local magnetic intensity, the resistivity curve, and the ARPES feature that would separate it. The magnetic column should put the antiferromagnet in tension, because the momentum-summed intensity is zero from zero energy up to a finite threshold.
3. Implement `scripts/scan_prompt.py` to read `results/solver-prompt.md` and exit nonzero if it matches a forbidden specification: hopping or exchange symbols used as couplings, Hubbard interaction, orbital labels, filling fraction, layer count, the name of the target symmetric-gapping phase, or the inferred phrases square lattice, charge gap, spin gap, and superconductivity. Write the matched or empty result to `results/prompt-scan.json`.
4. Confirm the scan passes on `solver-prompt.md` and fails on a one-line fixture that names an interlayer exchange. Keep the fixture inside this lab.
5. Update this report's findings, limitations, and search decision from those files. Hand only the supported claims to wiki ingest.

## Completion criteria

- `results/solver-prompt.md` matches the text of `problem/prompt.pdf` and the scan accepts it.
- `results/mechanism-table.md` covers all four rows and names an ARPES disagreement for at least one pair that survives the three facts.
- The negative fixture is rejected by the same scanner.
- The report does not claim that a spectrum was computed.

## Stop conditions

- Stop and return to the project talk if the transport sentence is changed before the files are written.
- Stop if every surviving row predicts the same ARPES features. Revise the question page before adding a spectral lab.
- Stop if the only way to make two rows disagree is to put a microscopic coupling into the public prompt.
