# Strict N=1/N=2 reproduction — running log

Date: 2026-08-30. Device: NVIDIA H200 NVL, torch 2.6.0+cu124, CUDA.

Two metrics are never mixed:

- **Paper-style stochastic backward**: new weak measurements on the reverse
  path, random pure initial states (`BackwardDiffusion.trajectory`).
- **Deterministic same-record reversal**: apply learned unitaries to the
  *same* forward final states and records, no new measurements.

## Protocol audit

See [`PROTOCOL.md`](PROTOCOL.md). The arXiv paper's Figs. 2–4 are
continuous-time Hamiltonian learning (\(T=3\), \(\gamma=1\), \(dt=0.01\),
mean-infidelity). The repository notebook `2026-03-14.ipynb` is a discrete
QR-transformer with Frobenius loss \(\|U K_t K_{t-1}-cI\|_F^2\),
\(\varepsilon=0.8\), \(T=30\), 2000 epochs. The notebook's own loss plateaus
at \(0.040487\).

## A. CUDA notebook reproduction (Frobenius loss)

Command:

```bash
CUDA_VISIBLE_DEVICES=1 python labs/lab-001-local-controller-feasibility/reproduce_paper_n1.py \
  --epochs 2000 --seed 7011 --eval-every 100 --output-name n1
```

| epoch | train loss | stochastic \(P(\|0\rangle)\) | deterministic same-record \(F\) |
|------:|-----------:|-----------------------------:|--------------------------------:|
| 1 | 0.0570 | 0.501 | 0.503 |
| 100 | 0.0404 | 0.489 | 0.516 |
| 200 | 0.0405 | 0.497 | 0.502 |
| 500 | 0.0405 | 0.500 | 0.501 |
| 800 | 0.0405 | 0.492 | 0.477 |
| 1200 | 0.0404 | 0.508 | 0.489 |
| 2000 | 0.0405 | 0.501 | 0.484 |

Finished in 2061 s on H200 (`CUDA_VISIBLE_DEVICES=1`, seed 7011). Final
loss 0.04047 matches the notebook epoch-2000 value 0.040487. Stochastic
\(P(|0\rangle)=0.501\) and same-record \(F=0.484\): **no recovery**.
Outputs: `n1.json`, `n1-policy.pt`, `n1-environment.json`.

## B. Oracle polar inverse of \(K_t K_{t-1}\)

`oracle_n1_reversal.py`, 512 trajectories, CPU.

- Mean Frobenius residual of the oracle: 0.0129 (better than learned 0.040).
- Companion `trajectory_reversal` indexing \(F\): 0.475.
- Skip-2 indexing \(F\): 0.485.
- Two-step state fidelity \(|\langle\psi_{t-1}|U|\psi_{t+1}\rangle|^2\): 0.522.

**Conclusion:** no unitary that inverts the Kraus *operators* can reverse
these states. The notebook objective is misspecified relative to
trajectory reversal. This is not an MPS failure.

## C. Infidelity + rollout loss (paper-style state objective)

Same PolicyModel, same \(\varepsilon,T\), same \(|0\rangle\) data, but loss
is one-step infidelity plus full-rollout infidelity to the initial state.

```bash
CUDA_VISIBLE_DEVICES=0 python labs/lab-001-local-controller-feasibility/train_infidelity_n1.py \
  --epochs 800 --seed 7111 --eval-every 25 --output-name n1-infidelity
```

| epoch | rollout infidelity | deterministic same-record \(F\) | polarization | stochastic \(P(\|0\rangle)\) |
|------:|-------------------:|--------------------------------:|-------------:|-----------------------------:|
| 1 | 0.492 | 0.504 | 0.012 | 0.512 |
| 50 | 0.320 | 0.714 | 0.429 | 0.503 |
| 75 | 0.129 | 0.936 | 0.880 | 0.488 |
| 150 | 0.026 | 0.959 | 0.950 | 0.509 |
| 200 | 0.0087 | 0.988 | 0.976 | 0.505 |
| 250 | 0.0095 | 0.990 | 0.981 | 0.507 |
| 300 | 0.0090 | 0.991 | 0.983 | 0.486 |

Same-record reversal reaches **fidelity \(\approx 0.99\)**. The stochastic
backward metric stays \(\approx 0.5\) and is reported separately; it is not
the recovery criterion used here.

## Next

1. Finish the 800-epoch infidelity checkpoint and a second N=1 seed.
2. Run the same infidelity protocol at N=2 (`train_infidelity.py --n-qubits 2`).
3. Only then replace the global QR head by a two-qubit brickwork + MPS
   parity (labs 003/005 already show execution-layer parity; they are not
   recovery fidelity).
