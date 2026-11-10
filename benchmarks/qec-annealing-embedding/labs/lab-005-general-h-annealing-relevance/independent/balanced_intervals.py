"""Independent positive interval partition transfer, balanced XOR compiler."""
from fractions import Fraction as F
from decimal import Decimal as D,localcontext
import numpy as np
import math,sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'lab-004-general-h-evaluation-embedding-loop/independent'))
from logical_gibbs_intervals import exp_interval,mul,add

def interval_mass(rows,n,syndrome,weights,penalty,t):
 assert n<=20;t=F(t);M=F(penalty);ids=np.arange(1<<n,dtype=np.uint64);bits=((ids[:,None]>>np.arange(n,dtype=np.uint64))&1).astype(np.int8)
 w4=[F(w)*4 for w in weights];assert all(w.denominator==1 for w in w4);cost=bits@np.array([int(w) for w in w4]);floor=sum(min(0,int(w)) for w in w4);feasible=np.ones(len(ids),bool);lo=np.ones(len(ids));hi=np.ones(len(ids))
 rlo,rhi=exp_interval(-t*M)
 def positive_row(degree):
  one=np.array(1.);rl=np.array(rlo);rh=np.array(rhi);al=add(one,rl,False);ah=add(one,rh,True)
  al=mul(mul(al,al,False),mul(al,al,False),False);ah=mul(mul(ah,ah,True),mul(ah,ah,True),True)
  bl=mul(np.array(8.),mul(rl,add(one,mul(rl,rl,False),False),False),False);bh=mul(np.array(8.),mul(rh,add(one,mul(rh,rh,True),True),True),True)
  vl,il,vh,ih=one,rl,one,rh
  for _ in range(max(0,degree-2)):
   vl,il=add(mul(al,vl,False),mul(bl,il,False),False),add(mul(al,il,False),mul(bl,vl,False),False)
   vh,ih=add(mul(ah,vh,True),mul(bh,ih,True),True),add(mul(ah,ih,True),mul(bh,vh,True),True)
  return float(vl),float(vh),float(il),float(ih)
 for row,s in zip(rows,syndrome):
  ok=bits[:,row].sum(axis=1)%2==s;feasible&=ok
  if not row:assert not s;continue
  vl,vh,il,ih=positive_row(len(row));lo=mul(lo,np.where(ok,vl,il),False);hi=mul(hi,np.where(ok,vh,ih),True)
 exps={int(c):exp_interval(-t*F(int(c)-floor,4)) for c in set(cost)}
 lo=mul(lo,np.array([exps[int(c)][0] for c in cost]),False);hi=mul(hi,np.array([exps[int(c)][1] for c in cost]),True)
 gamma=len(ids)*np.finfo(float).eps/(1-len(ids)*np.finfo(float).eps)
 def summ(a,up):return math.nextafter(float(a.sum())/(1-gamma if up else 1+gamma),math.inf if up else -math.inf)
 zl,zh=summ(lo,False),summ(hi,True);best=cost[feasible].min();opt=feasible&(cost==best)
 return {'decoded_error_lower':max(0.,math.nextafter(summ(lo[opt],False)/zh,-math.inf)),'decoded_error_upper':min(1.,math.nextafter(summ(hi[opt],True)/zl,math.inf)),
  'feasible_lower':max(0.,math.nextafter(summ(lo[feasible],False)/zh,-math.inf)),'feasible_upper':min(1.,math.nextafter(summ(hi[feasible],True)/zl,math.inf)),
  'ground_cost':int(best)/4,'ground_degeneracy':int(opt.sum()),'original_patterns':len(ids),'auxiliary_partition_summed':True}

def self_check():
 rows=[[0,1,2]];s=[1];w=[-.5,.25,1.];M=F(5,2);t=F(7,5);bound=interval_mass(rows,3,s,w,M,t);vals=[];flags=[]
 for state in range(256):
  b=[(state>>i)&1 for i in range(8)];x,y,z,p=b[:4];energy=sum(F(wi)*v for wi,v in zip(w,b));
  for k,(g1,g2,g3) in enumerate([(0,0,0),(0,1,1),(1,0,1),(1,1,0)]):energy+=M*F(((x^g1)+(y^g2)-(p^g3)-2*b[4+k])**2,4)
  energy+=M*(p^z^s[0]);vals.append(energy);flags.append((x+y+z)%2==s[0] and sum(F(wi)*v for wi,v in zip(w,b))==F(bound['ground_cost']))
 with localcontext() as c:
  c.prec=70;ws=[(-D(t.numerator)/D(t.denominator)*D(e.numerator)/D(e.denominator)).exp() for e in vals];prob=sum(v for v,ok in zip(ws,flags) if ok)/sum(ws)
  assert D.from_float(bound['decoded_error_lower'])<=prob<=D.from_float(bound['decoded_error_upper']),(bound,prob)
 return {'status':'pass','full_physical_assignments':256,'decoded_probability':str(prob),'interval':bound}
if __name__=='__main__':print(self_check())
