"""Execute pinned HLE functions on synthetic data, without API or dataset calls.

This file is original test orchestration. Upstream functions are AST-extracted
from separate hash-verified source inputs; this artifact does not vendor them.
"""
import argparse
import ast
import asyncio
import contextlib
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import tempfile
from types import SimpleNamespace as NS
import copy
import numpy as np

HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--source-dir',type=Path,required=True)
parser.add_argument('--output',type=Path,default=HERE/'results.json')
args0=parser.parse_args()
manifest=json.loads((HERE/'source-manifest.json').read_text())
for item in manifest['files']:
 b=(args0.source_dir/item['path']).read_bytes()
 assert hashlib.sha256(b).hexdigest()==item['sha256'],item['path']
 assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==item['git_blob_sha'],item['path']

class Gather:
 @staticmethod
 async def gather(*tasks): return await asyncio.gather(*tasks)

def source_namespace(path,names):
 tree=ast.parse((args0.source_dir/path).read_text())
 nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in names]
 nodes += [n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in {'SYSTEM_PROMPT','JUDGE_PROMPT'} for t in n.targets)]
 g=dict(np=np,math=math,asyncio=asyncio,copy=copy,json=json,os=os,tqdm_asyncio=Gather)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),g)
 return g
pred=source_namespace('hle_eval/run_model_predictions.py',{'format_message','attempt_question','attempt_all','main'})
judge=source_namespace('hle_eval/run_judge_results.py',{'calib_err','dump_metrics','add_judge_response','judge_all_responses','main'})
results=[]
def add(name,observed,expected=None,scope='synthetic component'):
 if expected is not None:
  if isinstance(expected,float): assert math.isclose(observed,expected,rel_tol=1e-10,abs_tol=1e-10),(name,observed,expected)
  else: assert observed==expected,(name,observed,expected)
 results.append(dict(id=f'HLE{len(results)+1:02}',name=name,observed=observed,scope=scope))
def outcome(fn):
 try:return {'returned':fn()}
 except Exception as e:return {'exception_type':type(e).__name__,'message':str(e)}
def capture(fn):
 out=io.StringIO()
 with contextlib.redirect_stdout(out): status=outcome(fn)
 return dict(status=status,stdout=out.getvalue())

