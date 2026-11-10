"""Exhaustive checks of pointwise repair, Gibbs bound, conditional law, and compiler."""
import math,json,random,time
from pathlib import Path
import numpy as np
import networkx as nx
from evaluator import evaluate,rooted_tree,json_program
from embedding import ising_energy
from compiler import compile_instance,energy,feasible
OUT=Path(__file__).resolve().parents[1]/'results'


def physical_checks():
    rng=random.Random(9481);records=[];max_violation=0.;max_conditional_error=0.
    for case in range(100):
        sizes=[rng.randint(1,3) for _ in range(4)];embedding={};target=nx.Graph();cursor=0
        for i,k in enumerate(sizes):
            nodes=list(range(cursor,cursor+k));cursor+=k;embedding[i]=nodes
            target.add_nodes_from(nodes);target.add_edges_from(zip(nodes,nodes[1:]))
        h={i:rng.randint(-4,4)/4 for i in embedding};J={}
        for i in embedding:
            for j in embedding:
                if i<j and rng.random()<.75:
                    J[i,j]=rng.choice([-1.,-.75,-.25,.25,.5,1.])
                    # Multiple contacts intentionally exercise fractional splitting.
                    for q in embedding[i]:
                        target.add_edge(q,rng.choice(embedding[j]))
        for beta in [5.,10.,20.]:
            p=evaluate(h,J,0.,target,embedding,beta=beta,groups=[])
            if not p['feasible']:raise AssertionError('unexpected certificate infeasible')
            N=cursor;states=1-2*((np.arange(2**N)[:,None]>>np.arange(N))&1)
            E=np.zeros(len(states))
            for q,v in p['h'].items():E+=v*states[:,q]
            for (q,r),v in p['J'].items():E+=v*states[:,q]*states[:,r]
            E+=p['offset'];roots=p['roots'];repair=np.empty_like(states)
            consistent=np.ones(len(states),dtype=bool)
            wallrhs=np.zeros(len(states))
            for i,chain in embedding.items():
                repair[:,chain]=states[:,roots[i],None]
                consistent&=np.all(states[:,chain]==states[:,roots[i],None],axis=1)
                for edge in p['chain_trees'][i]:
                    q,r=edge;wallrhs+=2*p['edge_margins'][edge]*(states[:,q]!=states[:,r])
            Er=np.zeros(len(states))
            for q,v in p['h'].items():Er+=v*repair[:,q]
            for (q,r),v in p['J'].items():Er+=v*repair[:,q]*repair[:,r]
            Er+=p['offset']
            violation=float(np.max(wallrhs-(E-Er)));max_violation=max(max_violation,violation)
            if violation>1e-10:raise AssertionError('pointwise repair failure')
            mass=np.exp(-beta*(E-E.min()));mass/=mass.sum();broken=float(mass[~consistent].sum())
            if broken>p['classical_break_bound']+1e-11:raise AssertionError('Gibbs bound failure')
            logical=1-2*((np.arange(16)[:,None]>>np.arange(4))&1)
            LE=sum(v*logical[:,i] for i,v in h.items())+sum(v*logical[:,i]*logical[:,j] for (i,j),v in J.items())
            ideal=np.exp(-beta*p['scale']*(LE-LE.min()));ideal/=ideal.sum()
            codes=sum(((1-states[:,roots[i]])//2)*(2**i) for i in range(4))
            cm=np.bincount(codes[consistent],weights=mass[consistent],minlength=16);cm/=cm.sum()
            err=float(np.max(np.abs(cm-ideal)));max_conditional_error=max(max_conditional_error,err)
            if err>1e-11:raise AssertionError('conditional law failure')
            ground=E<=E.min()+1e-10
            if np.any(~consistent&ground):raise AssertionError('broken ground state')
            records.append({'case':case,'physical_qubits':N,'beta':beta,'actual_break_probability':broken,
                            'certificate':p['classical_break_bound'],'conditional_error':err})
    return {'cases':len(records),'max_pointwise_violation_roundoff':max_violation,
            'max_conditional_probability_error':max_conditional_error,'records':records}


def compiler_checks():
    rng=random.Random(6621);records=[]
    for case in range(24):
        n=4;r1=sorted(rng.sample(range(n),3));r2=sorted(rng.sample(range(n),2))
        rows=[r1,r2,sorted(set(r1)^set(r2)),[]]
        truth=[rng.randrange(2) for _ in range(n)];s=[sum(truth[i] for i in r)%2 for r in rows]
        w=[rng.randint(-4,4)/4 for _ in range(n)];w[0]=0.
        model=compile_instance(rows,n,s,w);N=len(model['linear'])
        states=((np.arange(2**N)[:,None]>>np.arange(N))&1)
        energies=np.full(len(states),model['offset'])
        for i,a in enumerate(model['linear']):energies+=a*states[:,i]
        for i,j,a in model['quadratic']:energies+=a*states[:,i]*states[:,j]
        gs=states[np.isclose(energies,energies.min(),atol=1e-12,rtol=0)]
        feasible_errors=[tuple((x>>i)&1 for i in range(n)) for x in range(2**n)
                         if feasible(model,[(x>>i)&1 for i in range(n)])]
        optimum=min(sum(w[i]*e[i] for i in range(n)) for e in feasible_errors)
        if not all(feasible(model,y[:n]) and sum(w[i]*y[i] for i in range(n))==optimum for y in gs):
            raise AssertionError('compiler projected ground states invalid')
        tied={e for e in feasible_errors if sum(w[i]*e[i] for i in range(n))==optimum}
        if {tuple(y[:n]) for y in gs}!=tied:raise AssertionError('tie loss')
        records.append({'case':case,'variables':N,'ground_states':len(gs),'optimum':optimum})
    return {'cases':len(records),'records':records}


def main():
    start=time.perf_counter();result={'physical':physical_checks(),'compiler':compiler_checks()}
    result['elapsed_seconds']=time.perf_counter()-start;result['passed']=True
    (OUT/'theory_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('physical','compiler')},indent=2))
if __name__=='__main__':main()
