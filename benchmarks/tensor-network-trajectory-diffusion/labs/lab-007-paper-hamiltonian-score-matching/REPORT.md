---
document_type: lab_report
lab_id: lab-007
status: completed
idea_ids:
  - c-002
  - c-003
  - k-001
wiki_context:
  - ../../wiki/thesis.md
  - ../../wiki/ideas/research-frontier.md
related_labs:
  - lab-003-mps-dense-parity
  - lab-004-mps-forward-scaling
---

# Lab 007: paper control-Hamiltonian (dense N=1/N=2, then MPS reverse)

> **2026-09-07 correction:** The historical routine labeled 1-site TDVP was a
> projected-gate approximation, not site-forward/bond-backward TDVP. Its full-bond
> exactness claim is withdrawn. The [paired audit](results/tdvp-gap-audit-64-v2/summary.json)
> evaluates the unchanged five-qubit checkpoint on 64 identical trajectories:
> legacy F=0.2853, dense F=0.8050, corrected TDVP F=0.8050. Historical tables below
> are retained as recorded; their TDVP interpretation is superseded by this audit.
> Larger-chain shared-controller experiments are recorded in the continuation below.

Protocol is Liu et al. Sec. III.A / Figs. 2–4, not the repository QR notebooks:
\(T=3\), \(\gamma=1\), \(dt=0.01\) (300 steps); learn \(h_\theta(z,t)\);
score operator \(V=\exp[(\sum_j -\gamma/2\,\delta O_j^2+2iH)\,dt]\);
mean-infidelity loss; closed-loop reverse uses the *current* Pauli vector \(z\).
N=2 forward measures every qubit each step (paper Eq. sde_multisite).

## N=1 Fig. 2 (complete)

200 epochs on NVIDIA H200 NVL, seed 2026, 556 s.

| epoch | one-step infidelity | closed-loop \(z\) \(F\) | mean \(Z\) | polarization | oracle-\(z\) \(F\) |
|------:|--------------------:|------------------------:|-----------:|-------------:|-------------------:|
| 1 | 0.0131 | 0.535 | 0.075 | 0.347 | 0.518 |
| 10 | 0.0131 | 0.914 | 0.964 | 0.984 | 0.542 |
| 200 | 0.0131 | **0.904** | **0.932** | **0.934** | 0.529 |

Artifacts: `results/paper-fig2-n1-v1/`.

## N=2 Fig. 4(a) Bell (complete)

15-parameter \(H_\theta(z,t)\), singlet target. H200 `cuda:0`, seed 2026,
batch 128, 200 epochs, 391 s.

| epoch | closed-loop \(F\) to Bell | \(W_1\) (trace dist.) | \(\langle XX,YY,ZZ\rangle\) | oracle-\(z\) \(F\) |
|------:|--------------------------:|----------------------:|----------------------------:|-------------------:|
| 1 | 0.388 | 0.774 | −0.20, −0.26, −0.08 | 0.280 |
| 10 | 0.945 | 0.225 | −0.92, −0.93, −0.93 | 0.259 |
| 170 | 0.983 | 0.118 | −0.98, −0.98, −0.97 | 0.280 |
| 200 | **0.973** | **0.094** | **−0.96, −0.96, −0.97** | 0.254 |

Artifacts: `results/paper-fig4-n2-bell-v1/`.

## N=2 Fig. 4(b) Heisenberg thermal (complete)

Same trainer, `--target heisenberg`: \(J=1\), \(B_x=B_z=0.5\),
\(T_H\sim\mathrm{Unif}[0,0.5]\), max-entropy unraveling. 200 epochs, 371 s.

| epoch | closed-loop same-record \(F\) | \(W_1\) to initial ensemble | oracle-\(z\) \(F\) |
|------:|------------------------------:|----------------------------:|-------------------:|
| 1 | 0.368 | 0.776 | 0.289 |
| 10 | 0.938 | 0.233 | 0.257 |
| 170 | 0.982 | 0.111 | 0.251 |
| 200 | **0.978** | **0.091** | 0.256 |

Artifacts: `results/paper-fig4-n2-heisenberg-v1/`.

## MPS reverse of the same \(H(z,t)\) (complete at N=1,2)

The reverse generator is not a unitary. Exact backend: apply dense \(V\) as
an MPS gate. Scalable backend: first-order Trotter
\(\exp(-\gamma dt/2\sum_j\delta O_j^2)\) then \(\exp(2i H\,dt)\)
(1D TEBD / TDVP split of Wu & Nys).

