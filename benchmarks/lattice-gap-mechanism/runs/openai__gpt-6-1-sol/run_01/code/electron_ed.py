"""Exact diagonalization of physical one-orbital electron Hamiltonians.

Fock basis contains only 2 spin modes per metal site. No auxiliary orbitals.
H=-t K1-tp K2+U D+J1(S.S-nn/4)_1+J2(S.S-nn/4)_2-P pair_hopping_1.
The 10-site tilted torus has primitive vectors (3,1),(-1,3).
"""
import os
for n in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ.setdefault(n,'1')
from pathlib import Path
from itertools import combinations
import json,time,sys
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh

ROOT=Path(__file__).resolve().parents[1]
def states(N,n):
    return np.array([sum(1<<i for i in p) for p in combinations(range(N),n)],dtype=np.int64)

class Sector:
    def __init__(self,N,nu,nd,nn=None,nnn=None):
        self.N=N;self.nu=nu;self.nd=nd
        if nn is None:
            assert N==10
            nn=sorted(set(tuple(sorted((i,(i+d)%N))) for i in range(N) for d in [1,-3]))
            nnn=sorted(set(tuple(sorted((i,(i+d)%N))) for i in range(N) for d in [-2,4]))
        self.nn=nn;self.nnn=nnn or []
        self.us=states(N,nu);self.ds=states(N,nd);self.nD=len(self.ds)
        self.bits=(self.us[:,None]|(self.ds[None,:]<<N)).ravel()
        self.dim=len(self.bits);self.rows=np.arange(self.dim)
        self.ui=np.full(1<<N,-1,dtype=int);self.ui[self.us]=np.arange(len(self.us))
        self.di=np.full(1<<N,-1,dtype=int);self.di[self.ds]=np.arange(len(self.ds))
        self.occ=np.array([(self.bits>>i)&1 for i in range(2*N)],dtype=np.int8)
        self.terms={}
        self.terms['K1']=self.hop(nn)
        self.terms['K2']=self.hop(self.nnn)
        self.terms['D']=sp.diags(np.sum(self.occ[:N]*self.occ[N:],axis=0),format='csr')
        self.terms['J1']=self.exchange(nn)
        self.terms['J2']=self.exchange(self.nnn)
        self.terms['P']=self.pairhop(nn)
        diag=np.zeros(self.dim)
        for i,j in nn:
            diag+=(self.occ[i]+self.occ[N+i]-1)*(self.occ[j]+self.occ[N+j]-1)
        self.terms['V1']=sp.diags(diag,format='csr')
        self.v0=None

    def op(self,ops):
        """ops are applied right-to-left, but listed in application order."""
        b=self.bits.copy();valid=np.ones(self.dim,dtype=bool);sign=np.ones(self.dim,dtype=np.int8)
        for p,create in ops:
            occupied=(b>>p)&1
            valid &= (occupied==0) if create else (occupied==1)
            parity=np.bitwise_count((b&((1<<p)-1)).astype(np.uint64))&1
            sign*=1-2*parity.astype(np.int8)
            b^=1<<p
        ind=np.flatnonzero(valid);dest=self.ui[b[ind]&((1<<self.N)-1)]*self.nD+self.di[b[ind]>>self.N]
        assert np.all(dest>=0)
        return sp.coo_matrix((sign[ind].astype(float),(dest,ind)),shape=(self.dim,self.dim)).tocsr()

    def hop(self,bonds):
        H=sp.csr_matrix((self.dim,self.dim))
        for i,j in bonds:
            for off in [0,self.N]:
                A=self.op([(j+off,False),(i+off,True)])
                H+=A+A.T
        return H

    def exchange(self,bonds):
        H=sp.csr_matrix((self.dim,self.dim));diag=np.zeros(self.dim)
        for i,j in bonds:
            diag-=.5*(self.occ[i]*self.occ[self.N+j]+self.occ[self.N+i]*self.occ[j])
            # S_i^+ S_j^- = c_iup^dag c_idn c_jdn^dag c_jup
            A=self.op([(j,False),(j+self.N,True),(i+self.N,False),(i,True)])
            H+=.5*(A+A.T)
        return H+sp.diags(diag,format='csr')

    def pairhop(self,bonds):
        H=sp.csr_matrix((self.dim,self.dim))
        for i,j in bonds:
            # Delta_i^dag Delta_j = c_iup^dag c_idn^dag c_jdn c_jup
            A=self.op([(j,False),(j+self.N,False),(i+self.N,True),(i,True)])
            H+=A+A.T
        return H

    def matrix(self,p):
        co={'K1':-p.get('t',1.),'K2':-p.get('tp',.2),'D':p.get('U',0.),
            'J1':p.get('J1',0.),'J2':p.get('J2',0.),'P':-p.get('P',0.),'V1':p.get('V1',0.)}
        H=sum((v*self.terms[k] for k,v in co.items() if v),sp.csr_matrix((self.dim,self.dim)))
        return H

    def ground(self,p,k=1):
        H=self.matrix(p)
        rng=np.random.default_rng(913+self.nu*100+self.nd)
        vstart=rng.normal(size=self.dim)
        vstart/=np.linalg.norm(vstart)
        if self.v0 is not None:vstart=.98*self.v0+.02*vstart
        ev,vec=eigsh(H,k=k,which='SA',tol=2e-9,maxiter=4000,v0=vstart)
        order=np.argsort(ev);ev=ev[order];vec=vec[:,order];self.v0=vec[:,0]
        v=vec[:,0]
        residual=np.linalg.norm(H@v-ev[0]*v)
        obs={key:float(v@(op@v)) for key,op in self.terms.items()}
        return {'energy':float(ev[0]),'excited_energies':ev[1:].tolist(),'residual':float(residual),
                'dim':self.dim,'observables':obs}

