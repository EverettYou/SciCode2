"""General sparse-H repair/penalty witness. No decoding optimization or code metadata."""
from fractions import Fraction as F
from pathlib import Path
from copy import deepcopy
import importlib.util,math,sys
sys.dont_write_bytecode=True
LAB=Path(__file__).resolve().parents[1];BENCH=LAB.parents[1]

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
compiler=load_module('qec_original_compiler',BENCH/'labs/lab-002-agent-test-general-h/scripts/compiler.py')

def add_vector(v,basis):
    while v:
        p=v.bit_length()-1
        if p in basis:v^=basis[p]
        else:basis[p]=v;return True
    return False

def inverse_columns(matrix_rows,r):
    a=[row | (1<<(r+i)) for i,row in enumerate(matrix_rows)]
    for i in range(r):
        pivot=next(j for j in range(i,r) if (a[j]>>i)&1);a[i],a[pivot]=a[pivot],a[i]
        for j in range(r):
            if j!=i and ((a[j]>>i)&1):a[j]^=a[i]
    assert all((v&((1<<r)-1))==(1<<i) for i,v in enumerate(a))
    rows=[v>>r for v in a]
    return [sum(((rows[i]>>j)&1)<<i for i in range(r)) for j in range(r)]

def xor_selected(v,columns):
    out=0
    while v:
        low=v&-v;out^=columns[low.bit_length()-1];v^=low
    return out

def witness(rows,n,weights):
    rows=compiler.normalize_rows(rows,n);weights=[F(w) for w in weights]
    if len(weights)!=n:raise ValueError('weight dimension mismatch')
    cols=[0]*n
    for i,row in enumerate(rows):
        for j in row:cols[j]|=1<<i
    selected=[];elim={}
    for j in sorted(range(n),key=lambda j:(abs(weights[j]),j)):
        if add_vector(cols[j],elim):selected.append(j)
    r=len(selected);index={j:k for k,j in enumerate(selected)};rowvectors=[]
    for row in rows:rowvectors.append(sum(1<<index[j] for j in row if j in index))
    selected_rows=[];elim={}
    for i,v in enumerate(rowvectors):
        if add_vector(v,elim):selected_rows.append(i)
    assert len(selected_rows)==r
    inverse=inverse_columns([rowvectors[i] for i in selected_rows],r)
    bcols=[cols[j] for j in selected]
    for col in cols:
        restricted=sum(((col>>i)&1)<<k for k,i in enumerate(selected_rows))
        coefficients=xor_selected(restricted,inverse)
        assert xor_selected(coefficients,bcols)==col
    loads=[sum((abs(weights[selected[k]]) for k in range(r) if (v>>k)&1),F(0)) for v in inverse]
    bound=max(loads,default=F(0));basis_total=sum((abs(weights[j]) for j in selected),F(0));global_total=sum(map(abs,weights),F(0))
    assert bound<=basis_total<=global_total
    return {'rank':r,'basis_columns':selected,'basis_rows':selected_rows,'inverse_columns_hex':[hex(v) for v in inverse],
      'repair_columns':[[selected[k] for k in range(r) if (v>>k)&1] for v in inverse],
      'repair_loads_exact':[[x.numerator,x.denominator] for x in loads],
      'repair_bound_exact':[bound.numerator,bound.denominator],'basis_total_exact':[basis_total.numerator,basis_total.denominator],
      'global_total_exact':[global_total.numerator,global_total.denominator],
      'identity_verified':'H[:,B] * inv(H[R,B]) * H[R,:] = H over GF(2)',
      'proof_scope':'For every residual d in image(H), this linear repair increases signed additive cost by at most C*|d|. No syndrome optimum is solved.'}

def compile_with_bound(rows,n,syndrome,weights,repair_witness,mode='repair',slack=1.):
    bound=F(*repair_witness['repair_bound_exact'])
    criterion={'repair':bound,'basis':F(*repair_witness['basis_total_exact']),'global':F(*repair_witness['global_total_exact'])}[mode]
    M=float(criterion+F(slack))
    if not math.isfinite(M) or F(M)<=bound:raise ValueError('cannot represent a finite strict certified penalty')
    original=compiler.compile_instance(rows,n,syndrome,weights)
    model=deepcopy(original);ratio=F(M)/F(original['penalty']);noriginal=model['n_original']
    exact_linear=[F(*v) for v in original['exact_coefficients']['linear']]
    exact_linear=[(F(weights[i])+(a-F(weights[i]))*ratio if i<noriginal else a*ratio) for i,a in enumerate(exact_linear)]
    exact_quad={(i,j):F(num,den)*ratio for i,j,num,den in original['exact_coefficients']['quadratic']}
    exact_offset=F(*original['exact_coefficients']['offset'])*ratio
    model['linear']=list(map(float,exact_linear));model['quadratic']=[[i,j,float(v)] for (i,j),v in sorted(exact_quad.items()) if v]
    model['offset']=float(exact_offset);model['penalty']=M
    if not all(math.isfinite(v) for v in model['linear']+[model['offset']]+[v for i,j,v in model['quadratic']]):raise ValueError('coefficient overflow')
    rho=sum((abs(F(a)-v) for a,v in zip(model['linear'],exact_linear)),F(0))
    rho+=sum((abs(F(float(v))-v) for v in exact_quad.values()),F(0))
    w=[F(v) for v in weights];den=max((v.denominator for v in w),default=1)
    num=math.gcd(*(abs(v.numerator)*(den//v.denominator) for v in w));lattice=F(num,den) if num else None
    margin=F(M)-bound;gap=min(margin,lattice) if lattice else margin
    pair=lambda v:[v.numerator,v.denominator]
    model['exact_coefficients']={'linear':[pair(v) for v in exact_linear],'quadratic':[[i,j,*pair(v)] for (i,j),v in sorted(exact_quad.items()) if v],'offset':pair(exact_offset),
     'interpretation':'Authoritative exact rational coefficients from the inherited XOR polynomial at a repair-certified penalty.'}
    model['numeric_certificate']={'float_ground_states_certified':2*rho<gap,'coefficient_error_l1_exact':pair(rho),'nonoptimal_gap_lower_bound_exact':pair(gap),
      'weight_lattice_step_exact':pair(lattice) if lattice else None,'exact_penalty_margin':pair(margin),'offset_error_exact':pair(abs(F(model['offset'])-exact_offset)),
      'condition':'2 * coefficient_error_l1 < min(cost lattice step, M-C); C from verified general-H repair witness'}
    assert model['numeric_certificate']['float_ground_states_certified']
    model['repair_penalty_certificate']={'mode':mode,'slack':slack,'witness':repair_witness}
    return model
