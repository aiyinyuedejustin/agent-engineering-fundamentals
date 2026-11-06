#!/usr/bin/env python3
"""Execute one reviewed upstream function against a disposable scratch fixture.

This is a source-fragment experiment, not a complete upstream module import.
Never pass real cache directories. The script constructs its own fixture.
"""
import argparse
import ast
import contextlib
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile

EXPECTED_BLOB = "6fac151ba282eeccbe0014c5e7b874fe1dbbce00"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Pinned upstream eval_from_generations.py")
    args = parser.parse_args()
    source_bytes = args.source.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(source_bytes)).encode() + b"\0" + source_bytes).hexdigest()
    if blob != EXPECTED_BLOB:
        raise SystemExit(f"Refusing unmatched source: {blob}")
    tree = ast.parse(source_bytes.decode("utf-8"))
    matches = [node for node in tree.body if isinstance(node, ast.FunctionDef)
               and node.name == "remove_cache_dir"]
    if len(matches) != 1:
        raise SystemExit("Expected exactly one reviewed remove_cache_dir function")
    # Compile the original AST node, unchanged; do not import torch/Modal or execute
    # top-level decorators, image builders, model calls or multiprocessing code.
    fragment = ast.Module(body=matches, type_ignores=[])
    namespace = {"os": os, "shutil": shutil}
    exec(compile(fragment, str(args.source), "exec"), namespace)

    with tempfile.TemporaryDirectory(prefix="kb-cache-scope-") as temporary:
        root = Path(temporary)
        cache = root / "cache"
        selected = cache / "run-A" / "1" / "0" / "selected.txt"
        sibling = cache / "run-A" / "2" / "0" / "sibling.txt"
        other_run = cache / "run-B" / "1" / "0" / "other-run.txt"
        outside = root / "outside-cache.txt"
        for path in (selected, sibling, other_run, outside):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("synthetic fixture\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            namespace["remove_cache_dir"](str(cache), "run-A", 1, 0)
        observed = {
            "selected_removed": not selected.exists(),
            "sibling_removed": not sibling.exists(),
            "other_run_removed": not other_run.exists(),
            "cache_root_removed": not cache.exists(),
            "outside_cache_preserved": outside.exists(),
        }
        assert all(observed.values()), observed
        print(json.dumps({
            "at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source_git_blob": blob,
            "scope": "one unchanged upstream AST function; actual temporary filesystem writes",
            "observed": observed,
            "result": "PASS: current broad-deletion behavior reproduced, not a correctness approval",
        }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
