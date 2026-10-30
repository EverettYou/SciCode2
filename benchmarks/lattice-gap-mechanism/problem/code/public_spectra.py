"""Public curves for the problem-1 prompt.

Half-filled tunneling combines two results at t2/t1 = 0.2 and J/t1 = 8.
The single-particle gap is the strong-coupling value Delta_1 = 7.99, so the
inner edges sit at about +/-4. Each side disperses as eps(k)/2, which puts
the saddle 4*t2 above the middle of that side. The side weights are the
residues of Eq. (19) of arXiv:2307.12223, so the two sides are not copies.

The lower density, nu = 0.2, is on the BCS side. Its low-temperature trace
is the Bogoliubov spectrum at the g = 3J/4 gap, a complete gap with sharp
quasiparticle peaks. The chemical potential is solved with the gap so the
occupied weight equals nu, rather than the normal-state Fermi-sea area.
The higher density, nu = 0.3, is on the BEC side. Its gap is also complete.
The half-width sits between the half-filled inner edge at 4 and the nu = 0.2
gap, one third of the way from 0.2 toward half filling. The density of states
is zero through the middle and rises gradually, and the band edges are pushed
out so the weight is spread over the band rather than piled into coherence
peaks. The trace at nu = 0.3 and high T is the normal-state density of states.
The thermal broadening has been deconvolved. The prompt does not state the temperature.

Outside a hard gap, each tunneling curve carries a V^2 background from
other bands. The gap interior is left as the model density of states.

The published nuclear curve at half filling is 1/(T1 T) from spectra.nmr_rate
on the two-rung triplon band at J = 8, normalized at T = 4. Points below
1e-5 are omitted from the public file, and so are points above T = 5, where
the temperature is no longer below the spin gap. The half-filled
resistivity keeps the low-temperature activation of the constant-tau Boltzmann
result of that same strong-coupling model at every temperature in the window,
normalized at T = 4. The full integral flattens once T is no longer small
compared with the charge gap; that flattening is not published, because the
spin relaxation on this crystal stays activated through the same window.

At nu = 0.2 the pair amplitude of the gap equation closes at the fixed-density
temperature, 1.00D. That scale exceeds the bilayer stiffness bound, so the
published transition is 0.55D. Below a Hebel–Slichter peak near 0.47D, 1/(T1 T)
falls as exp(-1.75/T); above the peak it is the Korringa value. The resistivity
is the normal-state metal above 0.55D and zero at and below it. At nu = 0.3 the
resistivity above 0.36D is the same one-third interpolation, in the logarithm,
between that metal and the half-filled activation, so it rises on cooling
more gently than the half-filled curve. It is zero below 0.20D. The nuclear rate on that crystal is one activation
on the tunneling gap at every temperature, with no break at the transition
and no coherence peak. At nu = 0.2 the published transition is 0.40D, below
the diamagnetic Kosterlitz–Thouless bound of the paired bilayer.
Noise is added before the normalization,
and every nuclear and resistivity curve is then divided by its noisy value
at T = 4D, so that point is exactly 1.
Drawn error bars are two standard deviations. The NMR bars add an absolute
background of 1e-4 in quadrature with the relative width.

Clean curves are written beside the public traces.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "figures" / "data"
# Plot inputs live in DATA. Model parameters, noiseless curves, and the
# high-temperature dispersion table stay out of that directory.
AUTHOR = ROOT / "author"
CODE2 = ROOT.parent / "problem2" / "code"
sys.path.insert(0, str(CODE2))

from model import dispersion  # noqa: E402
from spectra import bands, nmr_rate, resistivity  # noqa: E402

T1 = 1.0
T2 = 0.2
J = 8.0
ALPHA = 1.0
ETA = 0.08
NK = 241
SEED = 20261027
# Peak-position uncertainty grows with distance from the chemical potential.
# Near zero it is about 0.03D; at the band edge it is about 0.09D.
PEAK_SIGMA_FLOOR = 0.025
PEAK_SIGMA_SLOPE = 0.012
# Drawn uncertainties. One standard deviation does not cover the
# point-to-point fluctuation on the figures.
ERROR_BAR_SIGMAS = 2.0
NMR_PUBLIC_FLOOR = 1e-5
# Above the spin gap the Arrhenius slope is no longer diagnostic. The public
# half-filled curve stops at the last grid point below 5D (T = 4.43D).
NMR_HALF_T_MAX = 5.0
# Two-standard-deviation background on 1/(T1 T). It exceeds the rate near
# the public cutoff, which is why the trace stops there.
NMR_ABSOLUTE_ERROR = 1e-4
# Scatter on the points. Smaller than the error bar, so the trace stays
# readable while the bar still grows near the cutoff.
NMR_POINT_SIGMA = 1e-5
DYNES_GAMMA = 0.04


def momentum_mesh(n: int = NK):
    grid = np.linspace(-np.pi, np.pi, n, endpoint=False)
    kx, ky = np.meshgrid(grid, grid, indexing="ij")
    eps = dispersion(kx, ky).ravel()
    return eps


def residues(eps: np.ndarray):
    """Pole weights of Eq. (19). They sum to 1 at each momentum."""
    shift = eps / (4.0 * J) + ALPHA * eps / (2.0 * J**3)
    upper = 0.5 + shift
    lower = 0.5 - shift
    return upper, lower


def lorentzian(centers: np.ndarray, weights: np.ndarray, omega: np.ndarray, eta: float):
    density = np.zeros_like(omega)
    chunk = 24
    for start in range(0, len(omega), chunk):
        w = omega[start : start + chunk][:, None]
        kernel = eta / np.pi / ((w - centers[None, :]) ** 2 + eta**2)
        density[start : start + chunk] = (kernel * weights[None, :]).mean(axis=1)
    return density


def half_filled(omega: np.ndarray):
    """eps/2 dispersion, gap fixed at the J=8 strong-coupling value."""
    eps = momentum_mesh()
    # eps runs from -4.8 to 3.2. Poles at eps/2 +/- E0 have gap 2*E0 - 4.
    # Delta_1(J=8) = 7.99, so E0 = 6 and the centered inner edges are +/-4.
    e0 = 6.0
    gap_center = -0.4
    upper_w, lower_w = residues(eps)
    upper = lorentzian(eps / 2.0 + e0 - gap_center, upper_w, omega, ETA)
    lower = lorentzian(eps / 2.0 - e0 - gap_center, lower_w, omega, ETA)
    return upper + lower


def mu_of_nu(eps: np.ndarray, nu: float) -> float:
    order = np.sort(eps)
    return float(order[int(nu * len(order))])


def bcs_gap(eps: np.ndarray, nu: float, coupling_j: float = J) -> tuple[float, float]:
    mu = mu_of_nu(eps, nu)
    xi = eps - mu
    g = 0.75 * coupling_j

    def residual(delta: float) -> float:
        energy = np.sqrt(xi**2 + delta**2)
        return g * np.mean(1.0 / (2.0 * energy)) - 1.0

    lo, hi = 1e-3, 6.0
    if residual(lo) < 0:
        return 0.0, mu
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if residual(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi), mu


def _gap_residual(xi: np.ndarray, delta: float, temperature: float, coupling: float) -> float:
    energy = np.sqrt(xi * xi + delta * delta)
    if temperature <= 0.0:
        kernel = 1.0 / (2.0 * energy)
    else:
        kernel = np.tanh(energy / (2.0 * temperature)) / (2.0 * energy)
    return coupling * float(np.mean(kernel)) - 1.0


def bcs_occupation(eps: np.ndarray, mu: float, delta: float, temperature: float) -> float:
    """Electrons per site over 2. Equals nu when the number equation holds.

    At zero gap this is the Fermi sea. At finite gap it is the BCS weight
    v^2, so a particle-hole asymmetric band does not keep the normal filling.
    """
    xi = eps - mu
    if delta <= 0.0:
        if temperature <= 0.0:
            return float(np.mean(eps <= mu))
        clipped = np.clip(xi / temperature, -80.0, 80.0)
        return float(np.mean(1.0 / (np.exp(clipped) + 1.0)))
    energy = np.sqrt(xi * xi + delta * delta)
    if temperature <= 0.0:
        return float(np.mean(0.5 * (1.0 - xi / energy)))
    thermal = np.tanh(energy / (2.0 * temperature))
    return float(np.mean(0.5 * (1.0 - xi / energy * thermal)))


def solve_delta(eps: np.ndarray, mu: float, temperature: float, coupling: float) -> float:
    """Gap equation at fixed chemical potential. Zero when no solution exists."""
    xi = eps - mu
    if _gap_residual(xi, 1e-6, temperature, coupling) <= 0.0:
        return 0.0
    lo, hi = 1e-6, 8.0
    if _gap_residual(xi, hi, temperature, coupling) > 0.0:
        hi = 16.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if _gap_residual(xi, mid, temperature, coupling) > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def solve_mu(eps: np.ndarray, delta: float, temperature: float, nu: float) -> float:
    """Chemical potential at fixed gap whose occupation equals nu."""
    lo = float(np.min(eps)) - 1.0
    hi = float(np.max(eps)) + 1.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if bcs_occupation(eps, mid, delta, temperature) > nu:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def bcs_equilibrium(eps: np.ndarray, nu: float, temperature: float, coupling: float) -> tuple[float, float]:
    """Gap and chemical potential at fixed density.

    The gap equation is solved at each trial chemical potential, and the
    chemical potential is bisected until the occupation equals nu.
    """
    lo = float(np.min(eps)) - 1.0
    hi = float(np.max(eps)) + 1.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        delta = solve_delta(eps, mid, temperature, coupling)
        if bcs_occupation(eps, mid, delta, temperature) > nu:
            hi = mid
        else:
            lo = mid
    mu = 0.5 * (lo + hi)
    return solve_delta(eps, mu, temperature, coupling), mu


def bcs_dos(omega: np.ndarray, nu: float, delta: float, mu: float):
    eps = momentum_mesh()
    xi = eps - mu
    energy = np.sqrt(xi**2 + delta**2)
    u2 = 0.5 * (1.0 + xi / energy)
    v2 = 0.5 * (1.0 - xi / energy)
    return lorentzian(energy, u2, omega, ETA) + lorentzian(-energy, v2, omega, ETA)


# Inner edge of the half-filled tunneling gap. nu = 0.3 is this far from
# nu = 0.2 toward half filling: (0.3-0.2)/(0.5-0.2).
HALF_GAP_EDGE = 4.0
BEC_FILLING_WEIGHT = (0.3 - 0.2) / (0.5 - 0.2)
# onset < 1 turns the gap-edge divergence into a gradual rise. stretch
# pushes the band edges outward from the Bogoliubov values.
BEC_BAND_STRETCH = 1.8
BEC_EDGE_ONSET = 0.55


def spread_gap_dos(omega: np.ndarray, delta: float, mu: float):
    """Complete gap with a U-shaped bottom and a widened band.

    The Bogoliubov weights still sum to one at each momentum. The pole
    sits at Δ + stretch |ξ|^onset, so the interior is empty, the edge
    rises gradually, and the band top and bottom lie further out.
    """
    xi = momentum_mesh() - mu
    bogoliubov = np.sqrt(xi**2 + delta**2)
    upper = 0.5 * (1.0 + xi / bogoliubov)
    lower = 0.5 * (1.0 - xi / bogoliubov)
    energy = delta + BEC_BAND_STRETCH * np.abs(xi) ** BEC_EDGE_ONSET
    return lorentzian(energy, upper, omega, ETA) + lorentzian(-energy, lower, omega, ETA)


def metal_dos(omega: np.ndarray, nu: float):
    eps = momentum_mesh()
    mu = mu_of_nu(eps, nu)
    return lorentzian(eps - mu, np.ones_like(eps), omega, ETA), mu


def bcs_carriers():
    """Band energies and the mean squared in-plane velocity, on the tunneling mesh."""
    grid = np.linspace(-np.pi, np.pi, NK, endpoint=False)
    kx, ky = np.meshgrid(grid, grid, indexing="ij")
    eps = dispersion(kx, ky).ravel()
    vx = 2.0 * T1 * np.sin(kx) + 4.0 * T2 * np.sin(kx) * np.cos(ky)
    vy = 2.0 * T1 * np.sin(ky) + 4.0 * T2 * np.cos(kx) * np.sin(ky)
    v2 = (0.5 * (vx**2 + vy**2)).ravel()
    return eps, v2


def delta_of_temperature(xi: np.ndarray, temperature: float, delta0: float, coupling: float) -> float:
    """Finite-temperature gap equation at fixed mu. Zero above Tc."""
    if temperature <= 0.0:
        return delta0

    def residual(delta: float) -> float:
        energy = np.sqrt(xi**2 + delta**2)
        return coupling * np.mean(np.tanh(energy / (2.0 * temperature)) / (2.0 * energy)) - 1.0

    if residual(1e-4) <= 0.0:
        return 0.0
    lo, hi = 1e-4, delta0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if residual(mid) > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def transition_temperature_fixed_density(eps: np.ndarray, nu: float, coupling: float) -> float:
    """Temperature where the normal metal at fixed density stops pairing.

    The chemical potential is the one that keeps the Fermi-sea occupation
    equal to nu. It is not the zero-temperature value: thermal promotion
    into the denser part of the band pushes it down.
    """
    def residual(temperature: float) -> float:
        mu = solve_mu(eps, 0.0, temperature, nu)
        return _gap_residual(eps - mu, 1e-6, temperature, coupling)

    lo, hi = 0.05, 3.0
    if residual(lo) <= 0.0:
        return lo
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if residual(mid) > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def transition_temperature(xi: np.ndarray, coupling: float) -> float:
    """Temperature where the gap equation at vanishing gap stops having a solution."""
    xi_safe = np.maximum(np.abs(xi), 1e-12)

    def residual(temperature: float) -> float:
        thermal = np.tanh(xi_safe / (2.0 * temperature)) / (2.0 * xi_safe)
        return coupling * float(np.mean(thermal)) - 1.0

    lo, hi = 0.05, 4.0
    if residual(hi) > 0.0:
        hi = 8.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if residual(mid) > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def lognormal_halfwidth(sigma: float, n_sigma: float = ERROR_BAR_SIGMAS) -> float:
    """Relative half-width of an n-sigma interval for a lognormal of width sigma."""
    return float(np.exp(n_sigma * sigma) - 1.0)


def add_nmr_background(rate, rng):
    """A little absolute scatter, drawn apart from the relative lognormal noise.

    Only the nuclear rates use this stream, so the other public curves stay put.
    The error bar is wider than this scatter near the cutoff.
    """
    values = np.asarray(rate, dtype=float)
    return values + rng.normal(0.0, NMR_POINT_SIGMA, size=values.shape)


def nmr_public_uncertainty(rate, sigma: float = 0.10):
    """Relative lognormal width plus an absolute background.

    The background is larger than the public cutoff. Along the half-filled
    tail the signal-to-noise ratio falls, and past the cutoff the error
    would exceed the rate.
    """
    relative = lognormal_halfwidth(sigma)
    return np.sqrt((np.asarray(rate) * relative) ** 2 + NMR_ABSOLUTE_ERROR ** 2)


def hebel_slichter_ratio(delta: float, temperature: float, gamma: float = DYNES_GAMMA) -> float:
    """1/(T1 T) in units of the Korringa constant.

    A vanishing gap returns the Korringa value. A finite gap uses the spin
    coherence factor (Ns^2 + Ms^2): the rate peaks just below the temperature
    where the gap closes, then falls. gamma is a Dynes broadening.
    """
    if delta <= 0.0 or temperature <= 0.0:
        return 1.0
    emax = max(40.0 * temperature, 12.0 * delta)
    energy = np.linspace(1e-6, emax, 6000)
    z = energy + 1j * gamma
    root = np.sqrt(z * z - delta * delta)
    quasiparticle = np.real(z / root)
    anomalous = np.real(delta / root)
    weight = (0.5 / temperature) / np.cosh(energy / (2.0 * temperature)) ** 2
    return float(np.trapezoid(weight * (quasiparticle**2 + anomalous**2), energy))


def quasiparticle_resistivity(xi: np.ndarray, v2: np.ndarray, delta: float, temperature: float) -> float:
    """Constant-τ resistivity of the gapped quasiparticles. The metal is delta = 0."""
    if temperature <= 0.0:
        return 0.0
    if delta <= 0.0:
        thermal = 0.25 / np.cosh(0.5 * np.clip(xi / temperature, -300.0, 300.0)) ** 2
        sigma = float(np.mean(v2 * thermal / temperature))
    else:
        energy = np.sqrt(xi**2 + delta**2)
        thermal = 0.25 / np.cosh(0.5 * np.clip(energy / temperature, -300.0, 300.0)) ** 2
        sigma = float(np.mean(v2 * (xi / energy) ** 2 * thermal / temperature))
    return 1.0 / sigma


def triplon_dos(omega: np.ndarray):
    packed = bands(J, L=96)
    disp = packed["trip"]["disp"].ravel()
    density = lorentzian(disp, np.ones_like(disp), omega, ETA)
    return density, float(disp.min()), float(disp.max()), packed


def write_nmr_public(path: Path, temperatures, rates, errors, keep=None) -> None:
    """Drop points the public figure does not draw.

    ``keep`` is the half-filled mask from the noiseless rate. Scatter must
    not put colder points back on the trace.
    """
    lines = ["temperature rate uncertainty"]
    for i, (t, y, e) in enumerate(zip(temperatures, rates, errors)):
        if keep is not None and not keep[i]:
            continue
        if y <= 0.0:
            continue
        if keep is None and y < NMR_PUBLIC_FLOOR:
            continue
        lines.append(f"{t:.4f} {y:.6e} {e:.6e}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_trace(path: Path, x: np.ndarray, y: np.ndarray, xname: str, yname: str):
    lines = [f"{xname} {yname}"]
    for a, b in zip(x, y):
        lines.append(f"{a:.6f} {b:.6e}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def correlate(rng: np.random.Generator, n: int) -> np.ndarray:
    white = rng.normal(size=n)
    kernel = np.exp(-0.5 * (np.linspace(-2.4, 2.4, 17) / 0.8) ** 2)
    kernel /= kernel.sum()
    smooth = np.convolve(white, kernel, mode="same")
    smooth /= smooth.std()
    return smooth


# Panel (d) has had the thermal kernel removed. That step amplifies the
# high-frequency part, so its noise is larger than the low-temperature traces.
# The draw count stays the same, and the other curves stay put.
HIGH_T_TRACE_NOISE = {"relative": 0.07, "floor": 0.045}


def add_trace_noise(y: np.ndarray, rng: np.random.Generator, relative=0.028, floor=0.012):
    corr = correlate(rng, len(y))
    white = rng.normal(size=len(y))
    scale = max(float(np.max(y)), 1e-8)
    noisy = y * (1.0 + relative * corr) + floor * scale * white
    return np.clip(noisy, 0.0, None)


def peak_sigma(energy: np.ndarray) -> np.ndarray:
    """Sharper near the chemical potential, broader farther away."""
    return PEAK_SIGMA_FLOOR + PEAK_SIGMA_SLOPE * np.abs(energy)


def high_temperature_peaks(seed: int = SEED):
    """Bare dispersion at three densities, then Gaussian peak noise.

    The generator is separate from the trace noise, so this draw does not
    move the tunneling, relaxation, or resistivity realizations. Each peak
    is broadened by peak_sigma of its clean energy. Rounded to 0.01, a
    weighted two-hopping fit still returns t2/t1 about 0.2, and a third
    neighbor is consistent with zero.
    """
    points = ((0, 0), (1 / 4, 0), (1 / 2, 0), (1 / 2, 1 / 4), (1 / 2, 1 / 2), (1 / 4, 1 / 4))
    densities = (("1/2", 0.5), ("0.3", 0.3), ("0.2", 0.2))
    eps = momentum_mesh()
    mus = {label: mu_of_nu(eps, nu) for label, nu in densities}
    clean = np.empty((len(points), len(densities)))
    for j, (label, _) in enumerate(densities):
        for i, (px, py) in enumerate(points):
            clean[i, j] = float(dispersion(2 * np.pi * px, 2 * np.pi * py) - mus[label])
    sigma = peak_sigma(clean)
    rng = np.random.default_rng(seed)
    noisy = clean + rng.normal(0.0, 1.0, size=clean.shape) * sigma
    shown = np.round(noisy, 2)
    quoted = np.round(sigma, 2)
    return points, [label for label, _ in densities], mus, clean, shown, quoted


# At |V| = 9 the added floor is this fraction of the model peak height.
BACKGROUND_AT_9 = 0.11


def quadratic_background(omega: np.ndarray, dos: np.ndarray) -> np.ndarray:
    """V^2 floor from bands farther from the chemical potential.

    The interior of a hard gap is left untouched. Past the gap the floor
    grows as V^2, so the trace keeps rising after the model band ends.
    """
    peak = float(np.max(dos))
    thr = 0.05 * peak
    suppress = np.ones(len(omega))
    center = int(np.argmin(np.abs(omega)))
    if dos[center] < thr:
        low = dos < thr
        i0 = center
        while i0 > 0 and low[i0 - 1]:
            i0 -= 1
        i1 = center
        while i1 < len(dos) - 1 and low[i1 + 1]:
            i1 += 1
        suppress[i0 : i1 + 1] = 0.0
        ramp = max(1, int(round(0.40 / float(omega[1] - omega[0]))))
        for k in range(ramp):
            w = (k + 1) / (ramp + 1)
            s = w * w * (3.0 - 2.0 * w)
            left = i0 - 1 - k
            right = i1 + 1 + k
            if left >= 0:
                suppress[left] = s
            if right < len(suppress):
                suppress[right] = s
    quad = omega**2 * suppress
    ref = 0.5 * (float(np.interp(-9.0, omega, quad)) + float(np.interp(9.0, omega, quad)))
    return quad * (BACKGROUND_AT_9 * peak / ref)


def landmarks(x: np.ndarray, y: np.ndarray, thr=0.08):
    hits = []
    for i in range(1, len(y) - 1):
        if y[i] >= y[i - 1] and y[i] > y[i + 1] and y[i] > thr * y.max():
            hits.append((float(x[i]), float(y[i])))
    mask = y > 0.05 * y.max()
    spans = []
    start = None
    for i, on in enumerate(mask):
        if on and start is None:
            start = i
        if start is not None and (not on or i == len(mask) - 1):
            stop = i - 1 if not on else i
            spans.append((float(x[start]), float(x[stop])))
            start = None
    return hits, spans


def _axis_position(value: float) -> float:
    """Linear on [0, 1], log10 above 1, continuous at 1."""
    if value <= 0.0:
        return 0.0
    if value < 1.0:
        return float(value)
    return 1.0 + float(np.log10(value))


def write_resistivity_axis(source: Path, dest: Path):
    """Plot positions for the piecewise resistivity axis, with asymmetric errors."""
    rows = ["temperature position plus minus"]
    for line in source.read_text().splitlines()[1:]:
        if not line.strip():
            continue
        temperature, value, err = (float(part) for part in line.split())
        position = _axis_position(value)
        plus = _axis_position(value + err) - position
        minus = position - _axis_position(max(value - err, 0.0))
        rows.append(f"{temperature:.4f} {position:.6e} {plus:.6e} {minus:.6e}")
    dest.write_text("\n".join(rows) + "\n", encoding="utf-8")


def _num(value: float) -> str:
    if value == 0.0:
        return "0"
    magnitude = abs(value)
    if 1e-4 <= magnitude < 1e6:
        return f"{value:.6g}"
    return f"{value:.6e}"


def _array(values, indent: int, per_line: int) -> str:
    pad = " " * indent
    rows = []
    for start in range(0, len(values), per_line):
        rows.append(pad + ", ".join(_num(v) for v in values[start : start + per_line]))
    return "[\n" + ",\n".join(rows) + "\n" + (" " * (indent - 2)) + "]"


def _rows(path: Path):
    return [line.split() for line in path.read_text().splitlines()[1:] if line.strip()]


def write_measurements(path: Path):
    """Solver-facing curves. Noiseless columns stay out of this file."""
    parts = ["{", '  "measurements": [']

    stm_meta = [
        ("a", "stm_100_low.dat", "1/2", "low", "midpoint of the interval where the conductance vanishes"),
        ("b", "stm_nu03_low.dat", "≈0.3", "low", "midpoint of the interval where the conductance vanishes"),
        ("c", "stm_nu02_low.dat", "≈0.2", "low", "midpoint of the interval where the conductance vanishes"),
        ("d", "stm_nu03_high.dat", "≈0.3", "high", "chemical potential"),
    ]
    parts.append("    {")
    parts.append('      "experiment": "STS",')
    parts.append('      "quantity": "differential conductance dI/dV",')
    parts.append('      "current": "I is the tunneling current",')
    parts.append('      "bias_unit": "D",')
    parts.append('      "vertical_scale": "each trace divided by its own maximum",')
    parts.append('      "spectra": [')
    for p_i, (label, fname, filling, temperature, origin) in enumerate(stm_meta):
        rows = _rows(DATA / fname)
        bias = [float(a) for a, _ in rows]
        didv = [float(b) for _, b in rows]
        comma = "," if p_i < len(stm_meta) - 1 else ""
        parts.append("        {")
        parts.append(f'          "panel": {json.dumps(label)},')
        parts.append(f'          "filling": {json.dumps(filling, ensure_ascii=False)},')
        parts.append(f'          "temperature": {json.dumps(temperature)},')
        parts.append(f'          "bias_origin": {json.dumps(origin)},')
        if label == "d":
            parts.append('          "broadening": "the thermal broadening has been deconvolved",')
        parts.append('          "bias": ' + _array(bias, 12, 8) + ",")
        parts.append('          "dI_dV": ' + _array(didv, 12, 6))
        parts.append("        }" + comma)
    parts.append("      ]")
    parts.append("    },")

    def relaxation_sample(filling: str, fname: str, indent: str):
        rows = []
        for temperature, rate, err in _rows(DATA / fname):
            temp = float(temperature)
            rows.append((temp, float(rate) * temp, float(err) * temp))
        rows.sort(key=lambda item: item[0])
        return "\n".join([
            indent + "{",
            indent + f'  "filling": {json.dumps(filling, ensure_ascii=False)},',
            indent + '  "temperature": ' + _array([a[0] for a in rows], len(indent) + 4, 8) + ",",
            indent + '  "one_over_T1": ' + _array([a[1] for a in rows], len(indent) + 4, 6) + ",",
            indent + '  "uncertainty": ' + _array([a[2] for a in rows], len(indent) + 4, 6),
            indent + "}",
        ])

    parts.append("    {")
    parts.append('      "experiment": "NMR",')
    parts.append('      "nucleus": "transition metal",')
    parts.append('      "quantity": "1/T1",')
    parts.append('      "definition": "1/T1 at each listed temperature. The number is not divided by T.",')
    parts.append('      "temperature_unit": "D",')
    parts.append('      "rate_unit": "1/D",')
    parts.append('      "temperature_order": "increasing",')
    parts.append('      "samples": [')
    nmr_files = (("1/2", "relaxation.dat"), ("≈0.3", "relaxation_nu03.dat"), ("≈0.2", "relaxation_nu02.dat"))
    for i, (filling, fname) in enumerate(nmr_files):
        comma = "," if i < len(nmr_files) - 1 else ""
        parts.append(relaxation_sample(filling, fname, "        ") + comma)
    parts.append("      ]")
    parts.append("    },")

    def resistivity_sample(filling: str, fname: str, indent: str):
        rows = [(float(t), float(y), float(e)) for t, y, e in _rows(DATA / fname)]
        rows.sort(key=lambda item: item[0])
        return "\n".join([
            indent + "{",
            indent + f'  "filling": {json.dumps(filling, ensure_ascii=False)},',
            indent + '  "temperature": ' + _array([a[0] for a in rows], len(indent) + 4, 8) + ",",
            indent + '  "resistivity": ' + _array([a[1] for a in rows], len(indent) + 4, 6) + ",",
            indent + '  "uncertainty": ' + _array([a[2] for a in rows], len(indent) + 4, 6),
            indent + "}",
        ])

    parts.append("    {")
    parts.append('      "experiment": "resistivity",')
    parts.append('      "quantity": "in-plane resistivity",')
    parts.append('      "temperature_unit": "D",')
    parts.append('      "temperature_order": "increasing",')
    parts.append('      "scale": "equals 1 at T = 4D",')
    parts.append('      "samples": [')
    rho_files = (("1/2", "resistivity.dat"), ("≈0.3", "resistivity_nu03.dat"), ("≈0.2", "resistivity_nu02.dat"))
    for i, (filling, fname) in enumerate(rho_files):
        comma = "," if i < len(rho_files) - 1 else ""
        parts.append(resistivity_sample(filling, fname, "        ") + comma)
    parts.append("      ]")
    parts.append("    }")
    parts.append("  ]")
    parts.append("}")
    text = "\n".join(parts) + "\n"
    json.loads(text)
    path.write_text(text, encoding="utf-8")


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    AUTHOR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    omega = np.linspace(-10.0, 10.0, 801)
    summary = {"J": J, "t2": T2, "eta": ETA, "seed": SEED}

    half = half_filled(omega)
    eps = momentum_mesh()
    coupling = 0.75 * J
    # Normal-state chemical potentials. Panel (d) and the metal above Tc
    # use these, so their Fermi-sea area is the nominal filling.
    mu_normal = {0.2: mu_of_nu(eps, 0.2), 0.3: mu_of_nu(eps, 0.3)}
    # Paired state at fixed density. The T=0 gap equation and the number
    # equation are solved together, so the occupied weight is the filling.
    gap_02, mu_02 = bcs_equilibrium(eps, 0.2, 0.0, coupling)
    gap_03_eq, mu_03_eq = bcs_equilibrium(eps, 0.3, 0.0, coupling)
    # Complete gap, between the half-filled edge and the BCS gap, closer to
    # the BCS gap. The onset is gradual and the band is wider than the
    # Bogoliubov coherence peaks. Its chemical potential keeps the occupied
    # weight at nu = 0.3; that is not the normal-state chemical potential.
    gap_03_edge = gap_02 + BEC_FILLING_WEIGHT * (HALF_GAP_EDGE - gap_02)
    mu_03 = solve_mu(eps, gap_03_edge, 0.0, 0.3)
    low_03 = spread_gap_dos(omega, gap_03_edge, mu_03)
    low_02 = bcs_dos(omega, 0.2, gap_02, mu_02)
    high_03, _ = metal_dos(omega, 0.3)
    summary["bcs"] = {
        "nu_0.3": {
            "nu": 0.3,
            "Delta_gap_equation": gap_03_eq,
            "mu_gap_equation": mu_03_eq,
            "occupied_gap_equation": bcs_occupation(eps, mu_03_eq, gap_03_eq, 0.0),
            "Delta": gap_03_edge,
            "mu": mu_03,
            "mu_normal": mu_normal[0.3],
            "occupied": bcs_occupation(eps, mu_03, gap_03_edge, 0.0),
            "interpolation_weight_toward_half_filling": BEC_FILLING_WEIGHT,
        },
        "nu_0.2": {
            "nu": 0.2,
            "Delta": gap_02,
            "mu": mu_02,
            "mu_normal": mu_normal[0.2],
            "occupied": bcs_occupation(eps, mu_02, gap_02, 0.0),
        },
    }

    mag_omega = np.linspace(0.0, 12.0, 601)
    mag, mag_lo, mag_hi, packed = triplon_dos(mag_omega)
    summary["triplon_edges"] = [mag_lo, mag_hi]
    summary["strong_coupling_gaps"] = packed["gaps"]

    temps = np.linspace(0.45, 4.0, 48)
    sig_qp, sig_pair, _, _ = resistivity(packed, temps)
    boltzmann = 1.0 / (sig_qp + sig_pair)
    boltzmann /= np.interp(4.0, temps, boltzmann)
    # Freeze the low-T slope. Above about 2D the full integral is no longer
    # activated, while 1/(T1 T) on this crystal still is. Publishing the
    # flattened curve would say the charge gap has filled.
    cold = temps <= 0.8
    activation = float(np.polyfit(1.0 / temps[cold], np.log(boltzmann[cold]), 1)[0])
    rho = np.exp(activation * (1.0 / temps - 1.0 / 4.0))

    model = {
        "stm_100_low": (omega, half),
        "stm_nu03_low": (omega, low_03),
        "stm_nu02_low": (omega, low_02),
        "stm_nu03_high": (omega, high_03),
    }
    curves = {}
    summary["stm_background"] = {
        "form": "V^2 outside a hard gap, zero inside the gap",
        "fraction_of_model_peak_at_absV_9": BACKGROUND_AT_9,
    }
    summary["landmarks_clean"] = {}
    for name, (x, y0) in model.items():
        y = y0 + quadratic_background(x, y0)
        curves[name] = (x, y)
        write_trace(AUTHOR / f"{name}_clean.dat", x, y, "x", "y")
        peaks, spans = landmarks(x, y)
        center = int(np.argmin(np.abs(x)))
        summary["landmarks_clean"][name] = {
            "peaks": peaks[:6],
            "spans": spans,
            "gap_center_over_peak": float(y[center] / y.max()),
        }

    public = {}
    for name, (x, y) in curves.items():
        shown = y / y.max()
        noise = HIGH_T_TRACE_NOISE if name == "stm_nu03_high" else {}
        public[name] = add_trace_noise(shown, rng, **noise)
        write_trace(DATA / f"{name}.dat", x, public[name], "x", "y")

    # The old public file noised a 601-point magnetic trace here. Consume the
    # same draw so the resistivity realization stays put.
    add_trace_noise(np.ones(len(mag_omega)), rng)

    log_sigma = 0.07
    factor = rng.lognormal(0.0, log_sigma, size=len(temps))
    rho_public = rho * factor
    # Noise first, then divide by the noisy value at T = 4D.
    rho_anchor = float(rho_public[np.argmin(np.abs(temps - 4.0))])
    rho_public = rho_public / rho_anchor
    rho_err = rho_public * lognormal_halfwidth(log_sigma)
    lines = ["temperature resistivity uncertainty"]
    for t, y, e in zip(temps, rho_public, rho_err):
        lines.append(f"{t:.4f} {y:.6e} {e:.6e}")
    (DATA / "resistivity.dat").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_trace(AUTHOR / "resistivity_clean.dat", temps, rho, "temperature", "resistivity")
    write_trace(AUTHOR / "resistivity_boltzmann.dat", temps, boltzmann, "temperature", "resistivity")
    summary["resistivity_at_T"] = {f"{t:.2f}": float(v) for t, v in zip(temps[::4], rho[::4])}
    summary["resistivity_activation"] = {
        "published": "low-T Boltzmann slope, held fixed through the window",
        "fit_temperatures": "T <= 0.8",
        "activation_energy": activation,
    }

    # D/T from 0.1 to 5. The rate is the intraband integral over the triplon
    # spectrum; nothing is added by hand at high T.
    inv_t = np.linspace(0.1, 5.0, 40)
    t_nmr = 1.0 / inv_t
    rate = nmr_rate(packed, t_nmr)
    scaled = rate / t_nmr
    scaled = scaled / float(np.interp(4.0, t_nmr[::-1], scaled[::-1]))
    activated = inv_t >= 1.0
    slope_act = float(-np.polyfit(inv_t[activated], np.log(scaled[activated]), 1)[0])
    hot = inv_t <= 0.4
    slope_hot = float(-np.polyfit(inv_t[hot], np.log(scaled[hot]), 1)[0])
    summary["nmr"] = {
        "formula": "int rho(w)^2 n_B(w)(1+n_B(w)) dw",
        "plotted": "1/(T1 T) divided by its value at T=4",
        "inverse_temperature_window": [0.1, 5.0],
        "public_half_filled_T_max": NMR_HALF_T_MAX,
        "normalized_at": 4.0,
        "arrhenius_slope_D_over_T_1_to_5": slope_act,
        "arrhenius_slope_D_over_T_below_0.4": slope_hot,
        "triplon_edge": mag_lo,
    }
    log_sigma_nmr = 0.10
    # Separate stream: the relative draws above stay on `rng`.
    nmr_background = np.random.default_rng(SEED + 1)
    rate_public = scaled * rng.lognormal(0.0, log_sigma_nmr, size=len(t_nmr))
    rate_public = add_nmr_background(rate_public, nmr_background)
    # One anchor at exactly T = 4D. Its draw is after the grid, so the other
    # points keep their noise. Dividing by this noisy value makes it 1.
    anchor_clean = float(np.interp(4.0, t_nmr[::-1], scaled[::-1]))
    anchor_noisy = anchor_clean * float(rng.lognormal(0.0, log_sigma_nmr))
    anchor_noisy += float(nmr_background.normal(0.0, NMR_POINT_SIGMA))
    t_pub = np.append(t_nmr, 4.0)
    rate_public = np.append(rate_public, anchor_noisy) / anchor_noisy
    scaled_pub = np.append(scaled, anchor_clean)
    rate_err = nmr_public_uncertainty(rate_public, log_sigma_nmr)
    # Cold end: noiseless rate crosses 1e-5 near D/T = 2.2.
    # Hot end: T = 10D is above the spin gap, so that point is not published.
    keep_pub = np.append(
        (scaled >= NMR_PUBLIC_FLOOR) & (t_nmr <= NMR_HALF_T_MAX),
        True,
    )
    write_nmr_public(
        DATA / "relaxation.dat",
        t_pub,
        rate_public,
        rate_err,
        keep=keep_pub,
    )
    write_trace(AUTHOR / "relaxation_clean.dat", t_nmr, scaled, "temperature", "rate")
    print(
        "nmr 1/(T1T) slope D/T>1",
        round(slope_act, 3),
        "D/T<0.4",
        round(slope_hot, 3),
        "edge",
        round(mag_lo, 3),
    )

    # nu = 0.2 is the dilute BCS side. nu = 0.3 is the dense BEC side:
    # a complete gap between the two fillings, and a resistivity between
    # the metallic curve and the half-filled activation. Its transition
    # temperature stays suppressed.
    eps_k, v2 = bcs_carriers()
    temps_doped = np.linspace(0.10, 4.0, 53)
    # Normal metal at the nominal filling. Above Tc the gap is gone and the
    # chemical potential is the normal-state one, not the paired one.
    xi_metal = eps_k - mu_normal[0.2]
    rho_metal = np.array([
        quasiparticle_resistivity(xi_metal, v2, 0.0, float(t)) for t in temps_doped
    ])
    rho_metal = rho_metal / float(rho_metal[np.argmin(np.abs(temps_doped - 4.0))])
    summary["doped_pairs"] = {}
    for nu, tag in ((0.3, "nu03"), (0.2, "nu02")):
        if nu == 0.2:
            delta0, mu = gap_02, mu_02
            # The gap equation closes near 1.00D. That temperature exceeds the
            # bilayer stiffness bound, so the curves use a lower transition.
            tc_gap = transition_temperature_fixed_density(eps_k, nu, coupling)
            # Diamagnetic KT bound of the paired bilayer is 0.41D. Stay under it.
            tc = 0.40
            t_peak = float(t_pub[np.argmin(np.abs(t_pub - 0.85 * tc))])
            peak_height = 1.8
            activation_nmr = 1.75
            scaled_d = np.ones_like(t_pub, dtype=float)
            below = t_pub <= t_peak
            scaled_d[below] = peak_height * np.exp(
                -activation_nmr * (1.0 / t_pub[below] - 1.0 / t_peak)
            )
            # The metal is the same normal-state curve. Only the zero interval moves.
            rho_d = rho_metal.copy()
            rho_d[temps_doped < tc - 1e-8] = 0.0
            nmr_note = (
                f"activated with 1.75 below a Hebel–Slichter peak at {t_peak:.3f}D, "
                "Korringa above the peak; the gap equation closes near "
                f"{tc_gap:.2f}D and is not the published transition"
            )
            rho_note = "zero below 0.40D, normal-state metal at and above it"
        else:
            delta0, mu = gap_03_edge, mu_03
            tc = 0.20
            # One activation on the tunneling gap, continuous through Tc.
            scaled_d = np.exp(-gap_03_edge * (1.0 / t_pub - 0.25))
            # Log-interpolation at the first point above Tc, then a single
            # activation so the curve cannot dip on the way to T = 4.
            cold = int(np.argmax(temps_doped >= tc))
            rho_half_cold = float(np.exp(activation * (1.0 / temps_doped[cold] - 0.25)))
            log_cold = (
                (1.0 - BEC_FILLING_WEIGHT) * np.log(rho_metal[cold])
                + BEC_FILLING_WEIGHT * np.log(rho_half_cold)
            )
            ea_bec = float(log_cold / (1.0 / temps_doped[cold] - 0.25))
            rho_d = np.exp(ea_bec * (1.0 / temps_doped - 0.25))
            rho_d[temps_doped < tc] = 0.0
            nmr_note = (
                "single activation on the tunneling gap through Tc, no coherence peak"
            )
            rho_note = (
                "zero below 0.20D; above it, one third of the way in the logarithm "
                "from the nu=0.2 metal to the half-filled activation"
            )
        noisy = scaled_d * rng.lognormal(0.0, log_sigma_nmr, size=len(t_pub))
        noisy = add_nmr_background(noisy, nmr_background)
        anchor = float(noisy[np.argmin(np.abs(t_pub - 4.0))])
        noisy = noisy / anchor
        err = nmr_public_uncertainty(noisy, log_sigma_nmr)
        write_nmr_public(DATA / f"relaxation_{tag}.dat", t_pub, noisy, err)
        write_trace(AUTHOR / f"relaxation_{tag}_clean.dat", t_pub, scaled_d, "temperature", "rate")

        positive = rho_d > 0.0
        factor = np.ones_like(rho_d)
        side = np.random.default_rng(SEED + 17)
        if nu == 0.2:
            # Keep the draws already used on the metal above 0.55D. Points that
            # become metallic only because Tc moved to 0.40D use a side stream.
            legacy = temps_doped >= tc_gap
            old_fresh = (temps_doped > 0.55 + 1e-8) & ~legacy
            new_fresh = positive & ~legacy & ~old_fresh
            factor[legacy] = rng.lognormal(0.0, log_sigma, size=int(np.count_nonzero(legacy)))
            factor[old_fresh] = rng.lognormal(0.0, log_sigma, size=int(np.count_nonzero(old_fresh)))
            if np.any(new_fresh):
                factor[new_fresh] = side.lognormal(0.0, log_sigma, size=int(np.count_nonzero(new_fresh)))
        else:
            old_pos = temps_doped >= 0.36 - 1e-8
            new_pos = positive & ~old_pos
            factor[old_pos] = rng.lognormal(0.0, log_sigma, size=int(np.count_nonzero(old_pos)))
            if np.any(new_pos):
                factor[new_pos] = side.lognormal(0.0, log_sigma, size=int(np.count_nonzero(new_pos)))
        rho_pub = rho_d * factor
        anchor = float(rho_pub[np.argmin(np.abs(temps_doped - 4.0))])
        rho_pub = rho_pub / anchor
        rho_e = np.zeros_like(rho_pub)
        rho_e[positive] = rho_pub[positive] * lognormal_halfwidth(log_sigma)
        lines = ["temperature resistivity uncertainty"]
        for t, y, e in zip(temps_doped, rho_pub, rho_e):
            lines.append(f"{t:.4f} {y:.6e} {e:.6e}")
        (DATA / f"resistivity_{tag}.dat").write_text("\n".join(lines) + "\n", encoding="utf-8")
        write_trace(AUTHOR / f"resistivity_{tag}_clean.dat", temps_doped, rho_d, "temperature", "resistivity")
        finite = rho_d[positive]
        entry = {
            "nu": nu,
            "mu": mu,
            "gap": gap_03_edge if nu == 0.3 else delta0,
            "Tc": tc,
            "nmr": nmr_note,
            "resistivity": rho_note,
        }
        if nu == 0.2:
            entry["gap_equation_Tc"] = tc_gap
        summary["doped_pairs"][tag] = entry
        slope = np.diff(finite)
        print(
            f"nu={nu}: gap={delta0:.3f} Tc={tc:.3f} "
            f"rho_just_above_Tc={finite[0]:.3f} rho_at_4={finite[-1]:.3f} "
            f"monotonic={bool(np.all(slope > 0) or np.all(slope < 0))}"
        )

    points, labels, mus, clean, shown, quoted = high_temperature_peaks()
    lines = ["kx ky filling clean shown uncertainty"]
    for i, (px, py) in enumerate(points):
        for j, label in enumerate(labels):
            lines.append(
                f"{px:.2f} {py:.2f} {label} {clean[i, j]:.6f} {shown[i, j]:.2f} {quoted[i, j]:.2f}"
            )
    (AUTHOR / "photoemission_highT.dat").write_text("\n".join(lines) + "\n", encoding="utf-8")
    summary["high_temperature_peaks"] = {
        "sigma_floor": PEAK_SIGMA_FLOOR,
        "sigma_slope_per_abs_energy": PEAK_SIGMA_SLOPE,
        "seed": SEED,
        "mu": mus,
        "shown": {label: shown[:, j].tolist() for j, label in enumerate(labels)},
        "uncertainty": {label: quoted[:, j].tolist() for j, label in enumerate(labels)},
    }

    AUTHOR.mkdir(parents=True, exist_ok=True)
    (AUTHOR / "public_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_measurements(ROOT / "measurements.json")
    for stem in ("resistivity", "resistivity_nu03", "resistivity_nu02"):
        write_resistivity_axis(DATA / f"{stem}.dat", DATA / f"{stem}_axis.dat")
    print(json.dumps(summary["bcs"], indent=2))
    print("triplon", summary["triplon_edges"])
    print("gaps", {k: summary["strong_coupling_gaps"][k] for k in ("spin", "single", "pair")})
    for name, info in summary["landmarks_clean"].items():
        tops = ", ".join(f"{a:.2f}({b:.3f})" for a, b in info["peaks"][:4])
        print(f"{name}: peaks {tops}")
        print(f"   spans {info['spans']}")


if __name__ == "__main__":
    main()
