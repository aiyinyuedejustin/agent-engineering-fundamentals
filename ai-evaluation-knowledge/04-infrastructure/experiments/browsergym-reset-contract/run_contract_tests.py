#!/usr/bin/env python3
"""No-network, no-browser probes of pinned reset and dependency code.

Upstream function/class AST bodies are unchanged. Only imports, annotations,
environment, clock and HTTP providers are substituted. No sockets or processes
are created. Git blob validation applies to each entire input file first.
"""
import argparse
import ast
from collections import defaultdict
from copy import deepcopy
import csv
import datetime
import hashlib
import io
import json
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest

EXPECTED = {
    "bg_instance.py": "1e6a9f98ce91aaaa435ee8a7ed6e31836dfe93cf",
    "bg_metadata_utils.py": "f1fccd6f9c504b979f24ee66f1133ab0c3d0d7ae",
    "bg_webarena.csv": "b263a22d41d9dfd917be4eed4ee1a127753129e5",
    "agentlab_exp_utils.py": "27b909b2eefb9c8f5809384681c81da1c1d99b71",
}


def checked_sources(root):
    sources, manifest = {}, {}
    for name, expected in EXPECTED.items():
        data = (root / name).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if blob != expected:
            raise SystemExit(f"Refusing mismatched source: {name}: {blob}")
        sources[name] = data.decode()
        manifest[name] = {"git_blob": blob, "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()}
    return sources, manifest


def load_nodes(source, names, namespace):
    nodes = [node for node in ast.parse(source).body
             if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names]
    assert {node.name for node in nodes} == set(names)
    future = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
    tree = ast.fix_missing_locations(ast.Module(body=[future, *nodes], type_ignores=[]))
    exec(compile(tree, "hash-verified-upstream-ast.py", "exec"), namespace)
    return namespace


class ResetTests(unittest.TestCase):
    def setUp(self):
        self.env = {}
        self.calls = []
        self.clock = iter([0, 601])

        def fake_get(url, **kwargs):
            self.calls.append((url, kwargs))
            if url.endswith("/reset"):
                return SimpleNamespace(status_code=200, text="Reset initiated")
            if url.endswith("/status"):
                return SimpleNamespace(status_code=200, text="Ready for duty!")
            return SimpleNamespace(status_code=500, text="Synthetic unhealthy site")

        self.requests = SimpleNamespace(
            get=fake_get,
            exceptions=SimpleNamespace(ConnectionError=ConnectionError, Timeout=TimeoutError))
        self.ns = load_nodes(SOURCES["bg_instance.py"], {"WebArenaInstance"}, {
            "os": SimpleNamespace(environ=self.env),
            "requests": self.requests,
            "time": SimpleNamespace(time=lambda: next(self.clock), sleep=lambda _: None),
            "logger": logging.getLogger("reset-mock"),
        })
        cls = self.ns["WebArenaInstance"]
        self.instance = cls.__new__(cls)
        self.instance.urls = {"gitlab": "https://synthetic.invalid/gitlab"}

    def test_missing_reset_url_skips_but_checks_reachability(self):
        self.assertIs(self.instance.full_reset(), False)
        self.assertEqual(self.calls, [(self.instance.urls["gitlab"], {"timeout": 60})])

    def test_strict_missing_url_raises_before_provider_calls(self):
        with self.assertRaisesRegex(RuntimeError, "Could not reset"):
            self.instance.full_reset(skip_if_not_set=False)
        self.assertEqual(self.calls, [])

    def test_ready_protocol_can_pass_with_unhealthy_site_status(self):
        self.env["WA_FULL_RESET"] = "https://synthetic.invalid/control"
        self.assertIs(self.instance.full_reset(), True)
        self.assertEqual([kwargs for _, kwargs in self.calls], [{}, {}, {"timeout": 60}])
        # The actual readiness helper ignores the synthetic site's HTTP 500.
        # This is not an HTTP request, server run or external-state reset.

    def test_poll_deadline_only_checked_after_status_returns(self):
        self.env["WA_FULL_RESET"] = "https://synthetic.invalid/control"
        original = self.requests.get

        def pending(url, **kwargs):
            result = original(url, **kwargs)
            if url.endswith("/status"):
                result.text = "Reset ongoing"
            return result

        self.requests.get = pending
        with self.assertRaisesRegex(Exception, "601 seconds"):
            self.instance.full_reset()
        self.assertEqual([kwargs for _, kwargs in self.calls], [{}, {}])


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.ns = load_nodes(SOURCES["bg_metadata_utils.py"], {
            "extract_graph_children", "extract_sparse_task_dependency_graph_from_subset",
            "build_env_args_dependency_graphs",
        }, {"defaultdict": defaultdict, "deepcopy": deepcopy})
        self.parents = {r["task_name"]: r["depends_on"].split()
                        for r in csv.DictReader(io.StringIO(SOURCES["bg_webarena.csv"]))}

    def test_actual_metadata_contracts_removed_intermediate_tasks(self):
        subset = ["webarena.441", "webarena.445"]
        graph = self.ns["extract_sparse_task_dependency_graph_from_subset"](subset, self.parents)
        self.assertEqual(graph, {"webarena.441": [], "webarena.445": ["webarena.441"]})

    def test_nonparallel_seeds_produce_separate_graphs_not_reset_actions(self):
        args = [SimpleNamespace(task_name=n) for n in ["a", "a", "b", "b"]]
        graphs = self.ns["build_env_args_dependency_graphs"](
            args, {"a": [], "b": ["a"]}, supports_parallel_seeds=False)
        self.assertEqual(graphs, [{0: [], 2: [0]}, {1: [], 3: [1]}])

    def test_agentlab_consumer_rejects_repeated_task_names_with_dependencies(self):
        ns = load_nodes(SOURCES["agentlab_exp_utils.py"], {"add_dependencies"}, {})
        args = [SimpleNamespace(env_args=SimpleNamespace(task_name=n), make_id=lambda: None)
                for n in ["a", "a", "b", "b"]]
        with self.assertRaisesRegex(ValueError, "can't run multiple seeds"):
            ns["add_dependencies"](args, {"a": [], "b": ["a"]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source_directory", type=Path)
    args = parser.parse_args()
    SOURCES, manifest = checked_sources(args.source_directory)
    print(json.dumps({"timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      "scope": "local unchanged AST and mock HTTP/clock; no network or browser",
                      "sources": manifest}, indent=2), flush=True)
    unittest.main(argv=[__file__], verbosity=2)
