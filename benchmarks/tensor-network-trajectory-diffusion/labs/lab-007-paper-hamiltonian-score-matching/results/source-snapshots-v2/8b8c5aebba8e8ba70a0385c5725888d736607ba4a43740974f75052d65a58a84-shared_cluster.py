"""Size-independent three-site observations and two-local learned Hamiltonian.

Dense execution is only for short-chain training / parity. MPS evaluation
never constructs global Pauli matrices or a dense state vector.
"""
import itertools
import torch
from torch import nn
import mps_backend as mb

PAULI_WORDS=list(itertools.product(range(4),repeat=3))

def window_basis(n,site,device):
    """Missing physical sites are zero-padded features, except identity."""
    start=max(0,site-1); stop=min(n,site+2)
    ops=[]
    for word in PAULI_WORDS:
        op=torch.ones(1,1,dtype=torch.complex128,device=device)
        for j,axis in enumerate(word):
            pos=site-1+j
            if 0<=pos<n: op=torch.kron(op,mb.PAULI_IXYZ[axis].to(device))
            elif axis: op=op*0
        ops.append(op)
    return start,stop,torch.stack(ops)

def environments(mps):
    b=mps.tensors[0].new_ones(mps.batch,1,1)
    left=[b]; right=[None]*(mps.n_sites+1); right[-1]=b
    for a in mps.tensors:
        left.append(torch.einsum('blm,blsr,bmsd->brd',left[-1],a,a.conj()))
    for i in range(mps.n_sites-1,-1,-1):
        a=mps.tensors[i]
        right[i]=torch.einsum('brd,blsr,bmsd->blm',right[i+1],a,a.conj())
    return left,right

def reduced_density(mps,start,stop,env=None):
    left,right=environments(mps) if env is None else env
    theta=mps.tensors[start]
    for a in mps.tensors[start+1:stop]:
        theta=torch.einsum('b...r,brsd->b...sd',theta,a)
    theta=theta.reshape(mps.batch,theta.shape[1],2**(stop-start),theta.shape[-1])
    rho=torch.einsum('blm,bldr,bmeu,bru->bde',left[start],theta,theta.conj(),right[stop])
    return rho/left[-1][:,0,0].real[:,None,None]

class Windows:
    def __init__(self,n,device):
        self.n=n; self.spec=[window_basis(n,i,device) for i in range(n)]
        self.dense_basis=None
    def mps(self,mps):
        env=environments(mps)
        return torch.stack([torch.einsum('bij,kji->bk',reduced_density(mps,s,e,env),ops).real
                            for s,e,ops in self.spec],1)
    def dense(self,psi):
        if self.dense_basis is None:
            self.dense_basis=torch.stack([mb.embed_operator(ops,s,self.n) for s,e,ops in self.spec])
        return torch.einsum('bi,nkij,bj->bnk',psi.conj(),self.dense_basis,psi).real

class SharedControl(nn.Module):
    def __init__(self,hidden=32):
        super().__init__()
        def net(inp,out):
            return nn.Sequential(nn.Linear(inp,hidden),nn.Tanh(),nn.Linear(hidden,hidden),nn.Tanh(),nn.Linear(hidden,out))
        self.onsite=net(65,3); self.bond=net(129,9)
    def forward(self,z,t):
        b,n,_=z.shape; t=t[:,None,:].expand(b,n,1)
        on=self.onsite(torch.cat((z,t),-1).float()).double()
        bo=self.bond(torch.cat((z[:,:-1],z[:,1:],t[:,:-1]),-1).float()).double()
        return on,bo

@torch.no_grad()
def cluster_mps(n,batch,device,ancilla=False):
    plus=torch.ones(batch,n,2,dtype=torch.complex128,device=device)/2**.5
    state=mb.mps_product(plus)
    cz=torch.diag(torch.tensor([1,1,1,-1],dtype=torch.complex128,device=device)).expand(batch,4,4)
    for i in range(n-1): state=state.apply_bond_gate(i,cz,chi_max=2)
    if ancilla:
        had=(mb.PAULI_XYZ[0]+mb.PAULI_XYZ[2]).to(device).expand(batch,2,2)/2**.5
        state=state.apply_site_gate(0,had).apply_site_gate(n-1,had)
    return state.normalize()

def pad_bonds(state,chi):
    """Embed the same state in larger bonds, with exact zero padding."""
    ts=[]; n=state.n_sites
    for i,a in enumerate(state.tensors):
        l=min(chi,2**min(i,n-i)); r=min(chi,2**min(i+1,n-i-1))
        if l<a.shape[1] or r<a.shape[3]: raise ValueError('padding cannot truncate')
        ts.append(torch.nn.functional.pad(a,(0,r-a.shape[3],0,0,0,l-a.shape[1])))
    return mb.BatchMPS(ts)

@torch.no_grad()
def collect(n,batch,device,seed,steps=300,ancilla=False):
    torch.manual_seed(seed); initial=cluster_mps(n,batch,device,ancilla=ancilla); state=initial; axes=[]; states=[initial]
    for _ in range(steps):
        row=[]
        for i in range(n):
            state,axis,_=mb.sample_onsite_kraus(state,i,1.,.01); row.append(axis)
        state=state.balance(); states.append(state); axes.append(torch.stack(row,1))
    return states,axes

def check_values(state):
    z=Windows(state.n_sites,state.device).mps(state)
    idx={w:i for i,w in enumerate(PAULI_WORDS)}
    return torch.stack([z[:,i,idx[(0 if i==0 else 3,1,0 if i==state.n_sites-1 else 3)]]
                        for i in range(state.n_sites)],1)

def middle_entropy(state):
    # Gauge shifts preserve the state; singular values of the center give Schmidt values.
    mid=state.n_sites//2; s=state.right_canonical()
    for i in range(mid-1): s=s.qr_shift_right(i)
    a=s.tensors[mid-1]; vals=torch.linalg.svdvals(a.reshape(s.batch,a.shape[1]*2,a.shape[3]))
    p=vals.square(); p=p/p.sum(-1,keepdim=True)
    return -(p*p.clamp_min(1e-30).log2()).sum(-1)


def boundary_hadamards(state):
    """Fixed local Clifford map between cluster and ancilla-locked cluster."""
    h=(mb.PAULI_XYZ[0]+mb.PAULI_XYZ[2]).to(state.device).expand(state.batch,2,2)/2**.5
    return state.apply_site_gate(0,h).apply_site_gate(state.n_sites-1,h)


def ancilla_fields(on,bo):
    """H -> (Hadamard on both ends) H (Hadamard on both ends)."""
    on=on.clone(); bo=bo.clone(); sign=on.new_tensor([1.,-1.,1.])
    on[:,0]=on[:,0][:,[2,1,0]]*sign
    on[:,-1]=on[:,-1][:,[2,1,0]]*sign
    b=bo[:,0].reshape(-1,3,3); bo[:,0]=(b[:,[2,1,0],:]*sign[None,:,None]).reshape(-1,9)
    b=bo[:,-1].reshape(-1,3,3); bo[:,-1]=(b[:,:,[2,1,0]]*sign[None,None,:]).reshape(-1,9)
    return on,bo
