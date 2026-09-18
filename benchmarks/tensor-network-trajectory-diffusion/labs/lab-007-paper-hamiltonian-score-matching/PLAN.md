# Paper trajectory reversal: dense N=1/N=2, then MPS time evolution

## Objective

Qualify the paper-style learned control Hamiltonian, repair dense/MPS execution disagreement, and measure frozen short-to-long transfer under the user-authorized continuation.

Gate/QR brickwork is out of scope. The paper learns a control Hamiltonian
\(H_\theta(z_t,t)\) on Pauli coordinates \(z\), then reverses by Hamiltonian
time evolution. Do **dense** Fig. 2–4 first; only then replace the state
by an MPS and evolve with TDVP.

## Paper numerical targets (Liu et al., Sec. III.A.4)

Shared schedule: \(T=3\), \(\gamma=1\), \(dt=0.01\) (300 steps).

**N=1 (Figs. 2–3).** Training ensemble is \(|0\rangle\) plus complex Gaussian
noise of std 0.2. Learned object is the Bloch field
\(H=h_x\sigma_x+h_y\sigma_y+h_z\sigma_z\). Metric is Wasserstein-1 of the
backward ensemble versus the initial ensemble, plus the control-field
trajectory \(h(t)\).

**N=2 (Fig. 4).** Same schedule. (a) Fixed Bell target
\(|\psi_B\rangle=(|\uparrow\downarrow\rangle-|\downarrow\uparrow\rangle)/\sqrt{2}\).
(b) Thermal ensemble of
\(H=J\sigma_1\cdot\sigma_2+B_x\sigma_{1x}+B_z\sigma_{2x}\) with
\(B_x=B_z=0.5\), \(J=1\), \(T_H\in[0,0.5]\). \(z\) is the 15-dimensional
two-qubit Pauli vector; \(H_\theta\) is a 15-coefficient Hermitian combination
of those Paulis. Metric is again \(W_1(p_{\theta,t},p_{\mathrm{true},0})\).

Forward data: randomized on-site Pauli weak measurements. Training: generate
forward trajectories, then learn \(h_\theta(z,t)\) so that the score operator
\(V=\exp[(-\gamma/2\,\delta O^2+2iH)\,dt]\) matches consecutive states
(Eqs. 24–28). Reverse is closed-loop Hamiltonian flow using the *current*
\(z_t\), not a frozen record decoder.

## Current dense status

N=1 Fig. 2: closed-loop \(F\approx 0.90\), \(\langle Z\rangle\approx 0.93\).
N=2 Fig. 4(a) Bell: closed-loop \(F=0.973\), \(W_1=0.094\),
\(\langle XX,YY,ZZ\rangle\approx(-0.96,-0.96,-0.97)\).
N=2 Fig. 4(b) Heisenberg thermal: closed-loop \(F=0.978\), ensemble \(W_1=0.091\).
Frozen forward \(z\) fails in all three (\(F\sim 0.25\)–\(0.53\)).

MPS reverse of the same \(V\) matches dense to \(10^{-14}\) at N=1 and N=2.
The full MPS *training* loop is in place: local contractions for \(z\), MLP
for local/NN Hamiltonian coefficients, TEBD apply. Dense weights on that loop
give N=1 \(F=0.907\) and N=2 Bell \(F=0.939\). Training from scratch on MPS
reaches N=1 \(F=0.899\) and N=2 Bell \(F\approx 0.90\) (80 epochs). Remaining
paper gap is the shadow decoder for \(z\), not the MPS mechanics. Larger \(N\)
needs a bounded-range MPO, not the full \(4^N-1\) Pauli expansion.

The QuantumDiffusion / SciCode2 companion repo is a later QR-transformer
experiment. It is not the paper's N=1/2 implementation.

## MPS time evolution (after dense N=1/2 pass)

Do not replace \(H\) by a learned brickwork of gates. Keep \(H_\theta(z,t)\)
and evolve the state on the tensor-network manifold.

