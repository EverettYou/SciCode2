"""Exact finite-state check of local flow/gap and warm-start readout obstruction."""
import json,math,time
from pathlib import Path
import numpy as np
import networkx as nx
from scipy.sparse import coo_matrix
from scipy.linalg import eigh
from models import compile_model
from compiler import model_graph
from embedding import qubo_to_ising
from evaluator import evaluate,json_program
from dynamics import certificate
from repair_api import REPAIR
OUT=Path(__file__).resolve().parents[1]/'results'


def main():
    start=time.perf_counter();data={'n':3,'rows':[[0,1,2]],'syndrome':[0],'weights':[.5,-.25,.25]};model=compile_model(data['rows'],3,[0],data['weights'],'balanced')
    h,J,c=qubo_to_ising(model['linear'],model['quadratic'],model['offset']);L=len(h);target=nx.Graph();target.add_nodes_from(range(L+1));embedding={i:[i] for i in h};embedding[0]=[0,L];target.add_edge(0,L)
    for k,(i,j) in enumerate(J):
        q=(0 if k%2 else L) if i==0 else i;r=(0 if k%2 else L) if j==0 else j;target.add_edge(q,r)
    wit=REPAIR.witness(data['rows'],3,data['weights']);records=[]
    for beta in [2.,5.,10.]:
        p=evaluate(h,J,c,target,embedding,beta=beta,groups=[]);pw=json_program(p);N=p['physical_qubits'];S=2**N;bits=((np.arange(S)[:,None]>>np.arange(N))&1).astype(np.int16);spins=2*bits-1
        E=np.full(S,p['offset'])
        for q,v in p['h'].items():E+=v*spins[:,q]
        for (q,r),v in p['J'].items():E+=v*spins[:,q]*spins[:,r]
        pi=np.exp(-beta*(E-E.min()));pi/=pi.sum();row=[];col=[];val=[];diag=np.ones(S);states=np.arange(S)
        for q in range(N):
            flipped=states^(1<<q);prob=1/(N*(1+np.exp(beta*(E[flipped]-E))));row.extend(states);col.extend(flipped);val.extend(prob);diag-=prob
        row.extend(states);col.extend(states);val.extend(diag);P=coo_matrix((val,(row,col)),shape=(S,S)).tocsr()
        sym=(np.sqrt(pi)[:,None]*P.toarray())/np.sqrt(pi)[None,:];err=float(np.max(abs(sym-sym.T)))
        if err>1e-12:raise AssertionError('reversibility')
        lam=float(eigh(sym,subset_by_index=[S-2,S-2],eigvals_only=True)[0]);gap=1-lam;root=p['roots'][0];plus=spins[:,root]==1;pplus=float(pi[plus].sum());broken=spins[:,0]!=spins[:,L];pbreak=float(pi[broken].sum())
        qflow=float(sum(pi[s]*P[s,s^(1<<root)] for s in states[plus]));rayleigh=qflow/(pplus*(1-pplus));cert=certificate(data,wit,embedding,pw)
        if qflow>pbreak/N+1e-13 or gap>rayleigh+1e-11:raise AssertionError('flow/gap theorem')
        if cert['strongest'] and gap>cert['strongest']['gap_upper_per_attempt']+1e-11:raise AssertionError('cheap gap certificate')
        orig=bits[:,[p['roots'][i] for i in range(3)]];feasible=orig.sum(axis=1)%2==0;cost=orig@np.array(data['weights']);optimum=cost[feasible].min();optimal=feasible&(cost==optimum)
        if np.any(optimal&plus):raise AssertionError('reference optimum unexpectedly has root1')
        dist=pi*plus/pplus;readouts=[]
        for step in range(1,1001):
            dist=P.T@dist
            if step in [1,10,100,1000]:
                success=float(dist[optimal].sum());upper=min(1.,step*qflow/pplus)
                if success>upper+1e-11:raise AssertionError('warm-root readout upper bound')
                readouts.append({'attempts':step,'actual_optimum_probability':success,'crossing_upper_bound':upper})
        records.append({'beta':beta,'physical_sites':N,'gap':gap,'exact_rayleigh_upper':rayleigh,'actual_chain_break':pbreak,
                        'root_flow':qflow,'cheap_certificate':cert['strongest'],'warm_wrong_root_readout':readouts,'symmetry_error':err})
    (OUT/'dynamics_checks.json').write_text(json.dumps({'status':'pass','records':records,'elapsed_seconds':time.perf_counter()-start},indent=2)+'\n');print('exact dynamics checks passed',len(records))
if __name__=='__main__':main()
