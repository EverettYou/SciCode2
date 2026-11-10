import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
d=json.load(open('/app/measurements.json'))
sts=d['measurements'][0]['spectra']
fig,axs=plt.subplots(4,1,figsize=(14,16))
for ax,s in zip(axs,sts):
    V=np.array(s['bias']); g=np.array(s['dI_dV'])
    ax.plot(V,g,'-',lw=0.7)
    ax.set_title(f"panel {s['panel']} nu={s['filling']} T={s['temperature']}")
    ax.set_xticks(np.arange(-10,10.1,0.5)); ax.grid(True,alpha=0.4)
    ax.tick_params(axis='x',labelsize=7)
plt.tight_layout(); plt.savefig('sts_zoom.png',dpi=90)

for s in sts:
    V=np.array(s['bias']); g=np.array(s['dI_dV'])
    print("=== panel",s['panel'],s['filling'],s['temperature'])
    # background level statistics far outside
    for lo,hi in [(-10,-9),(9,10)]:
        m=(V>=lo)&(V<=hi); print(f"  bg [{lo},{hi}] mean={g[m].mean():.4f} std={g[m].std():.4f}")
    # zero region
    z = np.where(g==0)[0]
    print("  exact zeros count:",len(z), "range:", (V[z].min(),V[z].max()) if len(z) else None)
    # values below 0.005
    m=g<0.01
    if m.sum():
        idx=np.where(m)[0]
        # contiguous blocks
        blocks=[]; start=idx[0]; prev=idx[0]
        for i in idx[1:]:
            if i!=prev+1:
                blocks.append((start,prev)); start=i
            prev=i
        blocks.append((start,prev))
        for b in blocks:
            if b[1]-b[0]>5: print(f"  low(<0.01) block V in [{V[b[0]]:.3f},{V[b[1]]:.3f}] n={b[1]-b[0]+1}")
    # peaks
    from scipy.signal import find_peaks
    gs=np.convolve(g,np.ones(5)/5,mode='same')
    pk,_=find_peaks(gs,prominence=0.12)
    print("  peaks (smoothed):",[(round(V[p],3),round(gs[p],3)) for p in pk])
    # print coarse profile
    print("  coarse profile (V, mean g over 0.25 bins):")
    edges=np.arange(-10,10.01,0.25)
    out=[]
    for a,b in zip(edges[:-1],edges[1:]):
        m=(V>=a)&(V<b)
        out.append(f"{(a+b)/2:6.3f}:{g[m].mean():.3f}")
    for i in range(0,len(out),8): print("   "+"  ".join(out[i:i+8]))
