"""Hash the child-owned research snapshot without freezing parent-owned work."""
from pathlib import Path
import hashlib,json,datetime
LAB=Path(__file__).resolve().parents[1]
ROOT_NAMES=['README.md','requirements.txt','THEORY.md','RESEARCH_REPORT.md','PROTOCOL.md','DYNAMICS_PROTOCOL.md','CHAIN_RELAXATION_PROTOCOL.md','CLASSICAL_COMPILER_PROTOCOL.md','REPAIR_COMPILER_PROTOCOL.md']
CHILD_DIRS=['scripts','figures','results/anneals','results/dynamics','results/relaxation','results/relaxation_standard','results/repair_compilers','results/readout_audits']
EXCLUDE_PREFIXES=['forward_','fourth_order','independent_','moment_selection','penalty_','quantum_moment']

def main():
    paths={LAB/p for p in ROOT_NAMES}
    for name in CHILD_DIRS:
        paths.update(p for p in (LAB/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for p in (LAB/'results').glob('*'):
        if p.is_file() and p.name!='research_artifact_manifest.json' and not any(p.name.startswith(a) for a in EXCLUDE_PREFIXES):paths.add(p)
    records=[]
    for p in sorted(paths):
        if p.suffix=='.json':json.loads(p.read_text())
        raw=p.read_bytes();records.append({'path':str(p.relative_to(LAB)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    source=json.loads((LAB/'results/source_provenance.json').read_text())
    dependencies=[{'path':p,'recorded_sha256':h,'current_sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest(),'unchanged_since_main_run':hashlib.sha256(Path(p).read_bytes()).hexdigest()==h} for p,h in source.items()]
    if not all(d['unchanged_since_main_run'] for d in dependencies):raise AssertionError('inherited main-run dependencies changed')
    d={'status':'pass','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'child-owned research snapshot; parent independent branches, root REPORT/run metadata and issue are excluded','file_count':len(records),'total_bytes':sum(r['bytes'] for r in records),'files':records,'inherited_dependencies':dependencies}
    (LAB/'results/research_artifact_manifest.json').write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps({k:v for k,v in d.items() if k not in ('files','inherited_dependencies')}))
if __name__=='__main__':main()
