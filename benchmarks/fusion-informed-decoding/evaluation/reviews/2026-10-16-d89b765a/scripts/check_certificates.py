"""Independent rational envelopes plus replay of saved certificate functions."""
from fractions import Fraction as F
from math import isqrt
from pathlib import Path
import importlib.util,json,sys

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/Users/home/Downloads/20261014-102308_d89b765a')

def sqrt_up(x):
    scale=10**24
    return F(isqrt(x.numerator*scale*scale//x.denominator)+1,scale)

def cover(N,form,walk=None):
    mu2=2+sqrt_up(F(2)) if walk is None else walk*walk
    worst=F(0);K=4096
    for k in range(K):
        a,b=F(k,K),F(k+1,K)
        pq=b*(1-b) if b<=F(1,2) else a*(1-a) if a>=F(1,2) else F(1,4)
        if form=='degree':g2=(1+sqrt_up(1+b)/N)**2
        else:g2=(1-b)*(1+F(1,N))**2+b*(1+sqrt_up(F(2))/N)**2
        worst=max(worst,mu2*pq*g2)
    assert worst<1
    return dict(N0=N,form=form,intervals=K,uniform_squared_path_factor_upper=float(worst),exact_upper=str(worst),passed=True)

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

out={}
out['Opus1_and_Opus2_N15']=cover(15,'degree')
out['Opus3_N15']=cover(15,'branch')
out['Fable3_N19']=cover(19,'degree',F('1.876764'))
# Independent audit of the three rational ranges in GPT1's N=13 proof.
assert F('1.848')**2>2 and (F('1.848')**2-2)**2>2
assert (2*F('1.619')-1)**2>5
for q,r in [(F('1.057'),F(1,2)+F('0.55')*(F('1.619')-F(1,2))),
            (F('1.108'),F(1,2)+F('0.65')*(F('1.619')-F(1,2))),
            (F('1.273'),F('1.619'))]:assert q*q>r
assert F('.498')**2>F('.55')*F('.45')
assert F('.477')**2>F('.65')*F('.35')
v=[F('.924')*(1+F('1.057')/13),F('1.848')*F('.498')*(1+F('1.108')/13),F('1.848')*F('.477')*(1+F('1.273')/13)]
assert max(v)<1
out['GPT1_N13']={'ranges':['[0,.55]','[.55,.65]','[.65,1]'],'upper_factors':[float(t) for t in v],'passed':True}
g2=load(SOURCE/'openai__gpt-6-astra/run_02/large_n.py','g2_certificate').certificate()
out['GPT2_N13']={k:g2[k] for k in ['N0','cycle_K_upper_float','uniform_path_factor_upper_float','hexagon_enumeration_checks']};out['GPT2_N13']['passed']=True
g3=load(SOURCE/'openai__gpt-6-astra/run_03/proof_constants.py','g3_certificate').constants()
out['GPT3_N14']=g3
(ROOT/'results/proof-certificate-checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:{z:v[z] for z in v if z not in ['exact_upper','hexagon_enumeration_checks']} for k,v in out.items()},indent=2))
