"""Reproducible sparse-matrix-to-Zephyr experiments and reusable witnesses."""
from __future__ import annotations
import json
import pathlib
import time
import platform
import resource
import numpy as np
import networkx as nx
from compiler import compile_instance, model_graph, update_instance, complete_feasible, energy
from embedding import (make_target, CliqueTemplate, find_automatic_embedding,
    verify_embedding, allocate_physical_exact, qubo_to_ising, graph_witness,
    physical_witness, ising_energy, versions)
from theory_checks import pause_certificate

LAB=pathlib.Path(__file__).resolve().parents[1]
OUT=LAB/"results"


def save(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False))


def instances(seed=20261007):
    rng=np.random.default_rng(seed)
    specs=[]
    specs.append(("banded_three_body",16,[[i,i+1,i+2] for i in range(14)]))
    specs.append(("irregular_hyperchecks",18,[sorted(rng.choice(18,size=int(rng.integers(3,6)),replace=False).tolist()) for _ in range(10)]))
    rows=[[0]+sorted(rng.choice(np.arange(1,17),size=3,replace=False).tolist()) for _ in range(10)]
    specs.append(("high_column_degree_redundant_isolate",18,rows+[rows[0],[]]))
    rows=[[] for _ in range(12)]
    for column in range(24):
        for row in rng.choice(12,size=2,replace=False): rows[int(row)].append(column)
    specs.append(("graphlike_incidence",24,rows))
    specs.append(("single_large_hypercheck",30,[list(range(30))]))
    for name,n,rows in specs:
        truth=rng.integers(0,2,size=n).tolist()
        s=[sum(truth[i] for i in row)%2 for row in rows]
        w=(rng.integers(-8,9,size=n)/4).tolist()
        yield {"name":name,"n":n,"rows":rows,"syndrome":s,"weights":w,
               "generated_feasible_pattern":truth,"seed":seed,"penalty":100.0}


def program_certificate(program,embedding,gamma=.0001,duration=100.):
    chain_set={tuple(sorted(edge)) for edges in program["chain_edges"].values() for edge in edges}
    chains=[(a,b,-program["J"][a,b]) for a,b in sorted(chain_set)]
    edges=[(a,b,j) for (a,b),j in program["J"].items() if (a,b) not in chain_set]
    return pause_certificate([embedding[i] for i in sorted(embedding)],chains,
                             program["h"],edges,gamma,duration)


def evaluate(model,target,embedding,method,rng):
    start=time.perf_counter()
    h,J,c=qubo_to_ising(model["linear"],model["quadratic"],model["offset"])
    program=allocate_physical_exact(model,target,embedding)
    elapsed=time.perf_counter()-start
    discrepancies=[]
    for _ in range(12):
        y=rng.integers(0,2,size=len(model["linear"])).tolist()
        z={i:2*y[i]-1 for i in range(len(y))}
        physical={q:z[i] for i,branch in embedding.items() for q in branch}
        qenergy=energy(model,y)
        discrepancies.append(abs(ising_energy(program["h"],program["J"],program["offset"],physical)-program["scale"]*qenergy))
    assert max(discrepancies,default=0)<1e-8
    assert verify_embedding(model_graph(model),target,embedding)["valid"]
    assert all(-4-1e-12<=h<=4+1e-12 for h in program["h"].values())
    assert all(-1-1e-12<=j<=1+1e-12 for j in program["J"].values())
    assert all(-13-1e-12<=program["scale"]*j<=10+1e-12 for j in program["group_sums_raw"])
    cert_start=time.perf_counter();cert=program_certificate(program,embedding)
    certificate_elapsed=time.perf_counter()-cert_start
    witness=physical_witness(program)
    witness.pop("coupling_groups")
    witness["coupling_groups_reference"]="target_zephyr_g6.json"
    witness["embedding"]={str(i):list(q) for i,q in embedding.items()}
    witness["method"]=method
    witness["pause_certificate"] = cert
    summary={"method":method,**program["validation"],"scale":program["scale"],
             "scale_limiter":program["scale_limiter"],"programming_seconds":elapsed,
             "certificate_seconds":certificate_elapsed,"certificate_status":cert["status"],
             "certificate_g":cert["g"],"consistent_energy_max_error":max(discrepancies,default=0),
             "physical_rounding_certificate":{k:v for k,v in program["numeric_certificate"].items() if k!="exact_companion"}}
    return summary,witness


