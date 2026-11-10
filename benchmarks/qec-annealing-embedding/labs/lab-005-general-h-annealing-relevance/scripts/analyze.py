from pathlib import Path
import json,statistics,time
OUT=Path(__file__).resolve().parents[1]/'results'


def main():
    cases={};models=[]
    for p in OUT.glob('*_s*_standard.json'):
        a=json.loads(p.read_text());bpath=OUT/(p.stem.removesuffix('_standard')+'_balanced.json')
        if bpath.exists():cases[p.stem.removesuffix('_standard')]=(a,json.loads(bpath.read_text()))
    paired=[];reference=[]
    for name,(a,b) in sorted(cases.items()):
        if a['status']!='ok' or b['status']!='ok':continue
        x=a['selected']['program'];y=b['selected']['program'];row={'name':name,'n':a['input']['n'],'family':a['input']['family'],'split':a['input']['split'],
          'standard_qubits':x['physical_qubits'],'balanced_qubits':y['physical_qubits'],'qubit_ratio':y['physical_qubits']/x['physical_qubits'],
          'standard_scale':x['scale'],'balanced_scale':y['scale'],'scale_ratio':y['scale']/x['scale'],'curves':[]}
        for aa,bb in zip(a['thermal_curves'],b['thermal_curves']):
            rr={'beta':aa['beta'],'standard_tv_bound':aa['root_readout_tv_bound'],'balanced_tv_bound':bb['root_readout_tv_bound'],
                 'standard_feasibility_lower':aa['syndrome_certificate']['feasible_probability_lower'],'balanced_feasibility_lower':bb['syndrome_certificate']['feasible_probability_lower'],
                 'standard_aux_tv_bound':aa['syndrome_certificate']['conditional_feasible_tv_bound']}
            if 'exact_reference' in aa:
                ga=aa['exact_reference'];gb=bb['exact_reference'];rr.update({'standard_exact':ga,'balanced_exact':gb,
                    'balanced_actual_original_optimum_gain':gb['original_optimum_probability']/ga['original_optimum_probability'],
                    'balanced_consistent_optimum_lower':(1-bb['chain_defect_bound'])*gb['original_optimum_probability'],
                    'standard_root_optimum_upper':min(1.,ga['original_optimum_probability']+aa['chain_defect_bound']),
                    'standard_consistent_optimum_lower':(1-aa['chain_defect_bound'])*ga['original_optimum_probability'],
                    'balanced_root_optimum_upper':min(1.,gb['original_optimum_probability']+bb['chain_defect_bound'])})
                rr['balanced_strict_root_readout_order_numerical']=rr['balanced_consistent_optimum_lower']>rr['standard_root_optimum_upper']+1e-10
                rr['standard_strict_root_readout_order_numerical']=rr['standard_consistent_optimum_lower']>rr['balanced_root_optimum_upper']+1e-10
            row['curves'].append(rr)
        paired.append(row)
    beta_summary={}
    for beta in [10.,20.,40.,80.]:
        rr=[next(x for x in r['curves'] if x['beta']==beta) for r in paired];refs=[x for x in rr if 'standard_exact' in x]
        beta_summary[str(beta)]={'paired':len(rr),'standard_coverage_tv_25':sum(x['standard_tv_bound']<=.25 for x in rr),
          'balanced_coverage_tv_25':sum(x['balanced_tv_bound']<=.25 for x in rr),'standard_coverage_tv_10':sum(x['standard_tv_bound']<=.1 for x in rr),
          'balanced_coverage_tv_10':sum(x['balanced_tv_bound']<=.1 for x in rr),'standard_median_tv':statistics.median(x['standard_tv_bound'] for x in rr),
          'balanced_median_tv':statistics.median(x['balanced_tv_bound'] for x in rr),'reference_inputs':len(refs),
          'balanced_actual_original_optimum_improvements':sum(x['balanced_actual_original_optimum_gain']>1+1e-9 for x in refs),
          'mean_original_optimum_ratio':statistics.mean(x['balanced_actual_original_optimum_gain'] for x in refs),
          'strict_root_order_balanced_numerical':sum(x['balanced_strict_root_readout_order_numerical'] for x in refs),
          'strict_root_order_standard_numerical':sum(x['standard_strict_root_readout_order_numerical'] for x in refs),
          'maximum_standard_actual_aux_tv':max(x['standard_exact']['conditional_feasible_tv'] for x in refs),
          'maximum_balanced_actual_aux_tv':max(x['balanced_exact']['conditional_feasible_tv'] for x in refs)}
    summary={'paired_inputs':len(paired),'mean_qubit_ratio':statistics.mean(x['qubit_ratio'] for x in paired),
      'median_qubit_ratio':statistics.median(x['qubit_ratio'] for x in paired),'mean_scale_ratio':statistics.mean(x['scale_ratio'] for x in paired),
      'beta_summary':beta_summary,'pairs':paired}
    (OUT/'analysis_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='pairs'},indent=2))
if __name__=='__main__':main()
