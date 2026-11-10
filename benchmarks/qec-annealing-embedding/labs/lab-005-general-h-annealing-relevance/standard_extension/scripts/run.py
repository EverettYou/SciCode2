from pathlib import Path
from fractions import Fraction as F
import json,sys,time,statistics,hashlib,argparse
from optimality_lp import root_second,subtract,evaluate
sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parents[1];LAB=HERE.parent;METHODS=['basis','pairs','triangles']
def read(v):return F(int(v['numerator_hex'],16),int(v['denominator_hex'],16)) if isinstance(v,dict) else F(*v)
def pair(v):return {'numerator_hex':hex(v.numerator),'denominator_hex':hex(v.denominator)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--upper',choices=['particular','witness']);args=ap.parse_args();start=time.perf_counter();out=HERE/('results/'+args.upper+'_nested' if args.upper else 'results');out.mkdir(exist_ok=True);records=[]
    for path in sorted((LAB/'results/certified_mapping').glob('*_standard.json')):
        st=time.perf_counter();d=json.loads(path.read_text());inp=d['input'];oldm=d['moments'];m=dict(oldm)
        if args.upper:m=json.loads((HERE/'results'/args.upper/path.name).read_text())['moments_with_witness_upper']
        base=d['comparisons'][0];bp=root_second(inp,base['program'],m);allcomparisons=[]
        for a in d['comparisons']:
            delta=subtract(bp,root_second(inp,a['program'],m));old=read(a['L2_exact']);lam=read(a['lambda_exact'])
            # Check independent root-only q2 extraction against the saved exact Lagrange value.
            chars=[int(v,16) for v in m['kernel_character_hex']];ref=m['particular_solution'];cost={}
            for i,c in enumerate(chars):
                if c:cost[c]=cost.get(c,F(0))+F(inp['weights'][i])*(2*ref[i]-1)/2
            check=delta.get(0,F(0))+lam*(F(*oldm['mean_exact'])-F(*oldm['minimum_cost_upper_exact']))-sum((abs(delta.get(k,F(0))+lam*cost.get(k,F(0))) for k in delta.keys()|cost.keys() if k),F(0));assert check==old
            methods={};best=old
            for method in METHODS:
                r=evaluate(inp,m,delta,method);lower=max(best,r.get('bound',best));best=lower
                curves=[]
                for curve in a['curves']:
                    T=F(curve['T']);gap=None if curve['relative_advantage_lower_exact'] is None else read(curve['relative_advantage_lower_exact'])+(lower-old)*T*T
                    curves.append({'T':float(T),'strict':gap is not None and gap>0,'gap_exact':None if gap is None else pair(gap),'gap':None if gap is None else float(gap)})
                methods[method]={'status':r['status'],'bound_exact':pair(lower),'raw_dual_bound_exact':None if 'bound' not in r else pair(r['bound']),'gain_over_cost_bound':float(lower-old),'variables':r['variables'],'constraints':r['constraints'],'seconds':r['seconds'],'lp_seconds':r.get('lp_seconds',0),'dual_nonzero':[[row['id'],pair(nu)] for row,nu in zip(r['rows'],r.get('multipliers',[])) if nu],'curves':curves}
            allcomparisons.append({'seed':a['seed'],'physical_qubits':a['physical_qubits'],'delta_second_exact':[[hex(k),pair(v)] for k,v in delta.items()],'cost_only_lower_exact':pair(old),'methods':methods})
        selections={}
        for method in METHODS:
            selections[method]=[]
            for j,oldselect in enumerate(d['selections']):
                eligible=[a for a in allcomparisons if a['physical_qubits']<=base['physical_qubits'] and a['methods'][method]['curves'][j]['strict']]
                def exactgap(a):v=a['methods'][method]['curves'][j]['gap_exact'];return F(int(v['numerator_hex'],16),int(v['denominator_hex'],16))
                sel=min(eligible,key=lambda a:(a['physical_qubits'],-exactgap(a),a['seed'])) if eligible else allcomparisons[0]
                selections[method].append({'T':oldselect['T'],'selected_seed':sel['seed'],'certified_change':bool(eligible),'baseline_qubits':base['physical_qubits'],'selected_qubits':sel['physical_qubits'],'saved_qubits':base['physical_qubits']-sel['physical_qubits']})
        r={'name':d['name'],'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'input':inp,'moments':m,'comparisons':allcomparisons,'selections':selections,'seconds':time.perf_counter()-st};(out/path.name).write_text(json.dumps(r,indent=2)+'\n');records.append({'name':d['name'],'seconds':r['seconds'],'selections':selections});print(json.dumps({'name':d['name'],'seconds':r['seconds'],'primary':{method:next(x for x in s if x['T']==1/1024) for method,s in selections.items()}}),flush=True)
    summary={}
    for method in METHODS:
        summary[method]={}
        for T in [1/2**k for k in range(6,13)]:
            rows=[next(s for s in r['selections'][method] if s['T']==T) for r in records];summary[method][str(T)]={'models':len(rows),'certified_changes':sum(s['certified_change'] for s in rows),'strict_qubit_reductions':sum(s['saved_qubits']>0 for s in rows),'mean_qubit_reduction_fraction':statistics.mean(s['saved_qubits']/s['baseline_qubits'] for s in rows)}
    result={'status':'complete','models':len(records),'candidates':sum(len(json.loads(p.read_text())['comparisons']) for p in out.glob('*_standard.json')),'summary':summary,'seconds':time.perf_counter()-start,'records':records};(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='records'}))
if __name__=='__main__':main()
