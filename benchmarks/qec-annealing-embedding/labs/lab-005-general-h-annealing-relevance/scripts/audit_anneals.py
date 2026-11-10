"""Recompute every stochastic output score from saved final physical states."""
from pathlib import Path
import csv,json,math,time,argparse
OUT=Path(__file__).resolve().parents[1]/'results'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--standard',action='store_true');args=ap.parse_args()
    prefix='anneal_standard' if args.standard else 'anneal';source_folder=OUT/('relaxation_standard' if args.standard else 'relaxation')
    summary=json.loads((OUT/(prefix+'_summary.json')).read_text())
    start=time.perf_counter();cases=[];total=0
    for path in sorted(source_folder.glob('*.json')):
        r=json.loads(path.read_text());name=r['name'];data=r['input'];ref=None
        ref=next(x for x in summary['records'] if x['name']==name)['reference']
        variantrows={}
        for label,key in [('before','before_program'),('after','after_program')]:
            p=r[key];nodes=sorted(q for q,v in p['h']);ix={q:k for k,q in enumerate(nodes)};roots={int(i):q for i,q in p['roots'].items()};trees=[tuple(e) for es in p['chain_trees'].values() for e in es]
            scored={};count=0
            with (OUT/'anneals'/(name+'_'+label+'.csv')).open() as f:
                for x in csv.DictReader(f):
                    state=x['physical_bits'];error=[int(state[ix[roots[i]]]) for i in range(data['n'])]
                    consistent=all(state[ix[q]]==state[ix[s]] for q,s in trees)
                    feasible=all(sum(error[i] for i in row)%2==s for row,s in zip(data['rows'],data['syndrome']))
                    cost=sum(w*b for w,b in zip(data['weights'],error));optimal=int(feasible and abs(cost-ref['minimum_cost'])<1e-9) if ref['status']=='exact' else -1
                    mask=sum(b<<i for i,b in enumerate(error))
                    if (int(x['consistent'])!=consistent or int(x['feasible'])!=feasible or int(x['optimal'])!=optimal
                        or float(x['cost'])!=cost or int(x['error_mask'],16)!=mask):raise AssertionError(('stochastic score mismatch',name,label,x['replica']))
                    scored[int(x['attempts']),int(x['replica'])]={'consistent':consistent,'feasible':feasible,'optimal':optimal}
                    count+=1
            variantrows[label]=scored;total+=count
        pairs=[]
        for attempts in sorted(set(a for a,b in variantrows['before'])):
            keys=[k for k in variantrows['before'] if k[0]==attempts];row={'attempts':attempts,'replicas':len(keys)}
            for event in ['consistent','feasible','optimal']:
                if variantrows['before'][keys[0]][event]<0:row[event]=None;continue
                wins=sum(variantrows['after'][k][event]>variantrows['before'][k][event] for k in keys)
                losses=sum(variantrows['after'][k][event]<variantrows['before'][k][event] for k in keys)
                row[event]={'after_only':wins,'before_only':losses,'paired_rate_difference':(wins-losses)/len(keys)}
            pairs.append(row)
        cases.append({'name':name,'paired_results':pairs})
    (OUT/(prefix+'_score_audit.json')).write_text(json.dumps({'status':'pass','physical_outputs_checked':total,'cases':cases,'elapsed_seconds':time.perf_counter()-start},indent=2)+'\n');print('outputs checked',total)
if __name__=='__main__':main()
