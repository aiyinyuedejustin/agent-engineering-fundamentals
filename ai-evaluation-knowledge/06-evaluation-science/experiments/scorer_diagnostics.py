#!/usr/bin/env python3
"""Execute allowlisted functions from pinned official sources on synthetic fixtures.
No model calls; all judge calls are stubbed. Does not execute candidate code.
Run --download to fetch pinned files into a temporary directory if needed.
"""
from __future__ import annotations
import argparse
import ast
import collections
import hashlib
import itertools
import json
import math
import platform
import re
import string
import tempfile
from enum import Enum
from pathlib import Path
from types import SimpleNamespace
from typing import Any, List, Union
import numpy as np

HERE=Path(__file__).parent

def git_blob_sha(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def load_sources(download):
    sources={}
    metadata=[]
    for row in json.loads((HERE/'source_manifest.json').read_text()):
        p=Path(row['local_path'])
        if download:
            import urllib.request
            p=Path(tempfile.gettempdir())/('eval-science-downloaded-'+row['id']+'.py')
            p.write_bytes(urllib.request.urlopen(row['url'],timeout=30).read())
        data=p.read_bytes()
        # Connector snapshots may add a final newline; only that normalization is allowed.
        candidates=[data,data.rstrip(b'\n'),data.rstrip(b'\n')+b'\n']
        matched=next((d for d in candidates if git_blob_sha(d)==row['git_blob_sha']),None)
        if matched is None:
            raise RuntimeError('Source blob mismatch: '+row['id'])
        sources[row['id']]=matched.decode()
        metadata.append({k:v for k,v in row.items() if k!='local_path'} | {
            'sha256':hashlib.sha256(matched).hexdigest()})
    return sources,metadata

def select_nodes(source,names,namespace):
    tree=ast.parse(source)
    selected=[]
    ranges={}
    for node in tree.body:
        name=getattr(node,'name',None)
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            name=node.targets[0].id
        if name in names:
            selected.append(node)
            ranges[name]=[node.lineno,node.end_lineno]
    if set(ranges)!=set(names):
        raise RuntimeError('Missing allowlisted source nodes: '+str(set(names)-set(ranges)))
    module=ast.Module(body=selected,type_ignores=[])
    exec(compile(module,'<audited-official-source>','exec'),namespace)
    return ranges

def main(download=False):
    src,metadata=load_sources(download)
    result={'experiment_type':'official scoring functions on synthetic fixtures; no LLM benchmark inference',
            'python':platform.python_version(),'numpy':np.__version__,'source_provenance':metadata,'function_lines':{}}
    ns={'np':np,'itertools':itertools,'Union':Union,'List':List}
    result['function_lines']['humaneval']=select_nodes(src['humaneval_evaluation'],['estimate_pass_at_k'],ns)
    rows=[]
    for n,c,k in [(10,1,1),(10,1,5),(10,2,5),(4,1,4),(10,0,5),(10,10,5)]:
        upstream=float(ns['estimate_pass_at_k'](n,[c],k)[0])
        exact=1-math.comb(n-c,k)/math.comb(n,k) if n-c>=k else 1.
        assert abs(upstream-exact)<1e-12
        rows.append({'n':n,'correct':c,'k':k,'official':upstream,'naive_plugin':1-(1-c/n)**k})
    result['humaneval_pass_at_k']=rows
    ns={'re':re,'string':string,'collections':collections}
    result['function_lines']['squad']=select_nodes(src['squad_eval'],[
        'normalize_answer','get_tokens','compute_exact','compute_f1','get_raw_scores',
        'make_eval_dict','apply_no_ans_threshold'],ns)
    rows=[]
    for gold,pred in [('The Eiffel Tower.','eiffel tower'),('not guilty','guilty'),('0.5','05'),
                      ('twenty one','21'),('','the'),('Paris','Paris and London')]:
        rows.append({'gold':gold,'prediction':pred,'normalized_gold':ns['normalize_answer'](gold),
                     'normalized_prediction':ns['normalize_answer'](pred),
                     'exact':ns['compute_exact'](gold,pred),'f1':ns['compute_f1'](gold,pred)})
    assert rows[2]['exact']==1 and rows[4]['exact']==1
    result['squad_normalization']=rows
    result['squad_threshold_boundary']={
       str(t):ns['apply_no_ans_threshold']({'q':0.0},{'q':.5},{'q':False},t)['q'] for t in [.49,.5,.51]}
    class Conversation:
        roles=['user','assistant']
        def __init__(self): self.messages=[]
        def set_system_message(self,s): self.system=s
        def append_message(self,role,s): self.messages.append([role,s])
    judge_text={'text':''}
    ns={'ast':ast,'re':re,'TIE_DELTA':.1,
        'OPENAI_MODEL_LIST':['fake-judge'],'ANTHROPIC_MODEL_LIST':[],
        'get_conversation_template':lambda model:Conversation(),
        'chat_completion_openai':lambda *a,**kw:judge_text['text']}
    patterns=['two_score_pattern','two_score_pattern_backup','one_score_pattern','one_score_pattern_backup']
    result['function_lines']['fastchat']=select_nodes(src['fastchat_common'],patterns+['run_judge_pair','run_judge_single'],ns)
    question={'turns':['Synthetic question']}
    answer={'choices':[{'turns':['Synthetic answer']} ]}
    pair_judge=SimpleNamespace(model_name='fake-judge',prompt_template={
        'prompt_template':'Q: {question}\nA: {answer_a}\nB: {answer_b}',
        'system_prompt':'Synthetic rubric','output_format':'[[A]]'})
    rows=[]
    for text in ['The winner is [[B]].','I considered [[A]] but my final verdict is [[B]].',
                 'No decision.','[[C]]']:
        judge_text['text']=text
        winner,_,_=ns['run_judge_pair'](question,answer,answer,pair_judge,None)
        rows.append({'stubbed_judge_text':text,'parsed_winner':winner})
    assert rows[1]['parsed_winner']=='A'
    single_judge=SimpleNamespace(model_name='fake-judge',prompt_template={
        'prompt_template':'Q: {question}\n{answer}','system_prompt':'Synthetic rubric','output_format':'[[rating]]'})
    single=[]
    for text in ['[[8]]','[[11]]','Analysis [3], final rating [8]','No score']:
        judge_text['text']=text
        score,_,_=ns['run_judge_single'](question,answer,single_judge,None)
        single.append({'stubbed_judge_text':text,'parsed_score':score})
    assert single[1]['parsed_score']==11 and single[2]['parsed_score']==3
    result['fastchat_pair_parser']=rows
    result['fastchat_single_parser']=single
    ns={'Enum':Enum,'re':re,'Any':Any,'TestSpec':Any}
    constant_names=['ResolvedStatus','TestStatus','EvalType','FAIL_TO_PASS','FAIL_TO_FAIL','PASS_TO_PASS','PASS_TO_FAIL',
        'APPLY_PATCH_FAIL','RESET_FAILED','TESTS_ERROR','TESTS_TIMEOUT','START_TEST_OUTPUT','END_TEST_OUTPUT','TEST_EXIT_CODE']
    select_nodes(src['swe_constants'],constant_names,ns)
    names=['SUITE_RAN','TEST_EXIT_CODE_RE','parse_test_exit_code','_resolve_case','test_passed',
        'test_maintained','test_failed','get_logs_eval','get_eval_tests_report',
        'compute_fail_to_pass','compute_pass_to_pass','get_resolution_status']
    result['function_lines']['swe']=select_nodes(src['swe_grading'],names,ns)
    gold={ns['FAIL_TO_PASS']:['fix'],ns['PASS_TO_PASS']:['keep']}
    rows=[]
    for name,statuses in [
        ('all_pass',{'fix':'PASSED','keep':'PASSED'}),
        ('skip_fix',{'fix':'SKIPPED','keep':'PASSED'}),
        ('skip_regression',{'fix':'PASSED','keep':'SKIPPED'}),
        ('xfail_fix',{'fix':'XFAIL','keep':'PASSED'}),
        ('missing_fix',{'keep':'PASSED'}),
        ('missing_all',{})]:
        for mode in [ns['EvalType'].PASS_AND_FAIL,ns['EvalType'].FAIL_ONLY]:
            report=ns['get_eval_tests_report'](statuses,gold,eval_type=mode)
            rows.append({'case':name,'mode':mode.value,'resolution':ns['get_resolution_status'](report),'report':report})
    result['swe_status_fixtures']=rows
    result['swe_truncated_ids']={
       'uniform_pass':ns['test_passed']('test_x[a',{'test_x[abc]':'PASSED','test_x[abd]':'XFAIL'}),
       'mixed_pass_fail':ns['test_passed']('test_x[a',{'test_x[abc]':'PASSED','test_x[abd]':'FAILED'}),
       'complete_id_no_prefix_fallback':ns['test_passed']('test_x',{'test_xyz':'PASSED'})}
    logs=[]
    ns['PARSER_REGISTRY']={'fixture':lambda text,spec: {'fix':'PASSED'} if 'STUB_PASS' in text else {}}
    spec=SimpleNamespace(log_parser='fixture')
    for name,middle,exit_code in [('empty','',0),('zero_tests','Executed 0 of 0',0),
        ('real_runner_evidence','1 passing',0),('spoofed_pass_exit_1','STUB_PASS',1),
        ('pass_exit_0','STUB_PASS',0)]:
        with tempfile.NamedTemporaryFile(mode='w+',suffix='.log') as f:
            f.write(ns['START_TEST_OUTPUT']+'\n'+middle+'\n'+ns['END_TEST_OUTPUT']+'\n'+ns['TEST_EXIT_CODE']+f': {exit_code}\n')
            f.flush()
            status,valid=ns['get_logs_eval'](spec,f.name)
            logs.append({'case':name,'valid':valid,'status_map':status})
    assert [x['valid'] for x in logs]==[False,False,True,False,True]
    result['swe_log_gate_fixtures']=logs
    out=HERE/'results'/'scorer_diagnostics.json'
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--download',action='store_true',help='Fetch pinned upstream sources to a temporary directory.')
    main(p.parse_args().download)
