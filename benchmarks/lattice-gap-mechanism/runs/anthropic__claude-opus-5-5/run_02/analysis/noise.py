from load import *
import numpy as np
for p in 'abcd':
    V,G=sts(p)
    # local noise: difference between data and 9-pt running mean, in windows
    k=9; Gs=np.convolve(G,np.ones(k)/k,mode='same')
    r=G-Gs
    out=[]
    for lo,hi in [(-10,-8.5),(-7.5,-6.5),(-5,-4.5),(-1,1),(4.5,5),(5.5,6.5),(8.5,10)]:
        m=(V>lo)&(V<hi)
        out.append(f'[{lo},{hi}] std={np.std(r[m])*np.sqrt(k/(k-1)):.4f} mean={np.mean(G[m]):.3f}')
    print(p,' | '.join(out))
