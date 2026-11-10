from fitlib import *
import numpy as np
from scipy.integrate import trapezoid
for idx,bg in [(1,0.063),(2,0.064),(0,0.044)]:
    s=STS[idx]; V=np.array(s['bias']); g=np.array(s['dI_dV'])
    # bias-dependent background: fit quadratic to regions outside bands
    if idx==1: outs=[(-10,-7.0),(7.0,10)]; lo=(-7.0,-2.3); up=(2.3,7.0)
    if idx==2: outs=[(-10,-4.0),(6.0,10)]; lo=(-4.0,-1.5); up=(1.5,6.0)
    if idx==0: outs=[(-10,-8.3),(8.4,10)]; lo=(-8.3,-3.8); up=(3.8,8.4)
    mo=np.zeros_like(V,dtype=bool)
    for a,b in outs: mo|=(V>=a)&(V<=b)
    pq=np.polyfit(V[mo],g[mo],2); bgq=np.polyval(pq,V)
    print(f"panel {s['panel']}: quadratic bg fit coeffs {pq}; bg at 0: {np.polyval(pq,0):.3f}, at +-6.5: {np.polyval(pq,6.5):.3f}")
    for label,bgv in [('const bg',bg),('quad bg',bgq)]:
        ml=(V>=lo[0])&(V<=lo[1]); mu_=(V>=up[0])&(V<=up[1])
        wl=trapezoid(np.clip(g[ml]-(bgv if np.isscalar(bgv) else bgv[ml]),0,None),V[ml])
        wu=trapezoid(np.clip(g[mu_]-(bgv if np.isscalar(bgv) else bgv[mu_]),0,None),V[mu_])
        print(f"   [{label}] lower={wl:.3f} upper={wu:.3f} ratio={wl/wu:.3f} -> if all weight in window: n/2 = {wl/(wl+wu):.3f}")
