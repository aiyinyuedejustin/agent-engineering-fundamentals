#!/usr/bin/env python3
"""Run pinned Inspect Docker-config code, without Docker or network activity.

Only appdirs and compose-import plumbing are stubbed; PyYAML and filesystem calls
are real. Compose constants are literal-evaluated from hash-verified upstream code.
"""
import argparse
import ast
import datetime
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest

import yaml  # Preinstalled in the measured environment; this script never installs it.

CONFIG_BLOB = "cfdd5335f41e927ca7d141870a349ed5246a5a40"
COMPOSE_BLOB = "f3464f95ae8258bb851ffeb9b1c74bc427faa36e"


def checked_bytes(path, expected):
    content = path.read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
    if actual != expected:
        raise SystemExit(f"Refusing unmatched source {path.name}: {actual}")
    return content


def load_module(config_content, compose_content, central):
    for name in ("inspect_ai", "inspect_ai._util", "inspect_ai.util",
                 "inspect_ai.util._sandbox", "inspect_ai.util._sandbox.docker"):
        module = types.ModuleType(name)
        module.__path__ = []
        sys.modules[name] = module
    appdirs = types.ModuleType("inspect_ai._util.appdirs")

    def inspect_data_dir(subdir):
        directory = central / subdir
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    appdirs.inspect_data_dir = inspect_data_dir
    sys.modules[appdirs.__name__] = appdirs
    compose = types.ModuleType("inspect_ai.util._sandbox.compose")
    names = {"AUTO_COMPOSE_SUBDIR", "AUTO_COMPOSE_YAML", "COMPOSE_FILES", "DOCKERFILE"}
    for node in ast.parse(compose_content.decode()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    setattr(compose, target.id, ast.literal_eval(node.value))
    assert all(hasattr(compose, name) for name in names)
    sys.modules[compose.__name__] = compose
    module = types.ModuleType("inspect_ai.util._sandbox.docker.config")
    module.__package__ = "inspect_ai.util._sandbox.docker"
    exec(compile(config_content, "pinned-inspect-docker-config.py", "exec"), module.__dict__)
    return module


class ComposeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="compose-default-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def resolved(self, **kwargs):
        filename = MODULE.resolve_compose_file(str(self.root), **kwargs)
        return Path(filename), yaml.safe_load(Path(filename).read_text())

    def test_generic_has_no_network(self):
        _, config = self.resolved()
        self.assertEqual(config["services"]["default"]["network_mode"], "none")

    def test_dockerfile_has_no_network(self):
        (self.root / "Dockerfile").write_text("FROM scratch\n")
        _, config = self.resolved()
        self.assertEqual(config["services"]["default"]["network_mode"], "none")
        self.assertEqual(config["services"]["default"]["build"]["dockerfile"], "Dockerfile")

    def test_custom_compose_is_not_merged(self):
        original = "services:\n  default:\n    image: synthetic:test\n"
        path = self.root / "compose.yaml"
        path.write_text(original)
        actual, config = self.resolved()
        self.assertEqual(actual, path.resolve())
        self.assertEqual(path.read_text(), original)
        self.assertNotIn("network_mode", config["services"]["default"])
        self.assertNotIn("init", config["services"]["default"])

    def test_custom_compose_wins_over_legacy_auto_file(self):
        (self.root / ".compose.yaml").write_text("services: {}\n")
        path = self.root / "docker-compose.yml"
        path.write_text("services: {default: {image: synthetic:test}}\n")
        actual, _ = self.resolved()
        self.assertEqual(actual, path.resolve())

    def test_central_generation_uses_absolute_build_context(self):
        (self.root / "Dockerfile").write_text("FROM scratch\n")
        actual, config = self.resolved(project_name="synthetic-project")
        self.assertEqual(actual.parent, MODULE.auto_compose_dir())
        service = config["services"]["default"]
        self.assertEqual(service["build"]["context"], str(self.root.resolve()))
        self.assertEqual(service["network_mode"], "none")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config_source", type=Path)
    parser.add_argument("compose_source", type=Path)
    args = parser.parse_args()
    config = checked_bytes(args.config_source, CONFIG_BLOB)
    compose = checked_bytes(args.compose_source, COMPOSE_BLOB)
    with tempfile.TemporaryDirectory(prefix="compose-central-test-") as central:
        MODULE = load_module(config, compose, Path(central))
        print(json.dumps({
            "at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "config_blob": CONFIG_BLOB,
            "compose_constants_blob": COMPOSE_BLOB,
            "pyyaml": yaml.__version__,
            "scope": "actual upstream configuration code; import/appdir plumbing stubbed; no container",
        }, sort_keys=True), flush=True)
        result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(ComposeTests)
        )
        sys.exit(not result.wasSuccessful())
