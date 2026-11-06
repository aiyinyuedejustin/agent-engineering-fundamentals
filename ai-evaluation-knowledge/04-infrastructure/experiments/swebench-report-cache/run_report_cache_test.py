#!/usr/bin/env python3
"""Exercise only the pinned upstream report-cache branch using temporary files.

No Docker, dataset downloads, model calls, dependency installation or test suite.
Cache misses are stopped at the first logger call before live evaluation.
"""
import argparse
import ast
import datetime
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace

EXPECTED_BLOB = "bf9680f8d910f274ffbba35d57ec5d0e47a96243"


class BlockedLiveEvaluation(RuntimeError):
    pass


def stop_before_live_evaluation(*args, **kwargs):
    raise BlockedLiveEvaluation("Cache miss: no logger, container or test execution allowed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    source_bytes = args.source.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(source_bytes)).encode() + b"\0" + source_bytes).hexdigest()
    if blob != EXPECTED_BLOB:
        raise SystemExit(f"Refusing unmatched source: {blob}")
    tree = ast.parse(source_bytes.decode("utf-8"))
    matches = [node for node in tree.body if isinstance(node, ast.FunctionDef)
               and node.name == "run_instance"]
    if len(matches) != 1:
        raise SystemExit("Expected exactly one run_instance function")
    # Preserve the upstream future-annotations directive and function AST unchanged.
    future = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
    fragment = ast.fix_missing_locations(ast.Module(body=[future, *matches], type_ignores=[]))
    with tempfile.TemporaryDirectory(prefix="swe-report-cache-") as temporary:
        root = Path(temporary)
        globals_ = {
            "RUN_EVALUATION_LOG_DIR": root,
            "LOG_REPORT": "report.json",
            "LOG_INSTANCE": "run_instance.log",
            "json": json,
            "Path": Path,
            "setup_logger": stop_before_live_evaluation,
            "create_container": stop_before_live_evaluation,
        }
        exec(compile(fragment, str(args.source), "exec"), globals_)
        evaluate = globals_["run_instance"]
        instance_id = "synthetic__case-1"
        report_file = root / "run-A" / "model__name" / instance_id / "report.json"
        report_file.parent.mkdir(parents=True)
        original_report = {instance_id: {"resolved": True, "fixture": "old-run-result"}}
        report_file.write_text(json.dumps(original_report))
        spec = SimpleNamespace(instance_id=instance_id, image="synthetic:image-A")
        prediction = {"model_name_or_path": "model/name", "model_patch": "patch-A"}
        observed = {}
        observed["initial_cached_result"] = evaluate(spec, prediction, None, "run-A") == (instance_id, original_report)
        prediction["model_patch"] = "different-patch-B"
        observed["changed_patch_returns_same_report"] = evaluate(spec, prediction, None, "run-A") == (instance_id, original_report)
        spec.image = "synthetic:different-image-B"
        observed["changed_image_returns_same_report"] = evaluate(spec, prediction, None, "run-A") == (instance_id, original_report)
        observed["skip_patch_still_returns_same_report"] = evaluate(spec, prediction, None, "run-A", skip_patch=True) == (instance_id, original_report)
        try:
            evaluate(spec, prediction, None, "run-B")
        except BlockedLiveEvaluation:
            observed["new_run_id_misses_cache_and_is_safely_stopped"] = True
        else:
            observed["new_run_id_misses_cache_and_is_safely_stopped"] = False
        assert all(observed.values()), observed
        print(json.dumps({
            "at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source_git_blob": blob,
            "scope": "unchanged run_instance AST; real JSON cache files; live-evaluation branch blocked",
            "observed": observed,
            "result": "PASS: cache-key behavior reproduced; not benchmark scoring validation",
        }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
