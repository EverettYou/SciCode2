"""Independent ODE validation of local-observable bounds, frozen three-time menu."""
from pathlib import Path
from fractions import Fraction as F
import json,time,sys
sys.dont_write_bytecode=True
import numpy as np
from scipy.integrate import solve_ivp
from local_forward import local_data,remainder,certificate
LAB=Path(__file__).resolve().parents[1]
def main():
 start=time.perf_counter();records=[]
 for path in sorted((LAB/'results/forward_anchors').glob('*_n6_s9611.json')):
  d=json.loads(path.read_text());w=d['input']['weights'];means={}
  for label in ['baseline','amplified']:
   p=d[label+'_program'];nodes=sorted(q for q,v in p['h']);idx={q:i for i,q in enumerate(nodes)};N=len(nodes);ids=np.arange(1<<N);spins={q:2*((ids>>idx[q])&1)-1 for q in nodes};diag=sum(v*spins[q] for q,v in p['h'])+sum(v*spins[q]*spins[r] for q,r,v in p['J']);diag-=diag.mean();flips=[ids^(1<<q) for q in range(N)];roots={int(i):q for i,q in p['roots'].items()};cost=sum(wi*(spins[roots[i]]+1)/2 for i,wi in enumerate(w));coeff=local_data(p,w)
   for T in [F(1,80),F(1,40),F(1,20)]:
    def rhs(u,psi):return -1j*float(T)*(u*diag*psi-(1-u)*sum(psi[f] for f in flips))
    sol=solve_ivp(rhs,(0,1),np.ones(len(ids),complex)/np.sqrt(len(ids)),method='DOP853',rtol=2e-11,atol=2e-13);assert sol.success;probs=abs(sol.y[:,-1])**2;actual=float(probs@cost);pred=sum(w)/2+float(coeff['c2']*T*T+coeff['c4']*T**4);R=remainder(1,(1+coeff['gE'])*T);bound=float(coeff['weight_l1']*R/2);error=abs(actual-pred);assert error<=bound+5e-11
    means[label,float(T)]=actual;records.append({'name':d['name'],'label':label,'T':float(T),'N':N,'actual_mean_cost':actual,'fourth_order_mean_cost':pred,'observed_error':error,'rigorous_remainder':bound,'norm_error':abs(float(probs.sum())-1)})
  cert=certificate(d['baseline_program'],d['amplified_program'],w)
  for row in cert['menu']:
   if row['T'] not in [.0125,.025,.05] or 'cost_improvement_lower' not in row:continue
   observed=means['baseline',row['T']]-means['amplified',row['T']];assert observed>=row['cost_improvement_lower']-1e-10
 out={'status':'pass','records':records,'cases':len(records),'seconds':time.perf_counter()-start,'maximum_norm_error':max(r['norm_error'] for r in records),'maximum_observed_error_to_bound_ratio':max(r['observed_error']/r['rigorous_remainder'] for r in records)};(LAB/'results/local_forward_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'}))
if __name__=='__main__':main()
