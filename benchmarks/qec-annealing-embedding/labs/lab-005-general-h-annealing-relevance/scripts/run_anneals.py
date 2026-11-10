"""Matched finite-work classical heat-bath diagnostics; exact optima reference-only."""
from pathlib import Path
import json,time,hashlib,subprocess,csv,math,argparse
import numpy as np
from models import compile_model
OUT=Path(__file__).resolve().parents[1]/'results';SCRIPT=Path(__file__).resolve().parent


def affine_optimum(data,wit,max_nullity=18):
    start=time.perf_counter();B=set(wit['basis_columns']);R=wit['basis_rows'];delta=[sum(1<<i for i in v) for v in wit['repair_columns']]
    free=[i for i in range(data['n']) if i not in B];k=len(free)
    if k>max_nullity:return {'status':'unassessed_nullity_limit','nullity':k,'limit':max_nullity,'elapsed_seconds':time.perf_counter()-start}
    particular=0
    for row,v in zip(R,delta):
        if data['syndrome'][row]:particular^=v
    kernels=[]
    for i in free:
        v=1<<i
        for row,d in zip(R,delta):
            if i in data['rows'][row]:v^=d
        kernels.append(v)
    masks=np.full(2**k,particular,dtype=np.uint64);index=np.arange(2**k,dtype=np.uint64)
    for j,v in enumerate(kernels):masks^=np.where((index>>j)&1,np.uint64(v),np.uint64(0))
    cost=np.zeros(len(masks))
    for i,w in enumerate(data['weights']):cost+=w*((masks>>i)&1)
    optimum=float(cost.min());winner=int(masks[np.argmin(cost)])
    if not all(sum((winner>>i)&1 for i in row)%2==s for row,s in zip(data['rows'],data['syndrome'])):raise AssertionError('affine reference infeasible')
    return {'status':'exact','nullity':k,'feasible_states':len(masks),'minimum_cost':optimum,'ground_degeneracy':int((cost==optimum).sum()),
            'witness_error_mask_hex':hex(winner),'elapsed_seconds':time.perf_counter()-start}


def write_input(path,data,p,emb,reps,seed,ref):
    nodes=sorted(q for q,v in p['h']);ix={q:k for k,q in enumerate(nodes)};ph=dict(p['h']);edges=[(ix[q],ix[r],v) for q,r,v in p['J'] if v]
    roots={int(i):q for i,q in p['roots'].items()};trees=[tuple(e) for es in p['chain_trees'].values() for e in es]
    budgets=[data['n']*x for x in [100,1000,10000]];has=int(ref['status']=='exact')
    lines=[f"{len(nodes)} {len(edges)} {data['n']} {len(data['rows'])} {len(trees)} {reps} 3 20 {seed} {has} {ref.get('minimum_cost',0.)}",
      ' '.join(format(ph[q],'.17g') for q in nodes)]
    lines += [f'{q} {r} {v:.17g}' for q,r,v in edges];lines += [' '.join(str(ix[roots[i]]) for i in range(data['n']))]
    lines += [' '.join(map(str,[len(row),*row,s])) for row,s in zip(data['rows'],data['syndrome'])]
    lines += [' '.join(format(w,'.17g') for w in data['weights'])];lines += [f'{ix[q]} {ix[r]}' for q,r in trees];lines += [' '.join(map(str,budgets))]
    path.write_text('\n'.join(lines)+'\n');return {'physical_node_order':nodes,'budgets':budgets,'replicas':reps,'seed':seed,'reference':ref}


def summarize(csvpath):
    batches={}
    with csvpath.open() as f:
        for row in csv.DictReader(f):batches.setdefault(int(row['attempts']),[]).append(row)
    result=[]
    for attempts,rows in batches.items():
        N=len(rows);s={'attempts':attempts,'replicas':N}
        for event in ['consistent','feasible','optimal']:
            values=[int(x[event]) for x in rows]
            if min(values)<0:s[event]=None;continue
            successes=sum(values);p=successes/N;z=1.96;den=1+z*z/N;center=(p+z*z/(2*N))/den;half=z*math.sqrt(p*(1-p)/N+z*z/(4*N*N))/den
            s[event]={'count':successes,'rate':p,'wilson95':[max(0.,center-half),min(1.,center+half)]}
        feasiblecost=[float(x['cost']) for x in rows if x['feasible']=='1']
        s['mean_feasible_cost']=sum(feasiblecost)/len(feasiblecost) if feasiblecost else None
        result.append(s)
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--standard',action='store_true');args=ap.parse_args()
    source_folder=OUT/('relaxation_standard' if args.standard else 'relaxation');prefix='anneal_standard' if args.standard else 'anneal'
    folder=OUT/'anneals';folder.mkdir(exist_ok=True);records=[];start=time.perf_counter()
    for path in sorted(source_folder.glob('*.json')):
        r=json.loads(path.read_text());data=r['input'];ref=affine_optimum(data,r['repair_witness']);reps=512 if data['n']<=32 else 128
        seed=int(hashlib.sha256(r['name'].encode()).hexdigest()[:16],16);entry={'name':r['name'],'n':data['n'],'reference':ref,'variants':{}}
        for label,key in [('before','before_program'),('after','after_program')]:
            inputpath=folder/(r['name']+'_'+label+'.txt');csvpath=folder/(r['name']+'_'+label+'.csv')
            config=write_input(inputpath,data,r[key],r['embedding'],reps,seed,ref);t0=time.perf_counter()
            completed=subprocess.run([str(SCRIPT/'anneal_backend'),str(inputpath),str(csvpath)],check=True,capture_output=True,text=True)
            entry['variants'][label]={'config':config,'wall_seconds':time.perf_counter()-t0,'results':summarize(csvpath),'csv_file':csvpath.name}
        records.append(entry);(OUT/(prefix+'_progress.json')).write_text(json.dumps(records,indent=2)+'\n')
        print(json.dumps({'name':entry['name'],'seconds':sum(x['wall_seconds'] for x in entry['variants'].values()),
          'before_final':entry['variants']['before']['results'][-1],'after_final':entry['variants']['after']['results'][-1]}),flush=True)
    (OUT/(prefix+'_summary.json')).write_text(json.dumps({'records':records,'elapsed_seconds':time.perf_counter()-start},indent=2)+'\n')
if __name__=='__main__':main()
