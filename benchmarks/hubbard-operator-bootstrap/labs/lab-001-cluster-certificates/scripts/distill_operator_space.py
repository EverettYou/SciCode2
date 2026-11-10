#!/usr/bin/env python3
"""Turn a compressed full-T2 certificate into an explicitly counted O space.

Uses exact integer Gram factors from the certificate, then exact rational span
relations and independent modular rank lower bounds. The declared O consists
of the entire PQG core plus symmetry-closed cubic directions and their adjoints.
"""
from __future__ import annotations
import argparse,collections,fractions,itertools,json,math,os,resource,time
from pathlib import Path
import numpy as np
import scipy.sparse as sp
from audit_moment_maps import load_projections,mode_transform,momadd,momsub,modular_rank
F=fractions.Fraction

def primitive(v):
    v=tuple(map(int,v));g=math.gcd(*v)
    if not g:return None
    # Canonical first nonzero coefficient positive.
    first=next(z for z in v if z);g=g if first>0 else -g
    return tuple(z//g for z in v)

def exact_span(columns):
    """Independent integer columns plus explicit rational dependency relations."""
    basis=[];independent=[];relations=[]
    for j,col in enumerate(columns):
        v={i:F(z) for i,z in enumerate(col) if z};comb={j:F(1)}
        for pivot,b,bc in basis:
            factor=v.get(pivot,0)
            if not factor:continue
            for i,z in b.items():
                value=v.get(i,0)-factor*z
                if value:v[i]=value
                else:v.pop(i,None)
            for i,z in bc.items():
                value=comb.get(i,0)-factor*z
                if value:comb[i]=value
                else:comb.pop(i,None)
        if not v:
            assert comb[j]==1
            relations.append({'dependent_column':j,'coefficients':[[i,str(z.numerator),str(z.denominator)] for i,z in sorted(comb.items())]})
        else:
            pivot=min(v);scale=v[pivot];v={i:z/scale for i,z in v.items()};comb={i:z/scale for i,z in comb.items()}
            basis.append((pivot,v,comb));independent.append(j)
    # Recheck all returned upper-bound relations independently using integer
    # common denominators, with no floating arithmetic.
    for relation in relations:
        cs=[(i,F(int(n),int(d))) for i,n,d in relation['coefficients']];den=math.lcm(*(z.denominator for i,z in cs));ints=[(i,int(z*den)) for i,z in cs]
        for row in range(len(columns[0])):assert sum(columns[i][row]*z for i,z in ints)==0
    return independent,relations

def make_groups():
    groups=collections.defaultdict(list)
    for a,b in itertools.combinations(range(32),2):
        for c in range(32):groups[a//16+b//16-c//16,momsub(momadd(a%16,b%16),c%16)].append((a,b,c))
    return dict(groups)

def transformed_mode(p,rotation,reflect,spin):
    for _ in range(rotation):p=mode_transform(p,'rot')
    if reflect:p=mode_transform(p,'rx')
    if spin:p=mode_transform(p,'spin')
    return p


def direction_blocks(inp,exact):
    if (inp/'source_blocks.json').exists():
        for entry in json.loads((inp/'source_blocks.json').read_text()):
            data=np.load(inp/entry['projection']);R=data['R_integer'];n=entry['n_cubic_directions']
            assert np.issubdtype(R.dtype,np.integer) and R.shape[1]==n+1 and entry['augmentation_last_column']
            linear=np.zeros(R.shape[0],dtype=np.int64);linear[-1]=1<<entry['bits'];assert np.array_equal(R[:,-1],linear)
            block={'name':entry['name'],'prefix':entry['name'],'direction_bits':entry['bits']}
            yield block,{'source_name':entry['raw_source_name']},sp.csr_matrix(R),np.eye(R.shape[1],n,dtype=np.int64)
    elif (inp/'adaptive_cuts.json').exists():
        metadata=json.loads((inp/'adaptive_cuts.json').read_text());oracle=Path(metadata['oracle_directory']);projs={m['name']:m for m in load_projections(oracle)}
        for cut in metadata['cuts']:
            meta=projs[cut['source_name']];W=sp.load_npz(oracle/meta['projection']).astype(np.int64).tocsr();cp=inp/cut['file']
            if not cp.exists():cp=Path(metadata['cut_directory'])/cut['file']
            K=np.load(cp)['K'][:,None];block={'name':cut['source_name'],'prefix':cut['source_prefix'],'cut_index':cut['index'],'direction_bits':cut['bits']}
            yield block,meta,W,K
    else:
        projs={m['name']:m for m in load_projections(inp)}
        for block in json.loads((inp/'blocks.json').read_text()):
            if not block['name'].startswith('T2primefull_'):continue
            meta=projs[block['name']];W=sp.load_npz(inp/meta['projection']).astype(np.int64).tocsr();K=np.load(exact/(block['prefix']+'_factor_int.npy'))
            yield block,meta,W,K

def run(inp,exact,out):
    inp=Path(inp).resolve();exact=Path(exact).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True);tick=time.perf_counter()
    groups=make_groups();indices={key:{t:i for i,t in enumerate(ts)} for key,ts in groups.items()};projections={m['name']:m for m in load_projections(inp)}
    vectors=collections.defaultdict(dict);sources=[];total_active=0
    for block,meta,W,K in direction_blocks(inp,exact):
        source=meta['source_name'];import ast
        key=ast.literal_eval(source[len('T2primefull_'):])
        assert np.issubdtype(K.dtype,np.integer)
        maxw=max(map(abs,map(int,W.data)),default=0);maxk=max(map(abs,map(int,K.ravel())),default=0)
        assert W.shape[1]*maxw*maxk<2**63,'Integer map product may overflow'
        raw=W@K;ncubic=len(groups[key]);assert raw.shape[0] in [ncubic,ncubic+1]
        for j in range(raw.shape[1]):
            col=tuple(map(int,raw[:ncubic,j]));v=primitive(col)
            if v is None:continue
            source_id=len(sources);total_active+=1;sources.append({'source_block':block['name'],'source_prefix':block['prefix'],'factor_column':j,'cut_index':block.get('cut_index'),'direction_bits':block.get('direction_bits'),'raw_cubic_multiple_of_primitive':str(next(z for z in col if z)//next(z for z in v if z)),'source_charge_momentum':key,'removed_linear_coefficient':str(int(raw[-1,j])) if raw.shape[0]>ncubic else '0','cubic_terms':[[*t,str(z)] for t,z in zip(groups[key],v) if z]})
            for rotation,reflect,spin in itertools.product(range(4),range(2),range(2)):
                mapped=[]
                for (a,b,c),z in zip(groups[key],v):
                    if not z:continue
                    a,b,c=(transformed_mode(p,rotation,reflect,spin) for p in (a,b,c))
                    if a>b:a,b,z=b,a,-z
                    mapped.append(((a,b,c),z))
                t0=mapped[0][0];newkey=(t0[0]//16+t0[1]//16-t0[2]//16,momsub(momadd(t0[0]%16,t0[1]%16),t0[2]%16))
                dense=[0]*len(groups[newkey])
                for t,z in mapped:dense[indices[newkey][t]]+=z
                newv=primitive(dense);entry=vectors[newkey].setdefault(newv,[]);entry.append([source_id,rotation,reflect,spin])
    allops=[];ranks=[];relations_out=[]
    for key in sorted(vectors):
        cols=list(vectors[key]);A=np.array(cols,dtype=np.int64).T;rank_lower=modular_rank(A)
        chosen,relations=exact_span(cols);assert len(chosen)==rank_lower
        offset=len(allops)
        for j,col in enumerate(cols):allops.append({'charge_momentum':key,'column_in_sector':j,'selected_basis':j in chosen,'terms':[[*t,str(z)] for t,z in zip(groups[key],col) if z],'generated_by':vectors[key][col]})
        ranks.append({'charge_momentum':key,'raw_cubic_dimension':len(groups[key]),'distinct_primitive_generators':len(cols),'exact_rank':len(chosen),'modular_rank_lower':rank_lower,'selected_basis_column_indices':chosen,'global_operator_offset':offset,'dependent_relations':len(relations)})
        relations_out.append({'charge_momentum':key,'relations':relations})
    rank=sum(z['exact_rank'] for z in ranks);rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if os.uname().sysname=='Darwin' else 1024)
    verification=json.loads((exact/'verification.json').read_text())
    report={'compressed_certificate':str(inp),'exact_certificate_directory':str(exact),'exact_total_energy_lower_bound':verification['reported_total_energy_lower_bound'],'active_source_T2_factor_columns':total_active,'symmetry_group_order':16,'distinct_closed_cubic_generators':len(allops),'exact_closed_cubic_span_dimension':rank,'adjoint_span_dimension':rank,'PQG_core_dimension':2081,'declared_operator_space_dimension':2081+2*rank,'dimension_convention':'Original full Fock-space polynomial span, before further fixed-sector identities. Cubic net+1 and adjoint net-1 have disjoint canonical monomial supports; PQG has degree<=2.','rank_proof':'Exact rational dependency relations provide upper bounds; Gaussian elimination modulo proven prime1000003 gives matching lower bounds in every charge/momentum sector.','operator_definition':'O=span{I,allc,allc†,allpairannihilators/creators,allc†c,selected_basisclosedcubicpolynomials,theiradjoints}.','bound_proof':'Every retained dual square has its cubic part in this closed span and its linear part in PQG. All coefficient-residual positivity SOS operators have degree<=2 and lie in PQG. D4/spin closure permits certificate twirling, hence the inherited exact lower bound is valid for the literal operator-space relaxation.','elapsed_seconds':time.perf_counter()-tick,'peak_rss_bytes':rss,'sector_ranks':ranks}
    (out/'operators.json').write_text(json.dumps(allops,indent=2)+'\n');(out/'source_columns.json').write_text(json.dumps(sources,indent=2)+'\n');(out/'span_relations.json').write_text(json.dumps(relations_out,indent=2)+'\n');(out/'operator_space.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='sector_ranks'},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('compressed_input');p.add_argument('exact_certificate');p.add_argument('output');a=p.parse_args();run(a.compressed_input,a.exact_certificate,a.output)