def smoke():
    sec=Sector(2,1,1,[(0,1)],[]);p={'t':1,'tp':0,'U':12}
    val=sec.ground(p)['energy'];exact=(12-np.sqrt(12**2+16))/2
    assert abs(val-exact)<1e-9,(val,exact)
    # Independent direct spin singlet test: t=0, J1=2 -> energy -2.
    assert abs(sec.ground({'t':0,'tp':0,'U':12,'J1':2})['energy']+2)<1e-9
    assert all((v-v.T).nnz==0 for v in sec.terms.values())
    print('Two-site Hubbard and exchange checks pass.',flush=True)

def main():
    smoke();start=time.time()
    sectors={}
    for nu,nd in [(5,5),(6,4),(5,4),(6,5),(3,3),(4,2),(2,2),(3,1),(4,4),(6,6)]:
        tick=time.time();sectors[(nu,nd)]=Sector(10,nu,nd)
        print('Built',nu,nd,sectors[(nu,nd)].dim,'seconds',time.time()-tick,flush=True)
    params=[{'name':'Hubbard_U8','U':8},{'name':'Hubbard_U12','U':12},{'name':'Hubbard_U16','U':16},
            {'name':'extended_J2','U':8,'J1':2,'J2':1},
            {'name':'extended_J4','U':4,'J1':4,'J2':2},
            {'name':'extended_J6','U':0,'J1':6,'J2':3},
            {'name':'extended_pair','U':4,'J1':4,'J2':2,'P':2}]
    outfile='electron_ed_scan.json'
    if len(sys.argv)>1:
        cfg=json.load(open(sys.argv[1]));params=cfg['parameters'];outfile=cfg['output']
    out={'model':'physical one-orbital t-tprime-U-J1-J2-P-V1',
         'cluster':'10-site tilted square torus, vectors(3,1),(-1,3)',
         't':.99706833,'tp':.19534428,'results':[],
         'caution':'Finite-cluster diagnostic. NMR activation is not equated to triplet gap without further response calculation; no phase diagram inferred.'}
    for q in params:
        p={'t':out['t'],'tp':out['tp'],**q};r={}
        for key,sec in sectors.items():
            tick=time.time();r[str(key)]=sec.ground(p)
            print(q['name'],key,r[str(key)]['energy'],'sec',time.time()-tick,flush=True)
        E=lambda a,b:r[str((a,b))]['energy']
        gaps={'half_spin':E(6,4)-E(5,5),'half_charge':E(6,5)+E(5,4)-2*E(5,5),
              'half_mu_mid':(E(6,5)-E(5,4))/2,'nu_.3_spin':E(4,2)-E(3,3),
              'nu_.2_spin':E(3,1)-E(2,2),'half_pair_charge':E(6,6)+E(4,4)-2*E(5,5)}
        out['results'].append({'parameters':p,'gaps':gaps,'sectors':r})
        out['seconds']=time.time()-start
        (ROOT/'data'/outfile).write_text(json.dumps(out,indent=2))
        print('GAPS',q['name'],gaps,flush=True)

if __name__=='__main__':main()
