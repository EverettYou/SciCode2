"""
Effective theory used in the report (all energies in units of D).
Lattice: square, one orbital per transition-metal site, spin-1/2 electrons.
  eps_k = -2t(cos kx + cos ky) - 4t' cos kx cos ky        (bare band)
  t = 0.99, t' = 0.195, U = 12.02 (Mott splitting), g = 6.1 (s-wave pairing coupling)
Regimes:
  nu = 1/2 : paramagnetic Mott insulator, strong-coupling (first order in t/U) spectral function
             A(k,w) = (1/2)(1 - eps_k/U) d(w - E_-) + (1/2)(1 + eps_k/U) d(w - E_+),  E_± = ±U/2 + eps_k/2 + c0
  nu ~ 0.2 : BCS s-wave superconductor on the bare band (gap from the cutoff-free gap equation, coupling g)
  nu ~ 0.3 : pseudogap / superconducting state: mirror (Bogoliubov-type) bands on a Mott-compressed
             dispersion with low-energy spectral weight removed from the interior of the Fermi sea
             (parameters fitted to the STS, see report)
"""
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.optimize import brentq

T_HOP, TP_HOP, U_HUB, G_PAIR = 0.99, 0.195, 12.02, 6.1
NK = 400
_k = (np.arange(NK) + 0.5) / NK * 2 * np.pi - np.pi
KX, KY = np.meshgrid(_k, _k, indexing='ij')
CX, CY = np.cos(KX), np.cos(KY)

def band(t=T_HOP, tp=TP_HOP, kx=None, ky=None):
    if kx is None:
        cx, cy = CX, CY
    else:
        cx, cy = np.cos(kx), np.cos(ky)
    return -2 * t * (cx + cy) - 4 * tp * cx * cy

EPS = band()
GRID = np.linspace(-16, 16, 6401); DG = GRID[1] - GRID[0]
EDGES = np.append(GRID - DG / 2, GRID[-1] + DG / 2)

def dos(E, w, sigma=0.08):
    h, _ = np.histogram(np.ravel(E), bins=EDGES, weights=np.ravel(w))
    h = h / DG / np.size(E)
    return gaussian_filter1d(h, max(sigma, 1e-3) / DG)

def mu_for_filling(nu, eps=EPS):
    """chemical potential of the bare band at filling nu (nu=1 -> 2 electrons/site)"""
    es = np.sort(eps.ravel()); i = int(round(nu * es.size)); i = min(max(i, 0), es.size - 1); return es[i]

# ---------------- nu = 1/2 : Mott insulator (strong coupling) ----------------
def mott_bands(eps=EPS, U=U_HUB):
    c0 = -(eps.min() + eps.max()) / 4          # puts the midgap at w=0
    Em = -U / 2 + eps / 2 + c0; Ep = U / 2 + eps / 2 + c0
    wm = 0.5 * (1 - eps / U); wp = 1 - wm
    return Em, Ep, wm, wp

def mott_dos(sigma=0.08):
    Em, Ep, wm, wp = mott_bands()
    return dos(Em, wm, sigma) + dos(Ep, wp, sigma)

# ---------------- nu ~ 0.2 : BCS ----------------
def gap_equation_solve(mu, T=0.0, g=G_PAIR, eps=EPS):
    xi = eps - mu
    def f(D):
        E = np.sqrt(xi ** 2 + D ** 2) + 1e-12
        th = 1.0 if T <= 0 else np.tanh(E / (2 * T))
        return 1 - g * np.mean(th / (2 * E))
    if f(1e-6) > 0: return 0.0
    return brentq(f, 1e-6, 20)

def Tc_mf(mu, g=G_PAIR, eps=EPS):
    xi = np.abs(eps - mu) + 1e-12
    f = lambda T: 1 - g * np.mean(np.tanh(xi / (2 * T)) / (2 * xi))
    if f(0.01) > 0: return 0.0
    return brentq(f, 0.01, 30)

def bcs_bands(mu, Delta, eps=EPS):
    xi = eps - mu; E = np.maximum(np.sqrt(xi ** 2 + Delta ** 2), 1e-9); u2 = 0.5 * (1 + xi / E); v2 = 1 - u2
    return E, u2, v2, xi

def bcs_dos(mu, Delta, sigma=0.08):
    E, u2, v2, xi = bcs_bands(mu, Delta)
    return dos(E, u2, sigma) + dos(-E, v2, sigma)

# ---------------- nu ~ 0.3 low T : pseudogap / SC state (phenomenological, fitted to STS) ----------------
# parameters from fit of Fig.1(b) with D1 fixed to the spectral gap (2.45) and mu' = bare-band mu(nu=0.3): see report
PG = dict(c=4.650, a=0.558, b=0.0181, D1=2.45, alpha=1.031, beta=0.507, mu=-0.897)
def pg_bands(eps=EPS, p=PG):
    xi = eps - p['mu']
    Z = 0.5 * (1 + xi / np.sqrt(xi ** 2 + p['D1'] ** 2))          # in-window weight (Mott transfer factor)
    E = p['c'] + p['a'] * eps + p['b'] * eps ** 2                   # mirror bands ±E
    xt = p['alpha'] + p['beta'] * eps                                # 'normal' part controlling coherence factors
    s = np.clip(xt / np.maximum(E, 1e-6), -1, 1)
    pp = 0.5 * (1 + s); pm = 0.5 * (1 - s)
    return E, Z * pp, Z * pm, Z

def pg_dos(sigma=0.08):
    E, wp, wm, Z = pg_bands()
    return dos(E, wp, sigma) + dos(-E, wm, sigma)

def free_dos(mu, sigma=0.08):
    return dos(EPS - mu, np.ones_like(EPS), sigma)

def fermi_der(w, T):
    x = np.clip(w / T, -60, 60); return 1 / (4 * T * np.cosh(x / 2) ** 2)
