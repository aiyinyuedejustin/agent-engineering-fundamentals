"""Bounded RULER source experiments; no model or tokenizer execution.

Usage: python ruler_contract_probe.py /directory/containing/pinned/sources
The editdistance dependency is replaced by a transparent Levenshtein DP below.
This tests caller/scoring arithmetic, not the external library installation.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import os
import random
import re
import string
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np


def extract(path, names, ns):
    tree = ast.parse(path.read_text())
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    assert {n.name for n in nodes} == set(names)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), ns)
    return ns


def levenshtein(a, b):
    previous = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        current = [i]
        for j, y in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (x != y)))
        previous = current
    return previous[-1]


def main():
    src = Path(sys.argv[1])
    out = []
    def check(name, observed, expected):
        assert observed == expected, (name, observed, expected)
        out.append(dict(name=name, observed=observed, expected=expected))

    template_ns = {}
    exec((src / "ruler-v1-templates.py").read_text(), template_ns)
    task = template_ns["TASKS"]["variable_tracking"]
    random.seed(20261106)
    np.random.seed(20261106)
    vt = extract(src / "ruler-v1-variable-tracking.py", ["generate_chains", "generate_input_output"],
        dict(random=random, np=np, string=string,
            args=SimpleNamespace(type_haystack="noise", template=task["template"] + task["answer_prefix"]),
            haystack="The grass is green. The sky is blue. The sun is yellow. Here we go. There and back again.",
            TASKS=template_ns["TASKS"]))
    prompt, answers = vt["generate_input_output"](20, 1, 4)
    assignments = re.findall(r"VAR [A-Z]+ = (?:VAR [A-Z]+|\d+)", prompt)
    check("four hops give five target variables", len(answers), 5)
    check("five assignments inserted", len(assignments), 5)
    check("all target variable names appear", all(a in prompt for a in answers), True)
    check("assignments retain causal order", [s.split()[1] for s in assignments], answers)

    v1 = extract(src / "ruler-v1-scoring.py", ["string_match_all", "string_match_part"], {})
    check("all metric is fractional recall", v1["string_match_all"](["ABC"], [["ABC", "DEF"]]), 50.0)
    check("substring boundary is not required", v1["string_match_all"](["XABCY"], [["ABC"]]), 100.0)
    check("extra false answers do not reduce recall", v1["string_match_all"](["ABC WRONG DEF"], [["ABC", "DEF"]]), 100.0)
    check("part metric accepts any alias", v1["string_match_part"](["second"], [["first", "second"]]), 100.0)

    # An allowed numerical-key configuration, not the benchmark's default word-key config.
    tree = ast.parse((src / "ruler2-prepare-niah.py").read_text())
    templates = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in {"TEMPLATE_SINGLE", "TEMPLATE_MULTIPLE", "needle"}:
            templates[node.targets[0].id] = ast.literal_eval(node.value)
    args = SimpleNamespace(num_needle_k=1, num_needle_v=4, num_needle_q=1,
        type_needle_k="numbers", type_needle_v="numbers", num_digits_k=7, num_digits_v=10)
    random.seed(42)
    niah = extract(src / "ruler2-prepare-niah.py", ["generate_random_number", "generate_random", "generate_input_output"],
        dict(random=random, math=math, args=args, haystack=templates["needle"], **templates))
    prompt2, answers2 = niah["generate_input_output"](20)
    check("v2 multivalue generator emits four answers", len(answers2), 4)
    check("v2 ten-digit targets are in constructed prompt", all(len(x) == 10 and x in prompt2 for x in answers2), True)
    check("v2 distractors plus needles give 24 context statements", prompt2.count("One of the special magic"), 24)

    ns = extract(src / "ruler-ns-evaluator.py", ["eval_ruler", "eval_ruler2"],
        dict(json=json, os=os, re=re, editdistance=SimpleNamespace(eval=levenshtein),
             tqdm=lambda data, **kw: data,
             RulerEvaluatorConfig=lambda **kw: SimpleNamespace(parse_func="default", **kw)))
    def score(generation, refs, match="all", version=2):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "synthetic.jsonl"
            p.write_text(json.dumps(dict(generation=generation, expected_answer=refs)) + "\n")
            ns["eval_ruler2" if version == 2 else "eval_ruler"](dict(input_file=str(p), match_type=match))
            return json.loads(p.read_text())
    check("v2 WER supplies partial credit", score("red blue", ["red green"])["is_correct"], .5)
    check("v1 same paraphrase receives no credit", score("red blue", ["red green"], version=1)["is_correct"], 0)
    check("v2 full-reference substring gets full credit despite extra words", score("not red green but blue", ["red green"])["is_correct"], 1)
    check("two-step scorer only retains last blank-line segment", score("red green\n\nblue", ["red green"], "2steps")["is_correct"], 0)
    check("part scorer removes formatted copied documents", score("Document 123:\nred green\n\nblue", ["red green"], "part")["is_correct"], 0)
    check("predicted_answer field is normalized", score("red\x00green", ["red\ngreen"], version=1)["predicted_answer"], "red\ngreen")
    check("scorer uses raw generation rather than predicted_answer", score("red\x00green", ["red\ngreen"], version=1)["is_correct"], 0)

    ag = extract(src / "ruler2-score.py", ["compute_score"], {})
    tasks = [f"{family}_{level}" for family in ["mk_niah", "mv_niah", "qa"] for level in ["basic", "easy", "medium", "hard"]]
    metrics = {f"setup.{task}": {"pass@1": {"accuracy": 1 if i == 0 else 0}} for i, task in enumerate(tasks)}
    check("aggregate weights 12 tasks equally", ag["compute_score"](metrics)["setup"]["pass@1"]["accuracy"], 1/12)
    try:
        ag["compute_score"]({"setup.mk_niah_basic": {"pass@1": {"accuracy": 1}}})
        missing = False
    except KeyError:
        missing = True
    check("missing task fails instead of silently averaging subset", missing, True)

    files = ["ruler-v1-variable-tracking.py", "ruler-v1-scoring.py", "ruler-v1-templates.py", "ruler2-prepare-niah.py", "ruler-ns-evaluator.py", "ruler2-score.py"]
    print(json.dumps(dict(scope="Original generator core and scorer file-flow with synthetic inputs. No tokenizer, language model, official test corpus, serving backend or leaderboard reproduced. editdistance library substituted by explicit dynamic programming.",
        revisions={"NVIDIA/RULER":"db43f92ff634bbce1c33d1fb15858aec4bba509a", "NVIDIA-NeMo/Skills":"bcf059af55c20a89f797724598f9908d126153e6"},
        source_sha256={f:hashlib.sha256((src/f).read_bytes()).hexdigest() for f in files}, numpy_version=np.__version__,
        constructed_tasks=[dict(kind="v1 variable tracking", seed=20261106, noise_repetitions=20, hops=4, assignments=assignments, answers=answers, prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest()),
            dict(kind="v2 multivalue NIAH with nondefault numerical keys", seed=42, distractors=20, answers=answers2, prompt_sha256=hashlib.sha256(prompt2.encode()).hexdigest())],
        checks=out), indent=2))


if __name__ == "__main__":
    main()
