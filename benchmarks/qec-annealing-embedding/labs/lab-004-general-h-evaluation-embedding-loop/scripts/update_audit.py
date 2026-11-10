import json,random,time
from run_suite import OUT,FAMILIES,save
from compiler import update_instance,model_graph
from embedding import graph_from_witness,verify_embedding,qubo_to_ising
from evaluator import evaluate,brief


def main():
    td=json.loads((OUT/'target.json').read_text());target=graph_from_witness(td['target']);groups=[[tuple(e) for e in g] for g in td['coupling_groups']]
    records=[];start=time.perf_counter()
    for family in FAMILIES:
        r=json.loads((OUT/f'{family}_n64_s1101.json').read_text());base=r['model'];embedding={int(i):ch for i,ch in r['selected']['guided_pruned']['embedding'].items()}
        rng=random.Random(7733+FAMILIES.index(family));rows=[]
        for trial in range(40):
            truth=[rng.randrange(2) for _ in range(64)];syndrome=[sum(truth[i] for i in supp)%2 for supp in base['rows']]
            weights=list(base['weights']);rng.shuffle(weights)
            cstart=time.perf_counter();new=update_instance(base,syndrome,weights);comp=time.perf_counter()-cstart
            vstart=time.perf_counter();valid=verify_embedding(model_graph(new),target,embedding);check=time.perf_counter()-vstart
            row={'trial':trial,'compile_seconds':comp,'check_seconds':check,'valid_embedding':valid['valid']}
            if valid['valid']:
                h,J,c=qubo_to_ising(new['linear'],new['quadratic'],new['offset']);p=evaluate(h,J,c,target,embedding,groups=groups)
                row['evaluation']=brief(p)
            else:row['missing_edges']=valid['errors']
            rows.append(row)
        records.append({'family':family,'updates':rows,'base_qubits':r['selected']['guided_pruned']['program']['physical_qubits']})
    save(OUT/'update_audit.json',{'records':records,'elapsed_seconds':time.perf_counter()-start,
         'syndrome_seed_base':7733,'fixed_H':True,'fixed_penalty':True,'future_detector_data':False})
if __name__=='__main__':main()
