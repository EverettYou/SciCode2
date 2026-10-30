# Lattice Gap Mechanism from Experiment

This README is the benchmark onboarding summary. It points to the current research state; detailed claims and evidence live in the wiki and labs.

## Research goal

**Central question:** What microscopic mechanism accounts for a fourfold layered oxide whose spectra at one electron per metal site are gapped, whose high-temperature photoemission follows a square-lattice dispersion with both nearest-neighbor and next-nearest-neighbor hopping, and what low-temperature photoemission does that mechanism predict at 0.75 electrons per metal site?

**Objective:** From the Lab 004 spectra, all computed at one $(t_1,t_2,J)$, construct an explicit model and predict the low-temperature photoemission at 0.75 electrons per metal site, without being given the microscopic Hamiltonian.

**Success means:** `problem/prompt.pdf` contains only the schematic curves, the fourfold sheet symmetry, and the required answer, and an author-side comparison shows at least two mechanisms that fit those curves and disagree on ARPES.

**Scope boundary:** The public prompt does not say square lattice, charge gap, spin gap, or that superconductivity is absent. The resistivity curve rises on cooling. Interlayer-versus-intralayer coupling and doping stay on the author side. Large-scale Monte Carlo is not the workload.

## Current research status

- **Stage:** `problem-opened`
- **Overall state:** The phenomenon card is designed and has not been extracted or checked. No spectrum has been computed.
- **Current thesis:** The curves underdetermine the mechanism, so ARPES has to be a real prediction; an intralayer Hubbard antiferromagnet is the reading the local magnetic intensity should reject, because that intensity is zero up to a finite energy; see [the synthesis](wiki/thesis.md).
- **Active frontier:** `x-001` is the curve-level prompt, `k-001` lists the mechanisms that still fit, and `k-004` is the interlayer-singlet versus intralayer-antiferromagnet contrast; see [research frontier](wiki/ideas/research-frontier.md).
- **Active lab:** [Lab 003](labs/lab-003-local-spin-dos/REPORT.md) computed the local magnetic curve. [Lab 002](labs/lab-002-cluster-spectra/REPORT.md) computed the charge and photoemission numbers. [Lab 001](labs/lab-001-phenomenon-card/REPORT.md) still has to score mechanisms against that prompt.
- **Latest supported evidence:** Lab 004. Tunneling, high-temperature peaks, the local magnetic curve, and the resistivity all use $t_1$, $t_2=0.2t_1$, and $J=8t_1$. The eight-site ladder is not in the prompt.
- **Main uncertainty:** The mixed-dimensional DMRG papers define the geometry and the doped pairing; the undoped singlet-versus-antiferromagnet reading is the author interpretation and is not yet a catalogued paper.
- **Next decisive action:** Extract the text of `problem/prompt.pdf` and write the mechanism table in Lab 001, with the local magnetic intensity separating the antiferromagnet from the interlayer-singlet product.
- **Blockers or pending human input:** None. On [T-0007](../../talk/threads/T-0007-confirm-public-gap-prompt.md) the mixed-dimensional paper stays an external citation. The solver document is [`problem/prompt.pdf`](problem/prompt.pdf).
- **Last meaningful update:** 2026-10-26

Update this section only after a material evidence, frontier, lab, steering, or human-decision change. Treat it as a navigation snapshot, not as scientific evidence.

## Start here

Read in this order, stopping when the task has enough context:

1. [`metadata.yml`](metadata.yml) — authoritative identity, scope, research question, expected outputs, evidence requirements, stage, and review state.
2. [`problem/TASK.md`](problem/TASK.md) — full research proposal and the author boundary. The solver document is [`problem/prompt.pdf`](problem/prompt.pdf).
3. [`wiki/index.md`](wiki/index.md), then [`wiki/thesis.md`](wiki/thesis.md) — the local knowledge map and current synthesis.
4. [`wiki/ideas/research-frontier.md`](wiki/ideas/research-frontier.md) — idea ancestry, active frontier, next actions, and decision rules.
5. [`labs/README.md`](labs/README.md) — experiment index; the active lab is Lab 001.
6. [`src/`](src/) and [`note/`](note/) — stable deliverables. Both are empty of results.
7. [`../../talk/threads/T-0007-confirm-public-gap-prompt.md`](../../talk/threads/T-0007-confirm-public-gap-prompt.md) — open discussion of the public prompt.

## Independent numerical environment

Each benchmark is a standalone uv project. Add only this benchmark's numerical dependencies to [`pyproject.toml`](pyproject.toml), commit its `uv.lock`, and keep its `.venv` local:

```bash
uv sync
uv run python path/to/experiment.py
```

Do not use `uv sync --active` from a root environment. Benchmark environments share repository files and dependency policy, not installed `site-packages`.

## Source foundation

### Papers

- `chang2023fssmg` — Fermi surface symmetric mass generation: a quantum Monte-Carlo study

### Reference implementations and other inputs

See the `paper_ids` in [`metadata.yml`](metadata.yml). This paper has no companion repository. The global page is cited from [`wiki/sources.yml`](wiki/sources.yml). The solver does not receive the Hamiltonian.

## Reading discipline

- Use this README to orient and route work, not to substantiate scientific claims.
- `problem/prompt.pdf` is the solver statement. The rest of `problem/TASK.md` is author context and must not be pasted into that PDF.
- Use local `wiki/ideas/` for research decisions and lab reports for benchmark evidence.
- When detailed artifacts disagree with this summary, trust the detailed artifact and refresh this README.
