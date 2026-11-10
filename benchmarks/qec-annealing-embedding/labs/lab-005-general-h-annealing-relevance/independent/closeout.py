"""Archive this authorized research round without altering frozen science."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, sys
import yaml
LAB=Path(__file__).resolve().parents[1]
BASE=LAB.parents[1]
ROOT=BASE.parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d): p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def now(): return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
run=json.loads((LAB/'run.json').read_text())
deps=[]
for path,expected in run['source_dependencies'].items():
 actual=sha(ROOT/path); assert actual==expected,path
 deps.append({'path':path,'sha256':actual,'unchanged':True})
snapshots=[]
for name,scope in [('results/research_artifact_manifest.json',LAB),('theory_extensions/manifest.json',LAB/'theory_extensions'),('standard_extension/manifest.json',LAB/'standard_extension')]:
 d=json.loads((LAB/name).read_text());bad=[]
 for item in d['files']:
  p=scope/item['path']
  if not p.is_file() or sha(p)!=item['sha256']:bad.append(item['path'])
 assert not bad,(name,bad)
 snapshots.append({'manifest':name,'files_checked':len(d['files']),'hash_mismatches':bad})
pyfiles=list(LAB.rglob('*.py'))
for p in pyfiles:compile(p.read_text(),str(p),'exec')
reg=yaml.safe_load((BASE/'wiki/sources.yml').read_text())
r=next(r for r in reg['sources'] if r['source_id']=='lab:lab-005-general-h-annealing-relevance')
assert r['revision']=='sha256:'+sha(LAB/'REPORT.md')
lint=subprocess.run([sys.executable,str(ROOT/'skills/wiki-lint/scripts/lint_wiki.py'),str(BASE)],capture_output=True,text=True)
assert lint.returncode==0,lint.stdout+lint.stderr
validation=subprocess.run([sys.executable,str(ROOT/'skills/create-benchmark/scripts/validate_benchmark.py'),str(BASE)],capture_output=True,text=True)
findings=[s for s in validation.stdout.splitlines() if s.startswith('ERROR:')]
assert len(findings)==36 and all('labs/lab-002-' in s or 'labs/lab-003-' in s for s in findings),findings
qa=json.loads((LAB/'results/issue_pdf_qa.json').read_text())
for rel,h in qa['source_hashes'].items():assert sha(BASE/rel)==h,rel
checks={'status':'pass_with_unchanged_legacy_structure_findings','checked_utc':now(),'original_dependencies':deps,'frozen_scientific_snapshots':snapshots,'python_files_syntax_checked':len(pyfiles),'wiki_lint':lint.stdout.strip(),'wiki_report_revision_current':True,'repository_validator':{'legacy_findings':len(findings),'current_findings':[],'legacy_sources_unchanged':True},'issue_pdf_qa':{'status':qa['status'],'pages':qa['pages'],'source_hashes_current':True},'scientific_independent_audits':{},'active_work':{'scientific_child':'completed; confirmed by collaboration inventory','parent_scientific_jobs':'all known submitted jobs completed','os_process_inventory':'unavailable in sandbox; no global process claim'},'scope':'Continuing scientific research and local issue formulation, not a blind trial or organizer acceptance.'}
for fn in ['independent_certified_mapping_audit.json','independent_standard_extension_audit.json','independent_child_program_audit.json','event_projection_checks.json']:
 d=json.loads((LAB/'results'/fn).read_text());assert d['status']=='pass',fn
 checks['scientific_independent_audits'][fn]={k:v for k,v in d.items() if k not in ['records']}
save(LAB/'results/closeout_checks.json',checks)
completed=now();elapsed=(datetime.fromisoformat(completed.replace('Z','+00:00'))-datetime.fromisoformat(run['started_utc'].replace('Z','+00:00'))).total_seconds()
assert elapsed<run['budget_seconds']
run.update(status='completed',science_completed_utc='2026-10-16T11:14:40Z',completed_utc=completed,elapsed_seconds=elapsed,remaining_original_budget_seconds=run['budget_seconds']-elapsed,active_deliverable='Completed local English issue/TeX/PDF, final report, independently audited scientific evidence and provenance archive.',next_operation='No scientific job active; issue may enter separate fresh-session testing after a fair protocol is prepared.',progress='48/48 same-mapping early-time event orders; balanced15/23 strictly smaller certified mappings; standard1/24 zero-search+LP or3/24 charged-search+LP, all n16; practical regime remains open.',issue_assessment='pass-to-testing with feasibility/difficulty uncertainty; not organizer approval',artifact_manifest='artifact-manifest.json',transcript_index='transcripts/index.json',closeout_checks='results/closeout_checks.json',proof_clarification='independent/PROOF_CLARIFICATION.md',memory_telemetry='Not instrumented; no memory-performance claim.',fresh_blind_test=False,formal_calibration=False,automation_created=False)
save(LAB/'run.json',run)
p=ROOT/'talk/threads/T-0008-general-h-evaluation-guided-embedding-research-loop.md'
s=p.read_text();s=s.replace("updated: '2026-10-16T09:15:15Z'",f"updated: '{completed}'")
if '## M-006' not in s:
 s+='\n## M-006 · agent · resolution · '+completed+'\n\nCompleted Lab005 within the original three-hour budget. The actual authorizing user event was2026-10-16T08:56:56.699Z; M-004/M-005 timestamps record repository entry time, not a restarted allowance. Budget start08:57:05Z and deadline11:57:05Z remain unchanged.\n\nGeneral-H weighted repair, endpoint readout and finite-forward quantum proofs now support48/48 early-time same-mapping optimum-event orders. A certified compact-mapping loop reduces15/23 balanced mappings(mean4.075% across23) atT1/1024. Balanced compilation costs about twice standard. A standard optimal-set relaxation certifies1/24 smaller mappings with a zero-search feasible witness or3/24 with charged bounded search; every standard success is n16 and larger cases remain inconclusive. Independent audits pass375 actual candidate programs,329 basic selections and the192-program/960-dual standard extension. The proof wording clarification preserves all constants and frozen results.\n\nThe self-contained English issue/PDF passes the creation screen as a candidate for testing. Useful-time performance, fair-budget feasibility, calibrated difficulty and organizer acceptance remain unestablished. A permissive conditional formulation already has an agent-produced solution; earlier successes are preserved. This author-context collaboration is not a fresh blind trial or human expert intervention. No QPU, external publication or automation was used.\n\nArtifacts: benchmarks/qec-annealing-embedding/labs/lab-005-general-h-annealing-relevance/REPORT.md; benchmarks/qec-annealing-embedding/problem/ISSUE-general-h-finite-annealing.md; benchmarks/qec-annealing-embedding/problem/issue-general-h-finite-annealing.pdf; benchmarks/qec-annealing-embedding/evaluation/ISSUE-ASSESSMENT-general-h-finite-annealing.md. Thread remains open for subsequent user decisions.\n'
 s=s.replace('related:\n','related:\n- benchmarks/qec-annealing-embedding/labs/lab-005-general-h-annealing-relevance/REPORT.md\n- benchmarks/qec-annealing-embedding/problem/ISSUE-general-h-finite-annealing.md\n',1)
p.write_text(s)
subprocess.run([sys.executable,str(LAB/'independent/export_transcripts.py')],check=True)
outside=[BASE/p for p in ['problem/ISSUE-general-h-finite-annealing.md','problem/issue-general-h-finite-annealing.tex','problem/issue-general-h-finite-annealing.pdf','evaluation/ISSUE-ASSESSMENT-general-h-finite-annealing.md','metadata.yml','README.md','problem/README.md','labs/README.md','note/general-h-readout-and-forward.md','src/README.md','wiki/index.md','wiki/thesis.md','wiki/ideas/research-frontier.md','wiki/implementations/general-h-embedding-loop.md','wiki/sources.yml','wiki/log.md']]
outside += [ROOT/'benchmarks/benchmarks.yml',ROOT/'dashboard/frontend/static/generated/data.js',p]
files=[]
for p in sorted(LAB.rglob('*')):
 if not p.is_file() or p.name=='artifact-manifest.json' or '__pycache__' in p.parts or p.suffix=='.pyc':continue
 files.append({'path':str(p.relative_to(LAB)),'bytes':p.stat().st_size,'sha256':sha(p)})
external=[{'repository_path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in outside]
manifest={'status':'pass','generated_utc':now(),'scope':'Complete Lab005 archive excluding this self-referential manifest and bytecode caches; explicit external deliverable snapshots. No whole-runtime-log claim.','file_count':len(files),'total_bytes':sum(r['bytes'] for r in files),'files':files,'external_artifacts':external,'original_dependencies':deps,'frozen_snapshot_checks':snapshots}
save(LAB/'artifact-manifest.json',manifest)
for r in files:assert sha(LAB/r['path'])==r['sha256'],r['path']
for r in external:assert sha(ROOT/r['repository_path'])==r['sha256'],r['repository_path']
print(json.dumps({'status':'completed','completed_utc':completed,'elapsed_seconds':elapsed,'archive_files':len(files),'archive_bytes':manifest['total_bytes'],'external_artifacts':len(external),'wiki_lint':lint.stdout.strip(),'legacy_findings_only':len(findings)},indent=2))