def main():
    overall=time.perf_counter();rng=np.random.default_rng(714)
    target=make_target(6,t=4)
    from dwave.system.coupling_groups import coupling_groups
    targetw=graph_witness(target);targetw["coupling_groups"]=list(coupling_groups(target))
    save("target_zephyr_g6.json",targetw)
    template=CliqueTemplate(target)
    save("template_zephyr_g6.json",template.witness())
    reports=[]
    for instance in instances():
        name=instance["name"]
        save(f"input_{name}.json",instance)
        before=time.perf_counter()
        model=compile_instance(instance["rows"],instance["n"],instance["syndrome"],instance["weights"],instance["penalty"])
        compilation=time.perf_counter()-before
        graph=model_graph(model,structural=True)
        save(f"model_{name}.json",model)
        rowdegrees=[len(r) for r in model["rows"]]
        coldegrees=[sum(i in row for row in model["rows"]) for i in range(instance["n"])]
        case={"name":name,"n":instance["n"],"m":len(model["rows"]),
              "nnz":sum(rowdegrees),"max_row_degree":max(rowdegrees,default=0),
              "max_column_degree":max(coldegrees,default=0),
              "zero_columns":coldegrees.count(0),"qubo_variables":len(graph),
              "actual_edges":model_graph(model).number_of_edges(),
              "structural_edges":graph.number_of_edges(),"compilation_seconds":compilation,"mappings":[]}
        for method,prune in [("template_full",False),("template_pruned",True)]:
            before=time.perf_counter();embedding=template.embed(graph,prune=prune)
            mapping_elapsed=time.perf_counter()-before
            before=time.perf_counter();assert verify_embedding(graph,target,embedding)["valid"]
            validation_elapsed=time.perf_counter()-before
            summary,witness=evaluate(model,target,embedding,method,rng)
            summary["embedding_seconds"]=mapping_elapsed
            summary["independent_embedding_validation_seconds"]=validation_elapsed
            summary["embedding_with_validation_seconds"]=mapping_elapsed+validation_elapsed
            case["mappings"].append(summary)
            save(f"witness_{name}_{method}.json",witness)
        # The reference sees the same stable supergraph, target, and programming constraints.
        for seed in [11,29,47]:
            reference=find_automatic_embedding(graph,target,seed=seed,timeout=5.0,tries=4)
            if reference["status"] != "valid":
                case["mappings"].append({"method":f"minorminer_{seed}",
                                         "status":reference["status"],"embedding_seconds":reference["elapsed_seconds"]})
                continue
            summary,witness=evaluate(model,target,reference["embedding"],f"minorminer_{seed}",rng)
            summary["embedding_seconds"]=reference["elapsed_seconds"]
            summary["embedding_with_validation_seconds"]=reference["elapsed_seconds"]
            witness["reference_parameters"]=reference["parameters"]
            case["mappings"].append(summary)
            save(f"witness_{name}_minorminer_{seed}.json",witness)
        # New syndromes/weights: retain fixed penalty and all structural variables/edges.
        update_times=[]
        for trial in range(20):
            e=rng.integers(0,2,size=instance["n"])
            s=[int(e[row].sum()%2) for row in model["rows"]]
            weights=(rng.integers(-8,9,size=instance["n"])/4).tolist()
            before=time.perf_counter();updated=update_instance(model,s,weights)
            update_times.append(time.perf_counter()-before)
            assert updated["variables"]==model["variables"]
            assert updated["structural_edges"]==model["structural_edges"]
            assert abs(energy(updated,complete_feasible(updated,e))-float(e@np.asarray(weights)))<1e-8
        case["numeric_update_mean_seconds"]=float(np.mean(update_times))
        case["numeric_update_trials"]=len(update_times)
        reports.append(case)
        print(json.dumps({"case":name,"N":len(graph),"mapping_results":[[x["method"],x.get("physical_qubits"),x["embedding_seconds"]] for x in case["mappings"]]}),flush=True)
    # Matrix/window update: append columns/checks, rebuild logical structure,
    # and reuse only the same target's verified template.
    window=next(instances());n=window["n"]+2
    changed_rows=[list(r) for r in window["rows"]]+[[n-3,n-2,n-1]]
    e=rng.integers(0,2,size=n);s=[int(e[row].sum()%2) for row in changed_rows]
    start=time.perf_counter();changed=compile_instance(changed_rows,n,s,[.5]*n,penalty=100.)
    changed_embedding=template.embed(model_graph(changed,structural=True),prune=True)
    change_seconds=time.perf_counter()-start
    assert verify_embedding(model_graph(changed),target,changed_embedding)["valid"]
    save("matrix_update_witness.json",{"model":changed,"embedding":{str(k):v for k,v in changed_embedding.items()},"elapsed_seconds":change_seconds})
    report={"python":platform.python_version(),"versions":versions(),"seed":20261007,
            "target":{"g":6,"t":4,"nodes":len(target),"edges":target.number_of_edges(),"ideal":True},
            "template_capacity":template.capacity,"template_preprocessing_seconds":template.preprocessing_seconds,
            "conditions":{"h_range":[-4,4],"J_range":[-1,1],"coupling_group_range":[-13,10],"status":"illustrative parametric ranges, no device export","cap_scale_at_one":True},
            "matrix_update_seconds":change_seconds,"cases":reports,
            "elapsed_seconds":time.perf_counter()-overall,
            "process_maxrss_bytes_macos":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    save("experiment_summary.json",report)
    print(json.dumps({k:v for k,v in report.items() if k!="cases"},indent=2),flush=True)

if __name__=="__main__":main()
