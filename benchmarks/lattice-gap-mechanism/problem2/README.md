# problem2 — bilayer t1–t2–J phase diagram from a neural quantum state

Deliverable: `report/report.md` (Markdown) and `report/report.pdf` (same content, built by `code/md2pdf.py`).

- `code/` — all sources (model, exact diagonalization, NQS-VMC engine, batch plans, analysis, strong-coupling theory, spectra, figures).
- `data/` — one JSON (+ `.mpack` parameters) per optimized state; `summary.json` = per-point diagnostics; `phase_labels.json`; `validation_2x2.md`; `spectra_J8.json`.
- `figures/` — line cuts, n(k) and S(q) maps, phase diagram, strong-coupling bands and gaps, spectra.
- `logs/` — per-run logs and batch logs.
- `.venv/` — Python 3.11 environment (NetKet 3.23, JAX 0.10.2). All production runs used the CPU backend (both H200 GPUs were fully occupied by other users when the project started); the CUDA plugin was added afterwards. Select with `JAX_PLATFORMS=cpu` or `JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=<id>`; on the GPU use `--chunk 128`-style chunking for 6×6 (see `code/bench_device.py` for the CPU/GPU timing comparison).

Reproduce a point: `.venv/bin/python code/run_point.py --Lx 4 --Ly 4 --bc pa --J 4 --N1 16 --N2 16 --Nup 16 --Ndn 16 --init singlet --out data/example`.
Rebuild the analysis and report tables: `.venv/bin/python code/analyze.py && .venv/bin/python code/update_report_tables.py && .venv/bin/python code/md2pdf.py`.