# Calibration control: identical bins and normalization, but include every bin.
# This is an independent diagnostic comparator, not an official corrected score.
def full_bin_comparator(confidence,correct,beta=100):
 order=np.argsort(confidence);confidence=confidence[order];correct=correct[order]
 bins=[[i*beta,(i+1)*beta] for i in range(len(confidence)//beta)]
 if not bins: return None
 bins[-1][1]=len(confidence)
 return float(np.sqrt(sum((b-a)/len(confidence)*(np.mean(confidence[a:b])-np.mean(correct[a:b]))**2 for a,b in bins)))
for n in [0,99]:
 r=outcome(lambda n=n:judge['calib_err'](np.ones(n),np.zeros(n)))
 add(f'calibration n={n}',r,{'exception_type':'IndexError','message':'list index out of range'})
for n in [100,199,200,250,1000,2500]:
 c=np.ones(n);y=np.zeros(n);val=float(judge['calib_err'](c,y))
 expected=0.0 if n<200 else math.sqrt((n//100-1)*100/n)
 assert math.isclose(val,expected)
 add(f'all wrong with 100% confidence n={n}',{'source_rms':val,'all_bins_diagnostic':full_bin_comparator(c,y),'omitted_highest_confidence_examples':n-(n//100-1)*100})
c=np.r_[np.zeros(900),np.ones(100)]; y=np.zeros(1000)
add('only highest-confidence100 are miscalibrated',{'source_rms':float(judge['calib_err'](c,y)),'all_bins_diagnostic':full_bin_comparator(c,y)})
assert results[-1]['observed']['source_rms']==0
add('well-calibrated deterministic control',float(judge['calib_err'](c,c)),0.0)

# Metrics: the production function receives full dataset n, not judged count.
def predictions(n,correct='yes',confidence=100):
 return {str(i):{'judge_response':{'correct':correct,'confidence':confidence}} for i in range(n)}
r=capture(lambda:judge['dump_metrics'](predictions(200),1000))
assert 'Accuracy: 20.0% +/- 2.48% | n = 1000' in r['stdout']
add('200 successful judgements for1000 dataset questions',r)
r=capture(lambda:judge['dump_metrics'](predictions(200),200))
assert 'Accuracy: 100.0% +/- 0.0%' in r['stdout']
add('Wald endpoint all200correct has zero half-width',r)
r=capture(lambda:judge['dump_metrics']({},1000))
assert r['status']['exception_type']=='IndexError'
add('no judged responses cannot print final metrics',r)
r=capture(lambda:judge['dump_metrics'](predictions(300),200))
assert r['status']['exception_type']=='ValueError'
add('stale cache can exceed denominator and invalidate Wald sqrt',r,scope='synthetic cache mismatch, not observed published run')
add('unbounded synthetic confidence200percent',float(judge['calib_err'](np.ones(200)*2,np.zeros(200))),math.sqrt(2),scope='malformed persisted judge data; no claim actual judge emitted it')

q={'id':'synthetic-1','question':'Choose the synthetic label.','image':''}
pred['args']=NS(model='o1-test',num_workers=3,max_completion_tokens=19,temperature=0.23)
add('o1 substring selects user prompt role',pred['format_message'](q)[0]['role'],'user')
pred['args'].model='o3-test'
add('other model uses system prompt role',pred['format_message'](q)[0]['role'],'system')
q_img={**q,'image':'data:image/png;base64,SYNTHETIC_NOT_REAL'}
add('image field forwarded as URL without decode or resize',[v['type'] for v in pred['format_message'](q_img)[1]['content']],['text','image_url'])

calls=[]
async def create(**kwargs):
 calls.append(kwargs)
 return NS(choices=[NS(message=NS(content='synthetic response'))],usage=NS(json=lambda:json.dumps({'completion_tokens':3})))
pred['client']=NS(chat=NS(completions=NS(create=create)))
r=asyncio.run(pred['attempt_question'](q))
assert r[0]=='synthetic-1' and r[2]['completion_tokens']==3
add('temperature CLI value not sent to API',{'requested_temperature':pred['args'].temperature,'api_keys':sorted(calls[0]),'has_temperature': 'temperature' in calls[0]},scope='mock transport records actual kwargs; no API call')
assert not results[-1]['observed']['has_temperature']

async def concurrency_test(workers):
 pred['args'].num_workers=workers
 active=0;peak=0
 async def item(question):
  nonlocal active,peak
  active+=1;peak=max(peak,active)
  await asyncio.sleep(0.001)
  active-=1
  return question['id']
 original=pred['attempt_question'];pred['attempt_question']=item
 try:
  outputs=await pred['attempt_all']([{**q,'id':f'synthetic-{i}'} for i in range(8)])
 finally:pred['attempt_question']=original
 return {'num_workers':workers,'peak_in_flight':peak,'completed':len(outputs)}
for w in [2,3]:
 r=asyncio.run(concurrency_test(w));assert r['peak_in_flight']==w-1
 add(f'outer semaphore reserves one slot workers={w}',r)

# Explicitly test reuse of a judged item despite changed gold and response.
async def never_extract(*args):raise AssertionError('should not call judge')
judge['extract_answer']=never_extract
old={'response':'old response','judge_response':{'correct':'yes','confidence':100,'correct_answer':'old gold'}}
r=asyncio.run(judge['add_judge_response']({**q,'answer':'NEW GOLD'},{q['id']:old}))
assert r[1]['judge_response']['correct_answer']=='old gold'
add('cached judge response reused without checking changed gold',r[1],scope='synthetic cache reuse')

# Run unmodified prediction main in an isolated temporary cwd with a fake dataset
# and scheduler, showing max_samples truthiness and dataset-independent filename.
class Dataset:
 def to_dict(self):return {'id':['a','b','c'],'question':['syntheticA','syntheticB','syntheticC'],'image':['','','']}
seen=[]
async def fake_all(qs):
 seen.append([q['id'] for q in qs])
 return [(z['id'],'synthetic response',{'completion_tokens':1}) for z in qs]
pred['load_dataset']=lambda *a,**k:Dataset()
pred['attempt_all']=fake_all
cwd=Path.cwd()
with tempfile.TemporaryDirectory(prefix='hle-probe-') as td:
 os.chdir(td)
 try:
  for limit,expected in [(0,['a','b','c']),(2,['a','b'])]:
   pred['args']=NS(model='vendor/same-model',dataset='synthetic-dataset-A',num_workers=2,max_samples=limit)
   Path('hle_same-model.json').unlink(missing_ok=True)
   pred['main'](pred['args'])
   assert seen[-1]==expected
   add(f'prediction max_samples={limit}',{'attempted_ids':seen[-1],'filename':'hle_same-model.json'})
  pred['args'].dataset='synthetic-dataset-B';pred['args'].max_samples=None
  pred['main'](pred['args'])
  assert seen[-1]==['c']
  add('different dataset same model filename reuses matching IDs',{'attempted_ids':seen[-1],'cached_ids':sorted(json.loads(Path('hle_same-model.json').read_text()))},scope='synthetic datasets; no real datasets downloaded')
 finally:os.chdir(cwd)

out={'experiment':'HLE official simple runner synthetic component probes','commit':manifest['commit'],'environment':{'python':platform.python_version(),'numpy':np.__version__,'upstream_pinned_numpy':'1.26.4','dependency_match':False},'model_calls':0,'judge_calls':0,'network_calls':0,'real_dataset_loaded':False,'cases':results,'case_count':len(results),'limits':['AST-extracted functions only; mocked API transport and dataset/scheduler as explicitly marked.','The current simple-runner code is not proven to be the production Scale, CAIS Diamond, or AA leaderboard pipeline.','No change to any published model score is justified by these probes.','Diamond dataset rows returned401; no attempt to bypass or acquire restricted records.']}
args0.output.parent.mkdir(parents=True,exist_ok=True)
args0.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'cases':len(results),'output':str(args0.output),'all_assertions_passed':True}))
