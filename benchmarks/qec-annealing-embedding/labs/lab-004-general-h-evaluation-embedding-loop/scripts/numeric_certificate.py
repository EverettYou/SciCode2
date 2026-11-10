"""Exact-rational audit of final binary64 physical programs against compiler model."""
from fractions import Fraction as F
import math
from evaluator import PRIOR,rooted_tree
from embedding import exact_model_to_ising,edge_key


def rational_audit(model,program,embedding,target,groups):
    h,J,c=exact_model_to_ising(model); alpha=F(program['scale'])
    owner={q:i for i,ch in embedding.items() for q in ch}
    roots={int(i):q for i,q in program['roots'].items()}
    trees={int(i):[tuple(e) for e in es] for i,es in program['chain_trees'].items()}
    ph={q:F(v) for q,v in program['h']};pj={(q,r):F(v) for q,r,v in program['J']}
    contacts={pair:[] for pair in J}
    for q in sorted(owner):
        for r in sorted(target[q]):
            pair=edge_key(owner[q],owner[r]) if r in owner else None
            if q<r and pair in contacts:contacts[pair].append((q,r))
    ih={q:F(0) for q in owner};ij={}
    for i,r in roots.items():ih[r]=alpha*h[i]
    for pair,sites in contacts.items():
        for edge in sites:
            if program.get('allocation')=='lp':
                total=sum((pj[e] for e in sites),F(0))
                ij[edge]=alpha*J[pair]*(pj[edge]/total) if total else alpha*J[pair]/len(sites)
            else:ij[edge]=alpha*J[pair]/len(sites)
    chainset={tuple(e) for es in trees.values() for e in es}
    for edge in chainset:ij[edge]=pj[edge] # actual chain strengths define exact parameters
    rho=sum(abs(ph.get(q,F(0))-ih.get(q,F(0))) for q in set(ph)|set(ih))
    rho+=sum(abs(pj.get(e,F(0))-ij.get(e,F(0))) for e in set(pj)|set(ij))
    ideal_load={q:abs(ih[q]) for q in owner};actual_load={q:abs(ph[q]) for q in owner}
    for edge in set(ij)-chainset:
        for q in edge:ideal_load[q]+=abs(ij[edge]);actual_load[q]+=abs(pj[edge])
    margins=[];actual_margins=[]
    for i,nodes in embedding.items():
        _,parent,order=rooted_tree(trees[i],nodes,roots[i])
        sub={q:ideal_load[q] for q in nodes};subactual={q:actual_load[q] for q in nodes}
        for q in reversed(order[1:]):sub[parent[q]]+=sub[q];subactual[parent[q]]+=subactual[q]
        for q in order[1:]:
            e=edge_key(q,parent[q]);margins.append(-ij[e]-sub[q]);actual_margins.append(-pj[e]-subactual[q])
    g=alpha*F(*model['numeric_certificate']['nonoptimal_gap_lower_bound_exact'])
    delta=min([g]+[2*x for x in margins]);positive=all(x>0 for x in margins)
    ranges=program['ranges'];viol=[]
    for tag,coeff in [('h',ph),('J',pj)]:
        lo,hi=map(F,ranges[tag])
        for key,v in coeff.items():
            if not lo<=v<=hi:viol.append([tag,str(key)])
    if ranges['group'] is not None:
        lo,hi=map(F,ranges['group'])
        for idx,group in enumerate(groups):
            v=sum((pj.get(tuple(e),F(0)) for e in group),F(0))
            if not lo<=v<=hi:viol.append(['group',idx])
    beta=F(program['beta'])
    # Simple conservative classical Gibbs perturbation bound, avoiding any
    # claim that sums of rounded contacts exactly equal logical coefficients.
    correction=min(1.,math.expm1(float(2*beta*rho)))
    return {'float_projected_ground_states_certified':positive and not viol and 2*rho<delta,
            'ideal_repair_margins_positive':positive,'actual_repair_margins_positive':all(x>0 for x in actual_margins),
            'coefficient_error_l1_exact':[rho.numerator,rho.denominator],
            'coefficient_error_l1':float(rho),'physical_nonoptimal_gap_lower_bound_exact':[delta.numerator,delta.denominator],
            'physical_nonoptimal_gap_lower_bound':float(delta),
            'actual_margin_min':float(min(actual_margins)) if actual_margins else None,
            'range_violations':viol,'logical_gibbs_tv_rounding_correction':correction,
            'interpretation':'exact logical rational model, actual binary64 alpha and chain couplings as exact parameters; interbranch and field rounding bounded in L1'}
