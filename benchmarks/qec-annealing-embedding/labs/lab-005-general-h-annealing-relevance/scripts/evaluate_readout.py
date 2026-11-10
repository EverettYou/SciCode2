"""Decoder-free original-error Gibbs evaluation for a declared compiled program."""
from pathlib import Path
import argparse,json,math,time
from fractions import Fraction as F
from models import old
from repair_api import REPAIR
from thermal import row_envelopes,syndrome_certificate


def evaluate_readout(data,scheme,alpha,beta,penalty=None,chain_defect_bound=0.,rounding_tv=0.):
    start=time.perf_counter();n=data['n']
    if not isinstance(n,int) or n<0 or scheme not in ('standard','balanced'):raise ValueError('nonnegative integer n and known scheme required')
    rows=old.normalize_rows(data['rows'],n);syndrome=list(data['syndrome']);weights=list(map(float,data['weights']))
    if len(rows)!=len(syndrome) or len(weights)!=n or any(s not in (0,1) for s in syndrome):raise ValueError('dimensions or syndrome invalid')
    if not all(math.isfinite(w) for w in weights) or not math.isfinite(alpha) or not math.isfinite(beta) or not alpha>0 or not beta>0:raise ValueError('finite weights,alpha>0,beta>0 required')
    if not 0<=chain_defect_bound<=1 or not 0<=rounding_tv<=1:raise ValueError('probability bounds must be in[0,1]')
    witness=REPAIR.witness(rows,n,weights);C=F(*witness['repair_bound_exact'])
    M=float(sum(map(abs,weights))+1 if penalty is None else penalty)
    if not math.isfinite(M) or F(M)<=C:raise ValueError('declared compiler must satisfy the verified M>C fidelity condition')
    # Unweighted syndrome membership only; no cost optimization.
    particular=set()
    for row,delta in zip(witness['basis_rows'],witness['repair_columns']):
        if syndrome[row]:particular^=set(delta)
    if not all(sum(i in particular for i in row)%2==s for row,s in zip(rows,syndrome)):raise ValueError('syndrome not in image(H)')
    t=alpha*beta;env=row_envelopes(rows,syndrome,t*M,scheme);loads=[float(F(*v)) for v in witness['repair_loads_exact']];cert=syndrome_certificate(env,witness['basis_rows'],loads,t)
    tv=min(1.,chain_defect_bound+rounding_tv+cert.get('syndrome_defect_bound',1.)+cert.get('conditional_feasible_tv_bound',1.))
    return {'status':cert['status'],'scheme':scheme,'beta':beta,'alpha':alpha,'penalty':M,'repair_witness':witness,
       'syndrome_certificate':cert,'root_readout_tv_bound_including_supplied_physical_errors':tv,
       'supplied_chain_defect_bound':chain_defect_bound,'supplied_rounding_tv':rounding_tv,
       'conditional_feasible_law_exact':scheme=='balanced','decoding_optimization_performed':False,
       'guarantee_scope':'terminal Gibbs original-error law; supplied physical consistency/rounding bounds must be independently certified',
       'elapsed_seconds':time.perf_counter()-start}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--scheme',choices=['standard','balanced'],default='balanced');ap.add_argument('--alpha',type=float,required=True);ap.add_argument('--beta',type=float,default=20.)
    ap.add_argument('--penalty',type=float);ap.add_argument('--chain-bound',type=float,default=0.);ap.add_argument('--rounding-tv',type=float,default=0.);args=ap.parse_args()
    result=evaluate_readout(json.loads(args.input.read_text()),args.scheme,args.alpha,args.beta,args.penalty,args.chain_bound,args.rounding_tv)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(result['root_readout_tv_bound_including_supplied_physical_errors'])
if __name__=='__main__':main()
