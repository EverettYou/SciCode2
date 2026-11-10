from load import *
import numpy as np
from scipy.optimize import curve_fit
regions={'a':[(-10,-8.4),(8.4,10)],'b':[(-10,-6.9),(6.9,10)],'c':[(-10,-5.8),(5.8,10)],'d':[(-10,-4.4),(4.4,10)]}
for p in 'abcd':
    V,G=sts(p)
    m=np.zeros_like(V,bool)
    for lo,hi in regions[p]: m|=(V>lo)&(V<hi)
    x=np.abs(V[m]); y=G[m]
    f1=lambda x,a: a*x
    f2=lambda x,a,pw: a*x**pw
    f3=lambda x,a,b: a+b*x**2
    p1,_=curve_fit(f1,x,y); p2,_=curve_fit(f2,x,y,p0=[0.01,1]); p3,_=curve_fit(f3,x,y)
    r1=np.std(y-f1(x,*p1)); r2=np.std(y-f2(x,*p2)); r3=np.std(y-f3(x,*p3))
    print(p,'a|V|: a=%.4f rms=%.4f | a|V|^p: a=%.4f p=%.2f rms=%.4f | a+bV^2: a=%.4f b=%.5f rms=%.4f'%(p1[0],r1,p2[0],p2[1],r2,p3[0],p3[1],r3))
    # print binned means
    for lo,hi in [(4.5,5.5),(5.8,6.8),(6.9,7.9),(8.0,9.0),(9.0,10)]:
        mm=(np.abs(V)>=lo)&(np.abs(V)<hi)&m
        if mm.sum()>3: print('    |V| in [%.1f,%.1f): mean %.4f'%(lo,hi,np.mean(G[mm])))
