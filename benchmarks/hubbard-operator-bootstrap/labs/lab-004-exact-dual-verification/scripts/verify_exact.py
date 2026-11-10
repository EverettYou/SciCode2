#!/usr/bin/env python3
"""Certify exported moment-SDP dual data using exact dyadic integer arithmetic.

No solver is invoked. Gram factors K/2**q define PSD matrices exactly. Affine
moment maps must have integer coefficients and physical moments |x_i|<=1.
All residuals, dual constants and final lower-bound numerators are exact.
"""
from __future__ import annotations
import argparse, hashlib, json, os, resource, time
from collections import deque
from decimal import Decimal, localcontext, ROUND_FLOOR
from pathlib import Path
import numpy as np
import scipy.sparse as sp


def dyadic(v, q):
    """Round exact binary64 value to integer grid2**(-q), ties to even."""
    a,b=float(v).as_integer_ratio(); a <<= q
    n,r=divmod(a,b)
    return n + int(2*r>b or (2*r==b and n%2))


def integer_array(x, name):
    x=np.asarray(x)
    if not np.all(np.isfinite(x)) or not np.all(x==np.rint(x)):
        raise ValueError(name+' must contain exact integer coefficients')
    if np.any(x>=2**63) or np.any(x<-(2**63)):
        raise OverflowError(name+' exceeds int64 coefficient range')
    return x.astype(np.int64)


def coefficient_bits(arrays):
    """Minimum common binary denominator for finite stored coefficients."""
    bits=0
    for array in arrays:
        for value in np.asarray(array).ravel():
            if not np.isfinite(value):raise ValueError('Nonfinite affine coefficient')
            numerator,denominator=float(value).as_integer_ratio()
            bits=max(bits,denominator.bit_length()-1)
    return bits


