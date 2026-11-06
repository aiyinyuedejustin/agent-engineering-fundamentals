"""Offline BFCL v4 checker contracts on synthetic data, without model/tool runs.

Usage: python bfcl_checker_probe.py AST_SOURCE AGENTIC_SOURCE MULTITURN_SOURCE
Extracts reviewed pure checker functions, not imports or executable backends.
The final two checks use a deliberately mocked executor and are labelled so.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from enum import Enum
from pathlib import Path
from types import SimpleNamespace

REVISION = "6ea57973c7a6097fd7c5915698c54c17c5b1b6c8"


class Language(Enum):
    PYTHON = "Python"
    JAVA = "Java"
    JAVASCRIPT = "JavaScript"


def extract(path, names, constants=(), extra=None):
    raw = Path(path).read_bytes()
    tree = ast.parse(raw)
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            nodes.append(node)
        elif isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id in constants for t in node.targets
        ):
            nodes.append(node)
    assert {n.name for n in nodes if isinstance(n, ast.FunctionDef)} == set(names)
    ns = {"re": re, "Language": Language}
    ns.update(extra or {})
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), ns)
    return ns, hashlib.sha256(raw).hexdigest()


def main():
    ast_names = {
        "ast_checker", "find_description", "get_possible_answer_type", "convert_func_name",
        "type_checker", "standardize_string", "string_checker", "list_checker", "dict_checker",
        "list_dict_checker", "simple_function_checker", "parallel_function_checker_no_order",
        "multiple_function_checker",
    }
    a, ahash = extract(sys.argv[1], ast_names, ["PYTHON_TYPE_MAPPING", "PYTHON_NESTED_TYPE_CHECK_LIST"])
    g, ghash = extract(sys.argv[2], {"agentic_checker", "standardize_string"})
    m, mhash = extract(sys.argv[3], {
        "multi_turn_checker", "multi_turn_irrelevance_checker", "state_checker", "response_checker",
        "_compare_instances", "_is_subsequence_unordered",
    })
    records = []

    def check(name, observed, expected, scope="pure checker"):
        assert observed == expected, (name, observed, expected)
        records.append({"name": name, "observed": observed, "expected": expected, "scope": scope})

    desc = {"name": "sample", "parameters": {"properties": {
        "x": {"type": "integer"}, "label": {"type": "string"}}, "required": ["x"]}}
    gold = {"sample": {"x": [1], "label": ["re-sign", ""]}}

    def single(params, answer=gold):
        return a["simple_function_checker"](desc, {"sample": params}, answer, Language.PYTHON, "synthetic")["valid"]

    check("optional omitted with empty-string sentinel", single({"x": 1}), True)
    check("optional omitted without sentinel", single({"x": 1}, {"sample": {"x": [1], "label": ["abc"]}}), False)
    check("required boolean is not integer", single({"x": True}), False)
    check("string punctuation collision", single({"x": 1, "label": "resign"}), True)
    check("extra parameter rejected", single({"x": 1, "other": 2}), False)
    parallel_gold = [{"sample": {"x": [1, 2], "label": [""]}}, {"sample": {"x": [1], "label": [""]}}]
    outputs = [{"sample": {"x": 1}}, {"sample": {"x": 2}}]
    def parallel(out):
        return a["parallel_function_checker_no_order"]([desc], out, parallel_gold, Language.PYTHON, "synthetic")["valid"]
    check("greedy no-order match with ambiguous allowed values", parallel(outputs), False)
    check("same calls reversed avoid greedy mismatch", parallel(outputs[::-1]), True)
    check("agentic answer in negative sentence", g["agentic_checker"]("It is not amber.", ["amber"])["valid"], True)
    check("agentic whitespace is not removed", g["agentic_checker"]("NewYork", ["New York"])["valid"], False)
    check("agentic boundary rejects substring", g["agentic_checker"]("ambergris", ["amber"])["valid"], False)
    check("response result order not required", m["response_checker"](["B", "A"], ["A", "B"], 0)["valid"], True)
    check("response duplicate multiplicity required", m["response_checker"](["A"], ["A", "A"], 0)["valid"], False)
    check("extra model state and differing private state ignored", m["_compare_instances"](
        SimpleNamespace(value=1, extra="additional", _private=2), SimpleNamespace(value=1, _private=1))[0], True)

    # This is a checker control-flow probe, not execution of a BFCL environment.
    # Return unequal synthetic state after a nonempty model turn, but the gold turn is empty.
    def fake_execute(**kwargs):
        called = bool(kwargs["func_call_list"])
        return (["synthetic side effect"] if called else [], {"Stub": SimpleNamespace(value=int(called))})
    def is_empty(x):
        return len(x) == 0 or (len(x) == 1 and len(x[0]) == 0)
    m.update({"execute_multi_turn_func_call": fake_execute, "is_empty_execute_response": is_empty})
    model_turns, gold_turns = [[["synthetic_call()"]]], [[]]
    task = {"initial_config": {}, "involved_classes": ["Stub"], "id": "synthetic_0"}
    check("main checker skips state and response check for empty gold turn",
          m["multi_turn_checker"](model_turns, gold_turns, task, "synthetic", "synthetic")["valid"],
          True, "checker control flow with mocked executor")
    check("separate irrelevance checker rejects same decoded calls",
          m["multi_turn_irrelevance_checker"](model_turns, gold_turns)["valid"], False,
          "separate helper; not called by pinned eval_runner")
    print(json.dumps({"revision": REVISION, "source_sha256": {
        "ast_checker.py": ahash, "agentic_checker.py": ghash, "multi_turn_checker.py": mhash},
        "scope": "Synthetic component experiments only; no inference, actual environment execution, leaderboard reproduction or prevalence estimate.",
        "checks": records}, indent=2))


if __name__ == "__main__":
    main()
