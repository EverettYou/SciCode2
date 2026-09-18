# Protocol audit: paper figures vs repository notebook vs this lab

This note records mismatches found before treating any N=1 number as
a reproduction of "paper fidelity near 1".

## Paper numerical demonstration (arXiv:2508.08799, Figs. 2–4)

- Reverse model: a control Hamiltonian \(H_\theta(z_t,t)\) generating a
  unitary reverse flow \(V_\theta=\exp[(-\gamma/2\,\delta O^2+2i H_\theta)\,dt]\).
- Loss: mean infidelity \(1-\mathbb{E}|\langle\psi_{t-dt}|V_\theta|\psi_t\rangle|^2\).
- Schedule: \(T=3\), \(\gamma=1\), \(dt=0.01\) (about 300 reverse steps).
- Metric: Wasserstein-1 distance \(W_1(p_{\theta,t},p_{\mathrm{true},0})\)
  decaying toward 0. Single-qubit and two-qubit (Bell, Heisenberg) examples.
- State access: decoded Pauli expectations \(z_t\) from the measurement
  record, not a transformer over discrete outcome tokens.

The paper does **not** train a dense \(2^N\times 2^N\) QR head with a
Frobenius \(U K_t K_{t-1}\propto I\) loss.

## Repository notebook `test/2026-03-14.ipynb`

- Device: CUDA (`PolicyModel(...).to(device)`).
- Discrete weak measurements, \(\varepsilon=0.8\), \(T=30\), 1024
  trajectories/epoch, 2000 Adam steps at \(10^{-3}\), initial \(|0\rangle\).
- Policy: 2-layer Llama transformer pooling the **future measurement
  tokens**, emitting a full complex matrix then QR.
- Loss: \(\|U_t K_t K_{t-1}-c I\|_F^2\) averaged over \(t=1,\ldots,T-1\).
- Logged loss: 0.049800 at epoch 1, 0.040487 at epoch 2000; minimum
  0.040296. The notebook itself never drives this loss near zero.
- Evaluation cell: stochastic `BackwardDiffusion.trajectory` from **random
  pure states**, conditioned on a forward record from \(|0\rangle\). This
  samples **new** weak measurements on the backward path. The notebook
  plots a Bloch sphere and prints no numerical fidelity.

Notebook `test/2026-03-16.ipynb` adds `trajectory_reversal` (apply only
\(U\)'s, \(T-1\) steps, no new measurements) but uses a different training
budget (\(\varepsilon=0.5\), 100 epochs).

## This lab's previous N=1/2 numbers

Lab 001's held-out fidelities \(\approx 0.65\) (\(N=1\)) and \(\approx 0.42\)
(\(N=2\)) used \(\varepsilon=0.5\), \(T=6\), 128 Adam updates. That is a
short-budget interface qualification, not the notebook or paper protocol.

## Metrics that must stay separate

1. **Paper-style stochastic backward**: random initial pure states, new
   measurements each reverse step, then \(U\) from the recorded forward
   future. Notebook Fig-style. Report \(P(|0\rangle)\) and mean Bloch
   polarization, labeled as stochastic.
2. **Deterministic recorded-trajectory reversal**: start from the **same**
   forward final states and records, apply `trajectory_reversal` (no new
   measurements). This is the same-record fidelity.
3. **Training loss**: Frobenius residual. Matching the notebook means
   approaching \(\approx 0.040\) for \(\varepsilon=0.8\), \(T=30\), not 0.

A fidelity near 1, if it exists, belongs to the paper's continuous-time
Hamiltonian-learning experiment, not automatically to this discrete QR
notebook. If the CUDA notebook reproduction matches the 0.040 loss floor
and still does not recover \(P(|0\rangle)\approx 1\), that is a protocol
gap, not an MPS failure.
