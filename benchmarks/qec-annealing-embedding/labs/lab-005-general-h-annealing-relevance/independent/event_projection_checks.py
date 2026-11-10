"""Independent full-state exact Dyson validation of projected event inequalities."""
from fractions import Fraction as F
from pathlib import Path
import random,json,time,sys
sys.dont_write_bytecode=True
import numpy as np
from scipy.integrate import solve_ivp
from event_fourth import projected_fourth,tail_after_fourth,schedule_coefficients
from certified_mapping import second_bound,difference,local_strength
from forward_certificate import cost_moments
from penalty_bound import witness
LAB=Path(__file__).resolve().parents[1]
def dyson(p):
 h={q:F(v) for q,v in p['h']};J={(q,r):F(v) for q,r,v in p['J']};N=len(h);S=1<<N
 E=[sum((v*(1 if (x>>q)&1 else -1) for q,v in h.items()),F(0))+sum((v*(1 if ((x>>q)^(x>>r))&1==0 else -1) for (q,r),v in J.items()),F(0)) for x in range(S)]
 previous=[[F(1)] for x in range(S)];final=[[F(1)] for x in range(S)]
 for k in range(1,5):
  current=[[F(0)]*(2*k+1) for x in range(S)]
  for x in range(S):
   for j in range(len(previous[x])):
    d=-sum((previous[x^(1<<q)][j] for q in range(N)),F(0));current[x][j+1]+=d/F(j+1);current[x][j+2]+=(E[x]*previous[x][j]-d)/F(j+2)
  for x in range(S):final[x].append(sum(current[x],F(0)))
  previous=current
 return [v[1]**2-2*v[2] for v in final],[2*v[4]-2*v[1]*v[3]+v[2]**2 for v in final],E

def main():
 start=time.perf_counter();rng=random.Random(8813701);records=[];totalstates=0;projections=0;odechecks=0
 for trial in range(24):
  n=3+trial%2;rows=[sorted(rng.sample(range(n),rng.randrange(1,n+1))) for _ in range(2)];rows.append(rows[0].copy())
  truth=[rng.randrange(2) for _ in range(n)];syndrome=[sum(truth[i] for i in row)%2 for row in rows];weights=[rng.randrange(-3,5)/4 for i in range(n)]
  if trial%6==0:weights=[0.]*n
  inp={'n':n,'rows':rows,'syndrome':syndrome,'weights':weights};mom=cost_moments(rows,n,syndrome,weights);wit=witness(rows,n,weights);free=[i for i in range(n) if i not in wit['basis_columns']];feasible=[e for e in range(1<<n) if all(sum((e>>i)&1 for i in row)%2==s for row,s in zip(rows,syndrome))];cost={e:sum(F(weights[i])*((e>>i)&1) for i in range(n)) for e in feasible};opt=[e for e in feasible if cost[e]==min(cost.values())];programs=[];orders=[];actual=[];probabilities=[]
  def evalchar(poly,e):
   y=sum(((e>>i)&1)<<j for j,i in enumerate(free));return sum((v*(-1 if (k&y).bit_count()%2 else 1) for k,v in poly.items()),F(0))
  for label in [0,1]:
   N=n+1+(trial+label)%3;roots=rng.sample(range(N),n);p={'h':[[q,rng.randrange(-3,4)/4] for q in range(N)],'J':[[q,r,rng.randrange(-3,4)/4] for q in range(N) for r in range(q+1,N) if rng.random()<.5],'roots':{str(i):q for i,q in enumerate(roots)}}
   p2,p4,E=dyson(p);totalstates+=1<<N;project=projected_fourth(inp,p,mom,orders=True);scored={};success=[]
   for x in range(1<<N):success.append(sum(((x>>q)&1)<<i for i,q in enumerate(roots)) in opt)
   for e in feasible:
    states=[x for x in range(1<<N) if all(((x>>q)&1)==((e>>i)&1) for i,q in enumerate(roots))];a=sum((p2[x] for x in states),F(0))/len(states);b=sum((p4[x] for x in states),F(0))/len(states);assert evalchar(project[0],e)==a;assert evalchar(project[1],e)==b;scored[e]=(a,b);projections+=2
   ids=np.arange(1<<N);flips=[ids^(1<<q) for q in range(N)];diag=np.array(list(map(float,E)));T=F(1,32)
   def rhs(u,psi):return -1j*float(T)*(u*diag*psi-(1-u)*sum(psi[f] for f in flips))
   sol=solve_ivp(rhs,(0,1),np.ones(1<<N,complex)/np.sqrt(1<<N),method='DOP853',rtol=2e-12,atol=2e-14);assert sol.success;probabilities.append(float((abs(sol.y[:,-1])**2)[success].sum()));programs.append(p);orders.append(project);actual.append(scored)
  delta2=difference(orders[0][0],orders[1][0]);delta4=difference(orders[0][1],orders[1][1]);L2,lam,count=second_bound(delta2,inp,mom);L4=delta4.get(0,F(0))-sum((abs(v) for k,v in delta4.items() if k),F(0))
  assert all(L2<=actual[1][e][0]-actual[0][e][0] for e in opt);assert all(L4<=actual[1][e][1]-actual[0][e][1] for e in feasible)
  C=schedule_coefficients(n);r0=tail_after_fourth(n,local_strength(programs[0]),T,C);r1=tail_after_fourth(n,local_strength(programs[1]),T,C);lower=L2*T*T+L4*T**4-r0-r1;p0=F(len(opt),1<<n);observed=(probabilities[1]-probabilities[0])/float(p0);assert observed>=float(lower)-1e-10;odechecks+=1
  records.append({'trial':trial,'n':n,'physical_sizes':[len(p['h']) for p in programs],'feasible_patterns':len(feasible),'optimal_patterns':len(opt),'L2':float(L2),'L4':float(L4),'lambda':float(lam),'observed_relative_event_difference':observed,'rigorous_relative_lower':float(lower)})
 out={'status':'pass','cases':24,'exact_physical_basis_states':totalstates,'exact_projected_coefficients_checked':projections,'independent_ode_event_pair_checks':odechecks,'seconds':time.perf_counter()-start,'records':records};(LAB/'results/event_projection_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'}))
if __name__=='__main__':main()
