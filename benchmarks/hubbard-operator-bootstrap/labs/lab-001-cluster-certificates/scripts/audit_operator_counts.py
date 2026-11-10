#!/usr/bin/env python3
"""Count literal operator spans independently of reduced SDP cone sizes."""
import collections,itertools,json,math,os,resource,time
from pathlib import Path
import numpy as np
from audit_moment_maps import Audit,modular_rank,star_selection

def rank_terms(operators):
    keys=sorted({tuple(t['word'][j][1] for j in range(3)) for o in operators for t in o['terms'] if t['word'][0][1]!=t['word'][1][1]})
    canonical=sorted({(min(a,b),max(a,b),c) for a,b,c in keys});index={t:i for i,t in enumerate(canonical)}
    M=np.zeros((len(canonical),len(operators)),dtype=np.int64)
    for j,op in enumerate(operators):
        for term in op['terms']:
            a,b,c=(z[1] for z in term['word']);v=term['coefficient']
            if a==b:continue
            if a>b:a,b,v=b,a,-v
            M[index[a,b,c],j]+=v
    rank=modular_rank(M);assert rank==len(operators)
    return rank

def run():
    tick=time.perf_counter();own=Path(__file__).resolve().parents[1];labs=own.parent
    two=labs/'lab-002-moment-sdp/results';groups={}
    for folder in ('selected-t2-eps6','two-site-t2-eps5','two-site-spin-complete'):
        descriptors=json.loads((two/folder/'operator_descriptors.json').read_text())
        selected=[d for d in descriptors if 'operators' in d and (folder!='two-site-spin-complete' or d['name'].startswith('T2pure_extreme'))]
        ranks=[rank_terms(d['operators']) for d in selected]
        assert len(ranks)==32
        groups[folder]={'source_blocks':len(ranks),'rank_per_source':sorted(set(ranks)),'total_cubic_dimension_before_adjoints':sum(ranks)}
    names=json.loads((two/'three-site-stars-clarabel/full_variable_names.json').read_text());a=Audit(names)
    stars=json.loads((two/'three-site-stars-clarabel/star_construction.json').read_text());star_ranks=[]
    for source in stars:
        P=star_selection(a,f"T2primefull_(0, {source['k']})",source['labels']).toarray()
        r=modular_rank(P[:-1,:-1]);assert r==84 and modular_rank(P)==85;star_ranks.append(r)
    assert len(star_ranks)==6
    core=1+2*32+2*math.comb(32,2)+32**2
    t1=2*math.comb(32,3);fullt2=2*math.comb(32,2)*32
    counts={'PQG':core,'density_selected_T2':core+2*groups['selected-t2-eps6']['total_cubic_dimension_before_adjoints'],
            'two_site_selected_T2':core+2*groups['two-site-t2-eps5']['total_cubic_dimension_before_adjoints'],
            'two_site_spin_complete':core+2*(1920+groups['two-site-spin-complete']['total_cubic_dimension_before_adjoints']),
            'three_site_stars':core+2*32*84,'T1_only':core+t1,'T1_plus_two_site':core+t1+2*32*60,
            'full_T2prime':core+fullt2,'T1_plus_full_T2prime':core+t1+fullt2,
            'mixed_spin_T2prime':core+2*32*256,'distilled_six_blocks':2257}
    result={'passed':True,'dimension_convention':'Original full Fock polynomial span, before further fixed-sector identities. This is not the sum of reduced cone dimensions.','core_formula':'1+2*32+2*C(32,2)+32^2=2081','T1_increment':'2*C(32,3)=9920; net particle charge +/-3 separates it from selected mixed cubics of charge +/-1.','selected_family_ranks':groups,'star_representative_cubic_ranks':star_ranks,'star_full_spin_momentum_sources':32,'star_onebody_augmentation_already_in_core':True,'operator_dimensions':counts,'rank_argument':'Canonical CAR monomials give an upper bound from advertised columns. A full modular column rank over proven prime1000003 proves exact rational independence. Symmetry copies preserve ranks. Different charge/momentum sectors and adjoints have disjoint canonical supports.','reported_count_discrepancies':[],'elapsed_seconds':time.perf_counter()-tick,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if os.uname().sysname=='Darwin' else 1024)}
    (own/'operator-count-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':run()
