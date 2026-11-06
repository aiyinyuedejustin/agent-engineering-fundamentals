"""Exercise SciCode's evaluator bookkeeping using cached pass labels only.

No model, numeric test data or generated Python is executed. The only extracted
class is reviewed ScicodeEvaluator; subprocess.run is replaced by a trap.
Usage: python scicode_skip_probe.py /path/to/pinned/eval/inspect_ai/scicode.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

REVISION = "e3158ea011d4235245a547460d3688d7ccbf9900"


def main() -> None:
    source_path = Path(sys.argv[1]).resolve()
    source = source_path.read_bytes()
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
               and n.name == "ScicodeEvaluator")
    def no_subprocess(*args, **kwargs):
        raise AssertionError("The probe must not execute any candidate script")
    namespace = {"Path": Path, "time": time, "shutil": shutil,
                 "subprocess": SimpleNamespace(run=no_subprocess,
                    CalledProcessError=RuntimeError, TimeoutExpired=TimeoutError)}
    module = ast.Module(body=[cls], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(source_path), "exec"), namespace)
    results = []
    previous_cwd = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="scicode-bookkeeping-") as tmp:
        root = Path(tmp)
        try:
            os.chdir(root)
            for problem_id, total_steps, skipped in [
                ("77", 2, set()), ("13", 7, {6}),
                ("62", 2, {1}), ("76", 4, {3}),
            ]:
                work = root / problem_id
                code = work / "generated_code" / "without_background"
                logs = work / "evaluation_logs" / "without_background"
                code.mkdir(parents=True)
                logs.mkdir(parents=True)
                record = {"problem_id": problem_id, "sub_steps": []}
                for step in range(1, total_steps + 1):
                    step_id = f"{problem_id}.{step}"
                    record["sub_steps"].append({"step_number": step_id, "test_cases": []})
                    if step not in skipped:
                        (code / f"{step_id}.py").write_text("# Synthetic placeholder, never executed\n")
                        (logs / f"{step_id}.log").write_text("pass\n")
                evaluator = namespace["ScicodeEvaluator"]("not-read.h5", work, work, False)
                actual = evaluator.test_code(record)
                assert actual == (int(not skipped), total_steps - len(skipped), total_steps)
                results.append({"synthetic_problem_id": problem_id,
                    "listed_steps": total_steps, "provided_context_steps_skipped": sorted(skipped),
                    "all_evaluated_steps_have_cached_pass": True,
                    "returned_problem_correct": actual[0],
                    "returned_total_correct": actual[1], "returned_total_steps": actual[2]})
        finally:
            os.chdir(previous_cwd)
    print(json.dumps({
        "scope": "D4 only for cached-pass bookkeeping on synthetic metadata; no candidate execution or model evaluation",
        "revision": REVISION,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "source": f"https://github.com/scicode-bench/SciCode/blob/{REVISION}/eval/inspect_ai/scicode.py",
        "results": results, "subprocess_calls": 0, "all_assertions_passed": True,
        "limitation": "Does not establish frequency or effect on published model scores. Synthetic step counts are not claimed to match those real tasks."
    }, indent=2))


if __name__ == "__main__":
    main()
