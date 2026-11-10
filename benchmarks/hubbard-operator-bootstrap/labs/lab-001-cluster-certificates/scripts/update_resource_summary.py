#!/usr/bin/env python3
import json
from pathlib import Path
base=Path(__file__).resolve().parents[1]
clusters=[]
for p in sorted(base.glob('results*.json')):
 z=json.loads(p.read_text());clusters.append({'file':p.name,'total_energy_lower':z['target_lower'],'elapsed_seconds':z['elapsed_seconds'],'peak_rss_bytes':z['peak_rss_bytes'],'largest_sector_dimension':max(r['dimension'] for r in z['results'])})
audits=[]
for p in sorted(base.glob('audit*.json')):
 z=json.loads(p.read_text());audits.append({'file':p.name,'passed':z.get('passed',z.get('passed_construction_checks')),'full_export_audit_complete':z.get('full_export_audit_complete',z.get('passed',False)),'elapsed_seconds':z['elapsed_seconds'],'peak_rss_bytes':z['peak_rss_bytes'],'affine_nonzero_coefficients_checked':z.get('affine_nonzero_coefficients_checked')})
compressions=[]
for p in sorted((base/'compressed').glob('*/compression.json')):
 z=json.loads(p.read_text());vpath=p.parent.with_name(p.parent.name+'-exact')/'verification.json';v=json.loads(vpath.read_text()) if vpath.exists() else None
 compressions.append({'directory':str(p.parent.relative_to(base)),'compression_seconds':z['compression_seconds'],'retained_factor_columns':sum(q['retained_columns'] for q in z['counts'].values()),'positive_square_terms_before_group_closure_and_residual_completion':sum(q['retained_square_operators'] for q in z['counts'].values()),'exact_verification_seconds':v['validation_seconds'] if v else None,'exact_verification_peak_rss_bytes':v['peak_rss_bytes'] if v else None,'certified_lower':v['reported_total_energy_lower_bound'] if v else None,'factor_entries':v['factor_entries'] if v else None})
summary={'clusters':clusters,'audits':audits,'dual_witness_compressions':compressions,'sum_recorded_cluster_seconds':sum(x['elapsed_seconds'] for x in clusters),'sum_recorded_audit_seconds':sum(x['elapsed_seconds'] for x in audits),'sum_recorded_compression_seconds':sum(x['compression_seconds'] for x in compressions),'sum_recorded_compressed_exact_verification_seconds':sum(x['exact_verification_seconds'] or 0 for x in compressions),'additional_earlier_cylinder_run_seconds':107.20985045912676,'additional_earlier_cylinder_peak_rss_bytes':1126678528,'optimized_2x3_search_seconds':json.loads((base/'weights-2x3.json').read_text())['seconds'],'discovery_only_2x4_open_search_seconds':json.loads((base/'weights-2x4-open.json').read_text())['seconds'],'notes':['These are per-process observed measurements on a workstation shared by concurrent agents.','Audits include independent CAR pattern tests, physical map reconstruction and symmetry/cone checks.','Original exact integer SOS verification is measured by lab004; compressed-certificate reverification is listed here separately.','Latest result JSON timings do not capture every exploratory failed invocation or earlier rerun; explicitly retained initial cylinder timing is listed separately.','Retained dual columns are witness ranks, not dimensions of the complete literal operator space including symmetry closure and residual positivity operators.']}
(base/'resource-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k.startswith('sum_')},indent=2))
