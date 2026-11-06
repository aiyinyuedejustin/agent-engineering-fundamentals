"""Original offline caller-contract diagnostic on synthetic saved grades.

No dataset deserialization, candidate code, network or model calls are used.
Requires NumPy and two separately downloaded fixed upstream source files.
"""
import argparse
import ast
import contextlib
import hashlib
import io
import json
import tempfile
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import numpy as np


def load_functions(path, names, namespace):
    text = path.read_text()
    nodes = [x for x in ast.parse(text).body if isinstance(x, ast.FunctionDef) and x.name in names]
    assert {x.name for x in nodes} == set(names)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pass-k-utils", type=Path, required=True)
    p.add_argument("--compute-scores", type=Path, required=True)
    args = p.parse_args()
    namespace = {"np": np, "json": json, "datetime": datetime}
    hashes = {
        "pass_k_utils.py": load_functions(args.pass_k_utils, ["estimate_pass_at_k", "compute_metrics_from_results"], namespace),
        "compute_scores.py": load_functions(args.compute_scores, ["compute_scores"], namespace),
    }
    rows = [{"contest_date": "2025-01-01T00:00:00", "graded_list": [False] * 10,
             "difficulty": difficulty, "pass@1": 0.0, "platform": "synthetic"}
            for difficulty in ["easy", "medium", "hard"]]
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / "synthetic_eval_all.json"
        path.write_text(json.dumps(rows))
        settings = SimpleNamespace(eval_all_file=str(path), start_date=None, end_date=None, platform=None)
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            namespace["compute_scores"](settings)
    overall_lines = [line for line in captured.getvalue().splitlines() if line.startswith("Pass@")]
    canonical = namespace["compute_metrics_from_results"]({i: [[False] for _ in range(10)] for i in range(3)}, [1, 5, 10, 25])
    canonical = {k: float(v) for k, v in canonical.items() if k != "detail"}
    assert canonical == {"pass@1": 0.0, "pass@5": 0.0, "pass@10": 0.0}
    assert any(line.startswith("Pass@25 =") and float(line.split("=")[1]) == 1.0 for line in overall_lines)
    print(json.dumps({"scope": "Synthetic caller-contract experiment; not a published result audit",
                      "upstream_commit": "28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24",
                      "source_sha256": hashes, "fixture": "Three synthetic tasks, each n=10,c=0",
                      "compute_scores_stdout_overall": overall_lines,
                      "guarded_compute_metrics_from_results": canonical,
                      "interpretation": "k>n is not estimable by this estimator; printing1.0 is an invalid-domain artifact, not evidence of success"}, indent=2))


if __name__ == "__main__":
    main()
