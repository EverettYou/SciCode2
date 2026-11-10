from fitlib import *
import numpy as np, itertools
s=STS[1]; V=np.array(s['bias']); g=np.array(s['dI_dV'])
t,tp=0.99,0.195
eps=band(t,tp)
def model(p,V):
    a,m,D0,D1,D2,sig,bg,sc=p
    xi=a*eps-m; Dk=D0+D1*(CX+CY)+D2*CX*CY
    E=np.sqrt(xi**2+Dk**2); u2=0.5*(1+xi/E); v2=1-u2
    return sc*sample(dos(E,u2,sig)+dos(-E,v2,sig),V)+bg
best=None
for a0,m0,D00,D10,D20 in itertools.product([0.5,1.0],[ -1.0,0.5,2.0],[3.5,5.0],[-1.5,0.0,1.5],[-1.0,0.0,1.0]):
    p0=[a0,m0,D00,D10,D20,0.15,0.06,2.5]
    try:
        r=least_squares(lambda p: model(p,V)-g,p0,x_scale=[0.1,0.2,0.3,0.3,0.3,0.03,0.02,0.3],diff_step=2e-2,bounds=([0.05,-6,0,-6,-6,0.03,0,0.1],[1.5,6,12,6,6,1.0,0.3,10]))
        rms=np.sqrt(np.mean(r.fun**2))
        if best is None or rms<best[0]: best=(rms,r.x)
    except Exception as e: pass
rms,p=best
print("best rms",rms); print("params a,m,D0,D1,D2,sigma,bg,sc =",np.round(p,4))
a,m,D0,D1,D2,sig,bg,sc=p
xi=a*eps-m; Dk=D0+D1*(CX+CY)+D2*CX*CY; E=np.sqrt(xi**2+Dk**2)
print("Delta_k range:",Dk.min(),Dk.max()," E range:",E.min(),E.max(), " <v^2>=",np.mean(0.5*(1-xi/E)))
print("FS (xi=0) fraction of BZ inside (xi<0):",np.mean(xi<0))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.figure(figsize=(12,4)); plt.plot(V,g,'k',lw=0.6); plt.plot(V,model(p,V),'r'); plt.xlim(-10,10); plt.grid(alpha=0.3); plt.title(f'Bogoliubov lattice-harmonic gap, rms={rms:.4f}'); plt.savefig('fit_b4.png',dpi=80)
np.save('fit_b4.npy',p)