| check | dense \(F\) | MPS exact vs dense | Trotter vs dense | max \(\|ψ_{\mathrm{dense}}-ψ_{\mathrm{MPS}}\|\) |
|---|---:|---:|---:|---:|
| N=1, 64 traj, Fig. 2 checkpoint | 0.898 | **1.0** | 0.999999 | \(1.2\times 10^{-15}\) |
| N=2 Bell, 32 traj, Fig. 4a checkpoint | 0.993 | **1.0** | 0.999998 | \(4.0\times 10^{-14}\) |

Artifacts: `results/mps-n1-reverse-parity-v1/`, `results/mps-n2-bell-reverse-parity-v1/`.

## MPS training loop (the gap that was missing)

The reverse-parity scripts above still densified \(z\) and applied a \(2^N\) \(V\).
The loop that is actually needed is now in `mps_backend.py` +
`train_mps_control_hamiltonian.py`:

1. Forward: on-site Kraus as 2×2 MPS gates.
2. \(z_t\): local Pauli contractions on the MPS (N=1 Bloch; N=2 all 1-site and
   nearest-neighbor 2-site Paulis). Matches dense \(z\) to \(10^{-15}\).
3. \(h_\theta(z,t)\): same MLP as the dense trainer.
4. Apply: TEBD — on-site backaction, on-site \(H\), then the two-site \(H\) as
   one 4×4 bond gate (SVD split). At N=2 every term is already nearest-neighbor.
5. Loss: MPS overlap infidelity \(\,1-|\langle\psi_{t-dt}|V|\psi_t\rangle|^2\).

### Same dense weights, MPS TEBD reverse

| | dense reverse \(F\) | MPS TEBD \(F\) | MPS TEBD \(W_1(t{=}0)\) |
|---|---:|---:|---:|
| N=1 Fig. 2 checkpoint | 0.904 | **0.907** | 0.179 |
| N=2 Bell checkpoint | 0.973 | **0.939** | 0.128 |

TEBD Trotter vs the combined \(2^N\) generator costs \(\sim 0.03\) at N=2.
Paper-style \(W_1(t)\) on the Bell run falls from 0.86 at \(t=T\) to 0.13 at
\(t=0\) (`results/mps-n2-bell-tebd-dense-weights-v1/`).

### Trained on the MPS loop (not transferred weights)

| | epochs | closed-loop \(F\) | \(W_1\) | target observable |
|---|---:|---:|---:|---|
| N=1 MPS TEBD from scratch | 80 | **0.899** | 0.140 | \(\langle Z\rangle=0.924\) |
| N=2 Bell MPS TEBD from scratch | 80 (best 70) | **0.901** (0.922) | 0.308 (0.274) | \(\langle XX,YY,ZZ\rangle\approx(-0.90,-0.82,-0.88)\) |

Dense N=1 was \(F=0.904\) at 200 epochs; MPS N=1 matches it. Dense N=2 Bell
was \(F=0.973\) at 200 epochs / batch 128; MPS N=2 from scratch with batch 32
and 80 epochs reaches \(F\approx 0.90\), same qualitative recovery of the
singlet. Artifacts: `results/mps-n1-fig2-tebd-v1/`, `results/mps-n2-bell-tebd-v1/`.

Still open relative to the paper: \(z_t\) is contracted from the current MPS
state, not from the shadow decoder in Sec. III.A. That decoder is the remaining
conditioner gap, not an MPS mechanics gap.

Closed-loop \(z\) recovers the paper targets; frozen forward \(z\) does not
(\(F\sim 0.25\)–\(0.53\)). One-step infidelity stays near \(0.013\) (N=1) or
\(0.027\) (N=2 dense) / \(0.014\) (N=2 TEBD) because \(dt\) is small; the
300-step reverse is the discriminating metric.

Next: keep this TEBD loop, replace the N=2 15-parameter \(H\) by a
bounded-range MPO at \(N>2\), and optionally train on shadow-decoded \(z\).


## Motivation

The completed small-system experiments motivate a local-Hamiltonian extension.
The 2026-09-07 continuation isolates numerical disagreement before interpreting
poor ancilla recovery or increasing N. The user explicitly authorized repair,
larger-system research, and auto-research setup in the active session.

## Design

Keep old checkpoints fixed for the paired numerical audit. Use the complete
frozen generator G=2iH-gamma/2 sum(P-<P>)² in a bond-5 MPO. TDVP evolves each
site center forward and the intervening bond center backward, with right/left
orthonormal environments. The former sweep is kept as
`reverse_projected_gate_legacy`. No legacy result artifacts are overwritten.

