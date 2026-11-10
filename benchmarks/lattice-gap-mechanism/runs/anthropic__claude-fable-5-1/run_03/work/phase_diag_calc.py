from fitlib import *
import numpy as np
from scipy.optimize import brentq
import json
t,tp,U=0.99,0.195,12.02
eps=band(t,tp)
def Tc_mf(mu,gc):
    xi=eps-mu
    f=lambda T: 1-gc*np.mean(np.tanh(np.abs(xi)/(2*T))/(2*np.abs(xi)+1e-12))
    if f(0.02)>0: return 0.0
    return brentq(f,0.02,20)
def Delta0(mu,gc):
    xi=eps-mu
    f=lambda D: 1-gc*np.mean(1/(2*np.sqrt(xi**2+D**2)))
    if f(1e-6)>0: return 0.0
    return brentq(f,1e-6,20)
out={}
for gc in [5.97,6.1,6.25]:
    nus=np.linspace(0.02,0.98,49); Tcs=[]; Ds=[]
    for nu in nus:
        mu=mu_for_filling(eps,2*nu); Tcs.append(Tc_mf(mu,gc)); Ds.append(Delta0(mu,gc))
    out[str(gc)]={'nu':nus.tolist(),'Tmf':Tcs,'Delta0':Ds}
    print(f"g={gc}: Tmf at nu=0.1,0.2,0.3,0.4,0.5:",[round(np.interp(x,nus,Tcs),3) for x in [0.1,0.2,0.3,0.4,0.5]], " Delta0:",[round(np.interp(x,nus,Ds),3) for x in [0.1,0.2,0.3,0.4,0.5]])
json.dump(out,open('phase_calc.json','w'))
# where is vH filling
print("filling nu at which mu hits the vH:",np.mean(eps<4*tp))
