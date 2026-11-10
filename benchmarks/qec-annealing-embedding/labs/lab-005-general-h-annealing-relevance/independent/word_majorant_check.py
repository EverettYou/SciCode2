"""Independent explicit D/E-word integration of the mixed commutator bound."""
from fractions import Fraction as F
from itertools import product
import json,time,sys
sys.dont_write_bytecode=True
from pathlib import Path
LAB=Path(__file__).resolve().parents[1]
def integrated(poly):
 out=[F(0)]*(len(poly)+1)
 for k,v in enumerate(poly):out[0]+=v/F(k+1);out[k+1]-=v/F(k+1)
 return out

def word_sum(n,g,k):
 total=F(0)
 for middle in product('DE',repeat=k-2):
  word=('D',)+middle+('E',);p=[F(1)];d=m=0
  for letter in word:
   if letter=='D':
    a=2*(n+m);q=[F(0)]*(len(p)+1)
    for j,v in enumerate(p):q[j]+=a*v;q[j+1]-=a*v
    d+=1
   else:
    q=[F(0)]+[2*d*g*v for v in p];m+=1
   p=integrated(q)
  total+=p[0]
 return total

def main():
 start=time.perf_counter();rows=[]
 for n,g in [(1,F(1,2)),(3,F(2)),(8,F(7,3))]:
  c={str(k):word_sum(n,g,k) for k in [2,4,6,8,10,12]};assert c['2']==n*g/6
  rows.append({'n':n,'gE_exact':[g.numerator,g.denominator],'coefficients':{k:[v.numerator,v.denominator] for k,v in c.items()}})
 out={'status':'pass','records':rows,'seconds':time.perf_counter()-start};(LAB/'results/independent_word_majorants.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':'pass','cases':len(rows),'seconds':out['seconds']}))
if __name__=='__main__':main()
