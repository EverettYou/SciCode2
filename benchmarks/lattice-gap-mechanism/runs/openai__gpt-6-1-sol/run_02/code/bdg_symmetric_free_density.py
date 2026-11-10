"""Saved form of the originally inline shared-linewidth/free-density diagnostic.

Run after bdg_symmetric_poles.py. This preserves the exact model, starting point,
bounds, optimizer settings, and output of the diagnostic used in the analysis.
No claim that its fitted density is independently established by normalized STS.
"""
import json
import numpy as np
from scipy.optimize import least_squares
import bdg_symmetric_poles as b


def main():
    best=json.load(open(b.ROOT/'data/bdg_symmetric_results.json'))['best']['params']
    initial=[*best,.38]
    def model(p):
        return b.model(p[:-1],p[-1])
    result=least_squares(
        lambda p:model(p)-b.y,initial,
        bounds=([.1,.1,-.06,.015,.1,-.08,-.001,.1],
                [2.5,6,.06,.8,15,.2,.003,.8]),
        max_nfev=200,x_scale='jac',ftol=1e-10,xtol=1e-10)
    rms=np.sqrt(result.fun@result.fun/(len(b.x)-len(initial)))
    print('free nu',result.x,'rms',rms)
    np.savez(b.ROOT/'data/bdg_symmetric_free_nu.npz',
             params=result.x,bias=b.x,fit=model(result.x),observed=b.y)


if __name__=='__main__':
    main()
