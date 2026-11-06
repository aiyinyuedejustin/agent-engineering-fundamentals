#!/usr/bin/env python3
"""Original, stdlib-only runtime mechanism lab. Not an upstream benchmark.

No network, credentials, model calls, packages, Docker or cloud resources.
All subprocesses are controlled local Python/bash processes, waited for by us.
Writes only a requested report and temporary files. See mock-conformance-lab.md.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def check(case_id: str, kind: str, observed: dict, expected: bool) -> dict:
    if not expected:
        raise AssertionError(f"Unexpected result in {case_id}: {observed}")
    return {"id": case_id, "kind": kind, "passed": True, "observed": observed}


def turn_and_cost_limits() -> list[dict]:
    # Model a turn-boundary policy. This does not import any agent framework.
    action_batches = [1, 3, 2, 5]
    turn_limit, actions, calls = 3, 0, 0
    for count in action_batches:
        if calls >= turn_limit:
            break
        calls += 1
        actions += count
    first = check("turns_are_not_actions", "original_algorithm_mock", {
        "turn_limit": turn_limit, "model_calls": calls, "actions": actions,
    }, calls == 3 and actions == 6)
    limit, spent, billed_calls = 1.0, 0.0, 0
    for charge in [0.6, 0.6, 0.6]:
        if spent >= limit:
            break
        billed_calls += 1
        spent += charge
    second = check("precall_cost_check_can_overshoot", "original_algorithm_mock", {
        "limit": limit, "reported_cost": spent, "calls": billed_calls,
        "overshoot": round(spent - limit, 9),
    }, billed_calls == 2 and spent > limit)
    return [first, second]


def trace_completeness() -> dict:
    # This intentionally models only a reference check, not the ATIF validator.
    trace = [{"calls": ["call-1"], "results": []}]
    references_valid = all(
        result in step["calls"] for step in trace for result in step["results"]
    )
    all_calls_have_results = all(set(s["calls"]) <= set(s["results"]) for s in trace)
    return check("references_do_not_prove_completeness", "original_algorithm_mock", {
        "references_valid": references_valid,
        "all_calls_have_results": all_calls_have_results,
    }, references_valid and not all_calls_have_results)


def subtree_totals() -> dict:
    # Inclusive totals: root owns 60, child owns 30, grandchild owns 10.
    inclusive = {"root": 100, "child": 40, "grandchild": 10}
    naive_sum = sum(inclusive.values())
    return check("inclusive_tree_totals_double_count", "original_algorithm_mock", {
        "inclusive_totals": inclusive, "sum_all_nodes": naive_sum,
        "whole_run_total": inclusive["root"],
    }, naive_sum == 150 and inclusive["root"] == 100)


def cache_identity() -> dict:
    cache = {}

    def evaluate(run: str, patch: str) -> dict:
        key = (run, "model", "instance")
        if key not in cache:
            cache[key] = {"evaluated_patch_sha256": digest(patch)}
        return cache[key]

    first = evaluate("run-1", "patch-A")
    stale = evaluate("run-1", "patch-B")
    fresh = evaluate("run-2", "patch-B")
    return check("cache_key_omitting_patch_reuses_old_result", "original_algorithm_mock", {
        "first": first, "same_run_changed_patch": stale, "new_run_changed_patch": fresh,
    }, stale == first and fresh != first)


def checkpoint_side_effects() -> dict:
    # Files/state commit and remote side-effect commit are different domains.
    committed = {"next_operation": 0}
    external_writes = []
    external_writes.append("operation-0")
    # Crash before the checkpoint captures next_operation=1.
    restored = dict(committed)
    external_writes.append(f"operation-{restored['next_operation']}")
    return check("restoring_state_does_not_undo_external_effect", "original_algorithm_mock", {
        "restored": restored, "external_writes": external_writes,
        "duplicate_count": len(external_writes) - len(set(external_writes)),
    }, external_writes == ["operation-0", "operation-0"])


def observation_truncation() -> dict:
    original = "A" * 6000 + "IMPORTANT_MIDDLE_RESULT" + "Z" * 6000
    shown = original[:5000] + original[-5000:]
    return check("head_tail_observation_is_not_complete_output", "original_algorithm_mock", {
        "original_chars": len(original), "shown_chars": len(shown),
        "middle_marker_visible": "IMPORTANT_MIDDLE_RESULT" in shown,
        "full_output_sha256": digest(original), "shown_output_sha256": digest(shown),
    }, len(shown) == 10000 and "IMPORTANT_MIDDLE_RESULT" not in shown)


async def cancellation_vs_kill(directory: Path) -> dict:
    # The outer lab owns and reaps both workers. No grandchildren are spawned.
    worker = (
        "import pathlib,sys,time; "
        "pathlib.Path(sys.argv[1]).write_text('ready'); "
        "time.sleep(0.25); pathlib.Path(sys.argv[2]).write_text('completed')"
    )

    async def launch(prefix: str):
        ready, marker = directory / f"{prefix}.ready", directory / f"{prefix}.artifact"
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-I", "-c", worker, str(ready), str(marker),
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
        )
        deadline = time.monotonic() + 5
        while not ready.exists():
            if process.returncode is not None or time.monotonic() >= deadline:
                if process.returncode is None:
                    process.kill()
                await process.wait()
                raise RuntimeError("Controlled worker did not become ready")
            await asyncio.sleep(0.002)
        return process, marker

    process, marker = await launch("cancel_wait")
    try:
        waiter = asyncio.create_task(process.wait())
        await asyncio.sleep(0)  # Let the waiter start before cancelling it.
        waiter.cancel()
        try:
            await waiter
        except asyncio.CancelledError:
            pass
        still_running = process.returncode is None
        await asyncio.wait_for(process.wait(), timeout=5)
        artifact_after_cancel = marker.exists()
    finally:
        if process.returncode is None:
            process.kill()
        await process.wait()

    process, marker = await launch("terminate_process")
    try:
        process.terminate()
        await asyncio.wait_for(process.wait(), timeout=5)
        artifact_after_terminate = marker.exists()
    finally:
        if process.returncode is None:
            process.kill()
        await process.wait()
    return check("cancelling_wait_is_not_terminating_worker", "actual_local_subprocess", {
        "worker_running_after_waiter_cancel": still_running,
        "artifact_after_waiter_cancel": artifact_after_cancel,
        "artifact_after_worker_terminate": artifact_after_terminate,
        "all_workers_reaped": True,
    }, still_running and artifact_after_cancel and not artifact_after_terminate)


def shell_context(directory: Path) -> list[dict]:
    bash = shutil.which("bash")
    if not bash:
        raise RuntimeError("This local experiment requires bash")
    env = {"PATH": os.defpath, "LC_ALL": "C"}
    space_dir = directory / "directory with spaces"
    space_dir.mkdir()

    def run(command):
        return subprocess.run([bash, "--noprofile", "--norc", "-c", command],
                              cwd=directory, env=env, capture_output=True,
                              text=True, timeout=5, check=False)

    initial = run("mkdir -p child; cd child; export LAB_ONLY=changed; printf saved > ../persistent.txt")
    later = run("printf '%s|%s|%s' \"$PWD\" \"${LAB_ONLY-unset}\" \"$(cat persistent.txt)\"")
    parts = later.stdout.split("|")
    first = check("fresh_shell_preserves_files_not_cd_or_export", "actual_local_bash", {
        "first_returncode": initial.returncode, "second_returncode": later.returncode,
        "cwd_is_initial": parts[0] == str(directory), "variable": parts[1],
        "file_contents": parts[2],
    }, initial.returncode == later.returncode == 0 and parts == [str(directory), "unset", "saved"])
    unquoted = run(f"cd {space_dir} && printf reached")
    quoted = run(f"cd {shlex.quote(str(space_dir))} && printf reached")
    second = check("cwd_string_requires_shell_quoting", "actual_local_bash", {
        "unquoted_returncode": unquoted.returncode,
        "quoted_returncode": quoted.returncode, "quoted_stdout": quoted.stdout,
    }, unquoted.returncode != 0 and quoted.returncode == 0 and quoted.stdout == "reached")
    return [first, second]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repetitions", default=3, type=int)
    args = parser.parse_args()
    if not 1 <= args.repetitions <= 20:
        parser.error("--repetitions must be between 1 and 20")
    started = datetime.now(timezone.utc).isoformat()
    clock = time.monotonic()
    runs = []
    for iteration in range(args.repetitions):
        with tempfile.TemporaryDirectory(prefix="agent-runtime-lab-") as tmp:
            directory = Path(tmp)
            cases = [*turn_and_cost_limits(), trace_completeness(), subtree_totals(),
                     cache_identity(), checkpoint_side_effects(), observation_truncation(),
                     asyncio.run(cancellation_vs_kill(directory)), *shell_context(directory)]
            runs.append({"iteration": iteration + 1, "cases": cases})
    report = {
        "schema_version": "original-agent-runtime-lab-1",
        "scope": "D4 for original mocks and listed local subprocess/bash experiments only",
        "not_executed": ["Harbor", "Inspect", "mini-SWE-agent", "SWE-bench", "OSWorld",
                         "BrowserGym", "Docker daemon", "cloud providers", "model APIs"],
        "started_utc": started, "completed_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.monotonic() - clock, 6),
        "python": platform.python_version(), "system": platform.system(),
        "machine": platform.machine(), "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "repetitions": args.repetitions, "passed_cases": sum(len(r["cases"]) for r in runs),
        "runs": runs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ["scope", "elapsed_seconds", "repetitions", "passed_cases", "script_sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
