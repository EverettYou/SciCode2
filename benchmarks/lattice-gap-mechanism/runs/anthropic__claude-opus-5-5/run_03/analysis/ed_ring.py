import sys; sys.path.insert(0,'/app/analysis')
import numpy as np
from ed_rungs import build
from scipy.sparse.linalg import eigsh
t,J,U=1.0,8.0,0.0
for L in [4]:
    # sites: rung r, layer l -> index 2r+l
    bonds=[]; Jb=[]
    for r in range(L):
        s=(r+1)%L
        bonds += [(2*r,2*s,t),(2*r+1,2*s+1,t)]
        Jb.append((2*r,2*r+1,J))
    H0,_=build(2*L,bonds,U,Jb,2*L,0); H1,_=build(2*L,bonds,U,Jb,2*L,2)
    e0=eigsh(H0,k=2,which='SA')[0]; e1=eigsh(H1,k=2,which='SA')[0]
    print('L=%d ring: E0=%.4f  lowest S=1: %.4f  spin gap=%.4f'%(L,e0[0],e1[0],e1[0]-e0[0]))
# 2nd-order prediction for a ring (z=2): J + 2(dts-dss) - 2|t_trip| with 4-rung momenta q=0,pi/2,pi -> min over allowed q
d=-0.2349; tt=0.4142
for q in [0,np.pi/2,np.pi]:
    print('  2nd order q=%.2f: %.4f / %.4f'%(q, 8+2*d+2*tt*np.cos(q), 8+2*d-2*tt*np.cos(q)))
