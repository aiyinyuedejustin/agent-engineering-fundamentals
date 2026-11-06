#!/usr/bin/env python3
"""Execute unchanged pinned lifecycle AST with all device/providers mocked.

No Android imports, ADB commands, subprocesses, sockets, network, permission
changes or device data operations are executed. Recorded commands are strings.
"""
import argparse
import ast
import datetime
import hashlib
import json
import logging
from pathlib import Path
import types
import unittest
from unittest.mock import Mock

EXPECTED = {
    "controller.py": "3ce79c02e62208c7e3271826c1621bd52f9b43a8",
    "task_eval.py": "bce5a4e19f90be5754d2ee401cf3223054d6e81b",
    "app_snapshot.py": "e2d23cab729c5352c28b5080013b63e855b72e25",
    "suite_utils.py": "2c72a418f773779d60799ef4eebae0eff192c635",
}


def checked_sources(root):
    sources, manifest = {}, {}
    for name, expected in EXPECTED.items():
        data = (root / name).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if blob != expected:
            raise SystemExit(f"Refusing unmatched source {name}: {blob}")
        sources[name] = data.decode()
        manifest[name] = {"git_blob": blob, "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()}
    return sources, manifest


def load_functions(source, names, globals_dict, class_name=None):
    tree = ast.parse(source)
    body = tree.body
    if class_name:
        body = next(n for n in body if isinstance(n, ast.ClassDef) and n.name == class_name).body
    nodes = [n for n in body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes} == set(names)
    assert all(not n.decorator_list for n in nodes)
    future = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
    module = ast.fix_missing_locations(ast.Module(body=[future, *nodes], type_ignores=[]))
    exec(compile(module, "hash-verified-upstream-ast.py", "exec"), globals_dict)
    return globals_dict


class LifecycleTests(unittest.TestCase):
    def test_observation_can_request_network_enable(self):
        forest = object()
        env = types.SimpleNamespace(
            attempt_enable_networking=Mock(),
            accumulate_new_extras=lambda: {"accessibility_tree": [forest]},
        )
        ns = load_functions(SOURCES["controller.py"], {"get_a11y_tree"}, {
            "_has_wrapper": lambda *_: True,
            "a11y_grpc_wrapper": types.SimpleNamespace(A11yGrpcWrapper=object),
            "cast": lambda _, value: value,
            "adb_utils": types.SimpleNamespace(retry=lambda _: lambda f: f,
                                                check_airplane_mode=lambda _: True),
            "logging": logging,
            "time": types.SimpleNamespace(sleep=lambda _: None),
        })
        self.assertIs(ns["get_a11y_tree"](env), forest)
        env.attempt_enable_networking.assert_called_once_with()

    def make_task(self, *, initialized=False):
        restore = Mock(side_effect=RuntimeError("synthetic missing snapshot"))
        ns = load_functions(SOURCES["task_eval.py"], {"_initialize_apps", "initialize_task"}, {
            "logging": logging,
            "app_snapshot": types.SimpleNamespace(restore_snapshot=restore),
            "random": types.SimpleNamespace(seed=Mock()),
        }, class_name="TaskEval")
        task = types.SimpleNamespace(app_names=("synthetic",), name="SyntheticTask",
                                     initialized=initialized, params={},
                                     initialize_device_time=Mock())
        task._initialize_apps = types.MethodType(ns["_initialize_apps"], task)
        return task, ns["initialize_task"], restore

    def test_missing_snapshot_does_not_prevent_initialized_flag(self):
        task, initialize, restore = self.make_task()
        env = types.SimpleNamespace(controller=object(), interaction_cache="previous")
        initialize(task, env)
        self.assertIs(task.initialized, True)
        self.assertEqual(env.interaction_cache, "")
        restore.assert_called_once_with("synthetic", env.controller)

    def test_duplicate_initialization_checks_after_reset_side_effects(self):
        task, initialize, restore = self.make_task(initialized=True)
        env = types.SimpleNamespace(controller=object(), interaction_cache="previous")
        with self.assertRaisesRegex(RuntimeError, "already called"):
            initialize(task, env)
        task.initialize_device_time.assert_called_once_with(env)
        restore.assert_called_once()
        self.assertEqual(env.interaction_cache, "")

    def test_restore_clear_failure_continues_copy_and_permission_commands(self):
        commands = []
        copy_dir = Mock()
        close_app = Mock()
        ns = load_functions(SOURCES["app_snapshot.py"], {"restore_snapshot"}, {
            "_snapshot_path": lambda _: "/synthetic/snapshot",
            "_app_data_path": lambda _: "/synthetic/app",
            "logging": logging,
            "file_utils": types.SimpleNamespace(
                check_directory_exists=lambda *_: True,
                clear_directory=Mock(side_effect=RuntimeError("synthetic clear failure")),
                copy_dir=copy_dir,
            ),
            "adb_utils": types.SimpleNamespace(
                close_app=close_app, check_ok=lambda *_: None,
                issue_generic_request=lambda command, _: commands.append(command),
            ),
        })
        env = object()
        ns["restore_snapshot"]("synthetic", env)
        close_app.assert_called_once_with("synthetic", env)
        copy_dir.assert_called_once_with("/synthetic/snapshot", "/synthetic/app", env)
        self.assertEqual(commands, [
            ["shell", "restorecon", "-RD", "/synthetic/app"],
            ["shell", "chmod", "777", "-R", "/synthetic/app"],
        ])

    def test_episode_exception_returns_before_teardown(self):
        task = types.SimpleNamespace(name="SyntheticTask", goal="synthetic goal",
                                     initialize_task=Mock(), is_successful=Mock(),
                                     tear_down=Mock())
        ns = load_functions(SOURCES["suite_utils.py"], {"_run_task"}, {
            "time": types.SimpleNamespace(time=lambda: 0),
            "logging": logging,
            "traceback": types.SimpleNamespace(print_exc=lambda: None,
                                                format_exc=lambda: "synthetic traceback"),
            "_log_and_print": lambda *_: None,
            "_create_failed_result": lambda *args: {"failed_args": args},
        })
        env = object()
        result = ns["_run_task"](task, Mock(side_effect=ValueError("synthetic episode failure")),
                                  env, demo_mode=False)
        self.assertEqual(result["failed_args"][0], "SyntheticTask")
        task.initialize_task.assert_called_once_with(env)
        task.is_successful.assert_not_called()
        task.tear_down.assert_not_called()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source_directory", type=Path)
    args = parser.parse_args()
    SOURCES, manifest = checked_sources(args.source_directory)
    print(json.dumps({"timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      "scope": "unchanged local AST; all Android/provider operations mocked",
                      "sources": manifest}, indent=2), flush=True)
    unittest.main(argv=[__file__], verbosity=2)
