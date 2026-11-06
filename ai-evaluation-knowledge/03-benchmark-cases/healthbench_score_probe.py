"""Offline HealthBench reference-score probes; no medical or model evaluation.

Usage: python healthbench_score_probe.py /path/to/pinned/healthbench_eval.py
Only reviewed rubric/arithmetic/aggregation definitions are AST-extracted.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

import numpy as np

REVISION = "652c89d0ca9df547706735883097e9537d40dc47"


def main() -> None:
    path = Path(sys.argv[1])
    source = path.read_bytes()
    tree = ast.parse(source)
    selected = {"RubricItem", "calculate_score", "calculate_length_adjusted_score",
                "_compute_clipped_stats", "_aggregate_get_clipped_mean"}
    nodes = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))
             and n.name in selected]
    assert len(nodes) == len(selected)
    module = ast.Module(body=[ast.ImportFrom(module="__future__",
        names=[ast.alias(name="annotations")], level=0)] + nodes, type_ignores=[])
    ns = {"np": np, "defaultdict": defaultdict,
          "EvalResult": lambda **kw: SimpleNamespace(**kw)}
    exec(compile(ast.fix_missing_locations(module), str(path), "exec"), ns)
    item = ns["RubricItem"]
    raw_negative = ns["calculate_score"](
        [item("synthetic positive criterion", 2, []), item("synthetic penalty", -3, [])],
        [{"criteria_met": True}, {"criteria_met": True}])
    assert raw_negative == -0.5
    negative_only = ns["calculate_score"]([item("synthetic penalty", -3, [])],
                                         [{"criteria_met": True}])
    assert negative_only is None
    values = [-0.5, 1.0]
    late_clip = float(ns["_compute_clipped_stats"](values, "mean"))
    early_clip = float(np.mean(np.clip(values, 0, 1)))
    assert late_clip == 0.25 and early_clip == 0.5
    adjustments = []
    for length, expected in [(1500, 0.8147), (2000, 0.8), (2500, 0.7853)]:
        actual = ns["calculate_length_adjusted_score"](0.8, "a" * length,
            center=2000, penalty_per_500_chars=0.0147)
        assert math.isclose(actual, expected)
        adjustments.append({"characters": length, "raw": 0.8, "adjusted": actual})
    sample = SimpleNamespace(score=0.8,
        metrics={"overall_score": 0.8, "overall_score_length_adjusted": adjustments[-1]["adjusted"]},
        html="synthetic", convo=[], example_level_metadata={})
    np.random.seed(0)
    aggregate = ns["_aggregate_get_clipped_mean"]([sample])
    assert aggregate.score == 0.8
    assert math.isclose(aggregate.metrics["overall_score_length_adjusted"], 0.7853)
    print(json.dumps({
        "scope": "D4 only for isolated synthetic scoring and field aggregation, not medical/model evaluation",
        "revision": REVISION, "source_sha256": hashlib.sha256(source).hexdigest(),
        "negative_rubric_score": raw_negative, "negative_only_tag_score": negative_only,
        "clipping_order": {"input": values, "actual_mean_then_clip": late_clip,
                           "different_clip_each_then_mean": early_clip},
        "length_adjustment": adjustments,
        "aggregate_fields": {"score": aggregate.score,
            "overall_score_length_adjusted": aggregate.metrics["overall_score_length_adjusted"]},
        "all_assertions_passed": True,
        "limitation": "Public reference is not the unreleased HealthBench Professional production implementation."
    }, indent=2))


if __name__ == "__main__":
    main()
