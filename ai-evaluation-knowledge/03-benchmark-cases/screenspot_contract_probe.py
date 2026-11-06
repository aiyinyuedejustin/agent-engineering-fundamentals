"""ScreenSpot-Pro annotation reanalysis and bounded scorer/control-flow checks.

Usage: python screenspot_contract_probe.py /pinned/source/directory /annotations-bundle.json
Bundle schema: revision plus files [{path, source, rows}]. Raw questions/boxes stay local.
No image pixels, language model, UI action, GPU or API call is used.
"""
from __future__ import annotations
import ast
import collections
import contextlib
import copy
import hashlib
import io
import itertools
import json
import logging
import os
import statistics
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace


def funcs(path, names, ns):
    tree = ast.parse(path.read_text())
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    assert {n.name for n in nodes} == set(names)
    exec(compile(ast.Module(body=ast.parse("from __future__ import annotations").body + nodes, type_ignores=[]), str(path), "exec", dont_inherit=True), ns)
    return ns


def main():
    src, bundle_path = Path(sys.argv[1]), Path(sys.argv[2])
    bundle = json.loads(bundle_path.read_text())
    rows = [r for f in bundle["files"] for r in f["rows"]]
    def area(r):
        x1,y1,x2,y2=r["bbox"];w,h=r["img_size"]
        return 100*(x2-x1)*(y2-y1)/(w*h)
    areas = [area(r) for r in rows]
    out=[]
    def check(name, observed, expected):
        assert observed == expected, (name, observed, expected)
        out.append(dict(name=name, observed=observed, expected=expected))
    check("annotation file count", len(bundle["files"]), 26)
    check("actual task row count", len(rows), 1581)
    check("task IDs unique", len({r["id"] for r in rows}), 1581)
    check("image paths unique", len({r["img_filename"] for r in rows}), 1581)

    names=["collect_results_to_eval","calc_metric_for_result_list","eval_sample_positive_gt","eval_sample_negative_gt","main"]
    ns=funcs(src/"screenspot-eval.py",names,dict(copy=copy,itertools=itertools,json=json,os=os,logging=logging,tqdm=lambda x,**kw:x,
        GT_TYPES=["positive","negative"],INSTRUCTION_STYLES=["instruction","action","description"],LANGUAGES=["en","cn"]))
    # Pure scorer tests use synthetic geometry, not benchmark ground truth.
    task=dict(bbox=[20,10,40,30],img_size=[100,100])
    score=ns["eval_sample_positive_gt"]
    check("normalized point inside pixel gold box",score(task,dict(point=[.3,.2])),"correct")
    check("box boundary included",score(task,dict(point=[.2,.1])),"correct")
    check("unconverted pixel point fails",score(task,dict(point=[30,20])),"wrong")
    check("missing point is wrong format",score(task,dict(point=None)),"wrong_format")
    check("positive scorer ignores conflicting negative label",score(task,dict(point=[.3,.2],result="negative")),"correct")
    m=ns["calc_metric_for_result_list"]([dict(correctness="correct",ui_type="text"),dict(correctness="wrong",ui_type="icon"),dict(correctness="wrong_format",ui_type="icon")])
    check("format errors remain in overall denominator",m["action_acc"],1/3)
    check("text/icon macro average would differ",(m["text_acc"]+m["icon_acc"])/2,.5)
    check("empty group reports zero",ns["calc_metric_for_result_list"]([])["action_acc"],0)
    check("lang output does not satisfy language filter",len(ns["collect_results_to_eval"]([dict(lang="en")],language="en")),0)

    calls=[]
    class Model:
        def ground_only_positive(self,instruction,image):
            calls.append(("positive",instruction))
            return dict(point=[.3,.2],result="positive",raw_response="synthetic")
        def ground_allow_negative(self,instruction,image):
            calls.append(("negative",instruction))
            return dict(point=None,result="negative",raw_response="synthetic")
    ns["build_model"]=lambda args:Model()
    ns["evaluate"]=lambda results:dict(details=results,metrics=ns["calc_metric_for_result_list"](results))
    with tempfile.TemporaryDirectory() as d:
        p=Path(d);(p/"data").mkdir()
        synthetic=dict(id="synthetic",img_filename="not-read.png",bbox=[20,10,40,30],img_size=[100,100],instruction="Synthetic target",instruction_cn="Synthetic alternate",platform="test",application="test",group="test",ui_type="text")
        (p/"data"/"synthetic.json").write_text(json.dumps([synthetic]))
        args=SimpleNamespace(task="synthetic",screenspot_test=str(p/"data"),screenspot_imgs=d,inst_style="all",language="en",gt_type="positive",log_path=str(p/"out"/"a.json"))
        ns["main"](args)
        check("all styles cause three inference calls",len(calls),3)
        check("English style expansion reuses same instruction",len({c[1] for c in calls}),1)
        calls.clear();args.inst_style="instruction";args.gt_type="all"
        ns["main"](args)
        check("serial all-types route uses last task type for both",[c[0] for c in calls],["negative","negative"])
        results=json.loads((p/"out"/"a.json").read_text())["details"]
        check("stored sample types still differ despite shared route",[r["gt_type"] for r in results],["positive","negative"])

    par=funcs(src/"screenspot-eval-parallel.py",["worker_function"],dict(os=os,worker_model=Model(),eval_sample_positive_gt=ns["eval_sample_positive_gt"],eval_sample_negative_gt=ns["eval_sample_negative_gt"]))
    calls.clear()
    for gt in ["positive","negative"]:
        par["worker_function"]({**synthetic,"screenspot_imgs":"not-read", "prompt_to_evaluate":"Synthetic target","language":"en","instruction_style":"instruction","task_filename":"synthetic","gt_type":gt})
    check("parallel worker routes each task's own type",[c[0] for c in calls],["positive","negative"])

    geo=funcs(src/"screenspot-narrowing.py",["view_bbox_to_real_bbox"],{})
    check("crop-local box maps through parent viewport",geo["view_bbox_to_real_bbox"]([0,0,1,1],[.25,.125,.75,.625]),[.25,.125,.75,.625])
    check("crop center is not global center",geo["view_bbox_to_real_bbox"]([.5,.5,.5,.5],[0,0,.5,.5]),[.25,.25,.25,.25])

    def inside(r):
        x1,y1,x2,y2=r["bbox"];w,h=r["img_size"]
        return 0<=x1<x2<=w and 0<=y1<y2<=h
    stats=dict(rows=len(rows),unique_ids=len({r["id"] for r in rows}),unique_image_paths=len({r["img_filename"] for r in rows}),
        ui_types=dict(collections.Counter(r["ui_type"] for r in rows)),platforms=dict(collections.Counter(r["platform"] for r in rows)),groups=dict(collections.Counter(r["group"] for r in rows)),
        mean_target_area_percent=statistics.mean(areas),median_target_area_percent=statistics.median(areas),
        target_area_below_0_1_percent=sum(a<.1 for a in areas),
        per_type={typ:dict(count=len(q),mean_area_percent=statistics.mean(map(area,q)),median_area_percent=statistics.median(map(area,q))) for typ in ["icon","text"] for q in [[r for r in rows if r["ui_type"]==typ]]},
        invalid_box_count=sum(not inside(r) for r in rows),invalid_box_task_ids=[r["id"] for r in rows if not inside(r)],
        source_files=[dict(path=f["path"],source=f["source"],rows=len(f["rows"]),canonical_json_sha256=hashlib.sha256(json.dumps(f["rows"],ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()) for f in bundle["files"]])
    return dict(scope="All26 pinned annotation files reanalyzed; original scorer/serial control flow/parallel worker and coordinate transforms tested with synthetic responses. No screenshot pixels inspected, no model or UI executed. Canonical JSON hashes identify parsed data, not original HTTP bytes.",
        code_revision="dbe00114bc53a32c61c1a267786da85967710da8",data_revision=bundle["revision"],
        source_sha256={f:hashlib.sha256((src/f).read_bytes()).hexdigest() for f in ["screenspot-eval.py","screenspot-eval-parallel.py","screenspot-narrowing.py"]},annotation_statistics=stats,checks=out)


if __name__=="__main__":
    # Original routines print coordinates and progress; keep public output machine readable.
    with contextlib.redirect_stdout(io.StringIO()):
        result=main()
    print(json.dumps(result,indent=2))
