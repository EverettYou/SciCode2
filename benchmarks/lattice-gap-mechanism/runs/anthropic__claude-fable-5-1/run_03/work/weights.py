from fitlib import *
import numpy as np
for s in STS:
    V=np.array(s['bias']); g=np.array(s['dI_dV'])
    bgm=np.concatenate([g[(V<-9)],g[(V>9)]]); bg=np.median(bgm)
    print(f"panel {s['panel']} nu={s['filling']} T={s['temperature']}: bg median={bg:.3f}")
    # find band intervals: regions where g-bg > 0.05 after smoothing
    gs=np.convolve(g-bg,np.ones(9)/9,mode='same')
    m=gs>0.06
    idx=np.where(m)[0]; blocks=[]; st=idx[0]; pv=idx[0]
    for i in idx[1:]:
        if i!=pv+1: blocks.append((st,pv)); st=i
        pv=i
    blocks.append((st,pv))
    ws=[]
    for b in blocks:
        if b[1]-b[0]<10: continue
        w=np.trapz((g-bg)[b[0]:b[1]+1],V[b[0]:b[1]+1])
        ws.append(w); print(f"   band V in [{V[b[0]]:.2f},{V[b[1]]:.2f}] width={V[b[1]]-V[b[0]]:.2f} integrated weight={w:.3f}")
    if len(ws)>=2: print(f"   weight ratio lower/upper = {ws[0]/ws[-1]:.3f}")
# noise: residual distribution for panel c fit
p=np.load('fit_c.npy'); s=STS[2]; V=np.array(s['bias']); g=np.array(s['dI_dV'])
t,tp,mu,Dl,sig,bg,sc=p
eps=band(t,tp); xi=eps-mu; E=np.sqrt(xi**2+Dl**2); u2=0.5*(1+xi/E); v2=1-u2
mod=sc*sample(dos(E,u2,sig)+dos(-E,v2,sig),V)+bg
r=g-mod
print("panel c residual: std",r.std()," in-gap std",r[np.abs(V)<1.5].std()," bg region std",r[np.abs(V)>7].std())
print("gap region raw values stats (|V|<1.5): mean",g[np.abs(V)<1.5].mean(),"std",g[np.abs(V)<1.5].std(), "min",g[np.abs(V)<1.5].min())
# is noise multiplicative? compare std in regions of different mean
for lo,hi in [(-3.3,-2.3),(2.3,3.3),(4,5),(7,10),(-10,-7)]:
    mm=(V>lo)&(V<hi); print(f"  region [{lo},{hi}]: mean g={g[mm].mean():.3f} resid std={r[mm].std():.4f}")
