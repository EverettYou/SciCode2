"""Preserve exact visible conversation/tool JSONL plus source-line locators.

Original runtime logs remain unchanged at their recorded paths. The export is
explicitly scoped: it excludes private reasoning, system/developer content,
compaction/runtime state and duplicated event wrappers; it is not a whole-log copy.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
LAB=Path(__file__).resolve().parents[1]
SOURCES={'parent':Path('/Users/home/.codex/sessions/2026/10/07/rollout-2026-10-07T09-36-51-01a11739-9407-7a50-88e5-3951d9c7a4a4.jsonl'),'scientific_child':Path('/Users/home/.codex/sessions/2026/10/16/rollout-2026-10-16T01-09-08-01a143c1-f9c3-7f63-8331-18388c82ffd4.jsonl')}
START='2026-10-16T08:56:56.699Z'
records=[]
for role,path in SOURCES.items():
 source=path.read_bytes();kept=[];locators=[];excluded={};incomplete=0;settings=[]
 for line_number,line in enumerate(source.splitlines(keepends=True),1):
  try:d=json.loads(line)
  except json.JSONDecodeError:incomplete+=1;continue
  if d.get('timestamp','')<START:continue
  q=d.get('payload',{});kind=d.get('type');sub=q.get('type')
  if kind=='turn_context':settings.append({k:q[k] for k in ['model','effort','cwd'] if k in q})
  allowed=kind=='response_item' and (sub in ['function_call','function_call_output','custom_tool_call','custom_tool_call_output','agent_message'] or sub=='message' and q.get('role') in ['user','assistant'] and q.get('phase')!='analysis')
  if not allowed:
   key=str(kind)+':'+str(sub);excluded[key]=excluded.get(key,0)+1;continue
  kept.append(line);locators.append(line_number)
 output=LAB/'transcripts'/f'{role}.jsonl';output.parent.mkdir(exist_ok=True);output.write_bytes(b''.join(kept));records.append({'role':role,'original_runtime_log_path':str(path),'source_snapshot_sha256':hashlib.sha256(source).hexdigest(),'source_snapshot_bytes':len(source),'output_path':str(output.relative_to(LAB)),'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'output_lines':len(kept),'source_line_numbers':locators,'excluded_record_type_counts':excluded,'ignored_incomplete_source_lines':incomplete,'turn_settings':settings,'whole_historical_session_export':False,'capture_limit':'Snapshot excludes later active-parent closeout and final response; original log remains at source.' if role=='parent' else 'Current-round visible/tool record snapshot; prior child research context is not included.'})
index={'captured_utc':datetime.now(timezone.utc).isoformat(),'authorizing_user_event_utc':START,'budget_started_utc':'2026-10-16T08:57:05Z','budget_deadline_utc':'2026-10-16T11:57:05Z','selection':'Exact unmodified original JSONL conversation/tool records from the two known sessions, timestamp>=authorizing user event. Private/runtime records excluded; no reconstructed tool output. Full original runtime logs remain unchanged at recorded paths.','context_limit':'Parent and same scientific child retain prior research context. Scientific review messages are collaboration, not human expert interventions or blind calibration.','sessions':records}
(LAB/'transcripts/index.json').write_text(json.dumps(index,indent=2)+'\n');print(json.dumps({'sessions':len(records),'visible_tool_lines':{r['role']:r['output_lines'] for r in records},'captured_utc':index['captured_utc']}))