Wu and Nys, [PRX Quantum (2026)](https://journals.aps.org/prxquantum/abstract/10.1103/tggc-8fjx)
([arXiv:2512.06768](https://arxiv.org/abs/2512.06768)), formulate real-time
TN dynamics as TDVP / tVMC: integrate \(\sum_\beta S_{\alpha\beta}\dot\theta_\beta=-ig_\alpha\)
on the variational manifold, after removing gauge null directions of the
quantum geometric tensor. That is the 2D PEPS construction. In 1D the same
geometry is standard MPS TDVP (Haegeman et al.), which Quimb already
implements. TEBD (Trotter + SVD) is a cheaper comparator, not the primary
reverse engine.

Pipeline after dense parity:

1. Forward: local Kraus updates on MPS (already checked at small \(N\)).
2. \(z_t\): local Pauli expectations from the MPS, not a dense \(2^N\) Bloch
   vector.
3. Reverse: one TDVP step of the local/MPO Hamiltonian \(H(z_t,t)\) (and the
   known \(-\gamma/2\,\delta O^2\) backaction term) per \(dt\).
4. Dense-vs-MPS parity at \(N=1,2\) with the same \(h_\theta\) weights, then
   larger \(N\) with reported max bond dimension.

## Parameterization for larger \(N\)

Do **not** let the network emit MPO tensors. An unconstrained MPO has gauge
redundancy, so the same \(H\) is many \(\theta\); a net that cannot gauge-fix
that output is likely untrainable. The learned object stays a **sum of local
Pauli terms** with coefficients \(h_P(z_{\mathrm{loc}},t)\). At range \(R=2\)
that is \(3N\) on-site plus \(9(N-1)\) nearest-neighbor two-site coefficients
(\(12N-9\): 15 at \(N=2\), 111 at \(N=10\)). Those coefficients may be packed
into an MPO only as an *application* format, or applied by TEBD; the
parameters themselves are the term coefficients.

Training loss remains per-step mean infidelity over all \(dt\) (diffusion-style
score matching). Closed-loop \(F\) / \(W_1\) are evaluation only. Shadow
decoding of \(z\) is deferred; it needs an A/B test against state-contracted
\(z\), and may well make learning worse.

## Order of work

1. Finish documenting N=1 dense Fig. 2. Done.
2. Dense N=2 Bell, then Heisenberg thermal. Done (\(F\approx 0.97\), \(W_1\approx 0.09\)).
3. MPS loop: local \(z\), TEBD apply, train at N=1/2, compare to dense. Done.
4. Lift \(H_\theta\) to translation-shared local Pauli coefficients (not MPO
   tensors). \(N=2\) Bell with radius-1 window matched the 15-parameter TEBD
   run (\(F\approx 0.91\), best 0.946). Reverse engine is now **1-site MPS-TDVP**
   (QR gauge, SVD-free), the 1D Wu–Nys flow. TEBD stays a no-grad comparator.
   \(N=3\) GHZ showed that local-\(z\) diffusion restores only *visible*
   stabilizers: \(\langle ZZ\rangle\to 0.99\) (repetition-code space) while
   \(\langle XXX\rangle\) stays \(\sim 0.1\) unless the observation window
   contains it *and* the loss uses the 300-step endpoint. Observation radius
   and Hamiltonian radius need not match (see 3-local, drive 2-local).
5. Local-stabilizer program (current). Do **not** scale GHZ; \(X^{\otimes N}\)
   is not a fixed-weight local stabilizer. Unique cluster and code-space
   ensembles are done at dense \(N=3\). Next is **ancilla-locked cluster**
   (Choi/EPR purification of the edge logicals). First training run: MPS
   2-local hybrid on \(A_L{-}1{-}2{-}3{-}A_R\). Haar code-space is not a
   uniqueness target. See the section below.
6. Later: A/B of shadow-decoded \(z\) vs MPS-contracted \(z\).

## Local-stabilizer program

Control \(H\) stays 2-local. Observation window is large enough to see every
*check* of the code, not necessarily the logicals. Metrics are stabilizer
expectations and the logical ensemble, not unique-state fidelity alone.

**Codes**

| code | local checks | logicals | GSD (OBC) |
|---|---|---|---|
| repetition / GHZ ferromagnet | \(Z_i Z_{i+1}\) (2-local) | \(Z_L=Z_1\), \(X_L=X^{\otimes N}\) | 2 |
| 1D cluster SPT | bulk \(Z_{i-1}X_i Z_{i+1}\) (3-local); edges \(X_1Z_2\), \(Z_{N-1}X_N\) | two edge qubits | 4 if edges free, 1 if edges pinned |

**Ensembles**

1. Unique ground state (all checks including edges): cluster \(\lvert C\rangle\), or GHZ. Asks whether a *particular* logical is pinned by the record.
2. Haar (Gaussian-projected) in the code space of *bulk* checks only. Asks: are checks restored, and does each trajectory return to *its* logical or scatter in the manifold?

**Losses**

- `one_step`: paper score matching. Expected to restore visible 2-local checks; 3-local checks may need the endpoint.
- `hybrid`: one-step + 300-step closed-loop overlap with the sampled initial state (same-record, not a fixed logical).

**Order**

1. Re-read N=3 GHZ A as repetition-code success (\(\langle ZZ\rangle\approx 0.99\), logical \(X\) free under one-step). Done.
2. N=3 unique cluster, \(z\) 3-local (=full), \(H\) 2-local, `one_step` then `hybrid`. Log \(\langle XZI\rangle,\langle ZXZ\rangle,\langle IZX\rangle\) and same-record \(F\). Done (dense); MPS-TDVP one-step in progress, same pattern at epoch 40.
3. N=3 cluster *code* ensemble (only bulk \(ZXZ\)). Log check restoration vs logical-edge Bloch mean/std across trajectories. Done (dense hybrid): \(\langle ZXZ\rangle\to 0.96\), same-record \(F=0.21\), ensemble collapsed to one edge logical. Logical was unspecified; no extra handle.
4. **Ancilla-locked cluster** (next). Unique purification of the code space: each edge logical is Bell-paired with an ancilla. See section below. First run is MPS 2-local hybrid on \(N=3+2\) (\(\chi=4\) is exact). Haar code-space is no longer a uniqueness target.
5. N=4,5 cluster (no ancilla) with a radius-2 observation window, then the same with ancillas on a longer chain, after the five-check table is filled.

## Ancilla-locked cluster (logical handle)

Core experiment: chain \(A_L{-}1{-}2{-}3{-}A_R\) (dense dim 32). 2-local \(H\) on those five sites. Log the **five checks separately**, not a single \(F\). Haar code-space is retired as a uniqueness target; the ancilla lock is the unique pure state.

Prediction: stepwise matching pulls the 2-local locks \(\langle Z_A Z_1\rangle\) (and \(\langle Z_3 Z_{A_R}\rangle\)) to 0.99, while 3-local \(ZXZ\) and \(X_A X_1 Z_2\) stay low; hybrid is what fills the unique purified state. If that table hits, the logical “extra signal” has to be a 2-local check in the same tier as the lane, or the paper’s stepwise loss will not learn it.

Control: same state, three-local \(H\), stepwise matching only — expect all five checks back (change \(H\), not the loss). MPS is the training loop for the first run; dense 32×32 is a parity check, not a prerequisite.

### Why

Unique cluster \(\lvert C\rangle\) pins the edges with \(X_1Z_2\) and \(Z_{N-1}X_N\). That is a *specific* logical of the bulk code, easy to train (hybrid \(F=0.997\)), but there is no register you can measure to teleport into the code.

The code-space ensemble leaves those logicals free (Haar pure states in the 4-fold GSD). Bulk \(\langle ZXZ\rangle\) comes back; the logical does not. Closed-loop reverse from \(t=T\) only sees the *current* \(z\), which no longer names which logical you started from. Collapse to one attractor is the expected failure of an unspecified logical, not a bug in TDVP.

The ancilla construction does not freeze the logical to \(\lvert C\rangle\). It **locks each edge logical to a physical ancilla** by a Bell pair. The joint state on \(A_L{-}1{-}\cdots{-}N{-}A_R\) is a unique pure state (Choi / EPR purification of the code), and the ancillas are the extra signal: measure them to teleport into the code.

This addresses **logical specification**, not the 3-local score-matching gap. 2-local \(H\) + one-step loss will still struggle with weight-3 checks; hybrid or a 3-local term in \(H\) is the separate knob for those.

### State

Chain: \(A_L,1,2,\ldots,N,A_R\). Open boundary, bulk cluster checks plus two Bell locks. For \(N=3\) system + 2 ancillas (5 qubits, dim 32):

| check | support | weight |
|---|---|---|
| \(Z_1 X_2 Z_3\) | bulk | 3 |
| \(Z_{A_L} Z_1\) | left lock | 2 |
| \(X_{A_L} X_1 Z_2\) | left lock | 3 |
| \(Z_3 Z_{A_R}\) | right lock | 2 |
| \(Z_2 X_3 X_{A_R}\) | right lock | 3 |

Five independent generators \(\Rightarrow\) unique stabilizer state. \(Z_A Z_1\) is the 2-local handle; \(X_A X_1 Z_2\) is the conjugate Bell check.

Prepare as a pure state, never a mixed logical \(\rho\): put the system in a reference code state (\(\bar Z_L=\bar Z_R=+1\)), ancillas in \(\lvert 0\rangle\), then two Hadamard+CNOT in the logical basis (or project onto the five generators). Forward protocol unchanged: \(T=3\), \(\gamma=1\), \(dt=0.01\), on-site weak Paulis on all five sites.

### What \(H\) and \(z\) see

- \(H\): 2-local on the **extended** 5-site chain (ancilla–system bonds are ordinary NN). \(3\cdot 5+9\cdot 4=51\) coefficients. Do not add 3-body terms in the first pass.
- \(z\): radius-2 window — every Pauli whose support span is \(\le 2\) (159 operators). That covers all five checks. Full \(4^5-1=1023\) is an optional dense ceiling, not required at \(N=3+2\).

Observation radius and Hamiltonian radius need not match: see 3-local checks, drive 2-local \(H\).

### Losses and metrics

Keep the two losses already in `train_n3_dense_ghz.py`:

- `one_step`: paper score matching.
- `hybrid`: one-step + 300-step closed-loop overlap with **this trajectory's** \(\psi_0\) (the unique ancilla-locked state).

Do **not** report a single \(F\) as the science. Log each check separately:

| quantity | locality | one-step prediction | hybrid prediction |
|---|---|---|---|
| \(\langle Z_{A_L}Z_1\rangle\), \(\langle Z_3 Z_{A_R}\rangle\) | 2-local lock | \(\to 0.99\) | \(\to 0.99\) |
| \(\langle X_{A_L}X_1Z_2\rangle\), \(\langle Z_2 X_3 X_{A_R}\rangle\) | 3-local lock | stays low (\(\sim 0.1\)) | \(\to 0.99\) |
| \(\langle Z_1 X_2 Z_3\rangle\) | 3-local bulk | stays low | \(\to 0.99\) |
| same-record \(F\) to \(\psi_0\) | full state | \(\sim 0.5\)–\(0.6\) (locks yes, bulk no) | \(\to 0.99\) |

If one-step already pulls \(Z_A Z_1\) to 0.99 while bulk \(ZXZ\) stays \(\sim 0.1\), that confirms: extra logical signal is learned under the paper loss **only when it is 2-local**, same as \(\langle ZZ\rangle\) and edge \(\langle XZI\rangle\).

Optional later: after a successful unique-state reverse, measure the recovered ancillas (or apply the teleportation circuit) and report the induced logical on the system. That is a use-case check, not the training target.

### Order of experiments

On five qubits the exact MPS bond is \(\chi=4\) (bonds \(2,4,4,2\)). 1-site TDVP at that \(\chi\) is the full 32-dimensional manifold, so the first run *is* MPS-level training, not a truncated proxy.

1. **First: MPS 2-local hybrid** (`train_mps_ancilla_cluster.py`). Forward is MPS Kraus. \(H\) is 51 on-site+NN coefficients. \(z\) is radius-2 (159 operators, every check visible). Training reverse uses the exact 32×32 score operator (\(\chi=4\) is the full manifold; 300-step BPTT through 1-site QR explodes). Eval reverse is still 1-site TDVP. Loss is one-step + 300-step closed-loop overlap with this trajectory’s \(\psi_0\). Log the five checks and same-record \(F\). Train on GPU 1, never CPU unless `--cpu` is passed.
2. Same MPS loop, 2-local \(H\), `one_step` only. Predict 2-local locks \(\to 0.99\), 3-local checks stay low.
3. Same state, 3-local (or full) \(H\), `one_step` only. Predict all five checks restore without hybrid (the GHZ-C / “change \(H\) not loss” knob).
4. Dense 32×32 parity against the MPS hybrid weights (or a from-scratch dense twin). Report check-by-check, not just \(F\).
5. Do not scale GHZ. Do not go back to Haar code-space as a uniqueness target; ancilla-lock replaces it. Longer chains with reported \(\chi\) only after this five-check table is filled.

### Out of scope here

Shadow-decoded \(z\), MPO-parameterized \(H\), mixed logical \(\rho\) as a forward ensemble, and using unique \(\lvert C\rangle\) as a substitute for the ancilla register. Those remain later items in the local-stabilizer program.

## 2026-09-07 authorized continuation: numerical repair and larger N

The user authorized closing the dense/MPS gap and increasing system size,
then requested auto-research. Scheduler management is unavailable in this
session; schedules remain paused, and these are manual, bounded stages.
Historical controls and checkpoints remain immutable.

1. Preserve the legacy projected-gate routine; implement site-forward /
   bond-backward projector-splitting TDVP for the full frozen local generator.
   Require normalized state parity <1e-10 at N=1,2,3,5 with maximal bonds;
   parameter gradients must match dense AD and central differences <1e-5.
2. On frozen N=5 ancilla weights, seed 72026, use identical 300-step forward
   trajectories and axes for dense, legacy, and corrected TDVP rollouts.
   Report paired full-state overlap and all five checks, per trajectory.
   No training or checkpoint selection in this diagnostic.
3. Only after these gates pass, evaluate larger entangled cluster chains,
   distinguish numerical size scaling from learned-policy transfer, and
   test one frozen spatially shared controller at two unseen sizes if the
   existing architecture permits it. Report chi/timestep sensitivity and
   per-trajectory fidelity, checks, entanglement, runtime and tensor storage.
   A failed transfer remains a result; do not substitute local checks for F.

Initial per-command runtime budget: 10 minutes, checkpoint before extending.
Use no new numerical dependencies. The historical Lab 007 runtime currently
available is /usr/bin/python, Torch 2.6.0+cu124; the declared benchmark .venv
is absent. Record this reproducibility deviation, exact versions and source
hashes in artifacts; do not imply that the current uv lock was executed.

### Shared-controller transfer control (2026-09-07)

A 3-site observation window feeds each shared on-site head; each bond head
receives both adjacent windows (at most four physical sites). Missing-site
nonidentity features are zero padded. Heads have width 32, independent of N.
Train with the same 80-epoch, batch-8 budget at N=3 and N=5, seed 72026,
Adam lr=0.003, hybrid loss. The one-step component uses 16 uniformly sampled
time indices per epoch; endpoint loss differentiates the full 300-step dense
short-chain rollout. This is a deliberate dense-training ceiling, not an
MPS-training or record-decoder claim. Freeze the final epoch, never select by
validation/test results. N=3 transfer is retained even if N=5 improves it.

The N=3 run failed at exact N=4 (F=0.463); N=5 training tests whether exposing
both-full-window interior bonds helps, without declaring that explanation
proven. Evaluate N=3,4,5,6,8,12 with chi=2,4; use chi=8 and projector substeps
as follow-on convergence controls if needed. Each fixed-size test seed is
82026+N, independent of training/validation; records are paired across cells.

Ancilla-locked chains are a local Hadamard on each endpoint of a cluster
chain. Test the same frozen model under that explicitly recorded local basis
change: transform boundary features and Hamiltonian coefficients, with no
retraining. Keep physical on-site weak measurements unchanged. Verify this
conversion by a dense-equivalent numerical test before using it for transfer.


## Stable interfaces

`mps_backend.reverse_tdvp_local` consumes normalized BatchMPS, on-site and
nearest-neighbor Hamiltonian coefficients, axes, gamma and dt. It returns a
normalized MPS on the same bond spaces. `SharedControl` uses fixed-width local
features at every N. Checkpoints are state dicts; output directories are unique
and evaluation scripts refuse to overwrite existing runs. Historical v1
artifacts remain unchanged.

## Steps

Execute the dated bounded continuation and shared-controller control above.
The five-qubit control takes about 9.4 seconds per epoch on this CPU. At its
saved epoch-30 checkpoint the remaining same-budget run was reviewed; extend
that command's runtime cap to 15 minutes to finish the predeclared 80 epochs.
This changes no optimization budget or checkpoint-selection rule.

## Completion criteria

For this bounded continuation: pass small-N dense/TDVP state and gradient
checks; finish the paired frozen five-qubit audit; retain the N=3 transfer
negative result; finish N=5 training and frozen larger-chain evaluation with
chi/refinement controls; record scripts, seeds, source hashes and individual
trajectory metrics; write an audited report and local-wiki handoff. The wider
record-conditioned scalable-training benchmark remains open even if these
bounded experiments complete.
