"""Weak-coupling BCS estimate of the interlayer s-wave pairing gap.
J S1.S2 = -(3J/4) P_singlet + (J/4) P_triplet on a rung; in the interlayer singlet
pair channel the coupling constant is g = 3J/4 (attractive, on-site in r, s-wave in k).
Gap equation: 1 = g (1/N) sum_k 1/(2 E_k),  E_k = sqrt(xi_k^2 + D^2), mu fixed by the filling."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.optimize import brentq
from model import dispersion
L = 400
k = 2*np.pi*np.arange(L)/L
KX, KY = np.meshgrid(k, k, indexing="ij")
eps = dispersion(KX, KY).ravel()
def mu_of_nu(nu):
    # filling per flavor nu = fraction of states occupied at Delta=0
    return np.sort(eps)[int(nu*len(eps))]
out = {}
for nu in (0.5, 0.25, 0.125):
    mu = mu_of_nu(nu); xi = eps - mu
    g_of_D = lambda D: 1.0/np.mean(1.0/(2*np.sqrt(xi**2 + D**2)))
    Ds = np.logspace(-4, 0.7, 60)
    Js = [4/3*g_of_D(D) for D in Ds]
    out[nu] = dict(J=Js, Delta=Ds.tolist(), mu=float(mu))
    print(f"nu={nu}: mu={mu:.3f}; N(0) per site per flavor ~ {np.mean(np.abs(xi)<0.05)/0.1:.3f}")
    for J in (0.5, 1.0, 2.0, 3.0, 4.0):
        D = np.interp(J, Js, Ds)
        print(f"   J={J}: BCS gap Delta = {D:.4f}  (level spacing L=4 ~ 1, L=6 ~ 0.5, L=8 ~ 0.2)")
json.dump({str(k): v for k, v in out.items()}, open(os.path.join(os.path.dirname(__file__), "..", "data", "bcs_weak.json"), "w"))
