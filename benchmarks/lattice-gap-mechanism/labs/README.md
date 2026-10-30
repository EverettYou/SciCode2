# Labs

This is the index of experiments. Every lab lives in a stable-identity `lab-NNN-slug/` folder, begins with a prospective `REPORT.md` and executable `PLAN.md`, and links to local `wiki/ideas/` pages plus the synthesis context that motivated it.

## Nodes

- [lab-001-phenomenon-card](lab-001-phenomenon-card/REPORT.md) — Extract the solver prompt and the mechanism table. Not run.
- [lab-002-cluster-spectra](lab-002-cluster-spectra/REPORT.md) — Exact diagonalization of a bilayer plaquette and the infinite-lattice nearest-neighbor band. Run.
- [lab-003-local-spin-dos](lab-003-local-spin-dos/REPORT.md) — Leading strong-coupling spin excitation, summed over momentum. Run.
- [lab-004-stm-greens-function](lab-004-stm-greens-function/REPORT.md) — Tunneling density of states from the strong-coupling Green's function with two hoppings. Run.
- [lab-005-nqs-phase-diagram](lab-005-nqs-phase-diagram/REPORT.md) — Neural quantum state line cut of the forward-problem Hamiltonian. Not run.

## Graph conventions

Lab reports are raw sources for `$wiki-ingest`. Node-local scripts, results, and figures stay inside the lab folder. Scripts may import stable functions from `../src/`. Stable reusable code is promoted to `src/`; completed knowledge is compiled into `wiki/`, not copied into ad hoc notes.
