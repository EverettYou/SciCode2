import numpy as np
from cpt_bilayer import *
from band_lanczos_fast import band_lanczos_fast
import cpt_bilayer as cb
from ed_bilayer import BSector
pos = cluster_geometry(2, 2); M = 4
T = intra_hopping(pos, 1.0, 0.2, 0.0)
U, J = 1.8, 6.5
def dense(sec):
    H = np.zeros((sec.dim, sec.dim)); e = np.zeros(sec.shape)
    for i in range(sec.dim):
        e.ravel()[:] = 0; e.ravel()[i] = 1
        H[:, i] = sec.hv(e).ravel()
    return H
s0 = BSector(M, 4, 4, T, U, J); H0 = dense(s0); w0, v0 = np.linalg.eigh(H0); gs = v0[:, 0].reshape(s0.shape); E0 = w0[0]
sp = BSector(M, 5, 4, T, U, J); Hp = dense(sp); wp, vp = np.linalg.eigh(Hp)
sm = BSector(M, 3, 4, T, U, J); Hm = dense(sm); wm, vm = np.linalg.eigh(Hm)
P = []; Hh = []
for s in range(M):
    a = np.empty(sp.shape); cb._cdag_site(gs, sp.mu, s0.lu, s0.shape[1], s, a); P.append(vp.T @ a.ravel())
    b = np.empty(sm.shape); cb._c_site(gs, sm.mu, s0.lu, s0.shape[1], s, b); Hh.append(vm.T @ b.ravel())
P = np.array(P); Hh = np.array(Hh)
def Gex(z):
    return (P / (z - (wp - E0))) @ P.T + (Hh / (z - (E0 - wm))) @ Hh.T
cg1 = ClusterGF(pos, 1.0, 0.2, U, J, 4, 4, sites_list=list(range(M)), nsteps=40, verbose=False)
cb.band_lanczos = band_lanczos_fast
cg2 = ClusterGF(pos, 1.0, 0.2, U, J, 4, 4, sites_list=list(range(M)), nsteps=40, verbose=False)
for z in [0.3+0.05j, -6+0.1j, 6.5+0.1j, -4.5+0.1j]:
    g = Gex(z)
    print(z, 'orig err', np.abs(cg1.G(z)-g).max(), ' fast err', np.abs(cg2.G(z)-g).max(), ' |G|', np.abs(g).max())
