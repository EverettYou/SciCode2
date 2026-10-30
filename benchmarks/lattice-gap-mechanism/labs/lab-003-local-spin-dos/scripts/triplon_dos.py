"""Leading-order triplon dispersion and its local density of states.

Strong-coupling expansion of two layers with intralayer hopping t and
interlayer exchange J. The unperturbed state is a product of rung singlets.
The leading spin excitation is one rung triplet. Its hopping and energy shift
are the second-order virtual processes across one bond, computed by degenerate
perturbation theory on two rungs and checked against exact diagonalization.
The local spectrum is the momentum sum of that triplon band on the square lattice.
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import numpy as np

J = 8.0
T_HOP = 1.0
OUT = Path(__file__).resolve().parents[1] / "results"


def masks(n_sites: int, n_particles: int) -> list[int]:
    out = []
    for occupied in combinations(range(n_sites), n_particles):
        mask = 0
        for site in occupied:
            mask |= 1 << site
        out.append(mask)
    return out


def parity_below(mask: int, site: int) -> float:
    return -1.0 if (mask & ((1 << site) - 1)).bit_count() % 2 else 1.0


def annihilate(mask: int, site: int):
    if (mask >> site) & 1 == 0:
        return None
    return parity_below(mask, site), mask ^ (1 << site)


def create(mask: int, site: int):
    if (mask >> site) & 1 == 1:
        return None
    return parity_below(mask, site), mask ^ (1 << site)


def hop(mask: int, i: int, j: int):
    removed = annihilate(mask, j)
    if removed is None:
        return None
    sign_r, mask_r = removed
    added = create(mask_r, i)
    if added is None:
        return None
    sign_c, mask_c = added
    return sign_r * sign_c, mask_c


def sector(n_up: int, n_dn: int):
    basis = [(up, dn) for up in masks(4, n_up) for dn in masks(4, n_dn)]
    index = {state: i for i, state in enumerate(basis)}
    return basis, index


def hamiltonian(n_up: int, n_dn: int, hopping: float, exchange: float):
    basis, index = sector(n_up, n_dn)
    dim = len(basis)
    ham = np.zeros((dim, dim))
    rungs = ((0, 1), (2, 3))
    bonds = ((0, 2), (1, 3))
    for col, (up, dn) in enumerate(basis):
        for a, b in rungs:
            sz_a = 0.5 * (((up >> a) & 1) - ((dn >> a) & 1))
            sz_b = 0.5 * (((up >> b) & 1) - ((dn >> b) & 1))
            ham[col, col] += exchange * sz_a * sz_b
            for src, dst in ((a, b), (b, a)):
                removed = annihilate(up, src)
                if removed is None:
                    continue
                sign_r, up1 = removed
                added = create(dn, src)
                if added is None:
                    continue
                sign_d, dn1 = added
                removed2 = annihilate(dn1, dst)
                if removed2 is None:
                    continue
                sign_r2, dn2 = removed2
                added2 = create(up1, dst)
                if added2 is None:
                    continue
                sign_u2, up2 = added2
                ham[index[(up2, dn2)], col] += 0.5 * exchange * sign_r * sign_d * sign_r2 * sign_u2
        if hopping != 0.0:
            for i, j in bonds:
                for which in ("up", "dn"):
                    mask = up if which == "up" else dn
                    for src, dst in ((j, i), (i, j)):
                        hopped = hop(mask, dst, src)
                        if hopped is None:
                            continue
                        sign, new_mask = hopped
                        new = (new_mask, dn) if which == "up" else (up, new_mask)
                        ham[index[new], col] += -hopping * sign
    return 0.5 * (ham + ham.T)


def second_order(hopping: float, exchange: float):
    """Return (singlet shift, triplon diagonal, triplon hopping) for one bond."""
    h0_s = hamiltonian(2, 2, 0.0, exchange)
    ht_s = hamiltonian(2, 2, hopping, 0.0)
    eval_s, evec_s = np.linalg.eigh(h0_s)
    ground = np.flatnonzero(np.abs(eval_s - eval_s[0]) < 1e-8)
    if len(ground) != 1:
        raise RuntimeError(f"expected a unique two-singlet state, found {len(ground)}")
    e_s = eval_s[0]
    excited = np.flatnonzero(np.abs(eval_s - eval_s[0]) >= 1e-8)
    amp = evec_s[:, ground].T @ ht_s @ evec_s[:, excited]
    shift_s = float(np.sum(np.abs(amp) ** 2 / (e_s - eval_s[excited])))

    h0_t = hamiltonian(3, 1, 0.0, exchange)
    ht_t = hamiltonian(3, 1, hopping, 0.0)
    eval_t, evec_t = np.linalg.eigh(h0_t)
    e_t = eval_t[0]
    manifold = np.flatnonzero(np.abs(eval_t - e_t) < 1e-8)
    if len(manifold) != 2:
        raise RuntimeError(f"expected two one-triplon states, found {len(manifold)} at {e_t}")
    outside = np.flatnonzero(np.abs(eval_t - e_t) >= 1e-8)
    coupling = evec_t[:, manifold].T @ ht_t @ evec_t[:, outside]
    heff = coupling @ ((1.0 / (e_t - eval_t[outside]))[:, None] * coupling.T)
    heff = 0.5 * (heff + heff.T)
    eigenvalues = np.linalg.eigvalsh(heff)
    diagonal = float(np.mean(eigenvalues))
    hopping_eff = float(0.5 * (eigenvalues[-1] - eigenvalues[0]))
    return {
        "singlet_shift": shift_s,
        "triplon_diagonal": diagonal,
        "triplon_hopping": hopping_eff,
        "unperturbed_gap": float(e_t - e_s),
    }


def exact_gaps(hopping: float, exchange: float):
    e_s = np.linalg.eigvalsh(hamiltonian(2, 2, hopping, exchange))[0]
    triplet = np.linalg.eigvalsh(hamiltonian(3, 1, hopping, exchange))
    lowest_two = triplet[:2]
    return {
        "ground": float(e_s),
        "triplon_levels": [float(x) for x in lowest_two],
        "gaps": [float(x - e_s) for x in lowest_two],
    }


def elliptic_k(modulus_squared: np.ndarray) -> np.ndarray:
    """Complete elliptic integral K(k), with the argument k^2, by the AGM."""
    a = np.ones_like(modulus_squared, dtype=float)
    b = np.sqrt(np.maximum(1.0 - modulus_squared, 0.0))
    for _ in range(30):
        a, b = 0.5 * (a + b), np.sqrt(np.maximum(a * b, 0.0))
    return np.pi / (2.0 * a)


def smooth_local_density(center: float, half_width: float, sigma: float = 0.035):
    """Momentum sum of a cosine band, broadened so the van Hove peak is finite.

    The bare density is (1/pi^2) K(sqrt(1-u^2)) on |u|<1, which integrates to 1
    and equals 1/(2 pi) at each edge. The plotted curve divides by that edge value.
    """
    energy = np.linspace(0.0, 10.0, 2001)
    reduced = (energy - center) / half_width
    inside = np.abs(reduced) < 1.0 - 1e-6
    modulus = np.zeros_like(energy)
    modulus[inside] = 1.0 - reduced[inside] ** 2
    bare = np.zeros_like(energy)
    bare[inside] = elliptic_k(modulus[inside]) / np.pi**2
    window = np.linspace(-0.4, 0.4, 401)
    kernel = np.exp(-0.5 * (window / sigma) ** 2)
    kernel /= kernel.sum()
    smooth = np.convolve(bare, kernel, mode="same")
    edge = (np.pi / 2.0) / np.pi**2
    return energy, smooth / edge


def local_density(center: float, hopping: float, n_k: int = 401):
    """Density of omega = center + 2*hopping*(cos kx + cos ky)."""
    grid = np.linspace(-np.pi, np.pi, n_k, endpoint=False)
    kx, ky = np.meshgrid(grid, grid, indexing="ij")
    omega = center + 2.0 * hopping * (np.cos(kx) + np.cos(ky))
    lo, hi = float(omega.min()), float(omega.max())
    bins = np.linspace(lo, hi, 401)
    counts, edges = np.histogram(omega, bins=bins)
    centers = 0.5 * (edges[:-1] + edges[1:])
    density = counts / (counts.sum() * (edges[1] - edges[0]))
    return lo, hi, centers, density


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    bare = second_order(1.0, J)
    # Scale to the physical hopping. Second order is proportional to t^2.
    scale = T_HOP ** 2
    shift_s = bare["singlet_shift"] * scale
    diagonal = bare["triplon_diagonal"] * scale
    t_bond = bare["triplon_hopping"] * scale
    gap0 = bare["unperturbed_gap"]
    center = gap0 + 4.0 * (diagonal - shift_s)
    # Two-rung exact check at small t, where the lattice coordination is 1.
    small = 0.05
    pt = second_order(small, J)
    exact = exact_gaps(small, J)
    predicted = [
        gap0 + (pt["triplon_diagonal"] - pt["singlet_shift"]) + pt["triplon_hopping"],
        gap0 + (pt["triplon_diagonal"] - pt["singlet_shift"]) - pt["triplon_hopping"],
    ]
    half_width = 4.0 * abs(t_bond)
    lo = center - half_width
    hi = center + half_width
    _, _, energy, density = local_density(center, t_bond)
    curve = [
        {"energy": float(e), "intensity": float(d)}
        for e, d in zip(energy, density)
        if d > 0.0 or abs(e - lo) < 1e-8 or abs(e - hi) < 1e-8
    ]
    summary = {
        "J": J,
        "t": T_HOP,
        "unperturbed_gap": gap0,
        "singlet_shift_per_bond": shift_s,
        "triplon_diagonal_per_bond": diagonal,
        "triplon_hopping_per_bond": t_bond,
        "band_center": center,
        "band_bottom": lo,
        "band_top": hi,
        "small_t_check": {
            "t": small,
            "perturbation_gaps": predicted,
            "exact_gaps": exact["gaps"],
        },
    }
    smooth_energy, smooth_intensity = smooth_local_density(center, half_width)
    summary["broadening"] = 0.035
    summary["normalization"] = "unsmeared edge value 1/(2 pi)"
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (OUT / "local_dos.json").write_text(json.dumps(curve), encoding="utf-8")
    chosen = np.linspace(0, len(smooth_energy) - 1, 241).astype(int)
    lines = ["energy intensity"]
    for index in chosen:
        lines.append(f"{smooth_energy[index]:.5f} {smooth_intensity[index]:.6f}")
    text = "\n".join(lines) + "\n"
    (OUT / "local-magnetic-dos.dat").write_text(text, encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
