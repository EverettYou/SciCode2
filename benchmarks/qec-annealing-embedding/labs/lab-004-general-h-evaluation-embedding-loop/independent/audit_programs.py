"""Independent saved-witness audit. Imports neither compiler nor evaluator."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D,localcontext,ROUND_FLOOR,ROUND_CEILING
from collections import defaultdict
import json,math,time
import networkx as nx
LAB=Path(__file__).resolve().parents[1]

def pair(a,b):return tuple(sorted((int(a),int(b))))
def dec_lower(x):
    with localcontext() as c:c.prec=60;c.rounding=ROUND_FLOOR;return D(x.numerator)/D(x.denominator)
def dec_upper(x):
    with localcontext() as c:c.prec=60;c.rounding=ROUND_CEILING;return D(x.numerator)/D(x.denominator)
def exp_upper(x):
    with localcontext() as c:c.prec=60;return x.exp().next_plus()
def product_defect_upper(margins,beta):
    with localcontext() as c:
        c.prec=60;c.rounding=ROUND_CEILING;prod=D(1)
        for margin in margins:
            exponent=-D(2)*D(beta)*dec_lower(margin)
            prod*=D(1)+exp_upper(exponent)
        c.rounding=ROUND_FLOOR;recip=D(1)/prod
        c.rounding=ROUND_CEILING;return min(D(1),D(1)-recip)
def quantum_upper(branch_margins,sizes,beta,gamma):
    with localcontext() as c:
        c.prec=60;c.rounding=ROUND_CEILING;total=D(0)
        for margins,size in zip(branch_margins,sizes):
            classical=product_defect_upper(margins,beta)
            x=dec_upper(F(beta)*F(gamma)*size)
            # The dense validation separately checked the cosh and linear lemmas.
            cosh=(exp_upper(x)+exp_upper(-x))/2-D(1)
            total+=min(D(1),classical+min(x,max(D(0),cosh)))
        return min(D(1),total)
def fup(x):
    y=float(x)
    return math.nextafter(y,math.inf) if D.from_float(y)<x else y

def audit(data,label,entry,target,groups):
    p=entry['program'];emb={int(i):list(map(int,v)) for i,v in entry['embedding'].items()}
    owners={};trees={int(i):[pair(*e) for e in v] for i,v in p['chain_trees'].items()}
    roots={int(i):int(v) for i,v in p['roots'].items()}
    h={int(i):F(v) for i,v in p['h']};J={pair(i,j):F(v) for i,j,v in p['J']}
    logical_h={int(i):F(v) for i,v in data['logical_ising']['h']};logical_J={pair(i,j):F(v) for i,j,v in data['logical_ising']['J']}
    assert set(emb)==set(logical_h)
    for i,nodes in emb.items():
        assert nodes and len(set(nodes))==len(nodes)
        for q in nodes:assert q in target and q not in owners;owners[q]=i
        tree=nx.Graph();tree.add_nodes_from(nodes);tree.add_edges_from(trees[i])
        assert nx.is_tree(tree) and roots[i] in nodes
        assert all(target.has_edge(*e) for e in trees[i])
    assert set(h)==set(owners)
    assert all(target.has_edge(*e) and e[0] in owners and e[1] in owners for e in J)
    chain_edges={e for v in trees.values() for e in v}
    for e,v in J.items():
        if owners[e[0]]==owners[e[1]]:assert e in chain_edges and v<0
    assert all(e in J for e in chain_edges)
    # Actual coefficient and coupling-group constraints checked exactly.
    bounds=p['ranges'];hr=list(map(F,bounds['h']));jr=list(map(F,bounds['J']));gr=list(map(F,bounds['group']))
    assert all(hr[0]<=v<=hr[1] for v in h.values())
    assert all(jr[0]<=v<=jr[1] for v in J.values())
    assert all(gr[0]<=sum((J.get(e,F(0)) for e in g),F(0))<=gr[1] for g in groups)
    eh=defaultdict(F);eJ=defaultdict(F);external_load={q:abs(h[q]) for q in owners}
    for q,v in h.items():eh[owners[q]]+=v
    chain_const=F(0)
    for (q,r),v in J.items():
        i,j=owners[q],owners[r]
        if i==j:chain_const+=v
        else:eJ[pair(i,j)]+=v;external_load[q]+=abs(v);external_load[r]+=abs(v)
    assert set(eJ)==set(logical_J)
    alpha=F(p['scale']);rho=sum((abs(eh[i]-alpha*v) for i,v in logical_h.items()),F(0))
    rho+=sum((abs(eJ[e]-alpha*v) for e,v in logical_J.items()),F(0))
    offset_error=abs(F(p['offset'])+chain_const-alpha*F(data['logical_ising']['offset']))
    gap=F(*data['model']['numeric_certificate']['nonoptimal_gap_lower_bound_exact'])
    assert 2*rho<alpha*gap
    margins=[];branch_margins=[];sizes=[]
    for i,nodes in emb.items():
        root=roots[i];adj={q:[] for q in nodes}
        for q,r in trees[i]:adj[q].append(r);adj[r].append(q)
        parents={root:None};order=[root]
        for q in order:
            for r in adj[q]:
                if r not in parents:parents[r]=q;order.append(r)
        sub={q:external_load[q] for q in nodes};bm=[]
        for q in reversed(order[1:]):
            e=pair(q,parents[q]);delta=-J[e]-sub[q]
            assert delta>0,(data['name'],label,'nonpositive margin')
            bm.append(delta);margins.append(delta);sub[parents[q]]+=sub[q]
        if bm:branch_margins.append(bm);sizes.append(len(nodes))
    classical=product_defect_upper(margins,int(p['beta']))
    assert classical<D(str(p['epsilon_requested']))
    quantum={str(g):fup(quantum_upper(branch_margins,sizes,int(p['beta']),g)) for g in [0.,1e-5,1e-4,1e-3]}
    first_scale=F(data['selected']['first']['program']['scale'])
    return {'instance':data['name'],'split':data['input']['split'],'selection':label,'physical_qubits':len(owners),'scale':float(alpha),'exact_scale_difference_from_first':str(alpha-first_scale),'scale_at_least_first_exact':alpha>=first_scale,'static_ground_fidelity':True,'minimum_exact_margin':str(min(margins,default=F(0))),'consistent_nonconstant_coefficient_error':str(rho),'consistent_offset_error':str(offset_error),'thermal_rounding_tv_upper':fup(dec_upper(F(int(p['beta']))*rho)),'classical_defect_upper':fup(classical),'quantum_defect_upper':quantum}

def main():
    start=time.perf_counter();td=json.loads((LAB/'results/target.json').read_text());tw=td['target'];G=nx.Graph();G.add_nodes_from(tw['nodes']);G.add_edges_from(tw['edges'])
    groups=[[pair(*e) for e in group] for group in td['coupling_groups']]
    rows=[];files=sorted((LAB/'results').glob('*_n*_s*.json'))
    for path in files:
        data=json.loads(path.read_text())
        if data['status']!='ok':continue
        useG,usegroups=G,groups
        if data['input'].get('extension')=='synthetic_defects':
            defect=json.loads((LAB/'results/defect_target.json').read_text());useG=nx.Graph()
            useG.add_nodes_from(defect['target']['nodes']);useG.add_edges_from(defect['target']['edges'])
            usegroups=[[pair(*e) for e in group] for group in defect['coupling_groups']]
        for label,entry in data['selected'].items():rows.append(audit(data,label,entry,useG,usegroups))
    lp_files=sorted((LAB/'results/lp').glob('*.json'))
    for path in lp_files:
        lpdata=json.loads(path.read_text())
        if 'selected' not in lpdata:continue
        original=json.loads((LAB/'results'/path.name).read_text())
        rows.append(audit(original,'lp_selected',lpdata['selected'],G,groups))
    lp_refinement_files=sorted((LAB/'results/lp_refinement').glob('*.json'))
    for path in lp_refinement_files:
        refined=json.loads(path.read_text())
        if refined.get('status')!='ok':continue
        original=json.loads((LAB/'results'/path.name).read_text())
        for label,entry in refined['selected'].items():rows.append(audit(original,'lp_refinement_'+label,entry,G,groups))
    summary={'status':'pass','lp_refinement_instances':len(lp_refinement_files),'lp_instances':len(lp_files),'instances':len(files),'programs':len(rows),'outward_arithmetic':'exact Fraction of actual binary64 coefficients; 60-digit Decimal lower margins and outward exponential/product enclosures','maximum_classical_bound':max(x['classical_defect_upper'] for x in rows),'maximum_thermal_rounding_tv':max(x['thermal_rounding_tv_upper'] for x in rows),'guided_exact_scale_decreases':sum(not r['scale_at_least_first_exact'] for r in rows if r['selection'] in ['guided_pool','guided_pruned']),'seconds':time.perf_counter()-start,'records':rows}
    (LAB/'results/independent_program_audit.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='records'},indent=2))
if __name__=='__main__':main()
