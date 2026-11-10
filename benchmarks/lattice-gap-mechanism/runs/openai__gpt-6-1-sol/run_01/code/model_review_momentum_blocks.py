"""Physical single-orbital momentum-pair interaction: exact 16-state screen.

This is a candidate-screening calculation, not an inferred microscopic model.
Physical orbitals: k up, k down, -k up, -k down. The interactions are highly
nonlocal in real space. The reduced BCS term is treated by its linearized
thermodynamic mean-field instability; it is not a local-model BKT calculation.
"""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parents[1]

def annihilator(a):
    C=np.zeros((16,16))
    for state in range(16):
        if (state>>a)&1:
            C[state^(1<<a),state]=(-1)**((state&((1<<a)-1)).bit_count())
    return C

C=[annihilator(i) for i in range(4)]
num=[c.T@c for c in C]
N=sum(num);n0=num[0]+num[1];n1=num[2]+num[3];nn=n0@n1
D=num[0]@num[1]+num[2]@num[3]
sz0=(num[0]-num[1])/2;sz1=(num[2]-num[3])/2
sp0=C[0].T@C[1];sp1=C[2].T@C[3]
Sdot=sz0@sz1+.5*(sp0@sp1.T+sp0.T@sp1)
B=C[3]@C[0]-C[2]@C[1]
Y=B+B.T

class Blocks:
    def __init__(self,U=3.69,J=5.54,v=-.5,V0=0.,L=100,t=1.,tp=.2):
        # Tiny generic diagonal conserved-quantity perturbation chooses a common
        # eigenbasis within accidental degeneracies without changing true energies.
        Hconst=U*D+V0*nn+J*Sdot
        _,Q=np.linalg.eigh(Hconst+1e-7*N+1e-8*nn+1e-9*(sz0+sz1))
        self.base=np.diag(Q.T@Hconst@Q)
        self.count=np.diag(Q.T@N@Q)
        self.slope=np.diag(Q.T@(N+v*nn)@Q)
        self.yy=(Q.T@Y@Q)**2
        self.c=(Q.T@C[0]@Q)**2
        k=2*np.pi*(np.arange(L)+.5)/L
        self.eps=(-2*t*(np.cos(k)[:,None]+np.cos(k)[None,:])-4*tp*np.cos(k)[:,None]*np.cos(k)[None,:]).ravel()
        self.e0=self.eps[:,None]*self.slope+self.base
        assert np.max(np.abs(Q.T@Hconst@Q-np.diag(self.base)))<1e-6
        assert np.max(np.abs(Q.T@(N+v*nn)@Q-np.diag(self.slope)))<1e-6
        self.edges=np.argwhere(self.yy>1e-10)

    def probabilities(self,mu,T):
        e=self.e0-mu*self.count
        q=np.exp(-(e-e.min(axis=1)[:,None])/T)
        return e,q/q.sum(axis=1)[:,None]

    def filling(self,mu,T):
        return float(np.mean(self.probabilities(mu,T)[1]@self.count)/4)

    def screen(self,nu,T):
        mu=brentq(lambda m:self.filling(m,T)-nu,-40,40)
        e,p=self.probabilities(mu,T)
        chi=np.zeros(len(self.eps))
        for a,b in self.edges:
            de=e[:,b]-e[:,a];dp=p[:,a]-p[:,b]
            ratio=np.divide(dp,de,out=np.zeros_like(dp),where=np.abs(de)>1e-9)
            deg=np.abs(de)<=1e-9
            ratio[deg]=p[deg,a]/T
            chi+=self.yy[a,b]*ratio
        # Delta=g<B_total>/Nsites; B_total has one B per (k,-k) block.
        # d<B>/dDelta=chi_YY/2, and Nblocks/Nsites=1/2.
        gc=4/np.mean(chi)
        return {'nu':nu,'T':T,'mu':float(mu),'g_required_for_linear_instability':float(gc),
                'pair_susceptibility_YY_per_block':float(np.mean(chi))}


def free_energy_scan(V0,nu=.2,T=1.075,L=24):
    """Check for first-order pairing missed by a linear instability.

    g is taken as large as normal-state stability at nu=.3,T=.4 allows.
    This is a numerical Delta-grid screen, not a proof of global convexity.
    """
    model=Blocks(V0=V0,L=80)
    g=model.screen(.3,.4)['g_required_for_linear_instability']
    k=2*np.pi*(np.arange(L)+.5)/L
    eps=(-2*(np.cos(k)[:,None]+np.cos(k)[None,:])-.8*np.cos(k)[:,None]*np.cos(k)[None,:]).ravel()
    H=eps[:,None,None]*(N-.5*nn)+3.69*D+V0*nn+5.54*Sdot
    Ndiag=np.diag(N)
    def compute(mu,Delta,energy=False):
        E,Q=np.linalg.eigh(H-mu*N-Delta*Y)
        e0=E.min(axis=1)
        q=np.exp(-(E-e0[:,None])/T)
        Z=q.sum(axis=1);p=q/Z[:,None]
        ne=np.einsum('r,krj,krj->kj',Ndiag,Q,Q)
        fill=float(np.mean(np.sum(p*ne,axis=1))/4)
        if not energy:return fill
        F=Delta*Delta/g+.5*np.mean(e0-T*np.log(Z))+mu*(2*nu)
        return float(F)
    ds=np.linspace(0,g,17)
    Fs=[];mus=[]
    for delta in ds:
        mu=brentq(lambda m:compute(m,delta)-nu,-40,40,xtol=2e-8)
        Fs.append(compute(mu,delta,True));mus.append(mu)
    df=np.array(Fs)-Fs[0]
    return {'V0':V0,'nu':nu,'T':T,'grid':[L,L],
            'g_ceiling_from_nu0p3_normal_stability_at_T0p4':float(g),
            'Delta_grid':ds.tolist(),'F_minus_F_normal':df.tolist(),
            'minimum_on_grid_Delta':float(ds[np.argmin(df)]),
            'chemical_potentials':mus}

def main():
    rows=[]
    for V0 in np.linspace(-4,4,17):
        obj=Blocks(V0=float(V0),L=80)
        a=obj.screen(.3,.3625);b=obj.screen(.2,1.1125)
        rows.append({'V0':float(V0),'at_nu0p3':a,'at_nu0p2':b,
                     'g_ratio_nu0p3_over_nu0p2':a['g_required_for_linear_instability']/b['g_required_for_linear_instability']})
    out={'status':'candidate screen, not fit; one physical orbital/site with nonlocal interactions',
         'Hamiltonian_block':'epsilon*N+U*(Dk+Dminus)+(V0+v*epsilon)*nk*nminus+J*Sk.Sminus',
         'pair_interaction':'-g/Nsites Btotal^dagger Btotal; Bblock=c_-down c_kup-c_-up c_kdown',
         'fixed_parameters':{'t':1.,'tprime':.2,'U':3.69,'J':5.54,'v':-.5},
         'momentum_grid':[80,80],'exact_block_dimension':16,'rows':rows,
         'free_energy_screens':[free_energy_scan(v0) for v0 in [0.,2.,4.]],
         'caveats':['No NMR or resistivity fit has been performed.',
                    'Linear instability need not locate first-order transition.',
                    'No local BKT interpretation; real-space interactions are infinite range.',
                    'J was provisionally equated to NMR activation only to screen this hypothesis.']}
    (ROOT/'data'/'model_review_momentum_blocks.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
