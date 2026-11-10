"""Exact extreme-weight checks and a common-target decoding pause witness."""
from pathlib import Path
from fractions import Fraction as F
import itertools,json,math,time
import numpy as np
from scipy.linalg import expm
from compiler import compile_instance
from exact_pipeline import compile_exact_instance,allocate_symbolic,exact_graph
from embedding import make_target,allocate_physical_exact,physical_witness,verify_embedding
from run_experiments import program_certificate

LAB=Path(__file__).resolve().parents[1];OUT=LAB/"results"

def energy_rat(coeff,assignment):
    return (F(*coeff["offset"])+sum((F(a,b)*assignment[i] for i,(a,b) in enumerate(coeff["linear"])),F(0))
            +sum((F(a,b)*assignment[i]*assignment[j] for i,j,a,b in coeff["quadratic"]),F(0)))

def find_path(target):
    for a in sorted(target):
        for b in sorted(target[a]):
            for c in sorted(target[b]):
                if c==a:continue
                for d in sorted(target[c]):
                    if d not in (a,b):return [a,b,c,d]
    raise RuntimeError("target has no four-vertex path")

def symbolic_energy(program,spins):
    return (F(*program["offset"])+sum((F(a,b)*spins[q] for q,a,b in program["h"]),F(0))
            +sum((F(a,b)*spins[q]*spins[r] for q,r,a,b in program["J"]),F(0)))

def matrix(program):
    nodes=sorted(program["h"]);pos={q:i for i,q in enumerate(nodes)};size=1<<len(nodes)
    states=np.arange(size);z=1-2*((states[:,None]>>np.arange(len(nodes)))&1)
    diag=sum((h*z[:,pos[q]] for q,h in program["h"].items()),np.zeros(size))
    diag+=sum((j*z[:,pos[q]]*z[:,pos[r]] for (q,r),j in program["J"].items()),np.zeros(size))
    H=np.diag(diag)
    for i in range(len(nodes)):H[states,states^(1<<i)]-=.02
    return H,nodes,z

def main():
    start=time.perf_counter();target=make_target(6);path=find_path(target)
    native={0:[path[1]],1:[path[2]]};encoded={0:path[:2],1:path[2:]}
    reports=[]
    for index,weights in enumerate([[1e-300,0.],[1e308,-1e308],[1e308,1e-300],[5e-324,0.]]):
        model=compile_exact_instance([[0,1]],2,[1],weights)
        prog=allocate_symbolic(model,target,encoded)
        costs={tuple(e):sum(F(w)*b for w,b in zip(weights,e)) for e in itertools.product((0,1),repeat=2) if sum(e)%2==1}
        optimum=min(costs.values())
        logical_min=min(energy_rat(model["exact_coefficients"],e) for e in itertools.product((0,1),repeat=2))
        assert logical_min==optimum
        physical=[]
        for values in itertools.product((-1,1),repeat=4):
            spins=dict(zip(path,values));value=symbolic_energy(prog,spins)
            consistent=spins[path[0]]==spins[path[1]] and spins[path[2]]==spins[path[3]]
            e=((spins[path[0]]+1)//2,(spins[path[2]]+1)//2)
            physical.append((value,consistent,e))
        pmin=min(v for v,_,_ in physical)
        assert pmin==F(*prog["scale"])*optimum
        assert all(c and e in costs and costs[e]==optimum for v,c,e in physical if v==pmin)
        groups=prog.pop("coupling_groups");prog["coupling_groups_reference"]="target_zephyr_g6.json"
        reports.append({"case":index,"weights":weights,"physical_states_checked":16,
                        "logical_optimum_exact":[optimum.numerator,optimum.denominator],"all_ground_states_faithful":True})
        (OUT/f"exact_extreme_{index}.json").write_text(json.dumps({"model":model,"program":prog},indent=2))
    rejected=False
    try:compile_instance([[0,1]],2,[1],[1e-300,0.],penalty=1.)
    except ArithmeticError:rejected=True
    assert rejected
    # Verify an ordinary small exact model agrees with the floating compiler's
    # authoritative companion, then bridge the theorem to actual Zephyr edges.
    ordinary=compile_instance([[0,1,2],[0,1]],3,[1,0],[-1.,.5,0.],penalty=4.)
    exact=compile_exact_instance([[0,1,2],[0,1]],3,[1,0],[-1.,.5,0.],penalty=4.)
    assert all(ordinary["exact_coefficients"][k]==exact["exact_coefficients"][k] for k in ["linear","quadratic","offset"])
    model=compile_instance([[0,1]],2,[1],[0.,0.],penalty=.0002)
    programs={"native":allocate_physical_exact(model,target,native),
              "encoded":allocate_physical_exact(model,target,encoded,chain_margin=1.-.0001)}
    omega=math.sqrt(.0001**2+4*.02**2);duration=math.pi/(2*omega)
    comparisons={}
    for name,program in programs.items():
        emb=native if name=="native" else encoded
        assert verify_embedding(exact_graph(model),target,emb)["valid"]
        Hamiltonian,nodes,z=matrix(program);U=expm(-1j*duration*Hamiltonian);pos={q:i for i,q in enumerate(nodes)}
        e0=((z[:,pos[emb[0][0]]]+1)//2);e1=((z[:,pos[emb[1][0]]]+1)//2)
        good=e0!=e1
        allzero=(1<<len(nodes))-1  # e=(1+z)/2: e=0 means z=-1
        optimal_bits={q:0 if i==1 else 1 for i,branch in emb.items() for q in branch}
        optimal_index=sum(optimal_bits[q]<<pos[q] for q in nodes)
        repair=float(np.sum(np.abs(U[good,allzero])**2));retention=float(np.sum(np.abs(U[good,optimal_index])**2))
        certificate=program_certificate(program,emb,gamma=.02,duration=duration)
        comparisons[name]={"representative_repair_probability":repair,"representative_retention_probability":retention,
                           "certificate":certificate,"physical_qubits":len(nodes)}
        if name=="encoded":
            assert repair<=certificate["initially_zero_event_probability_bound"]+1e-13
            assert retention>=1-certificate["initially_zero_event_probability_bound"]-1e-13
        witness=physical_witness(program);witness.pop("coupling_groups")
        witness["coupling_groups_reference"]="target_zephyr_g6.json";witness["embedding"]={str(i):v for i,v in emb.items()}
        (OUT/f"pause_{name}_witness.json").write_text(json.dumps({"model":model,"program":witness},indent=2))
    result={"all_passed":True,"extreme_weight_cases":reports,"unsafe_float_expansion_rejected":rejected,
            "target_path":path,"A":.04,"B":2.,"Gamma":.02,"duration":duration,
            "schedule":"constant closed-system hold; hbar=1; no preparation/ramp included",
            "comparisons":comparisons,"elapsed_seconds":time.perf_counter()-start}
    (OUT/"exact_and_pause_validation.json").write_text(json.dumps(result,indent=2))
    print(json.dumps({"all_passed":True,"path":path,"comparisons":comparisons,"elapsed_seconds":result["elapsed_seconds"]},indent=2))

if __name__=="__main__":main()
