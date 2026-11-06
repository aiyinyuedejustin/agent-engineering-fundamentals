"""Offline synthetic probe of pinned ARC toolkit score functions, not game play.

Usage: python arc_score_probe.py /path/to/pinned/arc_agi/scorecard.py
Only the reviewed arithmetic class and one property getter are AST-extracted.
No package import, network request, game engine or model is used.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace

REVISION = "f12822c4d550121c35a275008d964afbbed47d2f"


def main() -> None:
    path = Path(sys.argv[1])
    source = path.read_bytes()
    tree = ast.parse(source)
    calculator = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                      and n.name == "EnvironmentScoreCalculator")
    run_list = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                   and n.name == "EnvironmentScoreList")
    best = next(n for n in run_list.body if isinstance(n, ast.FunctionDef)
                and n.name == "score")
    best.decorator_list = []
    best.name = "run_list_score"
    module = ast.Module(body=[ast.ImportFrom(module="__future__",
        names=[ast.alias(name="annotations")], level=0), calculator, best], type_ignores=[])
    namespace = {"EnvironmentScore": lambda **kw: SimpleNamespace(**kw)}
    exec(compile(ast.fix_missing_locations(module), str(path), "exec"), namespace)
    cls = namespace["EnvironmentScoreCalculator"]
    fixtures = [
        ("all_five_human_efficiency", 5, 10, 100.0),
        ("all_five_twice_human_actions", 5, 20, 25.0),
        ("first_four_very_fast_completion_cap", 4, 1, 100 * 10 / 15),
        ("only_first_at_human_efficiency", 1, 10, 100 / 15),
        ("completed_but_zero_actions_guard", 5, 0, 0.0),
    ]
    results = []
    for name, completed, actions, expected in fixtures:
        obj = cls()
        for i in range(1, 6):
            obj.add_level(i, i <= completed, actions if i <= completed else 0, 10)
        out = obj.to_score()
        assert math.isclose(out.score, expected), (name, out.score, expected)
        results.append({"case": name, "score": out.score,
                        "per_level_scores": out.level_scores,
                        "expected": expected})
    best_of = namespace["run_list_score"](SimpleNamespace(
        runs=[SimpleNamespace(score=20.0), SimpleNamespace(score=80.0)]))
    assert best_of == 80.0
    print(json.dumps({
        "scope": "D4 only for isolated arithmetic/property probes; no ARC game or model run",
        "toolkit_revision": REVISION,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "source": f"https://github.com/arcprize/ARC-AGI/blob/{REVISION}/arc_agi/scorecard.py",
        "fixtures": results,
        "multi_run_property": {"input_scores": [20.0, 80.0], "actual": best_of,
                               "arithmetic_mean_not_used": 50.0,
                               "scope": "EnvironmentScoreList.score property, not competition server"},
        "all_assertions_passed": True,
    }, indent=2))


if __name__ == "__main__":
    main()