Then compare the same shared local controller architecture trained at N=3 and
N=5, with 80 epochs, batch 8 and final-checkpoint selection. Larger-system
rollouts use only local MPS contractions and effective center exponentials.
The three-site site windows and the union of two windows at a bond have
bounded support at every N. Dense training is a short-chain ceiling; the main
record-conditioned, scalable-training question remains open.

## Methods and execution

New numerical runs use /usr/bin/python, Torch 2.6.0+cu124, complex128 states,
float32 model weights, one CPU thread, no new numerical dependencies. This
is the available historical Lab 007 runtime, not the absent benchmark uv
venv; every artifact records that reproducibility deviation. Root wiki checks
use the existing frozen uv environment offline. Configuration, seeds, source
SHA256, checkpoint hashes, and per-trajectory results are in the new v2 JSON
artifacts. Exact source versions are preserved in `results/source-snapshots-v2/`.

The protocol remains T=3, gamma=1, dt=0.01, 300 steps of random on-site weak
Pauli measurements. Forward trajectories preserve rank; reverse one-site TDVP
uses explicitly padded bonds, fixed per rollout, with no SVD truncation or
claimed discarded-weight bound. Local reduced-state distances, point-target
ensemble W1, entropy, tensor storage and runtime accompany full-state fidelity.

From this lab directory, commands are:

```bash
python diagnose_tdvp_gap.py --device cpu --batch 64 --output results/tdvp-gap-audit-64-v2
python train_shared_cluster.py --n 3 --epochs 80 --batch 8 --output results/shared-cluster-n3-hybrid-v2
python train_shared_cluster.py --n 5 --epochs 80 --batch 8 --output results/shared-cluster-n5-hybrid-v2
python evaluate_shared_scaling.py --checkpoint results/shared-cluster-n3-hybrid-v2/model.pt --output results/shared-cluster-transfer-v2 --sizes 3 4 5 6 8 12 --chis 2 4 --batch 16
python diagnose_rollout_gradients.py --output results/tdvp-rollout-gradient-audit-v2
python -m pytest -q test_tdvp_projector.py
```

Training/evaluation drivers refuse to overwrite existing experiment directories;
use a fresh output directory when reproducing the commands. Numerical source
snapshots identify the exact versions run; later documentation-only revisions
are not silently substituted in the artifact hashes.


## Findings

The paired audit identifies a numerical backend error. Correcting it restores
dense/MPS agreement; the new shared policy improves transfer but retains
size-dependent global recovery error, as quantified below.

### Numerical repair: paired frozen checkpoint

