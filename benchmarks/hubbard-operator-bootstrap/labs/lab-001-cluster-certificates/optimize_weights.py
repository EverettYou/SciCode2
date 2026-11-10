#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.sparse.linalg import eigsh
import cluster_bound as cb

p=argparse.ArgumentParser();p.add_argument('--shape',choices=['2x3','2x4-open'],default='2x3');p.add_argument('--output',required=True);args=p.parse_args()
w=3 if args.shape=='2x3' else 4;h=2
sites,edges=cb.geometry(w,h);n=len(sites);log=[]

def weights(x):
    if w==3:
        ue,ve=x
        us=np.array([ue if xx in [0,2] else 24-2*ue for xx,yy in sites])
        ts=np.array([1.5 if axis==0 else (ve if sites[i][0] in [0,2] else 6-2*ve) for i,j,axis in edges])
    else:
        ue,ve,te=x
        us=np.array([ue if xx in [0,3] else 16-ue for xx,yy in sites])
        ts=np.array([(te if min(sites[i][0],sites[j][0]) in [0,2] else 4-2*te) if axis==0 else (ve if sites[i][0] in [0,3] else 4-ve) for i,j,axis in edges])
    return ts,us

def obj(x):
    t,u=weights(x);A=cb.build_block(n,n//2,n//2,edges,t,u)
    d=float(eigsh(A,k=1,which='SA',tol=1e-10,return_eigenvectors=False)[0]);log.append({'x':list(x),'ritz':d});return -d

x0=[8,2] if w==3 else [8,2,4/3]
bounds=[(0,12),(0,3)] if w==3 else [(0,16),(0,4),(0,2)]
tick=time.perf_counter();r=minimize(obj,x0,bounds=bounds,method='Nelder-Mead',options={'xatol':1e-7,'fatol':1e-9,'maxiter':100})
# Dyadic coefficients ensure exact decomposition and exact represented matrix.
x=np.round(r.x*1024)/1024;t,u=weights(x)
z={'shape':args.shape,'weights':t.tolist(),'us':u.tolist(),'variables':x.tolist(),'target_ritz':16/n*(-obj(x))+32,'seconds':time.perf_counter()-tick,'optimizer':str(r),'log':log}
Path(args.output).write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z,indent=2))
