"""Independent reader/checker of saved mathematical and hardware witnesses.

Does not import the compiler, embedding implementation, or minor-embedding
library. Checks exact rational coefficient relations and physical ranges.
"""
from fractions import Fraction as F
from pathlib import Path
from collections import defaultdict,deque
import json,math,time

LAB=Path(__file__).resolve().parents[1];OUT=LAB/"results"

def connected(nodes,edges):
    if not nodes:return False
    adj=defaultdict(set)
    for a,b in edges:adj[a].add(b);adj[b].add(a)
    seen={next(iter(nodes))};queue=deque(seen)
    while queue:
        for v in adj[queue.popleft()]:
            if v in nodes and v not in seen:seen.add(v);queue.append(v)
    return seen==nodes

def verify(target,model,witness):
    nodes=set(target["nodes"]);edges={tuple(sorted(e)) for e in target["edges"]}
    branches={int(i):set(c) for i,c in witness["embedding"].items()}
    assert set(branches)==set(range(len(model["variables"])))
    owners={}
    for i,branch in branches.items():
        assert branch<=nodes and connected(branch,edges)
        for q in branch:assert q not in owners;owners[q]=i
    realized={tuple(sorted((owners[a],owners[b]))) for a,b in edges
              if a in owners and b in owners and owners[a]!=owners[b]}
    qexact=model["exact_coefficients"]
    for i,j,a,b in qexact["quadratic"]:
        if a:assert (i,j) in realized
    h={i:F(*x)/2 for i,x in enumerate(qexact["linear"])}
    j={};constant=F(*qexact["offset"])+sum(h.values(),F(0))
    for a,b,num,den in qexact["quadratic"]:
        q=F(num,den);h[a]+=q/4;h[b]+=q/4;j[a,b]=q/4;constant+=q/4
    companion=witness["numeric_certificate"]["exact_companion"]
    ph={q:F(a,b) for q,a,b in companion["h"]}
    pj={(q,r):F(a,b) for q,r,a,b in companion["J"]}
    alpha=F(witness["scale"])
    assert alpha>0 and set(ph)==set(owners)
    assert set(pj)<=edges
    for i,branch in branches.items():assert sum((ph[q] for q in branch),F(0))==alpha*h[i]
    inter=defaultdict(F);internal=defaultdict(list);wall_offset=F(0)
    for (q,r),value in pj.items():
        a,b=owners[q],owners[r]
        if a==b:
            assert value<0;internal[a].append((q,r));wall_offset-=value
        else:inter[tuple(sorted((a,b)))]+=value
    assert dict(inter)=={e:alpha*v for e,v in j.items()}
    for i,branch in branches.items():
        assert connected(branch,internal[i])
    assert F(*companion["offset"])==alpha*constant+wall_offset
    raw_h={q:F(v) for q,v in witness["h"]}
    raw_j={(q,r):F(v) for q,r,v in witness["J"]}
    error=sum((abs(raw_h.get(q,0)-ph.get(q,0)) for q in set(raw_h)|set(ph)),F(0))
    error+=sum((abs(raw_j.get(e,0)-pj.get(e,0)) for e in set(raw_j)|set(pj)),F(0))
    certificate=witness["numeric_certificate"]
    assert error==F(*certificate["coefficient_error_l1_exact"])
    weights=list(map(F,model["weights"]));margin=F(model["penalty"])-sum(map(abs,weights),F(0))
    assert margin>0
    denominator=max((w.denominator for w in weights),default=1)
    num=math.gcd(*(abs(w.numerator)*(denominator//w.denominator) for w in weights))
    deltaq=min(margin,F(num,denominator)) if num else margin
    loads={i:abs(v) for i,v in h.items()}
    for (a,b),v in j.items():loads[a]+=abs(v);loads[b]+=abs(v)
    margins=[]
    for i,chain in internal.items():
        if chain:
            strength=min(-pj[tuple(sorted(e))]/alpha for e in chain)
            margins.append(strength-loads[i])
    assert all(x>0 for x in margins)
    delta=alpha*min([deltaq]+[2*x for x in margins])
    assert delta==F(*certificate["nonoptimal_gap_lower_bound_exact"])
    assert 2*error<delta
    assert certificate["float_ground_states_certified"]
    hr,jr,gr=[list(map(F,witness["ranges"][k])) for k in ["h","J","coupling_group"]]
    assert all(hr[0]<=v<=hr[1] for v in raw_h.values())
    assert all(jr[0]<=v<=jr[1] for v in raw_j.values())
    for group in target["coupling_groups"]:
        v=sum((raw_j.get(tuple(sorted(edge)),0) for edge in group),F(0))
        assert gr[0]<=v<=gr[1]
    return {"physical_qubits":len(owners),"logical_variables":len(branches),
            "exact_energy_relation":True,"exact_ranges":True,"numeric_ground_fidelity":True}

def main():
    start=time.perf_counter();target=json.loads((OUT/"target_zephyr_g6.json").read_text());reports=[]
    for path in sorted(OUT.glob("witness_*.json")):
        witness=json.loads(path.read_text());method=witness["method"]
        name=path.stem[len("witness_"):-len(method)-1]
        model=json.loads((OUT/f"model_{name}.json").read_text())
        reports.append({"file":path.name,**verify(target,model,witness)})
    result={"witnesses_checked":len(reports),"all_passed":True,"elapsed_seconds":time.perf_counter()-start,"checks":reports}
    (OUT/"independent_witness_validation.json").write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!="checks"},indent=2))

if __name__=="__main__":main()
