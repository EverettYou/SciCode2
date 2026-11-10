from load import *
import numpy as np
V,G=sts('b')
k=9; Gs=np.convolve(G,np.ones(k)/k,mode='same')
bg=0.0115*np.abs(V)
up=Gs-bg; 
E=np.arange(2.0,7.21,0.2)
print('  |E|   upper   lower   sum   ratio')
for e in E:
    iu=np.argmin(abs(V-e)); il=np.argmin(abs(V+e))
    u=up[iu]; l=up[il]
    print(f'{e:5.2f} {u:7.3f} {l:7.3f} {u+l:7.3f} {u/max(l,1e-3):6.2f}')
# bare DOS mapped
from smoothfit import *
t,tp=1.008,0.192
e=eps(t,tp)
Vg=np.linspace(-6,6,601)
d=gdos(Vg,e-(-0.912),np.ones_like(e),0.1)
print('bare DOS (relative to mu) normalized to max:')
for x in np.arange(-4,4.6,0.4):
    i=np.argmin(abs(Vg-x)); print(f'  xi={x:5.2f}  {d[i]/d.max():.3f}')
