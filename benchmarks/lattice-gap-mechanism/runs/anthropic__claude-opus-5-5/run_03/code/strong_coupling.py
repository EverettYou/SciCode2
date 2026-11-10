"""Strong-coupling quantities of the bilayer t-t'-J_perp model (rung-singlet / SMG regime), by exact
diagonalization of 1-, 2-, 3- and 4-rung clusters and the exact two-body problem.
Outputs: rung-triplet (spin) gap in 2D (2nd-order cluster expansion), rung-pair hopping and repulsion,
higher-order corrections to the hole band, pair dispersion at low density."""
import numpy as np
from scipy.optimize import brentq
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh
from ed_core import Cluster, singlet_product_state
from common import save_json, T_NN, T_NNN, J_PERP, U_HUB, kgrid, eps_c
out = {}


def lowest(cl, nup, ndn, k=4, layer_counts=None):
    st = cl.basis(nup, ndn, layer_counts)
    H = cl.H(st)
    return np.linalg.eigvalsh(H)[:k]


def bond_params(t, J, U):
    """second-order bond parameters from a 2-rung cluster"""
    single = Cluster(1, [], J, U)
    Es = lowest(single, 1, 1, 1)[0]                       # rung singlet
    Et = lowest(single, 2, 0, 1)[0]                       # rung triplet (Sz=1)
    two = Cluster(2, [(0, 1, t)], J, U)
    E_ss = lowest(two, 2, 2, 1)[0]                        # two singlets
    w1 = lowest(two, 3, 1, 2)                             # one triplon (Sz=1) on two rungs
    w_pair = lowest(two, 1, 1, 2)                         # one rung pair (2 electrons) on two rungs
    d_ss = E_ss - 2 * Es
    mid = 0.5 * (w1[0] + w1[1]) - (Et + Es); t_trip = 0.5 * (w1[1] - w1[0])
    t_b = 0.5 * (w_pair[1] - w_pair[0]); d_s0 = 0.5 * (w_pair[0] + w_pair[1]) - Es
    V_b = d_ss - 2 * d_s0
    return dict(singlet=Es, triplet=Et, d_ss=d_ss, d_ts_minus_d_ss=mid - d_ss, t_triplon=t_trip,
                t_pair=t_b, d_s0=d_s0, V_pair_NN=V_b)


for (J, U) in [(J_PERP, U_HUB), (6.0, 3.0)]:
    nn = bond_params(T_NN, J, U); nnn = bond_params(T_NNN, J, U)
    k = np.linspace(-np.pi, np.pi, 401); KX, KY = np.meshgrid(k, k)
    disp = (J + 4 * nn['d_ts_minus_d_ss'] + 4 * nnn['d_ts_minus_d_ss']
            + 2 * nn['t_triplon'] * (np.cos(KX) + np.cos(KY)) + 4 * nnn['t_triplon'] * np.cos(KX) * np.cos(KY))
    out['J=%g,U=%g' % (J, U)] = dict(NN=nn, NNN=nnn, triplon_gap_2D=float(disp.min()),
                                     triplon_band=[float(disp.min()), float(disp.max())])

# validation: 4-rung ring, exact spin gap vs 2nd-order prediction
ring = Cluster(4, [(r, (r + 1) % 4, T_NN) for r in range(4)], J_PERP, U_HUB)
st0 = ring.basis(4, 4); st1 = ring.basis(5, 3)
e0 = eigsh(csr_matrix(ring.H(st0)), k=1, which='SA')[0][0]; e1 = eigsh(csr_matrix(ring.H(st1)), k=1, which='SA')[0][0]
nn = out['J=%g,U=%g' % (J_PERP, U_HUB)]['NN']
pred = min(J_PERP + 2 * nn['d_ts_minus_d_ss'] - 2 * abs(nn['t_triplon']) * c for c in [1, -1])
out['ring4_validation'] = dict(exact_spin_gap=float(e1 - e0), second_order=float(J_PERP + 2 * nn['d_ts_minus_d_ss'] - 2 * abs(nn['t_triplon'])))


# CORE effective hole Hamiltonian (projection of exact low-lying states onto c|S..S>)
def hole_heff(R, rbonds, J, U):
    cl = Cluster(R, rbonds, J, U)
    stN = cl.basis(R, R); wN = np.linalg.eigvalsh(cl.H(stN)); E0 = wN[0]
    stH = cl.basis(R - 1, R, layer_counts=(R - 1, R)); wH, vH = np.linalg.eigh(cl.H(stH))
    S = singlet_product_state(cl, stN)
    refs = []
    for r in range(R):
        v = cl.op_c(2 * r, stN, stH) @ S; refs.append(v / np.linalg.norm(v))
    P = np.array(refs) @ vH[:, :R]
    Uu, s, Vt = np.linalg.svd(P); A = Uu @ Vt
    return A @ np.diag(wH[:R] - E0) @ A.T, s


