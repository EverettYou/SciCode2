from pathlib import Path
import json,time,statistics
from fractions import Fraction as F
from thermal import row_envelopes,syndrome_certificate
from repair_api import REPAIR
OUT=Path(__file__).resolve().parents[1]/'results'

def main():
    records=[]
    for path in sorted(OUT.glob('*_s*_*.json')):
        if not(path.stem.endswith('_balanced') or path.stem.endswith('_standard')):continue
        r=json.loads(path.read_text())
        if r['status']!='ok':continue
        data=r['input'];t=20*r['selected']['program']['scale'];times=[];pre=[];envelopetime=[];certtime=[]
        for _ in range(5):
            start=time.perf_counter();w=REPAIR.witness(data['rows'],data['n'],data['weights']);t0=time.perf_counter();env=row_envelopes(data['rows'],data['syndrome'],t*r['model']['penalty'],r['scheme']);t1=time.perf_counter();loads=[float(F(*v)) for v in w['repair_loads_exact']];cert=syndrome_certificate(env,w['basis_rows'],loads,t);t2=time.perf_counter()
            times.append(t2-start);pre.append(t0-start);envelopetime.append(t1-t0);certtime.append(t2-t1)
        records.append({'name':r['name'],'scheme':r['scheme'],'n':data['n'],'maximum_row_degree':max(map(len,data['rows']),default=0),
          'total_seconds_median':statistics.median(times),'witness_seconds_median':statistics.median(pre),
          'row_envelope_seconds_median':statistics.median(envelopetime),'syndrome_certificate_seconds_median':statistics.median(certtime)})
    (OUT/'readout_profile.json').write_text(json.dumps({'records':records,'repeat_count':5},indent=2)+'\n');print('profiled',len(records))
if __name__=='__main__':main()
