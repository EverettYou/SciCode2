"""Interlayer-singlet mean-field theory of the bilayer t1-t2-J model and the exact two-body
(rung-pair) problem.  g = 3J/4 is the attraction in the on-rung singlet channel.
Outputs data/meanfield.json."""
import numpy as np, json, sys
from scipy.optimize import brentq, fsolve
from scipy.special import expit
sys.path.insert(0, '.')
from band import eps, kgrid

t1, t2, J = 1.0, 0.2, 8.0
g = 0.75*J
kx, ky = kgrid(400); ek = eps(kx, ky, t1, t2).ravel()
N = ek.size

def gap_number(nu, T=0.0, Delta0=2.0, mu0=-1.0):
    """solve the T=0 (or finite-T) gap and number equations for Delta, mu at filling nu"""
    def eqs(p):
        D, mu = p; xi = ek-mu; E = np.sqrt(xi**2+D**2)
        th = np.tanh(E/(2*T)) if T > 0 else 1.0
        return [1 - g*np.mean(th/(2*E)), nu - 0.5*np.mean(1 - xi/E*th)]
    sol, info, ier, msg = fsolve(eqs, [Delta0, mu0], full_output=True)
    return sol[0], sol[1], ier == 1

def Tstar(nu):
    """mean-field pairing temperature: linearized gap equation with mu(T) from the normal state"""
    def mu_normal(T):
        f = lambda mu: np.mean(expit(-(ek-mu)/T)) - nu
        return brentq(f, -400, 400)
    def h(T):
        mu = mu_normal(T); xi = ek-mu
        return 1 - g*np.mean(np.tanh(xi/(2*T))/(2*xi))
    return brentq(h, 0.02, 20)

out = {'g': g, 'T0': {}, 'Tstar': {}}
nus = np.round(np.arange(0.02, 0.99, 0.02), 3)
D0, m0 = 2.0, -2.0
for nu in nus:
    D, mu, ok = gap_number(nu, 0.0, D0, m0)
    if ok: D0, m0 = D, mu
    xi = ek-mu; E = np.sqrt(xi**2+D**2)
    Emin = float(E.min())
    out['T0'][str(nu)] = dict(Delta=float(D), mu=float(mu), ok=bool(ok), Emin=Emin, mu_below_band=bool(mu < ek.min()))
    out['Tstar'][str(nu)] = float(Tstar(nu))
for nu in (0.2, 0.3, 0.206, 0.301, 0.5, 0.25):
    D, mu, ok = gap_number(nu, 0.0, 2.5, -1.5)
    print(f'nu={nu}: Delta_MF={D:.3f} mu={mu:.3f} (band bottom {ek.min():.2f}) ok={ok}; T*={Tstar(nu):.3f}  2Delta/T*={2*D/Tstar(nu):.2f}')
# T-dependence of the gap at nu=0.2 and 0.3 (mean field)
out['Delta_T'] = {}
for nu in (0.2, 0.3):
    Ts = np.linspace(0.05, Tstar(nu)*0.995, 25); Ds = []
    D0, m0 = gap_number(nu, 0.0, 2.5, -1.5)[:2]
    for T in Ts:
        D, mu, ok = gap_number(nu, T, D0, m0); Ds.append(D if ok else np.nan); D0 = max(D, 0.05)
    out['Delta_T'][str(nu)] = dict(T=Ts.tolist(), Delta=Ds)

# ---------------- exact two-body problem: rung pair in the empty lattice ----------------
def pair_energy(Kx, Ky):
    """bound-state energy of two electrons (layer 1 up, layer 2 down, singlet) at total momentum K"""
    e2 = eps(kx, ky, t1, t2) + eps(Kx-kx, Ky-ky, t1, t2)
    emin = e2.min()
    f = lambda E: 1 - g*np.mean(1/(e2-E))
    return brentq(f, emin-60, emin-1e-9), emin
E0p, cont = pair_energy(0, 0)
Ks = np.linspace(0, np.pi, 9)
disp = [pair_energy(K, 0)[0] for K in Ks]
dispd = [pair_energy(K, K)[0] for K in Ks]
# effective pair hopping from the dispersion along (K,0):  E(K)-E(0) ~ 2 t_b (1-cos K) (NN only)
tb_fit = np.polyfit(2*(1-np.cos(Ks)), np.array(disp)-E0p, 1)[0]
out['two_body'] = dict(E_pair_K0=float(E0p), two_particle_continuum_min=float(2*ek.min()), binding=float(2*ek.min()-E0p),
                       K=Ks.tolist(), E_K0=disp, E_KK=dispd, t_b_fit=float(tb_fit), bandwidth_pair=float(max(dispd)-E0p))
print(f'two-body: E_pair(0)={E0p:.4f}, continuum {2*ek.min():.3f}, binding {2*ek.min()-E0p:.4f}, t_b(fit)={tb_fit:.4f}, pair bandwidth {max(dispd)-E0p:.3f}')
json.dump(out, open('../data/meanfield.json', 'w'), indent=1)
