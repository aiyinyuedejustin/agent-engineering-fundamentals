"""Probe one exact BrowseComp reference-parser method with a mock grader.
Not a benchmark run: no dataset load, network, model API, or browser.
Usage: python browsecomp_parser_probe.py --source /path/to/browsecomp_eval.py
Source: openai/simple-evals@652c89d0ca9df547706735883097e9537d40dc47
"""
import argparse
import ast
import hashlib
import json
import re
import types
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True)
args = parser.parse_args()
source = Path(args.source).read_text()
tree = ast.parse(source)
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "BrowseCompEval")
method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "grade_sample")
namespace = {"re": re, "GRADER_TEMPLATE": "{question} {correct_answer} {response}"}
exec(compile(ast.Module(body=[method], type_ignores=[]), "<source-method>", "exec"), namespace)

rows = []
for judge_output in ["correct: yes", "correct: no", "invalid output"]:
    class MockGrader:
        def _pack_message(self, **kwargs):
            return kwargs
        def __call__(self, messages):
            return types.SimpleNamespace(response_text=judge_output)
    owner = types.SimpleNamespace(grader_model=MockGrader())
    parsed = namespace["grade_sample"](owner, "toy question", "toy answer", "toy response")
    rows.append({"mock_judge_output": judge_output, "grade_result": parsed,
                 "is_correct": parsed == "yes", "is_incorrect": parsed == "no"})
print(json.dumps({"scope": "parser-only mock experiment, not benchmark reproduction",
                  "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                  "rows": rows}, indent=2))