core = {}
for lab, R, rb in [('NN', 2, [(0, 1, T_NN)]), ('NNN', 2, [(0, 1, T_NNN)]), ('straight3', 3, [(0, 1, T_NN), (1, 2, T_NN)]),
                   ('L3', 3, [(0, 1, T_NN), (1, 2, T_NN), (0, 2, T_NNN)])]:
    H, s = hole_heff(R, rb, J_PERP, U_HUB)
    core[lab] = dict(Heff=H, overlap_singular_values=s)
t1 = core['NN']['Heff'][0, 1]; tnnn = core['L3']['Heff'][0, 2]; t3 = core['straight3']['Heff'][0, 2]
eps0 = 0.75 * J_PERP + 4 * (core['NN']['Heff'][0, 0] - 0.75 * J_PERP) + 4 * (core['NNN']['Heff'][0, 0] - 0.75 * J_PERP)
# hole (removal) energies E_h(k); addition by particle-hole map (t->-t, t'->-t'): odd parts change sign
t2_first = T_NNN / 2; t2_second = tnnn - t2_first
cx, cy = kgrid(300)
Eh = eps0 + 2 * t1 * (cx + cy) + 4 * tnnn * cx * cy + 2 * t3 * ((2 * cx ** 2 - 1) + (2 * cy ** 2 - 1))
Ep = eps0 - 2 * t1 * (cx + cy) + 4 * (-t2_first + t2_second) * cx * cy + 2 * t3 * ((2 * cx ** 2 - 1) + (2 * cy ** 2 - 1))
lower = -Eh; upper = Ep
mid = 0.5 * (lower.max() + upper.min())
out['hole_band_higher_order'] = dict(t_hole_NN=t1, t_hole_NNN=tnnn, t_hole_3rd=t3, onsite=eps0,
                                     lower_band=[float(lower.min() - mid), float(lower.max() - mid)],
                                     upper_band=[float(upper.min() - mid), float(upper.max() - mid)],
                                     gap_edge=float(upper.min() - mid), band_centre=float(0.5 * (upper.min() + upper.max()) - mid),
                                     leading_order=dict(t_hole_NN=T_NN / 2, gap_edge=0.75 * J_PERP - 2 * T_NN, band_centre=0.75 * J_PERP))

# exact two-body (one rung pair in an empty lattice): pair dispersion
N = 200; k = 2 * np.pi * (np.arange(N) + 0.5) / N; KX, KY = np.meshgrid(k, k, indexing='ij')
def e2d(kx, ky): return -2 * T_NN * (np.cos(kx) + np.cos(ky)) - 4 * T_NNN * np.cos(kx) * np.cos(ky)
V0 = 0.75 * J_PERP
def Epair(Qx, Qy):
    e2 = e2d(Qx / 2 + KX, Qy / 2 + KY) + e2d(Qx / 2 - KX, Qy / 2 - KY)
    return brentq(lambda E: 1 - V0 * np.mean(1 / (e2 - E)), -60, e2.min() - 1e-9)
EG, EX, EM = Epair(0, 0), Epair(np.pi, 0), Epair(np.pi, np.pi)
c, tb, tbp = np.linalg.solve(np.array([[1, -4, -4], [1, 0, 4], [1, 4, -4]]), [EG, EX, EM])
q = 0.2; curv = (Epair(q, 0) - EG) / q ** 2
out['two_body_pair'] = dict(E_Gamma=EG, E_X=EX, E_M=EM, continuum_bottom=2 * e2d(0, 0), binding=2 * e2d(0, 0) - EG,
                            t_pair_NN=tb, t_pair_NNN=tbp, inv_2m=curv)
# coherence (KT) temperature of hard-core rung pairs: T_KT(x) ~ 0.686 t_b * 4x(1-x)  (x = density of empty rungs)
def TKT(x, tb): return 0.686 * tb * 4 * x * (1 - x)
dense_tb = out['J=%g,U=%g' % (J_PERP, U_HUB)]['NN']['t_pair']
out['coherence_estimates'] = dict(tb_dense_2nd_order=dense_tb, tb_dilute_exact=tb, tb_dilute_curvature=curv,
                                  TKT_nu0p3_dense=TKT(0.4, dense_tb), TKT_nu0p3_dilute=TKT(0.4, tb),
                                  TKT_nu0p3_curv=TKT(0.4, curv), tb_needed_for_measured_Tc0p3=0.36 / (0.686 * 4 * 0.4 * 0.6))
save_json(out, 'strong_coupling.json')
import json
print(json.dumps(out, indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else float(o)))
