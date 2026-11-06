"""Synthetic MLE-bench grading/aggregation fixtures; no competition/model runs.

Usage: python mlebench_grade_probe.py GRADE_HELPERS AGGREGATE_REPORTS COMPETITION_UTILS
Only reviewed classes/functions are loaded; no registry, data download or agents.
"""
from __future__ import annotations

import ast
import inspect
import hashlib
import json
import logging
import math
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Optional

import numpy as np
import pandas as pd
from scipy import stats

REVISION = "507f92e1138bb6e40dac5c6ee7a6758e6424bf97"


def extract(path, names, extra=None):
    raw = Path(path).read_bytes()
    tree = ast.parse(raw)
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    assert {n.name for n in nodes} == set(names)
    module = ModuleType("probe_" + Path(path).stem.replace("-", "_"))
    sys.modules[module.__name__] = module
    ns = module.__dict__
    ns.update({"pd": pd, "np": np, "stats": stats, "Optional": Optional, "Any": Any,
          "inspect": inspect, "logger": logging.getLogger("probe"), "defaultdict": defaultdict,
          "dataclass": dataclass, "asdict": asdict})
    ns.update(extra or {})
    future = ast.parse("from __future__ import annotations").body
    exec(compile(ast.Module(body=future + nodes, type_ignores=[]), str(path), "exec", dont_inherit=True), ns)
    return ns, hashlib.sha256(raw).hexdigest()


def main():
    g, gh = extract(sys.argv[1], {"Grader", "InvalidSubmissionError"})
    a, ah = extract(sys.argv[2], {"CompetitionReport", "SeedMetrics", "AggregateMetric", "AggregateMetrics",
                                 "zero_report", "build_complete_seeds", "calculate_metrics_for_a_seed", "average_metrics_across_seeds"})
    u, uh = extract(sys.argv[3], {"prepare_for_accuracy_metric", "prepare_for_auroc_metric"},
                    {"InvalidSubmissionError": g["InvalidSubmissionError"]})
    out = []
    def check(name, observed, expected):
        if isinstance(observed, np.bool_): observed = bool(observed)
        assert observed == expected, (name, observed, expected)
        out.append({"name": name, "observed": observed, "expected": expected})
    def raises(fn):
        try: fn()
        except Exception as e: return type(e).__name__
        return None

    grader = object.__new__(g["Grader"])
    leaderboard = pd.DataFrame({"score": list(range(100, 0, -1))})
    rank = grader.rank_score(91, leaderboard)
    check("gold threshold equality counts", bool(rank["gold_medal"]), True)
    check("medals mutually exclusive", sum(bool(rank[k]) for k in ["gold_medal", "silver_medal", "bronze_medal"]), 1)
    check("median equality does not count above median", grader.rank_score(50.5, leaderboard)["above_median"], False)
    check("missing score receives no medal", any(grader.rank_score(None, leaderboard)[k] for k in ["gold_medal", "silver_medal", "bronze_medal"]), False)
    grader.grade_fn = lambda submission, answers: 60.999999
    rounded = grader(None, None)
    check("score rounded to five decimals before thresholding", rounded, 61.0)
    check("rounding crosses synthetic bronze boundary", grader.rank_score(rounded, leaderboard)["bronze_medal"], True)
    check("unrounded value is below synthetic bronze boundary", grader.rank_score(60.999999, leaderboard)["bronze_medal"], False)
    check("ascending leaderboard infers lower is better", grader.is_lower_better(leaderboard.iloc[::-1]), True)
    grader.grade_fn = lambda submission, answers: float("nan")
    score = grader(None, None)
    check("NaN returned by grade_fn passes wrapper as non-None", math.isnan(score) and score is not None, True)
    check("NaN earns no medal by comparisons", any(grader.rank_score(score, leaderboard)[k] for k in ["gold_medal", "silver_medal", "bronze_medal"]), False)

    Report = a["CompetitionReport"]
    def report(cid, medal):
        return Report(cid, bool(medal), False, False, bool(medal), True, True)
    reports = [report("A", True), report("B", True), report("A", False)]
    complete = a["build_complete_seeds"](reports, ["A", "B"], -1)
    padded = a["build_complete_seeds"](reports, ["A", "B"], -1, pad_missing=True)
    check("default truncates to minimum complete ordinal seed count", len(complete), 1)
    check("padding keeps maximum ordinal seed count", len(padded), 2)
    metrics = lambda xs: [a["calculate_metrics_for_a_seed"](x) for x in xs]
    check("default complete-seed mean", a["average_metrics_across_seeds"](metrics(complete), 2).metrics["any_medal_percentage"].mean, 100.0)
    check("padded-seed mean includes absent report failure", a["average_metrics_across_seeds"](metrics(padded), 2).metrics["any_medal_percentage"].mean, 50.0)
    check("single-seed SEM set to zero", a["average_metrics_across_seeds"](metrics(complete), 2).metrics["any_medal_percentage"].standard_error, 0.0)
    check("entire expected competition missing raises by default", raises(lambda: a["build_complete_seeds"]([report("A", True)], ["A", "B"], -1)), "ValueError")

    answers = pd.DataFrame({"id": ["a", "b"], "label": [0, 1]})
    submission = pd.DataFrame({"id": ["b", "a"], "label": [1, 0]})
    aligned = u["prepare_for_accuracy_metric"](submission, answers, "label", "id")
    check("submission rows are aligned by IDs", aligned["y_pred"].tolist(), [0, 1])
    wrong = pd.DataFrame({"id": ["a", "c"], "label": [0, 1]})
    check("equal length but wrong IDs rejected", raises(lambda: u["prepare_for_accuracy_metric"](wrong, answers, "label", "id")), "InvalidSubmissionError")
    probability = pd.DataFrame({"id": ["a", "b"], "label": [-0.1, 1]})
    check("out of range AUROC probabilities rejected", raises(lambda: u["prepare_for_auroc_metric"](probability, answers, "id", "label")), "InvalidSubmissionError")
    print(json.dumps({"revision": REVISION, "source_sha256": {"grade_helpers.py": gh,
        "aggregate_grading_reports.py": ah, "competitions/utils.py": uh},
        "dependencies": {"pandas": pd.__version__, "numpy": np.__version__},
        "scope": "Synthetic grader/aggregation behavior only; no real competition data, historical report reanalysis, model training or full reproduction.",
        "checks": out}, indent=2))


if __name__ == "__main__":
    main()
