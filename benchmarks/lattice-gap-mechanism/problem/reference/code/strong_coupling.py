"""Second-order strong-coupling theory from the exact two-rung problem.
Rung i has sites (i,1),(i,2).  Two rungs i, j joined by an in-plane bond of amplitude t in
both layers.  We compute the effective Hamiltonians in the degenerate manifolds and from them
the triplon dispersion, the pair-boson hopping t_b and the pair-pair interaction V,
and the first-order holon/trion hopping (t/2).  Then the triplon band on the lattice with t1, t2."""
import numpy as np, json, sys
sys.path.insert(0, '.')
from fock import Fock
from band import kgrid

J = 8.0
def two_rung(t, J=J, nelec=None):
    """sites: 0=(i,1), 1=(i,2), 2=(j,1), 3=(j,2)"""
    F = Fock(4, nelec)
    HJ = J*(F.SdotS(0, 1) + F.SdotS(2, 3))
    Ht = F.hopping([(0, 2, t), (1, 3, t)])
    return F, HJ.toarray(), Ht.toarray()

def eff_second_order(H0, V, P_idx, E0, tol=1e-9):
    """H_eff = P H0 P + P V P + P V Q (E0-H0)^-1 Q V P  for a degenerate manifold P (H0 diagonal)."""
    d = np.diag(H0)
    Q = np.ones(len(d), bool); Q[P_idx] = False
    denom = np.where(np.abs(E0-d) > tol, 1.0/np.where(np.abs(E0-d) > tol, E0-d, 1), 0.0)*Q
    VP = V[:, P_idx]
    Heff = H0[np.ix_(P_idx, P_idx)] + V[np.ix_(P_idx, P_idx)] + VP.T @ (denom[:, None]*VP)
    return Heff

results = {}
# ---------- triplon manifold: 4 electrons, each rung singly occupied in singlet/triplet ----------
F, H0, V = two_rung(1.0, nelec=4)
d = np.diag(H0)
# low manifold: states with H0 in {-3J/2 (ss), -J/2 (st, ts), J/2 (tt)}; off-diagonal H0 (spin flips) -> diagonalize H0 first
w, U = np.linalg.eigh(H0)
H0d = np.diag(w); Vd = U.T @ V @ U
def manifold(E): return np.where(np.abs(w-E) < 1e-9)[0]
Pss = manifold(-1.5*J); Pst = manifold(-0.5*J)
Hss = eff_second_order(H0d, Vd, Pss, -1.5*J)
e_ss = Hss[0, 0] + 1.5*J              # second-order bond energy of singlet-singlet
Hst = eff_second_order(H0d, Vd, Pst, -0.5*J)
# Pst is 6-dim: triplet on i (3) x singlet on j, singlet on i x triplet on j (3). Hopping couples same m.
ev = np.linalg.eigvalsh(Hst) + 0.5*J
# eigenvalues come in +-tau pairs around e_st
e_st = ev.mean(); tau = (ev.max()-ev.min())/2
# sign of tau: compute matrix element between |t_i s_j> and |s_i t_j> for m=0 explicitly
# identify states: use S^z_total and the rung singlet projector
Sz_i = (F.spin_ops(0)[2] + F.spin_ops(1)[2]).toarray(); Sz_j = (F.spin_ops(2)[2] + F.spin_ops(3)[2]).toarray()
SSi = F.SdotS(0, 1).toarray(); SSj = F.SdotS(2, 3).toarray()
# in the eigenbasis U, pick m=+1 triplet (Sz_i = 1) states to fix the sign of the hop
Szi_d = np.diag(U.T @ Sz_i @ U); Szj_d = np.diag(U.T @ Sz_j @ U)
a = [p for p in Pst if abs(Szi_d[p]-1) < 1e-6][0]; b = [p for p in Pst if abs(Szj_d[p]-1) < 1e-6][0]
ia, ib = list(Pst).index(a), list(Pst).index(b)
tau_signed = Hst[ia, ib]
results['triplon'] = dict(e_ss=e_ss, e_st=e_st, tau_abs=tau, tau_signed=float(tau_signed))
print('triplon: e_ss=%.5f e_st=%.5f  tau=%.5f (signed %.5f)   [units t^2/J... with t=1,J=8]' % (e_ss, e_st, tau, tau_signed))