def coefficient_array(x,bits,name):
    values=[]
    for value in np.asarray(x).ravel():
        a,b=float(value).as_integer_ratio();numerator=a<<bits
        if numerator%b:raise ValueError(name+' is not on the exact coefficient grid')
        values.append(numerator//b)
    if any(v>=2**63 or v<-(2**63) for v in values):
        raise OverflowError(name+' exact numerator exceeds int64 range')
    return np.array(values,dtype=np.int64).reshape(np.asarray(x).shape)


def gram_exact(B,q):
    # K is computed from the supplied factor; it is now the exact certificate.
    if B.ndim!=2 or not B.shape[0] or not B.shape[1] or not np.all(np.isfinite(B)):
        raise ValueError('Gram factor must be a nonempty finite matrix')
    if max(abs(float(B.min())),abs(float(B.max())))*2**q>=2**63-1:
        raise OverflowError('Quantized factor exceeds int64 storage range')
    K=np.array([[dyadic(v,q) for v in row] for row in B],dtype=np.int64)
    shift=24; base=1<<shift; hi=K//base;lo=K-hi*base; d=K.shape[1]
    # Bounds prove every int64 inner-product accumulation cannot overflow.
    cap=np.iinfo(np.int64).max
    mh=max(abs(int(hi.min(initial=0))),abs(int(hi.max(initial=0))))
    ml=max(abs(int(lo.min(initial=0))),abs(int(lo.max(initial=0))))
    for x,y in [(mh,mh),(ml,ml),(mh,ml)]:
        if d*x*y>cap:raise OverflowError('Increase splitting strategy; int64 accumulation unsafe')
    HH=hi@hi.T;LL=lo@lo.T;HL=hi@lo.T
    G=HH.astype(object)*(base*base)+(HL.astype(object)+HL.T.astype(object))*base+LL.astype(object)
    # Small independent exact spot checks detect reconstruction/indexing mistakes.
    for i,j in {(0,0),(0,len(K)-1),(len(K)//2,len(K)//2),(len(K)-1,len(K)-1)}:
        check=sum(int(a)*int(b) for a,b in zip(K[i],K[j]))
        if int(G[i,j])!=check:raise AssertionError('Gram reconstruction failed')
    return K,G


def aggregate_sparse_transpose(A,y,out,sign=1,bits=0):
    coeff=coefficient_array(A.data,bits,'affine map')
    for row in range(A.shape[0]):
        z=int(y[row])*sign
        if not z:continue
        for ptr in range(A.indptr[row],A.indptr[row+1]):
            col=A.indices[ptr];out[col]+=int(coeff[ptr])*z


def exact_hubbard_objective(names):
    """Independently reconstruct the exact4x4 Fourier Hamiltonian."""
    index={name:i for i,name in enumerate(names)}; c=np.zeros(len(names),dtype=np.int64)
    # Work with2*c to keep all interaction coefficients integral.
    cos=(1,0,-1,0)
    for a in range(32):
        k=a%16;c[index[f'n_{a}']]=-4*(cos[k%4]+cos[k//4])
    def add(a,b):return (a%4+b%4)%4+4*((a//4+b//4)%4)
    def sub(a,b):return (a%4-b%4)%4+4*((a//4-b//4)%4)
    for k in range(16):
        for p in range(16):
            for q in range(16):
                left=(add(k,q),16+sub(p,q));right=(k,16+p)
                a,b=left;d,e=right
                key=f'Gamma_{a}_{b}_{d}_{e}'
                if key not in index:key=f'Gamma_{d}_{e}_{a}_{b}'
                c[index[key]]+=1
    return c.astype(float)/2


def audit_symmetry_expansion(T,full_names,reduced_names):
    """Check that T spans exactly the signed D4/spin-swap fixed subspace."""
    T=T.tocsr();coeff=integer_array(T.data,'symmetry expansion')
    if T.shape!=(len(full_names),len(reduced_names)) or np.any(np.abs(coeff)!=1):
        raise ValueError('Symmetry expansion dimension/coefficient mismatch')
    if np.any(np.diff(T.indptr)>1):raise ValueError('Each original coordinate must be zero or one signed reduced coordinate')
    index={name:i for i,name in enumerate(full_names)}
    def transform_mode(a,kind):
        spin,k=divmod(a,16);x,y=k%4,k//4
        if kind=='rot':x,y=(-y)%4,x
        elif kind=='rx':x=(-x)%4
        elif kind=='spin':spin=1-spin
        return spin*16+x+4*y
    edges=[[] for _ in full_names]
    for i,name in enumerate(full_names):
        modes=list(map(int,name.split('_')[1:]))
        for kind in ('rot','rx','spin'):
            v=[transform_mode(a,kind) for a in modes];sign=1
            if len(v)==1:key=f'n_{v[0]}'
            else:
                a,b,c,d=v
                if a>b:a,b=b,a;sign=-sign
                if c>d:c,d=d,c;sign=-sign
                key=f'Gamma_{a}_{b}_{c}_{d}'
                if key not in index:key=f'Gamma_{c}_{d}_{a}_{b}'
            j=index[key];edges[i].append((j,sign));edges[j].append((i,sign))
    visited=set();orbits=0;zero_orbits=0;used_cols=set()
    for seed in range(len(full_names)):
        if seed in visited:continue
        signs={seed:1};queue=deque([seed]);zero=False
        while queue:
            i=queue.popleft()
            for j,s in edges[i]:
                expected=s*signs[i]
                if j not in signs:signs[j]=expected;queue.append(j)
                elif signs[j]!=expected:zero=True
        visited.update(signs);orbits+=1
        if zero:
            zero_orbits+=1
            if any(T.indptr[i+1]!=T.indptr[i] for i in signs):raise ValueError('Antisymmetric fixed-point coordinates must vanish')
        else:
            column=None;relative_sign=None
            for i,s in signs.items():
                ptr=T.indptr[i]
                if T.indptr[i+1]-ptr!=1:raise ValueError('Symmetry reduction removed an allowed orbit')
                col=int(T.indices[ptr]);rel=int(coeff[ptr])*s
                if column is None:column=col;relative_sign=rel
                if (col,rel)!=(column,relative_sign):raise ValueError('Incorrect signed symmetry orbit')
            if column in used_cols:raise ValueError('Independent symmetry orbits were conflated')
            used_cols.add(column)
    if used_cols!=set(range(len(reduced_names))):raise ValueError('Unused reduced coordinate')
    for j,name in enumerate(reduced_names):
        i=index[name];ptr=T.indptr[i]
        if T.indptr[i+1]-ptr!=1 or T.indices[ptr]!=j or coeff[ptr]!=1:
            raise ValueError('Reduced coordinate is not the advertised physical moment')
    return dict(full_variables=len(full_names),reduced_variables=len(reduced_names),orbits=orbits,zero_orbits=zero_orbits,passed=True)


def verify(inp,out,q=40):
    inp=Path(inp);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter()
    supplied_c=np.load(inp/'objective.npy')
    names=json.loads((inp/'variable_names.json').read_text())
    symmetry_audit=None
    if (inp/'symmetry_expansion.npz').exists():
        full_names=json.loads((inp/'full_variable_names.json').read_text())
        T=sp.load_npz(inp/'symmetry_expansion.npz').tocsr()
        symmetry_audit=audit_symmetry_expansion(T,full_names,names)
        c=np.asarray(T.T@exact_hubbard_objective(full_names)).ravel()
    else:c=exact_hubbard_objective(names)
    objective_delta=float(np.max(np.abs(c-supplied_c)))
    if objective_delta>1e-12:raise ValueError('Exported objective does not match the specified Hubbard Hamiltonian')
    E=sp.load_npz(inp/'equalities.npz').tocsr();rhs=np.load(inp/'rhs.npy');lam=np.load(inp/'lambda.npy')
    if supplied_c.shape!=c.shape or E.shape!=(len(rhs),len(c)) or lam.shape!=rhs.shape:
        raise ValueError('Objective and equality dimensions disagree')
    if not np.all(np.isfinite(lam)):
        raise ValueError('Equality multiplier is not finite')
    blocks=json.loads((inp/'blocks.json').read_text())
    cbits=coefficient_bits([rhs,E.data])
    for block in blocks:
        prefix=block['prefix'];data=np.load(inp/(prefix+'.npz'));A=sp.load_npz(inp/(prefix+'_A.npz'))
        cbits=max(cbits,coefficient_bits([data['b'],A.data]))
    scale=1<<(2*q+cbits)
    # Objective data must be exact on the dyadic grid, avoiding arbitrary changes.
    residual=np.array([dyadic(v,2*q+cbits) for v in c],dtype=object)
    if any(int(z)/scale!=float(v) for z,v in zip(residual,c)):
        raise ValueError('Objective is not exactly representable on certificate grid')
    lnum=np.array([dyadic(v,2*q) for v in lam],dtype=object)
    aggregate_sparse_transpose(E,lnum,residual,bits=cbits)
    enum=coefficient_array(rhs,cbits,'equality RHS')
    const=-sum(int(e)*int(l) for e,l in zip(enum,lnum))
    hashes={};maxdim=0;total_entries=0
    for block in blocks:
        prefix=block['prefix'];data=np.load(inp/(prefix+'.npz'));A=sp.load_npz(inp/(prefix+'_A.npz')).tocsr();b=coefficient_array(data['b'],cbits,'block constant')
        d=block['dim']
        if A.shape!=(d*d,len(c)) or b.shape!=(d*d,) or data['factor'].shape[0]!=d:
            raise ValueError('Block dimension mismatch: '+prefix)
        K,G=gram_exact(data['factor'],q);g=G.ravel()
        aggregate_sparse_transpose(A,g,residual,sign=-1,bits=cbits)
        const-=sum(int(a)*int(z) for a,z in zip(b,g))
        np.save(out/(prefix+'_factor_int.npy'),K)
        maxdim=max(maxdim,len(K));total_entries+=K.size
        hashes[prefix]=hashlib.sha256(K.tobytes()).hexdigest()
    correction=sum(abs(int(v)) for v in residual);num=const-correction
    with localcontext() as ctx:
        ctx.prec=70;ctx.rounding=ROUND_FLOOR
        value=Decimal(num)/Decimal(scale);per_site=value/16
        # Public bound is rounded downward to12decimal places, independently of float conversion.
        reported=value.quantize(Decimal('0.000000000001'),rounding=ROUND_FLOOR)
    (out/'residual_numerators.json').write_text(json.dumps([str(int(v)) for v in residual]))
    (out/'lambda_numerators.json').write_text(json.dumps([str(int(v)) for v in lnum]))
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if os.uname().sysname!='Darwin':rss*=1024
    result={'source_directory':str(inp.resolve()),'certificate_type':'exact dyadic Gram SOS with exact coefficient residual correction','factor_fractional_bits':q,'denominator':str(scale),'dual_constant_numerator':str(const),'residual_l1_numerator':str(correction),'lower_bound_numerator':str(num),'lower_bound_exact_decimal':str(value),'reported_total_energy_lower_bound':str(reported),'per_site_lower_bound_decimal':str(per_site),'residual_l1_float':correction/scale,'dual_constant_float':const/scale,'independent_hubbard_objective_max_difference':objective_delta,'nvar':len(c),'nblocks':len(blocks),'max_psd_dim':maxdim,'factor_entries':total_entries,'validation_seconds':time.perf_counter()-start,'peak_rss_bytes':rss,'factor_sha256':hashes,'assumptions':['All affine maps/equality coefficients/RHS are exact integers.','The objective is independently reconstructed from the exact4x4 Hubbard Fourier coefficients.','Each coordinate is a real occupation or pair-RDM moment with absolute value<=1, proved using n/hole,P,G positivity.','Equalities are valid on the fixed-spin sector; block maps follow exact CAR and momentum conservation.']}
    result['symmetry_expansion_audit']=symmetry_audit
    result['affine_coefficient_fractional_bits']=cbits
    result['equality_multiplier_denominator']=str(1<<(2*q))
    result['assumptions'][0]='All stored affine coefficients and RHS are treated as exact dyadic numbers; physical-map audits separately justify those coefficients.'
    (out/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['factor_sha256','assumptions']},indent=2),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);p.add_argument('--bits',type=int,default=40);a=p.parse_args();verify(a.input,a.output,a.bits)
