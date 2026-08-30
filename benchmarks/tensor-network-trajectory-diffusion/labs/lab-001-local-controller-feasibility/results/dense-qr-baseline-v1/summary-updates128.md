# Dense QR 128-update seed checkpoint

Declared budget: 128 Adam updates, batch size 16, learning rate 0.001, and three initialization seeds per system size. The fixture, model, loss, and evaluation path are frozen by `dense-splits-v1` and `train_dense_qr_baseline.py`.

| Qubits | Seeds | Validation loss (mean ± sample SD) | Test loss (mean ± sample SD) |
| --- | --- | --- | --- |
| 1 | 2301, 2303, 2305 | 0.022944153 ± 0.000021128 | 0.022626974 ± 0.000011772 |
| 2 | 2302, 2304, 2306 | 0.002409271 ± 0.000000868 | 0.002370824 ± 0.000000017 |

This is a bounded reproducibility checkpoint, not a convergence claim, fidelity result, controller-head comparison, or locality result.
