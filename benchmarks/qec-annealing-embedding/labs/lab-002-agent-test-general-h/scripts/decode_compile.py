"""CLI for arbitrary sparse-row decoding instances and a fixed hardware target.

Input JSON: {"n":..., "rows":[[column,...],...], "syndrome":[0,1,...],
             "weights":[...], "penalty": optional finite number}.
Input promise: syndrome is in image(H); the program does not solve decoding as
preprocessing. Repeated sparse coordinates cancel over GF(2).
"""
from pathlib import Path
import argparse,json,time
from exact_pipeline import compile_exact_instance,exact_graph,allocate_symbolic
from embedding import (make_target,graph_from_witness,graph_witness,CliqueTemplate,
    find_automatic_embedding,allocate_physical_exact,physical_witness,versions)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--g",type=int,default=6)
    parser.add_argument("--target",type=Path,help="saved target with nodes,edges,metadata,coupling_groups")
    parser.add_argument("--method",choices=["auto","template","automatic"],default="auto")
    parser.add_argument("--arithmetic",choices=["certified-float","exact"],default="certified-float")
    parser.add_argument("--seed",type=int,default=7)
    parser.add_argument("--timeout",type=float,default=5.)
    args=parser.parse_args();start=time.perf_counter()
    data=json.loads(args.input.read_text())
    model=compile_exact_instance(data["rows"],data["n"],data["syndrome"],data["weights"],data.get("penalty"))
    if args.target:
        targetw=json.loads(args.target.read_text());target=graph_from_witness(targetw)
        if "coupling_groups" not in targetw:raise ValueError("External target must supply its coupling groups")
        groups=targetw["coupling_groups"]
    else:
        target=make_target(args.g,t=4);targetw=graph_witness(target)
        from dwave.system.coupling_groups import coupling_groups
        groups=list(coupling_groups(target));targetw["coupling_groups"]=groups
    actual=exact_graph(model,structural=False);structure=exact_graph(model,structural=True)
    embedding=None;route={}
    # Counting obstruction concerns the actual QUBO, not its larger cache envelope.
    if len(actual)>len(target) or actual.number_of_edges()>target.number_of_edges():
        status="certified_resource_obstruction"
        route={"reason":"actual interaction graph exceeds target vertex or edge count"}
    else:
        if args.method in ("auto","template"):
            try:
                template=CliqueTemplate(target)
                embedding=template.embed(structure,prune=True)
                route={"method":"explicit-track-template-pruned","capacity":template.capacity,
                       "preprocessing_seconds":template.preprocessing_seconds,"uses_structural_envelope":True}
            except (ValueError,KeyError,NotImplementedError) as exc:
                route={"template_status":"unavailable_or_capacity_exceeded","reason":str(exc),
                       "meaning":"not an infeasibility certificate"}
        if embedding is None and args.method!="template":
            reference=find_automatic_embedding(actual,target,seed=args.seed,timeout=args.timeout)
            route["automatic_status"]=reference["status"]
            route["automatic_seconds"]=reference["elapsed_seconds"]
            if reference["status"]=="valid":
                embedding=reference["embedding"];route["method"]="automatic_actual_graph"
        status="embedding_unresolved" if embedding is None else "valid"
    result={"status":status,"input":data,"model":model,"target":targetw,"route":route,
            "versions":versions(),"input_promise":"syndrome in image(H)"}
    if embedding is not None:
        if args.arithmetic=="certified-float":
            try:
                program=allocate_physical_exact(model,target,embedding,coupling_groups=groups)
                result["program"]=physical_witness(program)
                result["arithmetic_status"]="programmed_binary64_ground_states_certified"
            except (ArithmeticError,OverflowError) as exc:
                result["arithmetic_status"]="exact_program_only_float_fidelity_unresolved"
                result["float_limitation"]=str(exc)
                result["program"]=allocate_symbolic(model,target,embedding,coupling_groups=groups)
        else:
            result["program"]=allocate_symbolic(model,target,embedding,coupling_groups=groups)
            result["arithmetic_status"]="exact_rational_program"
        result["embedding"]={str(i):b for i,b in embedding.items()}
    result["elapsed_seconds"]=time.perf_counter()-start
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False))
    print(json.dumps({"status":status,"arithmetic_status":result.get("arithmetic_status"),
                      "output":str(args.output.resolve()),"elapsed_seconds":result["elapsed_seconds"]},indent=2))

if __name__=="__main__":main()
