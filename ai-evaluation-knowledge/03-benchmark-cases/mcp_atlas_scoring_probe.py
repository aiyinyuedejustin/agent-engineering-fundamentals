"""Synthetic MCP-Atlas scorer/denominator checks, with no judge or server calls.

Usage: python mcp_atlas_scoring_probe.py /path/to/pinned/score_claims.py
Original scorer methods are extracted; the judge client returns synthetic labels.
"""
from __future__ import annotations

import ast
import asyncio
import hashlib
import json
import logging
import re
import sys
import tempfile
from pathlib import Path

import pandas as pd

REVISION = "e3dfef3ce93287c3d7b9e765c3a021f252eefbff"


async def main():
    path = Path(sys.argv[1])
    raw = path.read_bytes()
    names = {"merge_gtfa_with_model_data", "clean_claim_text", "extract_claims",
             "get_single_claim_evaluation_schema", "CoverageEvaluator", "evaluate_dataframe_async", "_compute_split_stats"}
    tree = ast.parse(raw)
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name in names]
    assert {n.name for n in nodes} == names
    ns = {"asyncio": asyncio, "ast": ast, "json": json, "logging": logging, "re": re, "pd": pd,
          "tqdm": lambda iterable, **kwargs: iterable}
    future = ast.parse("from __future__ import annotations").body
    exec(compile(ast.Module(body=future + nodes, type_ignores=[]), str(path), "exec", dont_inherit=True), ns)
    out = []
    def check(name, observed, expected):
        assert observed == expected, (name, observed, expected)
        out.append({"name": name, "observed": observed, "expected": expected})

    class StubClient:
        async def generate_structured_content(self, prompt, **kwargs):
            if "FAIL-CALL" in prompt: raise RuntimeError("synthetic judge outage")
            label = "partially_fulfilled" if "PARTIAL-CLAIM" in prompt else "fulfilled"
            return {"claim_text": "synthetic", "coverage_outcome": label, "justification": "stub", "confidence_level": 0.0}

    e = ns["CoverageEvaluator"](StubClient(), object())
    r = await e.evaluate(["FULL-CLAIM", "PARTIAL-CLAIM"], "synthetic response")
    check("fulfilled plus partial mean", r["coverage_score"], 0.75)
    check("reported zero confidence does not reduce score", r["confidence"], 0.0)
    r = await e.evaluate(["FULL-CLAIM", "FAIL-CALL"], "synthetic response")
    check("failed judge claim becomes zero while remaining in denominator", r["coverage_score"], 0.5)
    check("no claims with nonempty response yields None", (await e.evaluate([], "response"))["coverage_score"], None)
    check("short claims discarded by extraction", ns["extract_claims"](["yes", "long enough"]), ["long enough"])
    check("Python-list claim string accepted", ns["extract_claims"]("['First synthetic claim', 'Second synthetic claim']"), ["First synthetic claim", "Second synthetic claim"])

    df = pd.DataFrame({"GTFA_CLAIMS": ['["FULL-CLAIM"]'] * 2 + ['[]'],
                       "response": ["normal response", "ERROR: synthetic timeout", "normal response"]})
    scored = await ns["evaluate_dataframe_async"](df, e, "demo")
    check("error response scored zero rather than excluded", float(scored.iloc[1]["coverage_score"]), 0.0)
    check("no-claims row remains unscored", bool(pd.isna(scored.iloc[2]["coverage_score"])), True)
    s = ns["_compute_split_stats"](scored, "demo")
    check("stats retain three total rows", s["total_tasks"], 3)
    check("stats denominator excludes one None score", s["valid_responses"], 2)
    check("conditional pass rate differs from planned-task rate", s["pass_rate_0.75"], 50.0)
    both = ns["_compute_split_stats"](pd.DataFrame({"coverage_score": [None], "errors": ['["synthetic"]']}), "demo")
    check("clean_runs double subtraction can be negative", both["clean_runs"], -1)

    with tempfile.TemporaryDirectory() as tmp:
        gt, model, merged = [str(Path(tmp) / n) for n in ["gt.csv", "model.csv", "merged.csv"]]
        pd.DataFrame({"TASK": ["A", "B"], "GTFA_CLAIMS": ['["FULL-CLAIM"]'] * 2}).to_csv(gt, index=False)
        pd.DataFrame({"task_id": ["A"], "response": ["response"]}).to_csv(model, index=False)
        ns["merge_gtfa_with_model_data"](gt, model, "demo", merged)
        check("inner join drops task lacking model row", len(pd.read_csv(merged)), 1)
        pd.DataFrame({"task_id": ["A", "A"], "response": ["first", "second"]}).to_csv(model, index=False)
        ns["merge_gtfa_with_model_data"](gt, model, "demo", merged)
        joined = pd.read_csv(merged)
        check("duplicate output IDs produce duplicate scoring rows", len(joined), 2)
        check("duplicated rows still represent one unique task", joined["TASK"].nunique(), 1)

    print(json.dumps({"revision": REVISION, "source_sha256": hashlib.sha256(raw).hexdigest(),
        "pandas_version": pd.__version__, "scope": "Synthetic scorer control-flow and dataframe experiments; all judge responses mocked. No model, MCP server, tool action, live judge or leaderboard reproduction.",
        "checks": out}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
