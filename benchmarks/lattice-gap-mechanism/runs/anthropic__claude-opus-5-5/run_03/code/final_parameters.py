"""Collect the final coefficient values, uncertainties and derived scales into results/final_parameters.json.
Run after fit_sts.py, fit_nmr_rho.py, strong_coupling.py and luttinger.py."""
import json
import numpy as np
from scipy.optimize import brentq
from common import RES, kgrid, eps_c, save_json

sts = json.load(open(f'{RES}/sts_fits.json')); sc = json.load(open(f'{RES}/strong_coupling.json'))
nr = json.load(open(f'{RES}/nmr_rho_fits.json')); lt = json.load(open(f'{RES}/luttinger.json'))
t = sts['d']['params']['t'][0]; tp = sts['d']['params']['tp'][0]
pc = sts['c']['params']; Phi = sts['a']['translated_copies']['params']['Phi'][0]

# HFB coupling V = 3 J_perp / 4 that reproduces the measured nu~0.2 gap (mu at its fitted normal-state value)
cx, cy = kgrid(600); e = pc['g'][0] * eps_c(cx, cy, t, tp)
def V_of(D, mu): xi = e - mu; return 1 / np.mean(1 / (2 * np.sqrt(xi ** 2 + D ** 2)))
def Tc_of(V, mu):
    xi = e - mu; x = np.where(np.abs(xi) < 1e-12, 1e-12, xi)
    return brentq(lambda T: 1 - V * np.mean(np.tanh(x / (2 * T)) / (2 * x)), 0.05, 20)
D, dD = pc['Delta']; mu, dmu = pc['mu']
V = V_of(D, mu); dV = np.hypot(V_of(D + dD, mu) - V, V_of(D, mu + dmu) - V)
Vlo = brentq(lambda v: Tc_of(v, mu) - 1.075, 5.0, 7.0); Vhi = brentq(lambda v: Tc_of(v, mu) - 1.15, 5.0, 7.0)
J = 4 * V / 3; U = 2 * (Phi - V)

final = {
    "units": "energies in D; momenta in 2pi/a; k_B=1",
    "lattice": "bilayer square lattice (two equivalent TM sites per primitive cell = one rung), lattice constant a",
    "hamiltonian": "H = -t sum_<ij>,l,s c+c - t' sum_<<ij>>,l,s c+c + J_perp sum_i S_i1.S_i2  [+ t_perp, U, J_par terms consistent with zero]",
    "coefficients": {
        "t": {"value": t, "stat": sts['d']['params']['t'][1], "syst": 0.003, "from": "STS (d) band edges; consistent with (a),(c)"},
        "t_prime": {"value": tp, "stat": sts['d']['params']['tp'][1], "syst": 0.002,
                    "from": "STS (d) van Hove position; STS (a) gives %.4f" % sts['a']['translated_copies']['params']['tp'][0]},
        "J_perp": {"value": J, "stat": 4 * dV / 3, "syst": 0.3,
                   "from": "STS (c) gap via HFB coupling V=3J/4=%.4f; Tc(0.2) window -> J in (%.3f, %.3f); Phi(a); NMR spin gap" % (V, 4 * Vlo / 3, 4 * Vhi / 3)},
        "U": {"value": U, "stat": 2 * np.hypot(sts['a']['translated_copies']['params']['Phi'][1], dV), "syst_upper": 0.6,
              "from": "Phi(a) = 3J/4 + U/2 at leading order; O(t^2/J) corrections allow up to ~0.6"},
        "t_perp": {"value": 0.0, "bound": 0.1, "from": "no bonding/antibonding splitting in STS (d),(a)"},
        "J_par": {"value": 0.0, "bound": 0.1, "from": "spin-gap agreement; isotropic gap at nu=0.2"},
    },
    "derived": {
        "Phi_rung_charge_energy": Phi,
        "single_particle_gap_nu_half": 2 * sts['a']['gap_edge'],
        "spin_gap_theory_2D": sc['J=8,U=0']['triplon_gap_2D'],
        "spin_gap_NMR": nr['nmr']['1/2']['p=1'],
        "transport_activation_nu_half": nr['rho']['1/2']['p=0'],
        "BCS_gap_nu0.2": pc['Delta'], "Tc_MF_nu0.2": Tc_of(V, mu),
        "pair_hopping_dense_dilute": [sc['coherence_estimates']['tb_dense_2nd_order'], sc['coherence_estimates']['tb_dilute_exact'],
                                      sc['coherence_estimates']['tb_dilute_curvature']],
        "luttinger_zero_fraction": lt['fraction_central'],
    }}
save_json(final, 'final_parameters.json')
print(json.dumps(final['coefficients'], indent=1))