# ---------- pair-boson manifold: singlet + empty (2 electrons) ----------
F2, H0, V = two_rung(1.0, nelec=2)
w, U = np.linalg.eigh(H0); H0d = np.diag(w); Vd = U.T@V@U
P = np.where(np.abs(w+0.75*J) < 1e-9)[0]   # singlet on i or on j (2 states)
Hb = eff_second_order(H0d, Vd, P, -0.75*J)
ev = np.linalg.eigvalsh(Hb) + 0.75*J
e_s0 = ev.mean(); tb = (ev.max()-ev.min())/2
# sign: the symmetric combination should be lower for a normal (negative) boson hopping
vec = np.linalg.eigh(Hb)[1][:, 0]
results['boson'] = dict(e_s0=e_s0, t_b=tb, e_ss=e_ss, V_bb=e_ss-2*e_s0, lowest_is_symmetric=bool(np.sign(vec[0]*vec[1]) > 0))
print('boson: e_s0=%.5f t_b=%.5f  V=e_ss-2e_s0=%.5f  symmetric lowest: %s' % (e_s0, tb, e_ss-2*e_s0, results['boson']['lowest_is_symmetric']))

# ---------- holon (3 electrons): singlet + one-electron rung: first order hopping ----------
F3, H0, V = two_rung(1.0, nelec=3)
w, U = np.linalg.eigh(H0); H0d = np.diag(w); Vd = U.T@V@U
P = np.where(np.abs(w+0.75*J) < 1e-9)[0]  # 8 states: holon (4) on i with singlet on j, and vice versa
H1 = H0d[np.ix_(P, P)] + Vd[np.ix_(P, P)]
ev = np.linalg.eigvalsh(H1) + 0.75*J
results['holon_first_order'] = dict(levels=sorted(set(np.round(ev, 6).tolist())))
Hh = eff_second_order(H0d, Vd, P, -0.75*J)
ev2 = np.linalg.eigvalsh(Hh) + 0.75*J
results['holon_second_order'] = dict(levels=sorted(set(np.round(ev2, 6).tolist())))
print('holon first-order levels (t=1):', results['holon_first_order']['levels'])
print('holon second-order levels (t=1):', results['holon_second_order']['levels'])
F5, H0, V = two_rung(1.0, nelec=5)
w, U = np.linalg.eigh(H0); H0d = np.diag(w); Vd = U.T@V@U
P = np.where(np.abs(w+0.75*J) < 1e-9)[0]
H1 = H0d[np.ix_(P, P)] + Vd[np.ix_(P, P)]
ev = np.linalg.eigvalsh(H1) + 0.75*J
results['trion_first_order'] = dict(levels=sorted(set(np.round(ev, 6).tolist())))
print('trion first-order levels (t=1):', results['trion_first_order']['levels'])

# ---------- triplon dispersion on the lattice ----------
# bond contributions scale as t^2: e(t) = e(1)*t^2, tau(t) = tau(1)*t^2
t1, t2 = 1.0, 0.2
de1 = (e_st-e_ss)*t1**2; de2 = (e_st-e_ss)*t2**2
tau1 = tau_signed*t1**2; tau2 = tau_signed*t2**2
def omega_t(kx, ky):
    return J + 4*de1 + 4*de2 + 2*tau1*(np.cos(kx)+np.cos(ky)) + 4*tau2*np.cos(kx)*np.cos(ky)
kx, ky = kgrid(400); om = omega_t(kx, ky)
imin = np.unravel_index(np.argmin(om), om.shape)
results['triplon_band'] = dict(J=J, t1=t1, t2=t2, omega_min=float(om.min()), k_min=[float(kx[imin]), float(ky[imin])],
                               omega_max=float(om.max()), omega_pipi=float(omega_t(np.pi, np.pi)), omega_00=float(omega_t(0, 0)),
                               omega_pi0=float(omega_t(np.pi, 0)), de1=de1, de2=de2, tau1=tau1, tau2=tau2)
print('triplon band: min %.4f at k=(%.2f,%.2f); max %.4f; (pi,pi)=%.4f (0,0)=%.4f (pi,0)=%.4f' % (
    om.min(), kx[imin], ky[imin], om.max(), omega_t(np.pi, np.pi), omega_t(0, 0), omega_t(np.pi, 0)))
# one-triplon DOS for the NMR integral
E = np.linspace(om.min()-0.1, om.max()+0.1, 400)
h, _ = np.histogram(om.ravel(), bins=E); results['triplon_dos'] = dict(E=(0.5*(E[1:]+E[:-1])).tolist(), rho=(h/om.size/(E[1]-E[0])).tolist())

# ---------- first-order charge gap and the pair gap ----------
results['charge_gap_first_order'] = 1.5*J - 4*t1
results['pair_gap_second_order'] = 2*(0.75*J - 4*tb - 4*e_s0 + 0*e_ss)  # rough: remove/add a pair
json.dump(results, open('../data/strong_coupling.json', 'w'), indent=1)
