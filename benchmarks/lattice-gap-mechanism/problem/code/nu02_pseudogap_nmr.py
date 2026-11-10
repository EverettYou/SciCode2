"""Replacement 1/(T1 T) curve for the nu = 0.2 crystal (numpy only).

The published transition at nu = 0.2 is 0.40D, but the pairing amplitude of the
J = 8 inter-layer singlet gap equation at fixed density closes at T_MF = 1.00D.
Between 0.40D and 1.00D the amplitude is present and the phase is not ordered,
so the single-particle spectrum is gapped and the nuclear relaxation is
suppressed. A Hebel-Slichter peak needs a coherent BCS density of states
developing at the transition, which a phase-limited two-dimensional
superconductor does not have. This script therefore replaces the
"Korringa above a Hebel-Slichter peak" curve by the ratio

    s(T) = R_gapped(T) / R_normal(T),   R = int N(w)^2 (-df/dw) dw

with N(w) the Bogoliubov density of states of the t1-t2 band at the
fixed-density gap Delta(T), mu(T), Gaussian-broadened by SIGMA, without the
coherence-factor term. s(T) = 1 for T >= T_MF (Korringa), falls smoothly through
Tc = 0.40D with no feature there, and goes as exp(-Delta/T) at low T.

Output: relaxation_nu02_pseudogap_clean.dat with columns
    temperature  rate            (rate = 1/(T1 T) normalized to 1 at T = 4D)
on the temperature grid of author/relaxation_nu02_clean.dat if that file is
given as argv[1]; otherwise on a default grid.
"""
import sys
import numpy as np

T1, T2, J, NU = 1.0, 0.2, 8.0, 0.2
V = 0.75 * J          # inter-layer singlet channel of J S1.S2
NK = 400
SIGMA = 0.05          # Gaussian broadening of the quasiparticle DOS (no in-gap tails)
TC_PUBLISHED = 0.40

k = np.linspace(-np.pi, np.pi, NK, endpoint=False)
kx, ky = np.meshgrid(k, k)
EPS = (-2 * T1 * (np.cos(kx) + np.cos(ky)) - 4 * T2 * np.cos(kx) * np.cos(ky)).ravel()


def bisect(f, a, b, tol=1e-9, it=200):
    fa = f(a)
    for _ in range(it):
        m = 0.5 * (a + b)
        fm = f(m)
        if fa * fm <= 0:
            b = m
        else:
            a, fa = m, fm
        if b - a < tol:
            break
    return 0.5 * (a + b)


def number_eq(mu, delta, T):
    E = np.sqrt((EPS - mu) ** 2 + delta ** 2)
    return np.mean(1.0 - (EPS - mu) / E * np.tanh(E / (2 * T))) / 2 - NU


def gap_eq(delta, T):
    mu = bisect(lambda m: number_eq(m, delta, T), -8.0, 6.0)
    E = np.sqrt((EPS - mu) ** 2 + delta ** 2)
    return V * np.mean(np.tanh(E / (2 * T)) / (2 * E)) - 1.0, mu


def solve(T):
    g0, _ = gap_eq(1e-4, T)
    if g0 < 0:
        return 0.0, bisect(lambda m: number_eq(m, 0.0, T), -8.0, 6.0)
    d = bisect(lambda x: gap_eq(x, T)[0], 1e-4, 5.0)
    return d, gap_eq(d, T)[1]


W = np.linspace(-9, 9, 18001)
DW = W[1] - W[0]


def dos(delta, mu):
    xi = EPS - mu
    E = np.sqrt(xi ** 2 + delta ** 2)
    u2 = 0.5 * (1 + xi / E)
    edges = np.append(W - DW / 2, W[-1] + DW / 2)
    h = np.histogram(E, bins=edges, weights=u2)[0] + np.histogram(-E, bins=edges, weights=1 - u2)[0]
    h = h / EPS.size / DW
    # Gaussian broadening by convolution
    n = int(5 * SIGMA / DW)
    g = np.exp(-0.5 * (np.arange(-n, n + 1) * DW / SIGMA) ** 2)
    g /= g.sum()
    return np.convolve(h, g, mode="same")


def rate(T, delta, mu):
    N = dos(delta, mu)
    df = 1.0 / (4 * T * np.cosh(W / (2 * T)) ** 2)
    return float(np.sum(N ** 2 * df) * DW)


if len(sys.argv) > 1:
    grid = np.loadtxt(sys.argv[1], skiprows=1)[:, 0]
else:
    grid = np.concatenate([np.linspace(0.2, 1.0, 17), np.linspace(1.1, 4.0, 15), [4.4318, 10.0]])
grid = np.sort(np.unique(grid))

tmf = bisect(lambda T: solve(T)[0] - 1e-3, 0.3, 2.0)
rows = []
for T in grid:
    d, mu = solve(T)
    mu_n = bisect(lambda m: number_eq(m, 0.0, T), -8.0, 6.0)
    s = rate(T, d, mu) / rate(T, 0.0, mu_n)
    rows.append((T, d, s))
rows = np.array(rows)
s4 = rows[np.argmin(abs(rows[:, 0] - 4.0)), 2]
rows[:, 2] /= s4
np.savetxt("relaxation_nu02_pseudogap_clean.dat", rows[:, [0, 2]], header="temperature rate", comments="", fmt="%.6f %.6e")
print(f"T_MF (fixed density, J={J}) = {tmf:.3f};  Delta(0) = {solve(0.02)[0]:.3f};  published Tc = {TC_PUBLISHED}")
print(" T      Delta(T)   1/(T1T) (norm. at 4D)")
for T, d, s in rows:
    print(f"{T:6.3f}  {d:7.3f}   {s:9.4e}")
