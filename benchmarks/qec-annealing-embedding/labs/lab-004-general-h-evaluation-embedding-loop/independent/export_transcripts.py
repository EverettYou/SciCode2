"""Capture exact timestamp-selected raw JSONL from the two known round sessions."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
LAB=Path(__file__).resolve().parents[1]
SOURCES={
 'parent':Path('/Users/home/.codex/sessions/2026/10/07/rollout-2026-10-07T09-36-51-01a11739-9407-7a50-88e5-3951d9c7a4a4.jsonl'),
 'scientific_child':Path('/Users/home/.codex/sessions/2026/10/16/rollout-2026-10-16T01-09-08-01a143c1-f9c3-7f63-8331-18388c82ffd4.jsonl')}
START='2026-10-16T08:02:44'
records=[]
for role,path in SOURCES.items():
 data=path.read_bytes();kept=[];locators=[];contexts=[];incomplete=0
 for line_number,line in enumerate(data.splitlines(keepends=True),1):
  try:obj=json.loads(line)
  except json.JSONDecodeError:incomplete+=1;continue
  if obj.get('timestamp','')<START:continue
  kept.append(line);locators.append(line_number)
  if obj.get('type')=='turn_context':
   p=obj.get('payload',{});contexts.append({k:p[k] for k in ['model','effort','cwd'] if k in p})
 output=LAB/'transcripts'/f'{role}.jsonl';output.parent.mkdir(exist_ok=True);output.write_bytes(b''.join(kept))
 records.append({'role':role,'source_path':str(path),'source_snapshot_sha256':hashlib.sha256(data).hexdigest(),
  'source_snapshot_bytes':len(data),'output_path':str(output.relative_to(LAB)),
  'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'output_lines':len(kept),
  'source_line_numbers':locators,'ignored_incomplete_source_lines':incomplete,'turn_contexts':contexts,
  'complete_session':role=='scientific_child','capture_limit':'Active parent snapshot excludes later closeout/final response.' if role=='parent' else 'Child final response is included; transcript scope is this research session.'})
index={'captured_utc':datetime.now(timezone.utc).isoformat(),'selection':'Original JSONL lines with timestamps >=2026-10-16T08:02:44Z; no rewriting or reconstructed tool output. Exact known sessions only.',
 'context_limit':'Parent has inherited author/research history before this slice. Child was forked without history, then received scientific review messages. This is supervised continuing research, not blind calibration.',
 'sessions':records}
(LAB/'transcripts/index.json').write_text(json.dumps(index,indent=2)+'\n')
print(json.dumps({'sessions':len(records),'lines':{r['role']:r['output_lines'] for r in records},'captured_utc':index['captured_utc']}))
