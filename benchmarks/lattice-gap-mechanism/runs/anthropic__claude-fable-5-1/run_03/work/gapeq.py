from fitlib import *
import numpy as np
t,tp=0.99,0.195
eps=band(t,tp)
for nu,Dl in [(0.198,1.967),(0.295,2.45)]:
    mu=mu_for_filling(eps,2*nu); xi=eps-mu; E=np.sqrt(xi**2+Dl**2)
    inv_g=np.mean(1/(2*E))  # Delta = g/N sum Delta/(2E) -> 1 = g <1/(2E)>
    print(f"nu={nu}: mu={mu:.3f}, 1/g = <1/2E> = {inv_g:.4f} -> g = {1/inv_g:.3f} ; N(mu) free DOS=",np.mean(np.abs(xi)<0.05)/0.1)
    # also with a cutoff-free 'U_eff' and the BCS Tc: Delta(0)/Tc=1.764 -> Tc_MF
    print(f"   BCS mean-field Tc = Delta/1.764 = {Dl/1.764:.3f}")
