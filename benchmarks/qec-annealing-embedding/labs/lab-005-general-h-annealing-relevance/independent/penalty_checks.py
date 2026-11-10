"""Independent algebra/repair and full-QUBO enumeration checks for the parent branch."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
import numpy as np
import json,time,random
from penalty_bound import witness,compile_with_bound
LAB=Path(__file__).resolve().parents[1]

def rank(rows,n):
    a=np.zeros((len(rows),n),dtype=np.uint8)
    for i,row in enumerate(rows):
        for j in row:a[i,j]^=1
    k=0
    for j in range(n):
        candidates=np.flatnonzero(a[k:,j])
        if not len(candidates):continue
        p=k+int(candidates[0]);a[[k,p]]=a[[p,k]]
        for i in range(len(a)):
            if i!=k and a[i,j]:a[i]^=a[k]
        k+=1
        if k==len(a):break
    return k

def parity(rows,e):return [sum(e[j] for j in row)%2 for row in rows]
def main():
    start=time.perf_counter();rng=random.Random(91807);cases=[];errors=0;full=0;minbasis=0
    for q in range(120):
        n=q%9;m=rng.randrange(0,7);rows=[[j for j in range(n) if rng.random()<.4] for i in range(m)]
        if q%3==0 and rows:rows.append(rows[0][:])
        w=[rng.randrange(-4,7)/4 for j in range(n)];eplant=[rng.randrange(2) for j in range(n)];s=parity(rows,eplant)
        cert=witness(rows,n,w);r=cert['rank'];C=F(*cert['repair_bound_exact']);assert rank(rows,n)==r
        if q<40:
            costs=[]
            for columns in combinations(range(n),r):
                subrows=[[k for k,j in enumerate(columns) if j in row] for row in rows]
                if rank(subrows,r)==r:costs.append(sum(F(abs(w[j])) for j in columns))
            assert F(*cert['basis_total_exact'])==min(costs,default=F(0));minbasis+=1
        feasible_costs=[]
        for state in range(1<<n):
            e=[(state>>j)&1 for j in range(n)];d=[a^b for a,b in zip(parity(rows,e),s)];fixed=e[:]
            for k,rowindex in enumerate(cert['basis_rows']):
                if d[rowindex]:
                    for j in cert['repair_columns'][k]:fixed[j]^=1
            assert parity(rows,fixed)==s
            change=sum(F(w[j])*(fixed[j]-e[j]) for j in range(n));assert change<=C*sum(d)
            errors+=1
            if not any(d):feasible_costs.append(sum(F(w[j])*e[j] for j in range(n)))
        opt=min(feasible_costs);degen=sum(v==opt for v in feasible_costs)
        model=compile_with_bound(rows,n,s,w,cert);L=len(model['linear'])
        if L<=18:
            states=np.arange(1<<L,dtype=np.uint64);bits=((states[:,None]>>np.arange(L,dtype=np.uint64))&1).astype(np.int64)
            def exact4(x):
                v=F(x)*4;assert v.denominator==1;return int(v)
            energies=np.full(len(states),exact4(model['offset']),dtype=np.int64)
            for i,v in enumerate(model['linear']):energies+=exact4(v)*bits[:,i]
            for i,j,v in model['quadratic']:energies+=exact4(v)*bits[:,i]*bits[:,j]
            g=energies==energies.min();assert F(int(energies.min()),4)==opt
            for e in bits[g,:n]:assert parity(rows,e)==s
            assert int(g.sum())==degen;full+=1
        cases.append({'n':n,'m':len(rows),'rank':r,'repair_bound':float(C),'global_bound':float(F(*cert['global_total_exact'])),'logical_variables':L,'full_qubo_enumerated':L<=18})
    result={'status':'pass','cases':len(cases),'repair_errors_checked':errors,'full_qubo_cases':full,'minimum_weight_column_basis_bruteforce_cases':minbasis,'seconds':time.perf_counter()-start,'records':cases}
    (LAB/'results/penalty_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='records'}))
if __name__=='__main__':main()
