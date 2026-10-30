"""Correlated spectra of one bilayer plaquette, plus the infinite-lattice band.

The cluster is two layers of a 2x2 plaquette with periodic bonds counted once.
Intralayer hopping is t. The only interaction is an interlayer spin exchange J
on each rung. Full diagonalization in fixed (N_up, N_down) sectors.

The high-temperature momentum cuts are the infinite square lattice with the
same nearest-neighbor t. They are not cluster spectra.

Energies in this file are in units of t.
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import numpy as np

T = 1.0
J = 8.0
L = 2
N_SITES = 8
OUT = Path(__file__).resolve().parents[1] / "results"


def bit_count(mask: int) -> int:
    return int(mask).bit_count()


def parity_below(mask: int, site: int) -> float:
    return -1.0 if bit_count(mask & ((1 << site) - 1)) % 2 else 1.0


def site_index(layer: int, x: int, y: int) -> int:
    return layer * 4 + y * L + x


def coordinates(site: int) -> tuple[int, int, int]:
    layer, rest = divmod(site, 4)
    y, x = divmod(rest, L)
    return x, y, layer


def masks(n_particles: int) -> list[int]:
    out = []
    for occupied in combinations(range(N_SITES), n_particles):
        mask = 0
        for site in occupied:
            mask |= 1 << site
        out.append(mask)
    return out


def intralayer_bonds() -> list[tuple[int, int]]:
    bonds = []
    for layer in (0, 1):
        for x in range(L):
            for y in range(L):
                i = site_index(layer, x, y)
                j = site_index(layer, (x + 1) % L, y)
                k = site_index(layer, x, (y + 1) % L)
                bonds.append((min(i, j), max(i, j)))
                bonds.append((min(i, k), max(i, k)))
    return sorted(set(bonds))


def rungs() -> list[tuple[int, int]]:
    return [
        (site_index(0, x, y), site_index(1, x, y))
        for x in range(L)
        for y in range(L)
    ]


BONDS = intralayer_bonds()
RUNGS = rungs()


def sector(n_up: int, n_dn: int):
    up = masks(n_up)
    dn = masks(n_dn)
    basis = [(u, d) for u in up for d in dn]
    index = {state: i for i, state in enumerate(basis)}
    return basis, index


def annihilate(mask: int, site: int):
    if (mask >> site) & 1 == 0:
        return None
    return parity_below(mask, site), mask ^ (1 << site)


def create(mask: int, site: int):
    if (mask >> site) & 1 == 1:
        return None
    return parity_below(mask, site), mask ^ (1 << site)


def hop_masks(mask: int, i: int, j: int):
    removed = annihilate(mask, j)
    if removed is None:
        return None
    sign_r, mask_r = removed
    added = create(mask_r, i)
    if added is None:
        return None
    sign_c, mask_c = added
    return sign_r * sign_c, mask_c


def spin_flip(up: int, dn: int, source: int, target_up: bool):
    """Move one electron at `source` onto the other spin."""
    if target_up:
        removed = annihilate(dn, source)
        if removed is None:
            return None
        sign_r, dn2 = removed
        added = create(up, source)
        if added is None:
            return None
        sign_c, up2 = added
        return sign_r * sign_c, up2, dn2
    removed = annihilate(up, source)
    if removed is None:
        return None
    sign_r, up2 = removed
    added = create(dn, source)
    if added is None:
        return None
    sign_c, dn2 = added
    return sign_r * sign_c, up2, dn2


def build_hamiltonian(n_up: int, n_dn: int):
    basis, index = sector(n_up, n_dn)
    dim = len(basis)
    ham = np.zeros((dim, dim), dtype=np.float64)
    for col, (up, dn) in enumerate(basis):
        for a, b in RUNGS:
            sz_a = 0.5 * (((up >> a) & 1) - ((dn >> a) & 1))
            sz_b = 0.5 * (((up >> b) & 1) - ((dn >> b) & 1))
            ham[col, col] += J * sz_a * sz_b
        for i, j in BONDS:
            for which in ("up", "dn"):
                mask = up if which == "up" else dn
                hopped = hop_masks(mask, i, j)
                if hopped is not None:
                    sign, new_mask = hopped
                    new = (new_mask, dn) if which == "up" else (up, new_mask)
                    ham[index[new], col] += -T * sign
                hopped = hop_masks(mask, j, i)
                if hopped is not None:
                    sign, new_mask = hopped
                    new = (new_mask, dn) if which == "up" else (up, new_mask)
                    ham[index[new], col] += -T * sign
        for a, b in RUNGS:
            for src, dst in ((b, a), (a, b)):
                flipped = spin_flip(up, dn, src, target_up=False)
                if flipped is None:
                    continue
                sign1, up1, dn1 = flipped
                flipped2 = spin_flip(up1, dn1, dst, target_up=True)
                if flipped2 is None:
                    continue
                sign2, up2, dn2 = flipped2
                ham[index[(up2, dn2)], col] += 0.5 * J * sign1 * sign2
    ham = 0.5 * (ham + ham.T)
    return basis, index, ham


def ground_state(n_up: int, n_dn: int):
    basis, index, ham = build_hamiltonian(n_up, n_dn)
    energies, vectors = np.linalg.eigh(ham)
    return {
        "basis": basis,
        "index": index,
        "energies": energies,
        "vectors": vectors,
        "energy": float(energies[0]),
    }


def lowest_energy(n_up: int, n_dn: int) -> float:
    if n_up < 0 or n_dn < 0 or n_up > N_SITES or n_dn > N_SITES:
        return float("inf")
    _, _, ham = build_hamiltonian(n_up, n_dn)
    return float(np.linalg.eigvalsh(ham, subset_by_index=[0, 0])[0]) if False else float(np.linalg.eigvalsh(ham)[0])


def sector_ground(n_electrons: int) -> float:
    best = float("inf")
    for n_up in range(max(0, n_electrons - N_SITES), min(N_SITES, n_electrons) + 1):
        n_dn = n_electrons - n_up
        if abs(n_up - n_dn) > 1 and n_electrons % 2 == 0:
            continue
        best = min(best, lowest_energy(n_up, n_dn))
    return best


def singlet_ground(n_electrons: int):
    if n_electrons % 2:
        raise ValueError("singlet helper is for even electron number")
    n_up = n_electrons // 2
    return ground_state(n_up, n_up)


def apply_up_annihilation(vector, basis, index_dst, site: int) -> np.ndarray:
    out = np.zeros(len(index_dst), dtype=np.float64)
    for col, amplitude in enumerate(vector):
        if amplitude == 0.0:
            continue
        up, dn = basis[col]
        hopped = annihilate(up, site)
        if hopped is None:
            continue
        sign, new_up = hopped
        out[index_dst[(new_up, dn)]] += sign * amplitude
    return out


def apply_up_creation(vector, basis, index_dst, site: int) -> np.ndarray:
    out = np.zeros(len(index_dst), dtype=np.float64)
    for col, amplitude in enumerate(vector):
        if amplitude == 0.0:
            continue
        up, dn = basis[col]
        hopped = create(up, site)
        if hopped is None:
            continue
        sign, new_up = hopped
        out[index_dst[(new_up, dn)]] += sign * amplitude
    return out


def broaden(poles, weights, grid, sigma: float) -> np.ndarray:
    poles = np.asarray(poles, dtype=np.float64)
    weights = np.asarray(weights, dtype=np.float64)
    keep = weights > 1e-10
    poles, weights = poles[keep], weights[keep]
    if len(poles) == 0:
        return np.zeros_like(grid)
    delta = (grid[:, None] - poles[None, :]) / sigma
    kernel = np.exp(-0.5 * delta * delta) / (sigma * np.sqrt(2.0 * np.pi))
    return kernel @ weights


def local_spectrum(half, center: float, sigma: float = 0.2):
    """Tunneling spectrum of site 0, with omega measured from `center`."""
    basis, index, energies, vectors = half["basis"], half["index"], half["energies"], half["vectors"]
    gs = vectors[:, 0]
    e_gs = energies[0]
    removal = ground_state(3, 4)
    addition = ground_state(5, 4)
    v_rem = apply_up_annihilation(gs, basis, removal["index"], 0)
    v_add = apply_up_creation(gs, basis, addition["index"], 0)
    w_rem = np.abs(removal["vectors"].T @ v_rem) ** 2
    w_add = np.abs(addition["vectors"].T @ v_add) ** 2
    omega_rem = (e_gs - removal["energies"]) - center
    omega_add = (addition["energies"] - e_gs) - center
    grid = np.linspace(-12.0, 12.0, 481)
    intensity = broaden(omega_rem, w_rem, grid, sigma) + broaden(omega_add, w_add, grid, sigma)
    return grid, intensity, omega_rem, w_rem, omega_add, w_add


def momentum_removal(half, center: float):
    """Lowest removal energy at the plaquette momenta, measured from `center`."""
    basis = half["basis"]
    gs = half["vectors"][:, 0]
    e_gs = half["energies"][0]
    removal = ground_state(3, 4)
    peaks = []
    for qx, qy in ((0, 0), (1, 0), (1, 1)):
        vector = np.zeros(len(removal["index"]), dtype=np.complex128)
        for layer in (0, 1):
            for x in range(L):
                for y in range(L):
                    site = site_index(layer, x, y)
                    phase = np.exp(-1j * np.pi * (qx * x + qy * y))
                    piece = apply_up_annihilation(gs, basis, removal["index"], site)
                    vector += phase * piece
        vector /= np.sqrt(N_SITES)
        weights = np.abs(removal["vectors"].T @ vector) ** 2
        omegas = (e_gs - removal["energies"]) - center
        occupied = omegas < -1e-8
        if not np.any(occupied):
            peaks.append({"q": [qx, qy], "omega": None, "weight": 0.0})
            continue
        order = np.argsort(np.abs(omegas))
        chosen = next(i for i in order if occupied[i] and weights[i] > 1e-6)
        peaks.append(
            {
                "q": [qx, qy],
                "omega": float(omegas[chosen]),
                "weight": float(weights[chosen]),
            }
        )
    return peaks


def spin_spectrum(half):
    basis = half["basis"]
    gs = half["vectors"][:, 0].astype(np.complex128)
    e_gs = half["energies"][0]
    triplet = ground_state(5, 3)
    spectra = []
    for qx, qy, qz in (
        (0, 0, 1),
        (1, 0, 1),
        (1, 1, 1),
        (0, 0, 0),
        (1, 0, 0),
        (1, 1, 0),
    ):
        vector = np.zeros(len(triplet["index"]), dtype=np.complex128)
        for col, amplitude in enumerate(gs):
            if amplitude == 0.0:
                continue
            up, dn = basis[col]
            for site in range(N_SITES):
                flipped = spin_flip(up, dn, site, target_up=True)
                if flipped is None:
                    continue
                sign, up2, dn2 = flipped
                x, y, layer = coordinates(site)
                phase = np.exp(-1j * np.pi * (qx * x + qy * y + qz * layer))
                vector[triplet["index"][(up2, dn2)]] += amplitude * sign * phase
        weights = np.abs(triplet["vectors"].T @ vector) ** 2
        omegas = triplet["energies"] - e_gs
        positive = (omegas > 1e-8) & (weights > 1e-6)
        if not np.any(positive):
            onset, weight = None, 0.0
        else:
            onset_index = np.flatnonzero(positive)[np.argmin(omegas[positive])]
            onset = float(omegas[onset_index])
            weight = float(weights[onset_index])
        grid = np.linspace(0.0, 16.0, 321)
        curve = broaden(omegas, weights, grid, 0.25)
        spectra.append(
            {
                "q": [qx, qy, qz],
                "onset": onset,
                "onset_weight": weight,
                "curve_max": float(curve.max()),
                "omega": grid.tolist(),
                "intensity": curve.tolist(),
            }
        )
    return spectra


def correlators(solved) -> dict[str, float]:
    basis = solved["basis"]
    gs = solved["vectors"][:, 0]
    pair = 0.0
    exciton = 0.0
    for col, amplitude in enumerate(gs):
        up, dn = basis[col]
        if amplitude == 0.0:
            continue
        for x in range(L):
            for y in range(L):
                a = site_index(0, x, y)
                b = site_index(1, x, y)
                # Interlayer singlet amplitude on this rung: both spin arrangements.
                for src_up, dst_dn_site, src_dn, dst_up_site in (
                    (a, b, b, a),
                ):
                    pass
                removed_up = annihilate(up, a)
                removed_dn = annihilate(dn, b)
                if removed_up is not None and removed_dn is not None:
                    pair += abs(amplitude) ** 2
                removed_up = annihilate(up, b)
                removed_dn = annihilate(dn, a)
                if removed_up is not None and removed_dn is not None:
                    pair += abs(amplitude) ** 2
                # Density-density layer imbalance is not the exciton. Record double occupancy difference later.
                if ((up >> a) & 1) and ((dn >> b) & 1):
                    exciton += abs(amplitude) ** 2
                if ((up >> b) & 1) and ((dn >> a) & 1):
                    exciton += abs(amplitude) ** 2
    return {"singlet_weight": float(pair), "opposite_spin_rung_weight": float(exciton)}


def high_temperature_band(density: float, nk: int = 241):
    """Infinite-lattice nearest-neighbor band. Density is electrons per site, 0 to 2."""
    grid = np.linspace(-np.pi, np.pi, nk, endpoint=False)
    kx, ky = np.meshgrid(grid, grid, indexing="ij")
    epsilon = -2.0 * T * (np.cos(kx) + np.cos(ky))
    flat = np.sort(epsilon.ravel())
    # Two spins. Target count is density * nk^2 sites, each k holds 2 spins.
    target = density * flat.size
    # Each k-point in `flat` stands for one orbital; spin doubles the filling of that orbital.
    # n = (2 / Nk) * number of k with epsilon < mu, so number of occupied orbitals per spin is n/2 * Nk.
    occupied = 0.5 * density * flat.size

    def filling(mu: float) -> float:
        return 2.0 * np.count_nonzero(epsilon < mu) / epsilon.size

    lo, hi = float(flat[0] - 1.0), float(flat[-1] + 1.0)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if filling(mid) < density:
            lo = mid
        else:
            hi = mid
    mu = 0.5 * (lo + hi)
    path = []
    segments = (
        np.linspace(0.0, np.pi, 81),
        np.linspace(0.0, np.pi, 81),
        np.linspace(0.0, np.pi, 81),
    )
    # Gamma -> X -> M -> Gamma
    points = []
    for s in np.linspace(0.0, 1.0, 81):
        points.append((s * np.pi, 0.0, s))
    for s in np.linspace(0.0, 1.0, 81):
        points.append((np.pi, s * np.pi, 1.0 + s))
    for s in np.linspace(0.0, 1.0, 81):
        points.append(((1.0 - s) * np.pi, (1.0 - s) * np.pi, 2.0 + s))
    cut = []
    for kx_i, ky_i, distance in points:
        energy = -2.0 * T * (np.cos(kx_i) + np.cos(ky_i))
        cut.append({"s": float(distance), "k": [float(kx_i), float(ky_i)], "energy": float(energy - mu)})
    # Fermi surface samples
    mask = np.abs(epsilon - mu) < 0.06
    fs = [
        {"kx": float(kx[i, j]), "ky": float(ky[i, j])}
        for i, j in zip(*np.nonzero(mask))
    ]
    return {"density": density, "mu": float(mu), "filling_check": filling(mu), "cut": cut, "fermi_surface": fs}


def dimer_tests() -> None:
    global T, J, N_SITES, L, BONDS, RUNGS
    saved = (T, J, N_SITES, L, BONDS, RUNGS)
    T, J, N_SITES, L = 0.0, 1.0, 2, 1
    BONDS = []
    RUNGS = [(0, 1)]
    energy = lowest_energy(1, 1)
    if abs(energy + 0.75) > 1e-8:
        raise RuntimeError(f"dimer singlet energy {energy}, expected -0.75")
    T, J = 1.0, 0.0
    BONDS = [(0, 1)]
    RUNGS = []
    hopping = lowest_energy(1, 0)
    if abs(hopping + 1.0) > 1e-8:
        raise RuntimeError(f"dimer hopping energy {hopping}, expected -1")
    T, J, N_SITES, L, BONDS, RUNGS = saved


def main() -> None:
    dimer_tests()
    OUT.mkdir(parents=True, exist_ok=True)
    print("diagonalizing half filling")
    half = ground_state(4, 4)
    e8 = half["energy"]
    e7 = lowest_energy(4, 3)
    e9 = lowest_energy(5, 4)
    e6 = lowest_energy(3, 3)
    e5 = lowest_energy(3, 2)
    e4 = lowest_energy(2, 2)
    e3 = lowest_energy(2, 1)
    charge_gap = (e9 - e8) - (e8 - e7)
    spin = ground_state(5, 3)
    spin_gap = float(spin["energies"][0] - e8)
    pair_binding_from_8 = (e6 - e7) - (e7 - e8)
    # Addition peaks measured from the gap center at 8 electrons.
    center = 0.5 * ((e9 - e8) + (e8 - e7))
    # center here is the midpoint of the two chemical potentials, already an energy.
    # Removal energy of the N=7 ground state relative to mu_center:
    # mu_rem = e8 - e7, mu_add = e9 - e8, midpoint = (mu_add + mu_rem) / 2.
    midpoint = 0.5 * ((e9 - e8) + (e8 - e7))
    print("building spectra")
    grid, intensity, _, _, _, _ = local_spectrum(half, midpoint)
    peaks = momentum_removal(half, midpoint)
    neutrons = spin_spectrum(half)
    # Normalize tunneling by its value at the largest |bias| average.
    peak = float(np.max(intensity))
    tunneling = [
        {"bias": float(w), "conductance": float(y / peak)}
        for w, y in zip(grid, intensity)
        if abs(w) <= 8.0
    ]
    densities = []
    for n_el, label in ((8, 1.0), (6, 0.75), (4, 0.5)):
        if n_el == 8:
            gap = charge_gap
            binding = pair_binding_from_8
        elif n_el == 6:
            gap = (e7 - e6) - (e6 - e5)
            binding = (e4 - e5) - (e5 - e6)
        else:
            gap = (e5 - e4) - (e4 - e3)
            binding = None
        densities.append(
            {
                "electrons": n_el,
                "per_site": label,
                "charge_gap": gap,
                "pair_binding": binding,
            }
        )
    bands = [high_temperature_band(n) for n in (1.0, 0.75, 0.5)]
    summary = {
        "t": T,
        "J": J,
        "cluster": "2x2 bilayer plaquette, each intralayer bond once",
        "energies": {"N8": e8, "N7": e7, "N9": e9, "N6": e6, "N5": e5, "N4": e4, "N3": e3},
        "charge_gap_half_filling": charge_gap,
        "spin_gap_half_filling": spin_gap,
        "chemical_potential_midpoint": midpoint,
        "removal_peaks": peaks,
        "neutron": [
            {"q": item["q"], "onset": item["onset"], "onset_weight": item["onset_weight"], "curve_max": item["curve_max"]}
            for item in neutrons
        ],
        "densities": densities,
        "bands": [
            {"density": band["density"], "mu": band["mu"], "filling_check": band["filling_check"]}
            for band in bands
        ],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (OUT / "tunneling.json").write_text(json.dumps(tunneling), encoding="utf-8")
    (OUT / "neutron.json").write_text(
        json.dumps(
            [
                {"q": item["q"], "omega": item["omega"], "intensity": item["intensity"], "onset": item["onset"]}
                for item in neutrons
            ]
        ),
        encoding="utf-8",
    )
    for band in bands:
        name = f"band_{band['density']:.2f}.json"
        slim = {
            "density": band["density"],
            "mu": band["mu"],
            "cut": band["cut"][::4],
            "fermi_surface": band["fermi_surface"][::8],
        }
        (OUT / name).write_text(json.dumps(slim), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
