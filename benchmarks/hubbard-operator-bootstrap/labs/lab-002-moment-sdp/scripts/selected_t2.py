"""Affordable T2' from creation times opposite-spin site density.

For fixed spin sigma and total momentum k select
 A_q = sum_p c†_(k+q,sigma) c†_(p-q,other) c_(p,other), q != 0.
These span Fourier transforms of c†_(i,sigma)n_(j,other), with their
q=0 part removed because A_0=N_other c†_k in the physical sector.
The augmented positivity block is
 [[ <A_i† A_j + A_j A_i†>, 4<A_i† c†_k> ],
  [ 4<c_k A_j>,             16< c_k c†_k> ]].
It is the sum of Gram(A_i,4c†_k) and conjugate Gram(A_i†,0), hence PSD.
Degree-six terms in its upper-left block cancel by CAR.
"""
import itertools, json, time
from pathlib import Path
from momentum_pqg import adjoint

def addto(out,p,scale=1):
    for z,v in p.items():out[z]=out.get(z,0)+scale*v

def triple_t2(model,t,u):
    """Exact {A_t†,A_u} moment for A_(a,b,c)=a†_a a†_b a_c."""
    a,b,c=t;d,e,f=u;out={}
    # Double and single CAR contractions; sextic terms cancel identically.
    val=int(a==d)*int(b==e)-int(a==e)*int(b==d)
    if c==f and val:out[c]=val
    if a==d:addto(out,model.gamma(c,e,f,b),-1)
    if b==d:addto(out,model.gamma(c,e,f,a),1)
    if a==e:addto(out,model.gamma(c,d,f,b),1)
    if b==e:addto(out,model.gamma(c,d,f,a),-1)
    if f==c:addto(out,model.gamma(d,e,a,b),1)
    return {z:v for z,v in out.items() if v}

def add_selected_t2(model,descriptors_path=None,all_two_site=False):
    desc=[];start=time.perf_counter()
    for spin,k in itertools.product(range(2),range(model.V)):
        opposite=1-spin
        ops=[];labels=[]
        for q in range(1,model.V):
            triples=[(spin*model.V+model.add(k,q),opposite*model.V+model.sub(p,q),opposite*model.V+p) for p in range(model.V)]
            ops.append(triples);labels.append(('opposite_density',q))
        if all_two_site:
            for q in range(1,model.V):
                triples=[(spin*model.V+model.add(k,q),spin*model.V+model.sub(p,q),spin*model.V+p) for p in range(model.V)]
                ops.append(triples);labels.append(('same_density',q))
            # The p=0 members follow from the sum of the density family plus
            # N_other*c†_k. Keeping p=1..V-1 removes those exact dependencies.
            for p in range(1,model.V):
                triples=[(spin*model.V+q,opposite*model.V+model.sub(model.add(k,p),q),opposite*model.V+p) for q in range(model.V)]
                ops.append(triples);labels.append(('doublon_pair',p))
            for p in range(1,model.V):
                triples=[(spin*model.V+q,opposite*model.V+p,opposite*model.V+model.sub(model.add(q,p),k)) for q in range(model.V)]
                ops.append(triples);labels.append(('spin_exchange',p))
        dim=len(ops)+1;entries=[]
        for i,ts in enumerate(ops):
            for j in range(i,len(ops)):
                out={}
                for t,u in itertools.product(ts,ops[j]):addto(out,triple_t2(model,t,u))
                out={z:v for z,v in out.items() if v}
                entries.append((i,j,out))
                if j!=i:entries.append((j,i,out))
            out={}
            for a,b,c in ts:
                word=((1,c),(0,b),(0,a),(1,spin*model.V+k))
                addto(out,model.poly(word),4)
            entries.append((i,dim-1,out));entries.append((dim-1,i,out))
        entries.append((dim-1,dim-1,{-1:16,spin*model.V+k:-16}))
        name=f'T2prime_{"two_site" if all_two_site else "density"}_spin{spin}_k{k}'
        model.block(name,entries,dim)
        desc.append({'name':name,'form':'T2prime','operators':[{'family':label[0],'relative_momentum':label[1],'terms':[{'coefficient':1,'word':[[1,a],[1,b],[0,c]]} for a,b,c in ts]} for label,ts in zip(labels,ops)],'augmented_operator':{'coefficient':4,'word':[[1,spin*model.V+k]]}})
        print(f'T2prime built spin={spin} k={k} elapsed={time.perf_counter()-start:.2f}s',flush=True)
    if descriptors_path:Path(descriptors_path).write_text(json.dumps(desc,indent=2))
    return desc

def add_extreme_t2(model):
    """Two-site spin-3/2 cubic family, completing the missing spin sectors."""
    desc=[]
    for spin,k in itertools.product(range(2),range(model.V)):
        ops=[]
        for q in range(1,model.V):
            ops.append([(spin*model.V+model.add(k,q),spin*model.V+model.sub(p,q),(1-spin)*model.V+p) for p in range(model.V)])
        entries=[];dim=len(ops)
        for i,ts in enumerate(ops):
            for j in range(i,dim):
                out={}
                for t,u in itertools.product(ts,ops[j]):addto(out,triple_t2(model,t,u))
                out={z:v for z,v in out.items() if v}
                entries.append((i,j,out))
                if i!=j:entries.append((j,i,out))
        name=f'T2pure_extreme_spin{spin}_k{k}'
        model.block(name,entries,dim)
        desc.append({'name':name,'form':'T2pure','operators':[{'family':'spin_three_halves','relative_momentum':q,'terms':[{'coefficient':1,'word':[[1,a],[1,b],[0,c]]} for a,b,c in ts]} for q,ts in zip(range(1,model.V),ops)]})
    return desc

def test_formula():
    from momentum_pqg import Model,normal_order,adjoint
    m=Model();rng=__import__('numpy').random.default_rng(22)
    for unused in range(1000):
        t=tuple(rng.integers(0,32,3));u=tuple(rng.integers(0,32,3))
        at=tuple([(1,t[0]),(1,t[1]),(0,t[2])]);au=tuple([(1,u[0]),(1,u[1]),(0,u[2])])
        p={}
        for word in (adjoint(at)+au,au+adjoint(at)):
            for mon,coeff in normal_order(word).items():p[mon]=p.get(mon,0)+coeff
        p={mon:coeff for mon,coeff in p.items() if coeff}
        expected=m.normal_poly_to_affine(p)
        actual=triple_t2(m,t,u)
        assert actual==expected,(t,u,actual,expected)
    print('T2 CAR formula: 1000 random comparisons passed')

if __name__=='__main__':test_formula()
