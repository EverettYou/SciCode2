"""Local tunneling spectrum from the strong-coupling SMG Green's function.

Eq. (19) of Lu, Zeng, and You, arXiv:2307.12223:

    G(omega, k) = (omega + alpha * eps(k) / J**2)
                  / ((omega - eps(k) / 2)**2 - J**2)

The spectral function is -Im G(omega + i eta) / pi. The tunneling
curve is that function summed over the Brillouin zone.

The dispersion has nearest-neighbor hopping t1 and next-nearest
hopping t2. t2 moves the saddle off the band center. The high-
temperature photoemission table uses the same dispersion.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

T1 = 1.0
T2 = 0.2
J = 8.0
ALPHA = 1.0
ETA = 0.05
NK = 301
N_OMEGA = 1201
OMEGA_MIN = -14.0
OMEGA_MAX = 14.0

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = Path(__file__).resolve().parents[3]
OUT = ROOT / "results"
PUBLIC = BENCHMARK / "problem" / "figures" / "data"


def dispersion(kx: np.ndarray, ky: np.ndarray) -> np.ndarray:
    return -2.0 * T1 * (np.cos(kx) + np.cos(ky)) - 4.0 * T2 * np.cos(kx) * np.cos(ky)


def momentum_grid():
    grid = np.linspace(-np.pi, np.pi, NK, endpoint=False)
    kx, ky = np.meshgrid(grid, grid, indexing="ij")
    return dispersion(kx, ky).ravel()


def chemical_potential(eps: np.ndarray, electrons_per_site: float) -> float:
    """Both spins. electrons_per_site = 1 is one electron per site."""
    if not 0.0 < electrons_per_site < 2.0:
        raise ValueError(electrons_per_site)
    occupied_fraction = electrons_per_site / 2.0
    order = np.sort(eps)
    index = int(np.floor(occupied_fraction * len(order)))
    index = min(max(index, 0), len(order) - 1)
    return float(order[index])


def spectral_density(eps: np.ndarray):
    omega = np.linspace(OMEGA_MIN, OMEGA_MAX, N_OMEGA)
    density = np.zeros_like(omega)
    chunk = 40
    eye = 1j * ETA
    for start in range(0, len(omega), chunk):
        w = omega[start : start + chunk][:, None] + eye
        numer = w + ALPHA * eps[None, :] / J**2
        denom = (w - eps[None, :] / 2.0) ** 2 - J**2
        green = numer / denom
        spectral = -np.imag(green) / np.pi
        density[start : start + chunk] = spectral.mean(axis=1)
    return omega, density


def high_symmetry(mu: float) -> dict[str, float]:
    points = {
        "(0,0)": (0.0, 0.0),
        "(1/4,0)": (0.5 * np.pi, 0.0),
        "(1/2,0)": (np.pi, 0.0),
        "(1/2,1/4)": (np.pi, 0.5 * np.pi),
        "(1/2,1/2)": (np.pi, np.pi),
        "(1/4,1/4)": (0.5 * np.pi, 0.5 * np.pi),
    }
    return {name: float(dispersion(np.array(kx), np.array(ky)) - mu) for name, (kx, ky) in points.items()}


def bond_amplitudes(hopping: float) -> tuple[float, float, float]:
    """Second-order singlet shift, triplon diagonal, and triplon hopping on one bond.

    These match degenerate perturbation theory on two rungs: the shift is
    -(4/3) t^2/J, and the diagonal and hopping are -4 t^2/J and +4 t^2/J.
    A three-rung check shows distinct bonds add, with no extra cross term.
    """
    ratio = hopping**2 / J
    return -(4.0 / 3.0) * ratio, -4.0 * ratio, 4.0 * ratio


def magnetic_density():
    """Local density of the leading triplon band with both hoppings."""
    shift_1, diagonal_1, hop_1 = bond_amplitudes(T1)
    shift_2, diagonal_2, hop_2 = bond_amplitudes(T2)
    center = J + 4.0 * (diagonal_1 - shift_1) + 4.0 * (diagonal_2 - shift_2)
    grid = np.linspace(-np.pi, np.pi, 401, endpoint=False)
    kx, ky = np.meshgrid(grid, grid, indexing="ij")
    cos_x = np.cos(kx)
    cos_y = np.cos(ky)
    omega = center + 2.0 * hop_1 * (cos_x + cos_y) + 4.0 * hop_2 * cos_x * cos_y
    samples = {
        "(0,0)": center + 4.0 * hop_1 + 4.0 * hop_2,
        "(1/2,0)": center - 4.0 * hop_2,
        "(1/2,1/2)": center - 4.0 * hop_1 + 4.0 * hop_2,
    }
    edges = np.linspace(0.0, 10.0, 2001)
    counts, _ = np.histogram(omega, bins=edges)
    width = edges[1] - edges[0]
    bare = counts / (counts.sum() * width)
    sigma = 0.035
    window = np.linspace(-0.4, 0.4, 401)
    kernel = np.exp(-0.5 * (window / sigma) ** 2)
    kernel /= kernel.sum()
    smooth = np.convolve(bare, kernel, mode="same")
    centers = 0.5 * (edges[:-1] + edges[1:])
    bottom = samples["(1/2,1/2)"]
    # Plateau just inside the lower edge, before the saddle.
    plateau = (centers > bottom + 0.35) & (centers < bottom + 0.8)
    step = float(smooth[plateau].mean())
    return {
        "center": center,
        "hop_nn": hop_1,
        "hop_nnn": hop_2,
        "samples": samples,
        "bottom": bottom,
        "top": samples["(0,0)"],
        "saddle": samples["(1/2,0)"],
        "step": step,
        "energy": centers,
        "intensity": smooth / step,
    }


def resistivity_ratio() -> list[dict[str, float]]:
    """Activated ratio using the tunneling inner edge, 6D, as Delta/2."""
    half_gap = 6.0
    rows = []
    for temperature in (1.0, 1.5, 2.0, 3.0, 4.0):
        ratio = float(np.exp(half_gap * (1.0 / temperature - 0.25)))
        rows.append({"temperature": temperature, "ratio": ratio})
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    eps = momentum_grid()
    mu = {n: chemical_potential(eps, n) for n in (1.0, 0.75, 0.5)}
    bands = {f"{n:.2f}": high_symmetry(mu[n]) for n in mu}
    omega, density = spectral_density(eps)
    # Poles of Eq. (19). Gap center is the midpoint of the two inner edges.
    eps_min = -4.0 * T1 - 4.0 * T2
    eps_max = 4.0 * T1 - 4.0 * T2
    lower_inner = eps_max / 2.0 - J
    upper_inner = eps_min / 2.0 + J
    gap_center = 0.5 * (lower_inner + upper_inner)
    bias = omega - gap_center
    # Step height: mean of the DOS in a window just inside the lower band,
    # away from the outer edge and away from the saddle.
    lower_outer = eps_min / 2.0 - J
    saddle = 4.0 * T2
    lower_saddle = saddle / 2.0 - J
    window = (bias > (lower_outer - gap_center + 0.25)) & (bias < (lower_saddle - gap_center - 0.35))
    step = float(density[window].mean())
    scaled = density / step
    chosen = np.linspace(0, len(bias) - 1, 401).astype(int)
    lines = ["bias conductance"]
    for index in chosen:
        if -12.0 <= bias[index] <= 12.0:
            lines.append(f"{bias[index]:.5f} {max(scaled[index], 0.0):.6f}")
    text = "\n".join(lines) + "\n"
    (OUT / "stm-dos.dat").write_text(text, encoding="utf-8")
    PUBLIC.mkdir(parents=True, exist_ok=True)
    (PUBLIC / "stm-dos.dat").write_text(text, encoding="utf-8")
    occupied = {
        "(0,0)": float(dispersion(np.array(0.0), np.array(0.0)) / 2.0 - J - gap_center),
        "(1/2,0)": float(saddle / 2.0 - J - gap_center),
        "(1/2,1/2)": float(dispersion(np.array(np.pi), np.array(np.pi)) / 2.0 - J - gap_center),
    }
    summary = {
        "t1": T1,
        "t2": T2,
        "J": J,
        "alpha": ALPHA,
        "eta": ETA,
        "nk": NK,
        "eps_min": eps_min,
        "eps_max": eps_max,
        "saddle_energy": saddle,
        "gap_center": gap_center,
        "lower_outer_bias": float(lower_outer - gap_center),
        "lower_inner_bias": float(lower_inner - gap_center),
        "upper_inner_bias": float(upper_inner - gap_center),
        "upper_outer_bias": float(eps_max / 2.0 + J - gap_center),
        "lower_saddle_bias": float(lower_saddle - gap_center),
        "upper_saddle_bias": float(saddle / 2.0 + J - gap_center),
        "step_height": step,
        "sum_rule": float(np.trapezoid(density, omega)),
        "chemical_potential": {f"{n:.2f}": mu[n] for n in mu},
        "high_temperature_peaks": bands,
        "occupied_peaks_from_gap_center": occupied,
    }
    magnetic = magnetic_density()
    chosen_m = np.linspace(0, len(magnetic["energy"]) - 1, 241).astype(int)
    magnetic_lines = ["energy intensity"]
    for index in chosen_m:
        magnetic_lines.append(
            f"{magnetic['energy'][index]:.5f} {max(magnetic['intensity'][index], 0.0):.6f}"
        )
    magnetic_text = "\n".join(magnetic_lines) + "\n"
    (OUT / "local-magnetic-dos.dat").write_text(magnetic_text, encoding="utf-8")
    (PUBLIC / "local-magnetic-dos.dat").write_text(magnetic_text, encoding="utf-8")
    transport = resistivity_ratio()
    transport_lines = ["temperature ratio"]
    for row in transport:
        transport_lines.append(f"{row['temperature']:.2f} {row['ratio']:.6f}")
    (PUBLIC / "resistivity.dat").write_text("\n".join(transport_lines) + "\n", encoding="utf-8")
    summary["magnetic"] = {
        "center": magnetic["center"],
        "hop_nn": magnetic["hop_nn"],
        "hop_nnn": magnetic["hop_nnn"],
        "bottom": magnetic["bottom"],
        "saddle": magnetic["saddle"],
        "top": magnetic["top"],
        "step": magnetic["step"],
        "samples": magnetic["samples"],
    }
    summary["resistivity_ratio"] = transport
    summary["activation_half_gap"] = 6.0
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
