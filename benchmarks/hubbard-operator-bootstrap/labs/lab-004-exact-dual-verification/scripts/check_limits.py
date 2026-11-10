#!/usr/bin/env python3
"""Independent analytic checks of the4x4 geometry and Hamiltonian maps."""
from pathlib import Path
import sys, json, itertools
import numpy as np
import scipy.sparse as sp

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'labs/lab-002-moment-sdp/scripts'))
from momentum_pqg import Model


def checks():
    sites=list(itertools.product(range(4),repeat=2));bonds=set()
    for x,y in sites:
        i=x+4*y
        for dx,dy in [(1,0),(0,1)]:
            j=(x+dx)%4+4*((y+dy)%4);bonds.add(tuple(sorted((i,j))))
    assert len(bonds)==32
    hopping=np.zeros((16,16),dtype=int)
    for i,j in bonds:hopping[i,j]=hopping[j,i]=-1
    # Unnormalized Fourier vectors avoid an arbitrary norm convention.
    cos=(1,0,-1,0);disp=np.array([-2*(cos[k%4]+cos[k//4]) for k in range(16)])
    max_fourier_error=0.
    for k in range(16):
        v=np.array([np.exp(2j*np.pi*((k%4)*x+(k//4)*y)/4) for x,y in sites])
        # sites ordered xfirst in this independent check, hence build amplitudes byindex.
        v=np.array([np.exp(2j*np.pi*((k%4)*(i%4)+(k//4)*(i//4))/4) for i in range(16)])
        max_fourier_error=max(max_fourier_error,float(np.max(np.abs(hopping@v-disp[k]*v))))
    assert max_fourier_error<1e-13
    m=Model().build_pqg();kin=np.zeros(m.nvar);kin[:32]=np.tile(disp,2)
    interaction=m.c-kin
    # H_U = (U/V) sum_K v_K^T P_{K,updown} v_K, v_K=(1,...,1).
    reconstructed=np.zeros(m.nvar)
    for block in m.blocks:
        if block['name'].startswith('P_') and block['name'].endswith(', 1)'):
            reconstructed+=.5*np.asarray(block['A'].sum(axis=0)).ravel()
    assert np.max(np.abs(interaction-reconstructed))<1e-13
    # U=0 exact half-filled free energy: negativelevels filled, zeroenergies fill remainingN.
    free_energy=2*sum(sorted(disp)[:8]);assert free_energy==-24
    # t=0: above PSDdecomposition proves>=0; half-filledcheckerboard haszero doubleoccupancy.
    result={'distinct_nn_bonds':len(bonds),'site_degree':sorted(set(np.count_nonzero(hopping,axis=0).tolist())),'fourier_max_residual':max_fourier_error,'dispersion_multiplicities':{str(k):int(sum(disp==k)) for k in sorted(set(disp))},'U0_exact_total_energy':int(free_energy),'atomic_t0_exact_total_energy':0,'interaction_P_decomposition_max_error':float(np.max(np.abs(interaction-reconstructed))),'interpretation':'Analyticgeometryandlimits checked; these checks complement the independent fullmoment-map audit.'}
    return result

if __name__=='__main__':
    r=checks();out=ROOT/'labs/lab-004-exact-dual-verification/results/analytic-checks.json';out.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
