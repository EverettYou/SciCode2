"""Reproducible independent checks and same-target embedding reference runs.

Run from any directory:
  python /absolute/lab/scripts/embedding_checks.py --output /absolute/lab/results
Writes only embed_*.json. Results are numerical evidence, not performance proofs.
"""
from __future__ import annotations

import argparse
import copy
import itertools
import json
import math
from pathlib import Path
import platform
import random
import statistics
import sys
import time

import networkx as nx

from embedding import (CliqueTemplate, allocate_physical, allocate_physical_exact,
    certify_physical_rounding, exact_model_to_ising, find_automatic_embedding,
    graph_witness, interaction_graph, ising_energy, make_target, physical_witness,
    qubo_to_ising, verify_embedding, versions)


def spins(nodes):
    nodes = list(nodes)
    for values in itertools.product((-1, 1), repeat=len(nodes)):
        yield dict(zip(nodes, values))


def check_conversion(rng):
    count, error = 0, 0.0
    for n in range(1, 6):
        for trial in range(8):
            linear = [rng.uniform(-3, 3) for _ in range(n)]
            quadratic = [[i, j, rng.uniform(-2, 2)] for i in range(n)
                         for j in range(i, n) if rng.random() < 0.4]
            offset = rng.uniform(-3, 3)
            h, J, c = qubo_to_ising(linear, quadratic, offset)
            for z in spins(h):
                x = {i: (1 + z[i]) // 2 for i in z}
                expected = offset + sum(a*x[i] for i,a in enumerate(linear)) + sum(
                    b*x[i]*x[j] for i,j,b in quadratic)
                error = max(error, abs(ising_energy(h,J,c,z) - expected))
                count += 1
    assert error < 1e-10
    return {"assignments": count, "maximum_absolute_error": error}


def check_verifier():
    target = nx.path_graph(6)
    source = nx.Graph([(0, 1)])
    source.add_node(2)
    valid = {0:[0,1],1:[2,3],2:[5]}
    assert verify_embedding(source,target,valid)["valid"]
    corruptions = {
        "missing_isolate":{0:[0,1],1:[2,3]},
        "overlap":{0:[0,1],1:[1,2],2:[5]},
        "disconnected":{0:[0,2],1:[3],2:[5]},
        "missing_coupler":{0:[0],1:[3],2:[5]},
        "empty_chain":{0:[],1:[3],2:[5]},
        "unknown_target_node":{0:[100],1:[3],2:[5]},
    }
    result={name: verify_embedding(source,target,E) for name,E in corruptions.items()}
    assert all(not data["valid"] for data in result.values())
    return {"valid_case":True,"invalid_cases_rejected":result}


def check_pruning():
    target=make_target(2)
    template=CliqueTemplate(target,engine='native')
    nodes=list(range(5)); pairs=list(itertools.combinations(nodes,2))
    full=template.embed(nx.empty_graph(nodes),prune=False)
    count=0
    for mask in range(1<<len(pairs)):
        graph=nx.Graph();graph.add_nodes_from(nodes)
        graph.add_edges_from(pair for k,pair in enumerate(pairs) if mask>>k&1)
        E=template.embed(graph,prune=True)
        assert verify_embedding(graph,target,E)["valid"]
        assert all(set(E[i])<=set(full[i]) for i in graph)
        count+=1
    return {"graphs_checked":count,"all_valid":True,"all_subsets_of_template":True,
            "capacity":template.capacity,"target_g":2}


def check_physical(rng):
    target=make_target(1)
    template=CliqueTemplate(target)
    energy_checks, physical_states, broken_ground_states, maxerr=0,0,0,0.0
    witness=None
    for trial in range(16):
        n=2+trial%3
        h={i:rng.choice([-2.,-0.5,0.,1.,2.5]) for i in range(n)}
        J={(i,j):rng.choice([-1.5,-0.5,1.,2.]) for i in range(n)
           for j in range(i+1,n) if rng.random()<0.65}
        offset=rng.uniform(-1,1)
        graph=interaction_graph(h,J)
        E=template.embed(graph,prune=bool(trial%2))
        P=allocate_physical(h,J,offset,target,E,chain_margin=.25,
                            chain_factor=1+(trial%3),group_range=(-.25,.2))
        lmin=min(ising_energy(h,J,offset,z) for z in spins(h))
        for z in spins(h):
            physical={q:z[i] for i,chain in E.items() for q in chain}
            expected=ising_energy(h,J,offset,z)
            actual=ising_energy(P['h_raw'],P['J_raw'],P['offset_raw'],physical)
            maxerr=max(maxerr,abs(expected-actual)); energy_checks+=1
        pmin=math.inf; grounds=[]
        for z in spins(P['h']):
            energy=ising_energy(P['h'],P['J'],P['offset'],z)
            physical_states+=1
            if energy<pmin-1e-10:
                pmin=energy;grounds=[z]
            elif abs(energy-pmin)<=1e-10:
                grounds.append(z)
        assert abs(pmin-P['scale']*lmin)<1e-9
        for z in grounds:
            broken=any(len({z[q] for q in chain})>1 for chain in E.values())
            broken_ground_states+=int(broken)
            assert not broken
        for value in P['h'].values():
            assert -4-1e-12<=value<=4+1e-12
        for value in P['J'].values():
            assert -1-1e-12<=value<=1+1e-12
        for group_sum in P['group_sums_raw']:
            assert -.25-1e-12<=P['scale']*group_sum<=.2+1e-12
        if trial==5:
            witness={'target':graph_witness(target),'logical_h':h,
                     'logical_J':[[i,j,x] for (i,j),x in J.items()],
                     'logical_offset':offset,'embedding':E,
                     'program':physical_witness(P), 'logical_minimum':lmin,
                     'physical_minimum':pmin,'physical_ground_state_count':len(grounds)}
    assert maxerr<1e-10
    return ({'instances':16,'consistent_assignment_checks':energy_checks,
             'physical_states_enumerated':physical_states,'broken_physical_ground_states':broken_ground_states,
             'maximum_raw_energy_error':maxerr,'group_constraints_checked':True},witness)


def check_exact_physical():
    from compiler import compile_instance
    target=make_target(1);template=CliqueTemplate(target)
    records=[]
    for trial in range(8):
        weights=[.5,-.25,1.] if trial%2 else [0.,-.5,.25]
        model=compile_instance([[0,1],[1,2]],3,[trial%2,(trial//2)%2],weights)
        h,J,c=exact_model_to_ising(model)
        E=template.embed(interaction_graph(h,J),prune=bool(trial%2))
        P=allocate_physical_exact(model,target,E,chain_margin=.25,
                                 chain_factor=1+trial%3,group_range=(-.25,.2))
        certificate=P['numeric_certificate']
        assert certificate['float_ground_states_certified']
        ideal_min=min(ising_energy(h,J,c,z) for z in spins(h))
        actual_min=math.inf;ground_states=[]
        for z in spins(P['h']):
            energy=ising_energy(P['h'],P['J'],P['offset'],z)
            if energy<actual_min-1e-12:
                actual_min=energy;ground_states=[z]
            elif abs(energy-actual_min)<=1e-12:
                ground_states.append(z)
        for z in ground_states:
            assert all(len({z[q] for q in branch})==1 for branch in E.values())
            logical={i:z[branch[0]] for i,branch in E.items()}
            assert ising_energy(h,J,c,logical)==ideal_min
        corrupted=copy.deepcopy(P)
        first=next(iter(corrupted['h']))
        corrupted['h'][first]+=2.
        rejected=certify_physical_rounding(model,corrupted,E,target)
        assert not rejected['float_ground_states_certified']
        records.append({'trial':trial,'physical_states':1<<len(P['h']),
                        'ground_states_checked':len(ground_states),
                        'certificate':{k:v for k,v in certificate.items() if k!='exact_companion'},
                        'scale_nextafter_adjustments':P['scale_nextafter_adjustments'],
                        'corrupted_coefficient_rejected':True})
    # The tiny exact binary64 weight lattice can make the sufficient certificate
    # inconclusive. That outcome must be reported, never silently accepted.
    awkward=compile_instance([[0,1],[1,2]],3,[1,0],[.1,.2,.3],require_float_fidelity=False)
    h,J,c=exact_model_to_ising(awkward);E=template.embed(interaction_graph(h,J))
    P=allocate_physical_exact(awkward,target,E,require_float_fidelity=False)
    return {'certified_instances':records,'non_dyadic_decimal_input_example':{
        'weights':[.1,.2,.3],
        'compiler_certificate':awkward['numeric_certificate'],
        'physical_certificate':{k:v for k,v in P['numeric_certificate'].items() if k!='exact_companion'},
        'interpretation':'false means sufficient numerical certificate is inconclusive, not a proof of wrong physical ground states'}}


def benchmark(seed=7107):
    target=make_target(4)
    # Preserve the original experiment's native-template construction explicitly.
    template=CliqueTemplate(target,seed=seed,engine='native')
    cases=[]
    for n in (24,40,56):
        cases += [(f'path_n{n}',nx.path_graph(n)),
                  (f'cubic_n{n}',nx.random_regular_graph(3,n,seed=seed+n)),
                  (f'gnp_n{n}_p0.2',nx.gnp_random_graph(n,.2,seed=seed+n))]
    records=[]; witness={}
    for name,graph in cases:
        record={'name':name,'N':len(graph),'M':graph.number_of_edges(),'methods':{}}
        for method,prune in [('full_template',False),('pruned_template',True)]:
            timings=[]
            for _ in range(25):
                started=time.perf_counter();E=template.embed(graph,prune=prune)
                timings.append(time.perf_counter()-started)
            started=time.perf_counter();validation=verify_embedding(graph,target,E)
            vtime=time.perf_counter()-started
            assert validation['valid']
            record['methods'][method]={**validation,'query_seconds_median':statistics.median(timings),
                                       'validation_seconds':vtime,'query_repetitions':len(timings)}
            if name=='cubic_n40': witness[method]={str(i):list(c) for i,c in E.items()}
        trials=[]
        for trial in range(3):
            R=find_automatic_embedding(graph,target,seed=seed+trial,timeout=5.,tries=10)
            trials.append({k:v for k,v in R.items() if k!='embedding'})
            if name=='cubic_n40' and trial==0:
                witness['automatic']={str(i):list(c) for i,c in R['embedding'].items()}
        record['methods']['automatic']={'trials':trials,
             'elapsed_seconds_median':statistics.median(r['elapsed_seconds'] for r in trials)}
        records.append(record)
        print(json.dumps({'case':name,'full':record['methods']['full_template']['physical_qubits'],
              'pruned':record['methods']['pruned_template']['physical_qubits'],
              'automatic':[r.get('validation',{}).get('physical_qubits') for r in trials]}),flush=True)
    return ({'target_g':4,'target_t':4,'target_nodes':len(target),'target_edges':target.number_of_edges(),
             'template_capacity':template.capacity,'template_preprocessing_seconds':template.preprocessing_seconds,
             'records':records,'timing_scope':'template query excludes independent revalidation; automatic includes revalidation; no I/O or imports',
             'fixed_graph_reuse':'Any successful automatic embedding can also be reused without search for repeated identical support. No advantage over that reuse is claimed.',
             'seed':seed},
            {'target':graph_witness(target),'template':template.witness(),
             'graph':graph_witness(dict(cases)['cubic_n40']),'embeddings':witness})


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'results')
    parser.add_argument('--skip-benchmark',action='store_true')
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    rng=random.Random(7107)
    start=time.perf_counter()
    checks={'seed':7107,'versions':versions(),'python':sys.version,'platform':platform.platform()}
    checks['qubo_conversion']=check_conversion(rng)
    checks['verifier_corruptions']=check_verifier()
    checks['pruning']=check_pruning()
    checks['physical_allocation'],pwitness=check_physical(rng)
    checks['exact_physical_allocation']=check_exact_physical()
    checks['elapsed_seconds']=time.perf_counter()-start
    (args.output/'embed_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    (args.output/'embed_physical_witness.json').write_text(json.dumps(pwitness,indent=2)+'\n')
    if not args.skip_benchmark:
        bench,witness=benchmark()
        bench['versions']=versions()
        (args.output/'embed_benchmark.json').write_text(json.dumps(bench,indent=2)+'\n')
        (args.output/'embed_target_and_witnesses.json').write_text(json.dumps(witness,indent=2)+'\n')
    print(json.dumps(checks,indent=2))


if __name__=='__main__':
    main()
