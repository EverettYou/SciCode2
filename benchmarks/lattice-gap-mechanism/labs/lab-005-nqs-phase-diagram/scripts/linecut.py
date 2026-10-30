"""Half-filled line cut of the bilayer t1-t2-J model with a neural quantum state.

The ansatz is a Slater determinant plus a restricted Boltzmann machine.
J=0 is checked against the exact filled tight-binding band on the same cluster.
"""

from __future__ import annotations

import json
from pathlib import Path

import netket as nk
import numpy as np
from flax import linen as nn

T1 = 1.0
T2 = 0.2
L = 4
J_VALUES = (0.0, 0.5, 2.0, 4.0, 8.0)
N_ITER = 300
N_SAMPLES = 512
OUT = Path(__file__).resolve().parents[1] / "results"


class RBMSlater(nn.Module):
    hilbert: nk.hilbert.SpinOrbitalFermions
    alpha: int = 2

    @nn.compact
    def __call__(self, x):
        slater = nk.models.Slater2nd(
            self.hilbert, generalized=False, restricted=True, param_dtype=float
        )(x)
        rbm = nk.models.RBM(alpha=self.alpha, param_dtype=float)(x)
        return slater + rbm


def lattice():
    n_cell = L * L
    def index(layer, x, y):
        return layer * n_cell + (x % L) * L + (y % L)

    nn_bonds = []
    nnn_bonds = []
    for x in range(L):
        for y in range(L):
            for layer in (0, 1):
                i = index(layer, x, y)
                jx = index(layer, x + 1, y)
                jy = index(layer, x, y + 1)
                nn_bonds.append((i, jx))
                nn_bonds.append((i, jy))
                nnn_bonds.append((i, index(layer, x + 1, y + 1)))
                nnn_bonds.append((i, index(layer, x + 1, y - 1)))
    rungs = [(index(0, x, y), index(1, x, y)) for x in range(L) for y in range(L)]
    return n_cell * 2, nn_bonds, nnn_bonds, rungs


def free_energy(n_orbitals: int) -> float:
    """Half filling, nu = 1/2: two electrons per lattice site, Sz = 0."""
    n_cell = L * L
    energies = []
    for x in range(L):
        for y in range(L):
            kx = 2.0 * np.pi * x / L
            ky = 2.0 * np.pi * y / L
            eps = -2.0 * T1 * (np.cos(kx) + np.cos(ky)) - 4.0 * T2 * np.cos(kx) * np.cos(ky)
            energies.extend((eps, eps))  # two layers
    energies = np.sort(np.array(energies))
    per_spin = n_orbitals // 2  # nu = 1/2: two electrons per lattice site, Sz = 0
    if per_spin * 2 != n_orbitals:
        raise RuntimeError("orbital count is not even")
    return float(2.0 * energies[:per_spin].sum())


def hamiltonian(exchange: float):
    n_orbitals, nn_bonds, nnn_bonds, rungs = lattice()
    per_spin = n_orbitals // 2
    hi = nk.hilbert.SpinOrbitalFermions(
        n_orbitals, s=1 / 2, n_fermions_per_spin=(per_spin, per_spin)
    )
    create = nk.operator.fermion.create
    destroy = nk.operator.fermion.destroy
    number = nk.operator.fermion.number
    ham = nk.operator.fermion.zero(hi)

    def hop(i, j, amplitude):
        term = nk.operator.fermion.zero(hi)
        for sz in (+1, -1):
            term += create(hi, i, sz=sz) @ destroy(hi, j, sz=sz)
            term += create(hi, j, sz=sz) @ destroy(hi, i, sz=sz)
        return amplitude * term

    for i, j in nn_bonds:
        ham += hop(i, j, -T1)
    for i, j in nnn_bonds:
        ham += hop(i, j, -T2)
    if exchange != 0.0:
        for a, b in rungs:
            nu_a, nd_a = number(hi, a, sz=+1), number(hi, a, sz=-1)
            nu_b, nd_b = number(hi, b, sz=+1), number(hi, b, sz=-1)
            sz_term = (nu_a - nd_a) @ (nu_b - nd_b)
            # (1/2)(S+a S-b + S-a S+b), and Sz Sz = (nu-nd)(nu-nd)/4
            exchange_xy = (
                create(hi, a, sz=+1) @ destroy(hi, a, sz=-1) @ create(hi, b, sz=-1) @ destroy(hi, b, sz=+1)
                + create(hi, a, sz=-1) @ destroy(hi, a, sz=+1) @ create(hi, b, sz=+1) @ destroy(hi, b, sz=-1)
            )
            ham += exchange * (0.25 * sz_term + 0.5 * exchange_xy)
    ham = nk.experimental.operator.ParticleNumberAndSpinConservingFermioperator2nd.from_fermionoperator2nd(ham)
    return hi, ham, free_energy(n_orbitals)


def optimize(exchange: float, n_iter: int) -> dict:
    hi, ham, exact = hamiltonian(exchange)
    clusters = []
    for spin in (+1, -1):
        modes = [hi._get_index(orbital, spin) for orbital in range(hi.n_orbitals)]
        clusters.extend([modes[a], modes[b]] for a in range(len(modes)) for b in range(a + 1, len(modes)))
    sampler = nk.sampler.MetropolisFermionHop(hi, clusters=clusters, n_chains=16)
    model = RBMSlater(hilbert=hi, alpha=2)
    state = nk.vqs.MCState(sampler, model, n_samples=N_SAMPLES, n_discard_per_chain=8)
    driver = nk.driver.VMC_SR(
        ham,
        nk.optimizer.Adam(learning_rate=0.01),
        variational_state=state,
        diag_shift=0.01,
        mode="real",
    )
    driver.run(n_iter=n_iter, out=str(OUT / f"vmc_J{exchange:.2f}"))
    energy = state.expect(ham)
    return {
        "J": exchange,
        "energy": float(np.real(energy.mean)),
        "error": float(np.real(energy.error_of_mean)),
        "free_band_energy": exact,
        "n_sites": int(hi.n_orbitals),
        "iterations": n_iter,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [optimize(exchange, N_ITER if exchange == 0.0 else N_ITER) for exchange in J_VALUES]
    (OUT / "linecut.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