The projector-splitting construction follows [Haegeman et al., PRB 94,
165116 (2016)](https://doi.org/10.1103/PhysRevB.94.165116). The full frozen
non-Hermitian generator is used consistently; backaction expectations are
computed from the normalized input state. The legacy routine both omitted the
bond-backward evolution and applied split updates with sequential expectations.
The audit isolates a backend error as a whole, not a unique attribution of the
entire error to one omitted term.

On 64 forward trajectories (seed 72026), the same untouched five-qubit
checkpoint gives mean F=0.28533 +/- 0.01244 SEM under the legacy routine,
F=0.80504 +/- 0.01051 under dense evaluation, and F=0.80504 +/- 0.01051 under
corrected TDVP. The old run's F=0.201 used different trajectories and must not
be substituted for the paired legacy control. Dense/corrected final vectors
differ by at most 4.81e-8 in the 64-trajectory audit (float32 feedback network);
the independent batch-8 audit gives 3.98e-14. Per-trajectory dense/corrected
fidelities meet the 1-1e-8 gate. See
[paired data](results/tdvp-gap-audit-64-v2/summary.json).

Small-system random-state parity at N=1,2,3,5 gives maximum vector error
1.38e-15, maximum coefficient-gradient error 4.45e-18, and central finite-
difference error below 6.74e-12. Six focused regression tests cover these
checks, zero-rank QR isometry, local Pauli features, cluster/ancilla target
preparation, physical basis conversion, and an N=8 path that forbids calling
`to_dense`.

A separate 300-step gradient audit on actual diffused cluster trajectories at
N=3 and N=5 matches dense and MPS losses within 2.2e-15 and returns identical
float32 parameter-gradient arrays. The largest gradients are respectively
0.853 and 0.510, so this is not a zero-gradient degeneracy. These are two
trajectories per N and one initialization; the check establishes bounded
end-to-end differentiability, not robust large-N training. See
[full-rollout gradient audit](results/tdvp-rollout-gradient-audit-v3/summary.json).

### Shared-controller training and initial transfer

Both models have 8,780 parameters, the same initialization seed and optimizer
schedule, and 80 epochs. Validation F is 0.99874 for the N=3-trained model and
0.98690 for the N=5-trained model. The final checkpoint is used regardless of
whether an earlier epoch scored higher. N=3 training took 196 seconds; N=5
training took 750 seconds. Both use dense short-chain evolution with verified
MPS feature/update/gradient equivalence; no claim of scalable training is made.

At chi=4 on independent held-out records, the frozen N=3-trained controller
gives F=0.9984, 0.4634, 0.1892, 0.0903, 0.0625, 0.00769 at N=3,4,5,6,8,12.
The N=5-trained controller gives F=0.6618, 0.9064, 0.9869, 0.8896, 0.6667,
0.4157 at those same sizes. Shorter-chain transfer is not uniformly good
either. Improvement after N=5 training is consistent with better local-geometry
coverage, but does not isolate it from more qubit-level data and compute.
The N=3 failure is retained in
[its transfer data](results/shared-cluster-transfer-v2/summary.json).


### Completed size sweep through 32 qubits

One frozen N=5 checkpoint, 16 trajectories per size, chi=4, 300 reverse steps.
Errors below are trajectory SEMs. These are partial-recovery results, not a
claim of uniform high fidelity or converged chi at the largest sizes.

| N | F | SEM | mean 3-site trace distance | reverse seconds |
|---:|---:|---:|---:|---:|
| 3 | 0.661784 | 0.003259 | 0.5815 | 2.73 |
| 4 | 0.906401 | 0.001678 | 0.2674 | 4.06 |
| 5 | 0.986947 | 0.001517 | 0.0872 | 6.37 |
| 6 | 0.889581 | 0.003751 | 0.1900 | 8.56 |
| 8 | 0.666655 | 0.003881 | 0.2516 | 13.25 |
| 12 | 0.415677 | 0.004731 | 0.2753 | 22.05 |
| 16 | 0.266586 | 0.003882 | 0.2831 | 31.15 |
| 24 | 0.110546 | 0.001532 | 0.2922 | 52.52 |
| 32 | 0.046742 | 0.000523 | 0.2939 | 90.45 |

At N=32, the uncontrolled F is 2.08e-10; recovered F is 0.046742.
Minimum mean stabilizer is 0.6894, mean three-site trace distance is 0.2939,
and middle-cut entropy is 1.1957 bits (ideal cluster: 1 bit). Final MPS tensor
storage is 239,616 bytes for the batch; this is not peak process memory.
Forward generation takes 111.49 s, and reverse takes 90.45 s. No global dense
state or matrix is constructed in these evaluations.

The descriptive log-F fit over N=12,16,24,32 has slope -0.10928 per
qubit. This supports a finite-size observation of accumulating global error,
not an asymptotic theorem or seed-robust phase boundary. Local reduced-state
error also remains appreciable. Source data:
[large-size sweep](results/shared-cluster-large-transfer-v2/summary.json),
[descriptive fit](results/fidelity-decay-fit-v2.json).

The figure is generated by `plot_tdvp_transfer.py` from the paired audit and
both transfer sweeps: [repair and transfer](figures/tdvp-transfer-v2/repair-and-transfer.png).

## Analysis and limitations

- The numerical repair closes the dense/MPS backend disagreement on the
  tested full-bond systems. It does not repair an arbitrary learned policy or
  prove accuracy on an arbitrary truncated manifold.
- Current conditioning is exact local expectation values obtained from the
  simulator. No shadow decoder or measurement-record-only reconstruction was
  trained. Training still uses dense N=3 or N=5 states; only evaluation is
  demonstrated without global dense objects at larger N.
- Initial ensembles are fixed unique cluster or ancilla-locked pure states.
  The reported W1 is the mean pure-state trace distance to that point target;
  it is not a nontrivial two-sample ensemble test or proof of arbitrary logical
  information recovery/teleportation.
- Only one parameter-initialization seed per training size was used. SEMs
  quantify trajectory sampling, not training-seed uncertainty. There are 16
  trajectories per transfer cell; no favorable checkpoint selection occurs.
- Increasing chi and refining the projector sweep are different controls.
  Internal substeps keep h and backaction frozen within dt=0.01; they do not
  test a different forward schedule or a finer state-feedback sampling rate.
- One-site TDVP keeps a fixed bond space, initialized by exact zero padding.
  There is no discarded-weight estimate. Higher-chi checks are limited to the
  stated sizes; apparent low-chi success is not automatically convergence.
- Runtime is wall time on one CPU thread. Tensor storage counts final MPS
  tensors; process peak RSS is reported separately and includes Python/Torch
  and retained allocator memory. Neither is a claim of asymptotic scaling.
- An intended first ancilla command omitted its target flag and therefore
  repeated the cluster control. It is retained as
  `results/shared-cluster-n5-transfer-repeat-v2/`; it is not ancilla evidence.
  The actual ancilla run explicitly passes `--target ancilla`.
- The declared benchmark uv environment is absent; numeric runs use the
  recorded historical ambient stack. Exact source snapshots and run hashes
  are preserved, but isolated-environment reproduction remains a next step.


### Refinement and ancilla controls

At N=6, target F is 0.889581 with chi=4 and 0.887080 with exact chi=8.
At N=8 it is 0.666655 with chi=4 and 0.664633 with chi=8. Doubling internal
projector substeps changes these values by at most 8.6e-6 in the tested grid.
However, mean paired chi=4/8 state overlap at N=8 is only 0.98365: similar
target F does not establish full wavefunction convergence. No chi=8 claim
extends to the largest sizes. See
[refinement grid](results/shared-cluster-convergence-v2/summary.json).

The frozen N=5 controller, under the explicitly tested boundary Hadamard
conversion, gives ancilla-locked F=0.98609 +/- 0.00250 SEM at N=5,
0.67216 +/- 0.00210 at N=8, and 0.41808 +/- 0.00434 at N=12. These are physical
on-site weak-measurement trajectories, not a changed multi-site noise model.
All physical stabilizer strings are individually labeled in
[ancilla data](results/shared-ancilla-n5-transfer-v2/summary.json).

Additional commands (fresh output directories on reproduction):

```bash
python evaluate_shared_scaling.py --checkpoint results/shared-cluster-n5-hybrid-v2/model.pt --output results/shared-cluster-n5-transfer-v2 --sizes 3 4 5 6 8 12 --chis 2 4 --batch 16
python evaluate_shared_scaling.py --checkpoint results/shared-cluster-n5-hybrid-v2/model.pt --output results/shared-cluster-convergence-v2 --sizes 6 8 --chis 4 8 --substeps 1 2 --batch 16
python evaluate_shared_scaling.py --target ancilla --checkpoint results/shared-cluster-n5-hybrid-v2/model.pt --output results/shared-ancilla-n5-transfer-v2 --sizes 5 8 12 --chis 4 --batch 16
python evaluate_shared_scaling.py --checkpoint results/shared-cluster-n5-hybrid-v2/model.pt --output results/shared-cluster-large-transfer-v2 --sizes 16 24 32 --chis 4 --batch 16
python plot_tdvp_transfer.py
```

## Search decision

Retain the corrected projector-splitting backend and the validated gradient
path. Preserve the failed N=3 transfer branch. N=5 training improves transfer
but does not produce high global fidelity uniformly with N, even with exact
state features. The numerical repair is supported; broad scalable quantum
recovery is not established.

Candidate next controls, in information-value order: (1) compare two-local
versus three-local Hamiltonian support at matched training resources, with
fixed local observation access; (2) mix short training sizes at the same total
trajectory/update budget to test geometry dependence; (3) characterize the
remaining chi error with larger manifolds before any quantitative convergence
claim at N>=12. Additional decoder development should follow an adequate
state-feature ceiling. No new central question or Petz scope is introduced.

## Wiki ingest handoff

Ingest this completed bounded continuation into the local thesis, question,
frontier and a corrected-TDVP implementation page. Cite the paired audit,
shared-transfer tables and refinement grid directly. Preserve the historical
QR branch and explicitly withdraw the old projected-gate full-bond claim.
Do not promote code to src or conclusions to the research note until the
provenance and wiki validation gates pass. Keep the wider benchmark open.


## Validation and durable state

This report marks the bounded experiments above completed; the benchmark is
still researching. Auto-research schedule management is unavailable, so cached
scheduling state is paused and manual checkpoints/steering are recorded under
`.auto-research/`. Old automation IDs are unverified, not evidence of running
schedules. No talk thread awaits the user for this continuation.

The numerical regression suite passes. Repository-wide validation initially
also finds unrelated pre-existing missing reports/plan sections in Labs 005/006,
and three old `experiment` log headings rejected by the wiki linter. These
historical entries are preserved rather than rewritten. Those blockers prevent
advancing the synthesis digest or promoting to src/note; they do not invalidate
the independently recorded numerical results.
