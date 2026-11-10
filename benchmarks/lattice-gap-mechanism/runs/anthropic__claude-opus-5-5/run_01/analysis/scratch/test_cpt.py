import numpy as np
from cpt_bilayer import *
pos = cluster_geometry(2, 2)
cg = ClusterGF(pos, 1.0, 0.2, 0.0, 0.0, 2, 2, sites_list=list(range(8)), nsteps=40)
cpt = CPT(cg, Lx=2, Ly=2)
eta = 0.05
w = np.linspace(-6, 6, 1201)
for k in [(0,0), (np.pi,0), (np.pi,np.pi), (np.pi/3, 0.7)]:
    k = np.array(k)
    A = np.array([-cpt.Gk(k, ww+1j*eta).imag/np.pi for ww in w])
    eps = -2*(np.cos(k[0])+np.cos(k[1])) - 0.8*np.cos(k[0])*np.cos(k[1])
    # chemical potential reference: cluster energies are absolute (mu=0 in H), so peak should be at eps
    print(k, 'peak at', w[np.argmax(A)], ' eps_k =', round(eps,4), ' weight', np.trapezoid(A, w).round(3))
