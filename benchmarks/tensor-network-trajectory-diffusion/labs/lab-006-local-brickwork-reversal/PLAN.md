# Lab 006: local two-qubit brickwork reversal

## Objective

After dense N=1/N=2 infidelity reversal works, replace the global QR unitary
by a brickwork of local two-qubit QR gates. Verify dense-vs-MPS execution
parity at N=1,2,3, report bond-dimension growth, then scale N.

## Constraints

- Do not emit a learned \(2^N\times 2^N\) matrix.
- Each two-qubit gate may use dense QR internally (4x4).
- MPS means matrix-product state, not Apple Metal.
- Dmax=1 is not an entangling test; brickwork must report bond growth.
- Keep stochastic-backward and same-record reversal metrics separate.

## Gate

Dense N=1 same-record fidelity \(\approx 0.99\) under infidelity+rollout
loss is the permission to start this lab's N=1/2 brickwork parity. N>=3
training starts only after N=2 dense brickwork recovers the initial state.
