"""Independent affine moments, exact curvature and dense ODE checks."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from scipy.integrate import solve_ivp
import random,json,time
from forward_certificate import cost_moments,certificate
LAB=Path(__file__).resolve().parents[1]
def main():
    st=time.perf_counter();rng=random.Random(990071);records=[]
    for trial in range(40):
        n=rng.randrange(2,6);N=n+rng.randrange(0,3);rows=[[j for j in range(n) if rng.random()<.5] for k in range(rng.randrange(0,5))]
        true=[rng.randrange(2) for _ in range(n)];s=[sum(true[j] for j in row)%2 for row in rows];w=[F(rng.randrange(-3,6),4) for _ in range(n)]
        moments=cost_moments(rows,n,s,w);errors=[[((x>>i)&1) for i in range(n)] for x in range(1<<n)]
        feasible=[e for e in errors if all(sum(e[j] for j in row)%2==v for row,v in zip(rows,s))];costs=[sum((w[i]*e[i] for i in range(n)),F(0)) for e in feasible]
        mean=sum(costs,F(0))/len(costs);var=sum(((v-mean)**2 for v in costs),F(0))/len(costs);minimum=min(costs)
        assert mean==F(*moments['mean_exact']) and var==F(*moments['variance_exact']);assert minimum<=F(*moments['minimum_cost_upper_exact'])
        ids=np.arange(1<<N);z=np.array([2*((ids>>i)&1)-1 for i in range(N)])
        h=[F(rng.randrange(-3,4),8) for i in range(N)];J={(i,j):F(rng.randrange(-3,4),8) for i in range(N) for j in range(i+1,N) if rng.random()<.4}
        delta=F(3,4);h1=h[:]
        for i in range(n):h1[i]+=delta*w[i]/2
        def energies(fields):return np.array([float(sum((fields[i]*int(z[i,x]) for i in range(N)),F(0))+sum((v*int(z[i,x])*int(z[j,x]) for (i,j),v in J.items()),F(0))) for x in ids])
        E0=energies(h);E1=energies(h1);best={sum(e[i]<<i for i in range(n)) for e,c in zip(feasible,costs) if c==minimum};mask=np.array([(x&((1<<n)-1)) in best for x in ids]);P0=mask.mean()
        gradient0=sum((E0[ids^(1<<i)]-E0 for i in range(N)));gradient1=sum((E1[ids^(1<<i)]-E1 for i in range(N)))
        c2=float((gradient1[mask]-gradient0[mask]).sum()/(len(ids)*12*P0));pred=float(delta*(sum(w,F(0))-2*minimum)/12);assert abs(c2-pred)<2e-14
        driver=np.zeros((len(ids),len(ids)))
        for i in range(N):driver[ids,ids^(1<<i)]=-1
        psi0=np.ones(len(ids),dtype=complex)/np.sqrt(len(ids))
        def evolve(E,T):
            result=solve_ivp(lambda u,y:-1j*T*((1-u)*(driver@y)+u*E*y),(0.,1.),psi0,method='DOP853',rtol=2e-12,atol=2e-14)
            assert result.success;return float(np.sum(np.abs(result.y[:,-1][mask])**2))
        l0=(N+sum(map(abs,h),F(0))+sum(map(abs,J.values()),F(0)))/2;l1=(N+sum(map(abs,h1),F(0))+sum(map(abs,J.values()),F(0)))/2
        params={'eta_difference':delta,'rounding':F(0),'lambda0':l0,'lambda1':l1,'lambda_max':max(l0,l1)};cert=certificate(moments,params)
        T=.02;p0=evolve(E0,T);p1=evolve(E1,T);R=lambda lam:(2*float(lam)*T)**4/(24*(1-(2*float(lam)*T)**2/30))
        assert abs((p1-p0)/P0-pred*T*T)<=R(l0)+R(l1)+2e-11
        records.append({'n':n,'N':N,'mean':float(mean),'variance':float(var),'curvature_exact':pred,'curvature_direct':c2,'ode_duration':T,'ode_relative_difference':(p1-p0)/P0,'certificate':cert['status']})
    out={'status':'pass','cases':len(records),'exact_affine_moment_checks':len(records),'exact_curvature_checks':len(records),'dense_forward_ode_checks':len(records),'seconds':time.perf_counter()-st,'records':records}
    (LAB/'results/forward_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'}))
if __name__=='__main__':main()
