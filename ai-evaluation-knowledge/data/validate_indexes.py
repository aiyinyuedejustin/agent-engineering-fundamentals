#!/usr/bin/env python3
"""Validate central research indexes without network access or modifications."""
from pathlib import Path
import collections,csv,json,sys,hashlib
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data'
def csv_rows(name):
 with (DATA/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def jsonl_rows(name):return [json.loads(x) for x in (DATA/name).read_text().splitlines() if x.strip()]
models=csv_rows('models.csv');benchmarks=csv_rows('benchmarks.csv');concepts=csv_rows('concepts.csv');results=csv_rows('model_benchmark_evidence.csv');sources=jsonl_rows('sources.jsonl');evidence=jsonl_rows('evidence.jsonl')
errors=[]
def check(ok,msg):
 if not ok:errors.append(msg)
def unique(rows,key):
 ids=[x[key] for x in rows];check(len(ids)==len(set(ids)),f'Duplicate {key}');return set(ids)
mi=unique(models,'model_id');bi=unique(benchmarks,'benchmark_id');ci=unique(concepts,'concept_id');ri=unique(results,'result_id');si=unique(sources,'source_id');ei=unique(evidence,'evidence_id')
for label,rows in [('model',models),('benchmark',benchmarks),('concept',concepts),('result',results)]:
 for row in rows:
  for key,known in [('source_ids',si),('evidence_ids',ei)]:
   for value in filter(None,row.get(key,'').split(';')):check(value in known,f'{label}: unknown {key} {value}')
  if row.get('depth'):check(row['depth'] in ['D0','D1','D2','D3','D4'],f'{label}: bad depth')
for row in models:
 check(row.get('count_as_model_seed') in ['true','false'],'Model seed count policy missing')
 check(row.get('identity_status') in ['source_supported_label','named_voice_model_system','unresolved_reported_condition'],'Model identity status missing')
 if row.get('identity_status')!='source_supported_label':check(row.get('count_as_model_seed')=='false','Unresolved/system-only record incorrectly counted as model seed')
for row in results:
 check(row['model_id'] in mi,'Unknown result model');check(row['benchmark_id'] in bi,'Unknown result benchmark')
 check(row['comparability_status'] in ['unassessed','protocol_matched','partially_matched','not_comparable'],'Bad comparability state')
for row in benchmarks:
 if row.get('catalog_depth'):check(row['catalog_depth'] in ['D0','D1','D2','D3'],'Catalog depth incorrectly promoted from a component experiment')
 if row.get('parent_benchmark_id'):check(row['parent_benchmark_id'] in bi,'Unknown parent benchmark')
 if row.get('case_study_path'):check((ROOT/row['case_study_path']).is_file(),'Missing case study '+row['case_study_path'])
for row in evidence:
 if row.get('result_ref'):check(row['result_ref'] in ri,'Unknown evidence result reference')
 for entity in row['entity_ids']:check(entity in mi|bi|ci,'Unknown evidence entity '+entity)
 for ref in row['source_refs']:check(ref['source_id'] in si,'Unknown evidence source '+ref['source_id']);check(bool(ref.get('locator')),'Missing source locator')
 for path in row.get('artifact_paths',[]):check((ROOT/path).is_file(),'Missing evidence artifact '+path)
 if row['depth']=='D4':check(row.get('execution_performed') is True and bool(row.get('artifact_paths')),'D4 lacks executed artifact')
 if row['depth']=='D3':check(row.get('execution_performed') is False,'Source-trace evidence incorrectly implies execution')
for row in sources:
 if not row.get('url'):
  local=ROOT/row.get('local_path','')
  check(row.get('source_type')=='original_experiment' and local.is_file(),'Source URL/local experiment missing')
  if local.is_file():check(hashlib.sha256(local.read_bytes()).hexdigest()==row.get('sha256'),'Local source hash mismatch')
 if row.get('accessed_at_utc') is None:check(bool(row.get('accessed_date')) and row.get('access_time_precision')=='date','Undocumented access date precision')
summary={'model_records':len(models),'counted_model_seeds':sum(x.get('count_as_model_seed')=='true' for x in models),'model_identity_statuses':dict(collections.Counter(x.get('identity_status') for x in models)),'benchmark_or_protocol_records':len(benchmarks),'concepts':len(concepts),'model_result_observations':len(results),'sources':len(sources),'unique_source_urls':len({x['url'] for x in sources if x.get('url')}),'evidence':len(evidence),'evidence_depths':dict(collections.Counter(x['depth'] for x in evidence)),'fully_reviewed_deep_studies':sum(x['deep_study_review']=='reviewed_complete' for x in benchmarks),'errors':errors}
print(json.dumps(summary,indent=2));sys.exit(bool(errors))
