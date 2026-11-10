import numpy as np, itertools
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import eigsh
# generic small-cluster ED for spinful fermions; sites labelled 0..L-1; Fock basis bitstrings (spin-up bits then spin-down bits)
def build(L, bonds, U, Jbonds, Ne, Sz2, nnq=False):
    # basis
    states=[]
    for up in itertools.combinations(range(L), (Ne+Sz2)//2):
        for dn in itertools.combinations(range(L), (Ne-Sz2)//2):
            s=0
            for i in up: s|=1<<i
            for i in dn: s|=1<<(i+L)
            states.append(s)
    idx={s:i for i,s in enumerate(states)}
    D=len(states); H=lil_matrix((D,D))
    def n(s,i): return (s>>i)&1
    def hop(s, a, b):  # c^dag_a c_b ; returns (sign, newstate) or None
        if not n(s,b) or (n(s,a) and a!=b): return None
        sign = (-1)**bin(s & ((1<<b)-1)).count('1')
        s2 = s ^ (1<<b)
        sign *= (-1)**bin(s2 & ((1<<a)-1)).count('1')
        return sign, s2 | (1<<a)
    for k,s in enumerate(states):
        # hopping
        for (i,j,tij) in bonds:
            for off in (0,L):
                for (a,b) in ((i,j),(j,i)):
                    r = hop(s, a+off, b+off)
                    if r: H[idx[r[1]],k] += -tij*r[0]
        # U
        for i in range(L): H[k,k] += U*n(s,i)*n(s,i+L)
        # J S_i.S_j
        for (i,j,J) in Jbonds:
            szi = 0.5*(n(s,i)-n(s,i+L)); szj = 0.5*(n(s,j)-n(s,j+L))
            H[k,k] += J*szi*szj
            if nnq: H[k,k] -= J*0.25*(n(s,i)+n(s,i+L))*(n(s,j)+n(s,j+L))
            # 0.5 J (S+_i S-_j + h.c.)
            for (p,q) in ((i,j),(j,i)):
                # S+_p S-_q = c^dag_{p up} c_{p dn} c^dag_{q dn} c_{q up}
                r1 = hop(s, q+L, q)     # c^dag_{q dn} c_{q up}
                if r1:
                    r2 = hop(r1[1], p, p+L)  # c^dag_{p up} c_{p dn}
                    if r2: H[idx[r2[1]],k] += 0.5*J*r1[0]*r2[0]
    return H.tocsr(), states
def spectrum(L, bonds, U, Jbonds, Ne, Sz2, k=6, nnq=False):
    H,_ = build(L, bonds, U, Jbonds, Ne, Sz2, nnq)
    Hd = H.toarray()
    w = np.linalg.eigvalsh(Hd)
    return w[:k]
if __name__=='__main__':
    t=1.0
    for (U,J,nnq) in [(3.0,6.0,False),(3.0,6.0,True),(0.0,8.0,False),(0.0,6.0,False)]:
        # 2 rungs: sites 0=(r0,l1),1=(r0,l2),2=(r1,l1),3=(r1,l2)
        bonds=[(0,2,t),(1,3,t)]; Jb=[(0,1,J),(2,3,J)]
        w0 = spectrum(4,bonds,U,Jb,4,0,8,nnq); w1 = spectrum(4,bonds,U,Jb,4,2,6,nnq)
        # isolated rung reference
        r0 = spectrum(2,[],U,[(0,1,J)],2,0,4,nnq); 
        print('U=%.1f J=%.1f nnq=%s : 2-rung Sz=0 lowest:'%(U,J,nnq), np.round(w0[:4],4), ' Sz=1 lowest:', np.round(w1[:3],4), ' single rung:', np.round(r0[:4],3))
        Es = w0[0]; Et = np.sort(w1)[:2]
        print('    E_ss=%.4f  triplon levels %.4f %.4f  -> gap(sym/antisym) = %.4f, %.4f ; t_trip=%.4f ; 2-rung SS shift per bond=%.4f' % (Es, Et[0], Et[1], Et[0]-Es, Et[1]-Es, (Et[1]-Et[0])/2, Es-2*r0[0]))
