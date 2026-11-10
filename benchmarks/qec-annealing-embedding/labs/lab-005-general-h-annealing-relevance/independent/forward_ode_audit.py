"""Independent adaptive ODE validation, including declared-root readout moments."""
from pathlib import Path
import json,time,sys
sys.dont_write_bytecode=True
import numpy as np
from scipy.integrate import solve_ivp
from forward_moments import evaluate_moments
LAB=Path(__file__).resolve().parents[1]
def main():
 start=time.perf_counter();records=[]
 for path in sorted((LAB/'results/forward_anchors').glob('*_n6_s9611.json')):
  d=json.loads(path.read_text());data=d['input'];n=data['n']
  for label in ['baseline','amplified']:
   p=d[label+'_program'];nodes=sorted(q for q,v in p['h']);idx={q:i for i,q in enumerate(nodes)};N=len(nodes);states=np.arange(1<<N);spins={q:2*((states>>idx[q])&1)-1 for q in nodes}
   diag=sum(v*spins[q] for q,v in p['h'])+sum(v*spins[q]*spins[r] for q,r,v in p['J']);diag=diag-diag.mean();flips=[states^(1<<q) for q in range(N)]
   roots={int(i):q for i,q in p['roots'].items()};bits=np.array([((states>>idx[roots[i]])&1) for i in range(n)]).T;cost=bits@data['weights'];feasible=np.ones(len(states),dtype=bool)
   for row,s in zip(data['rows'],data['syndrome']):feasible&=(bits[:,row].sum(axis=1)%2==s)
   optimum=np.isin(sum(bits[:,i]<<i for i in range(n)),d['reference']['optimal_patterns']);coeff=evaluate_moments(data,p)
   for T in [.05,.25,1.,4.,16.]:
    st=time.perf_counter()
    def rhs(u,psi):return -1j*T*(u*diag*psi-(1-u)*sum(psi[flip] for flip in flips))
    sol=solve_ivp(rhs,(0,1),np.ones(len(states),dtype=complex)/np.sqrt(len(states)),method='DOP853',rtol=2e-9,atol=2e-11)
    assert sol.success;prob=abs(sol.y[:,-1])**2;f=float(prob[feasible].sum());c=float(prob[feasible]@cost[feasible]/f);opt=float(prob[optimum].sum());cpp=d['dynamics'][str(T)][label]['final']['original_optimal']
    row={'name':d['name'],'program':label,'T':T,'N':N,'nfev':sol.nfev,'seconds':time.perf_counter()-st,'norm_error':abs(float(prob.sum())-1),'original_optimum':opt,'cpp_original_optimum':cpp,'independent_probability_difference':abs(opt-cpp),'feasibility':f,'conditional_cost':c,
       'feasibility_T2':coeff['feasible_probability_at_zero']*(1+coeff['feasibility_relative_T2']*T*T),'feasibility_T4':coeff['feasible_probability_at_zero']*(1+coeff['feasibility_relative_T2']*T*T+coeff['feasibility_relative_T4']*T**4),
       'conditional_cost_T2':coeff['uniform_feasible_cost']+coeff['conditional_cost_T2']*T*T,'conditional_cost_T4':coeff['uniform_feasible_cost']+coeff['conditional_cost_T2']*T*T+coeff['conditional_cost_T4']*T**4}
    records.append(row);(LAB/'results/forward_ode_audit_progress.json').write_text(json.dumps({'finished':len(records),'total':40,'seconds':time.perf_counter()-start})+'\n')
   print(json.dumps({'name':d['name'],'program':label,'completed':len(records)}),flush=True)
 out={'status':'pass' if max(r['independent_probability_difference'] for r in records)<5e-5 else 'discrepancy','records':records,'seconds':time.perf_counter()-start,'maximum_probability_difference':max(r['independent_probability_difference'] for r in records),'maximum_norm_error':max(r['norm_error'] for r in records)}
 (LAB/'results/forward_ode_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'}))
if __name__=='__main__':main()
