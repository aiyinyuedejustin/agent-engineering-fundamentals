#!/usr/bin/env python3
"""Bounded, reviewed HumanEval/1 task execution; not an untrusted-code service.

Hardcoded controls only. Upstream code/data are hash checked. No installation or
model API. A temporary subprocess gets a minimal environment and resource limits.
These precautions are NOT a security sandbox for arbitrary model-generated code.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import tempfile
import time

EXPECTED_BLOBS = {
    "execution.py": "bcfd7c5d452e2dcbb1ea89317c47b9e0f1c2c4ca",
    "data.py": "ed497942668840b4d6d010bfab2d1798bc81eff6",
    "data/HumanEval.jsonl.gz": "998d25196e17af24daf9b6cb3a975fe752528e46",
}
CONTROLS = {
    "handwritten_correct": (
        "    groups, group, depth = [], '', 0\n"
        "    for char in paren_string:\n"
        "        if char == ' ':\n"
        "            continue\n"
        "        group += char\n"
        "        depth += 1 if char == '(' else -1\n"
        "        if depth == 0:\n"
        "            groups.append(group)\n"
        "            group = ''\n"
        "    return groups\n"
    ),
    "handwritten_incorrect": "    return []\n",
    "syntax_error": "    return [\n",
    "controlled_timeout": "    while True:\n        pass\n",
}
TIMEOUT = 0.25


def verify_sources(root):
    for relative, expected in EXPECTED_BLOBS.items():
        content = (root / relative).read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        if actual != expected:
            raise SystemExit(f"Refusing unmatched source {relative}: {actual}")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def worker(root):
    verify_sources(root)
    data = load_module("verified_humaneval_data", root / "data.py")
    execution = load_module("verified_humaneval_execution", root / "execution.py")
    problem = data.read_problems(str(root / "data/HumanEval.jsonl.gz"))["HumanEval/1"]
    assert problem["entry_point"] == "separate_paren_groups"
    # Entire selected prompt/test were reviewed. Never execute canonical_solution.
    reviewed = {key: problem[key] for key in ("task_id", "prompt", "entry_point", "test")}
    task_digest = hashlib.sha256(json.dumps(reviewed, sort_keys=True).encode()).hexdigest()
    results = []
    for completion_id, (name, completion) in enumerate(CONTROLS.items()):
        started = time.monotonic()
        result = execution.check_correctness(problem, completion, TIMEOUT, completion_id)
        result["control"] = name
        result["wall_seconds"] = round(time.monotonic() - started, 6)
        results.append(result)
    assert results[0]["passed"] is True, results
    assert results[1]["passed"] is False and results[1]["result"].startswith("failed:"), results
    assert results[2]["passed"] is False and results[2]["result"].startswith("failed:"), results
    assert results[3]["passed"] is False and results[3]["result"] == "timed out", results
    print(json.dumps({"reviewed_task_sha256": task_digest, "controls": results}))


def limit_child():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root", type=Path)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    root = args.source_root.resolve()
    if args.worker:
        worker(root)
        return
    if platform.system() != "Linux":
        raise SystemExit("This reviewed runner is scoped to Linux; do not assume portable signal semantics")
    verify_sources(root)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix="humaneval-reviewed-task-") as temporary:
        directory = Path(temporary)
        sentinel = directory / "parent-sentinel.txt"
        sentinel.write_text("synthetic parent control\n")
        env = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "TMPDIR": temporary}
        command = [sys.executable, "-I", str(Path(__file__).resolve()), str(root), "--worker"]
        process = subprocess.Popen(command, cwd=temporary, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, start_new_session=True,
                                   preexec_fn=limit_child)
        try:
            stdout, stderr = process.communicate(timeout=12)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
            raise SystemExit("Outer watchdog stopped owned process group; experiment did not pass")
        if process.returncode != 0:
            raise SystemExit(f"Worker exited {process.returncode}: {stderr}")
        payload = json.loads(stdout)
        assert sentinel.read_text() == "synthetic parent control\n"
        remaining = sorted(path.name for path in directory.iterdir())
        assert remaining == ["parent-sentinel.txt"], remaining
        payload.update({
            "started_at_utc": started,
            "finished_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source_commit": "b9453e8f1865df0a0057a1383767caa400acfbcf",
            "source_git_blobs": EXPECTED_BLOBS,
            "python": platform.python_version(),
            "system": platform.system(),
            "kernel": platform.release(),
            "upstream_task_timeout_seconds": TIMEOUT,
            "outer_watchdog_seconds": 12,
            "per_process_limits": {"cpu_seconds": 10, "address_space_mib": 256,
                                   "file_size_mib": 1, "file_descriptors": 64, "core_bytes": 0},
            "worker_stderr": stderr,
            "sentinel_preserved": True,
            "temporary_directory_cleanup_verified": True,
            "scope": "one official task, full unchanged upstream data and execution modules, four authored controls",
            "not_claimed": "model score, pass@k, full benchmark, robust security sandbox or production performance",
        })
        print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
