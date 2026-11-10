import numpy as np, json
d = json.load(open('/app/measurements.json'))
s = d['measurements'][0]['spectra'][1]
V = np.array(s['bias']); G = np.array(s['dI_dV'])
# smooth & background subtract
k=9; Gs = np.convolve(G, np.ones(k)/k, mode='same')
b = 0.0107
Gb = Gs - b*np.abs(V)*(np.abs(V)>2.5)
Gb[np.abs(V)<2.55] = 0
E = V[V>0]; Np = Gb[V>0]; Nm = Gb[V<0][::-1]
Nm = np.interp(E, -V[V<0][::-1], Gb[V<0][::-1])
norm = np.trapezoid(Np+Nm, E)
Np/=norm; Nm/=norm
# bare DOS per spin per site
N=1200; kk=(np.arange(N)+0.5)/N; KX,KY=np.meshgrid(kk,kk,indexing='ij')
e=(-2*0.9993*(np.cos(2*np.pi*KX)+np.cos(2*np.pi*KY))-4*0.1945*np.cos(2*np.pi*KX)*np.cos(2*np.pi*KY)).ravel()
mu=-0.907
h, ed = np.histogram(e-mu, bins=800, range=(-4.2,4.4)); xc=0.5*(ed[1:]+ed[:-1]); N0=h/len(e)/(ed[1]-ed[0])
N0f = lambda x: np.interp(x, xc, N0)
print('integral of bare DOS below mu:', np.trapezoid(N0[xc<0], xc[xc<0]), ' (should be 0.3)')
# integrate from E0 upward
S = Np+Nm; D = Np-Nm
i0 = np.argmax(S>0.02*S.max())
print('onset E ~', E[i0])
xp, xm = 1e-3, -1e-3
out=[]
for i in range(i0, len(E)-1):
    Ei = E[i]; dE = E[i+1]-E[i]
    if S[i] <= 0: 
        out.append((Ei, xp, xm)); continue
    npl = (D[i]*Ei - xm*S[i])/(xp - xm); nmi = (xp*S[i] - D[i]*Ei)/(xp - xm)
    npl = max(npl, 0); nmi = max(nmi, 0)
    xp += npl/max(N0f(xp),1e-3)*dE; xm -= nmi/max(N0f(xm),1e-3)*dE
    out.append((Ei, xp, xm))
out=np.array(out)
for r in out[::12]:
    Ei, xp_, xm_ = r
    Dp = np.sqrt(max(Ei**2-xp_**2,0)); Dm = np.sqrt(max(Ei**2-xm_**2,0))
    print('E=%.2f  xi+=%.3f (Delta=%.2f)   xi-=%.3f (Delta=%.2f)'%(Ei, xp_, Dp, xm_, Dm))
