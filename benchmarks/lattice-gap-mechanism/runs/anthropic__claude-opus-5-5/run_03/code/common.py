"""Shared utilities for the analysis of the layered-oxide measurement data.

Model (bilayer square lattice, one orbital per transition-metal site, layers l = 1, 2):
    H = sum_{k,l,s} eps_k c+_{kls} c_{kls} + J_perp sum_i S_{i1}.S_{i2}
    eps_k = -2 t (cos kx + cos ky) - 4 t' cos kx cos ky      (k in radians; data momenta are in 2pi/a)
Energies in units of D.
"""
import json, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'measurements.json')
FIG = os.path.join(ROOT, 'figures')
RES = os.path.join(ROOT, 'results')
os.makedirs(FIG, exist_ok=True)
os.makedirs(RES, exist_ok=True)

# ---- final coefficient values (see REPORT.md for derivation and uncertainties) ----
T_NN = 1.00        # nearest-neighbour in-plane hopping t
T_NNN = 0.195      # next-nearest-neighbour hopping t'  (eps_k = -2t(cx+cy) - 4t' cx cy)
J_PERP = 8.0       # interlayer (rung) Heisenberg exchange
U_HUB = 0.0        # on-site Hubbard U (consistent with zero)
PHI = 0.75 * J_PERP + 0.5 * U_HUB   # leading-order rung charge-excitation energy (=6)
V_PAIR = 0.75 * J_PERP              # HFB interlayer singlet pairing coupling (=6)


def load():
    d = json.load(open(DATA))
    m = {x['experiment']: x for x in d['measurements']}
    sts = {s['panel']: (np.array(s['bias']), np.array(s['dI_dV'])) for s in m['STS']['spectra']}
    nmr = {s['filling']: (np.array(s['temperature']), np.array(s['one_over_T1']), np.array(s['uncertainty']))
           for s in m['NMR']['samples']}
    rho = {s['filling']: (np.array(s['temperature']), np.array(s['resistivity']), np.array(s['uncertainty']))
           for s in m['resistivity']['samples']}
    return sts, nmr, rho


def kgrid(N):
    k = 2 * np.pi * (np.arange(N) + 0.5) / N
    KX, KY = np.meshgrid(k, k, indexing='ij')
    return np.cos(KX).ravel(), np.cos(KY).ravel()


def eps_c(cx, cy, t=T_NN, tp=T_NNN):
    return -2 * t * (cx + cy) - 4 * tp * cx * cy


def eps_k(kx, ky, t=T_NN, tp=T_NNN):
    """kx, ky in units of 2pi/a"""
    return eps_c(np.cos(2 * np.pi * kx), np.cos(2 * np.pi * ky), t, tp)


def band_center(t=T_NN, tp=T_NNN):
    # band bottom -4t-4t' (Gamma), top 4t-4t' (M)  (valid for |t'| < t/2)
    return -4 * tp


def mu_normal(nu, t=T_NN, tp=T_NNN, N=1200):
    cx, cy = kgrid(N)
    return np.quantile(eps_c(cx, cy, t, tp), nu)


def cic(E, W, V, Nk):
    """cloud-in-cell binning of weights W at energies E onto uniform grid V.
    Returns spectral density per k-point (divide by the number Nk of k-points)."""
    dV = V[1] - V[0]
    x = (E - V[0]) / dV
    i0 = np.floor(x).astype(int)
    f = x - i0
    h = np.zeros(len(V) + 2)
    m = (i0 >= -1) & (i0 < len(V))
    np.add.at(h, i0[m] + 1, W[m] * (1 - f[m]))
    np.add.at(h, i0[m] + 2, W[m] * f[m])
    return h[1:-1] / dV / Nk


def gauss_conv(h, dV, sig):
    if sig <= 0:
        return h
    n = int(6 * sig / dV) + 1
    x = np.arange(-n, n + 1) * dV
    g = np.exp(-x ** 2 / (2 * sig ** 2))
    g /= g.sum()
    return np.convolve(h, g, mode='same')


def fermi(x, T):
    return 0.5 * (1 - np.tanh(x / (2 * T)))


# ---- spectral functions used throughout ----
def smg_poles(e, Phi=PHI, alpha=0.0, ec=None):
    """leading-order strong-coupling (rung-singlet / SMG) spectrum at nu = 1/2, energies from mid-gap.
    returns energies (E+, E-) and weights (Z+, Z-)"""
    if ec is None:
        ec = band_center()
    x = e - ec
    return (Phi + x / 2, -Phi + x / 2), (0.5 * (1 + alpha * x), 0.5 * (1 - alpha * x))


def bcs_poles(xi, Delta):
    E = np.sqrt(xi ** 2 + Delta ** 2)
    return (E, -E), (0.5 * (1 + xi / E), 0.5 * (1 - xi / E))


def twogap_delta(xi, cx, cy, DF0, DF1, Dp, Dm, w):
    """phenomenological strong-coupling gap at nu ~ 0.3: Delta_F(k) at k_F (anisotropic),
    crossing over to Delta_inf (+: empty side, -: occupied side) away from k_F"""
    DF = DF0 + DF1 * (cx - cy) ** 2 / 4.0
    Dinf = np.where(xi >= 0, Dp, Dm)
    return np.sqrt(DF ** 2 + np.clip(Dinf ** 2 - DF ** 2, 0, None) * xi ** 2 / (xi ** 2 + w ** 2))


def save_json(obj, name):
    def conv(o):
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    with open(os.path.join(RES, name), 'w') as f:
        json.dump(obj, f, indent=2, default=conv)
