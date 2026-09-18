"""Verify saved certificates without importing CVXPY or trusting saved objectives."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from physical import objectives, full_record_formula
from certificates import verify


def check(path):
    path=Path(path)
    summary=json.loads((path/'summary.json').read_text())
    n,g,eta=(summary[k] for k in ['n','g','eta'])
    cs=objectives(n,g,eta,dense=True)
    if len(cs)!=len(summary['rows']):raise ValueError('missing records')
    lower=upper=0.
    seen=set(); diagnostics=[]
    for row in summary['rows']:
        key=tuple(row['record'])
        if key in seen or key not in cs:raise ValueError('duplicate or wrong record')
        seen.add(key)
        c=cs[key];weight=float(np.trace(c).real)
        if abs(weight-row['weight'])>1e-12:raise ValueError('record weight mismatch')
        name=Path(row['certificate'])
        if name.name!=str(name):raise ValueError('unsafe certificate path')
        with np.load(path/name,allow_pickle=False) as data:
            cert={k:data[k] for k in ['j','y','primal_factor','slack_factor','scale','shift','guard']}
            if tuple(data['record'])!=key:raise ValueError('certificate record mismatch')
        result=verify(c/weight,cert)
        lower+=weight*result['lower'];upper+=weight*result['upper']
        diagnostics.append(result)
    if max(abs(lower-summary['lower']),abs(upper-summary['upper']))>1e-11:
        raise ValueError('reported aggregate mismatch')
    exact=full_record_formula(n,g)
    if eta==1 and not lower-1e-11<=exact<=upper+1e-11:
        raise ValueError('fully observed analytic formula outside bounds')
    result=dict(status='independent-numerical-verification-passed',n=n,g=g,eta=eta,
                lower=lower,upper=upper,gap=upper-lower,records=len(cs),
                max_tp_residual=max(r['tp_residual'] for r in diagnostics),
                min_primal_eigenvalue=min(r['primal_min_eig'] for r in diagnostics),
                min_dual_eigenvalue=min(r['dual_min_eig'] for r in diagnostics),
                full_record_formula=exact,summary_sha256=hashlib.sha256((path/'summary.json').read_bytes()).hexdigest(),
                verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    print(json.dumps(result),flush=True)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=check(args.directory)
    if args.output:
        with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
