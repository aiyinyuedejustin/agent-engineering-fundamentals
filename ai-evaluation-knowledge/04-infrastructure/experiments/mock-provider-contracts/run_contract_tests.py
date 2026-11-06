#!/usr/bin/env python3
"""Execute pinned upstream pure/control-flow code without Docker or network.

Usage: python run_contract_tests.py HARBOR_ERROR_POLICY.py OSWORLD_DOCKER_PROVIDER.py
No dependency installation is needed. Docker, HTTP, process listing, file locks,
provider base classes, and sleeping are replaced by in-memory test doubles.
This tests controller decisions, not virtualization or sandbox security.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

POLICY_PATH, PROVIDER_PATH = map(Path, sys.argv[1:3])
sys.argv = sys.argv[:1]
EXPECTED_GIT_BLOBS = (
    "1e35a5801ccad8e50d9c7defcfe64bd137bb5334",
    "03dc71041ac79f167f077b0f03c7ea62f85e4cf1",
)
for path, expected in zip((POLICY_PATH, PROVIDER_PATH), EXPECTED_GIT_BLOBS):
    data = path.read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if actual != expected:
        raise SystemExit(f"Refusing to execute source with unexpected git blob: {path}: {actual}")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def make_module(name, **attributes):
    module = types.ModuleType(name)
    for key, value in attributes.items():
        setattr(module, key, value)
    return module


class FakeContainer:
    def __init__(self):
        self.stopped = 0
        self.removed = 0

    def stop(self):
        self.stopped += 1

    def remove(self):
        self.removed += 1


class FakeContainers:
    def __init__(self):
        self.calls = []
        self.last_container = None

    def list(self):
        return []

    def run(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        self.last_container = FakeContainer()
        return self.last_container


class FakeClient:
    def __init__(self):
        self.containers = FakeContainers()


class FakeLock:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeProviderBase:
    def __init__(self, region):
        self.region = region


clients = []


def from_env():
    client = FakeClient()
    clients.append(client)
    return client


# Any attempted unmocked HTTP call fails closed instead of touching a network.
def forbidden_http(*args, **kwargs):
    raise AssertionError("Network calls are forbidden in this experiment")


stubs = {
    "docker": make_module("docker", from_env=from_env),
    "psutil": make_module("psutil", net_connections=lambda: []),
    "requests": make_module("requests", get=forbidden_http),
    "filelock": make_module("filelock", FileLock=FakeLock),
    "desktop_env": make_module("desktop_env"),
    "desktop_env.providers": make_module("desktop_env.providers"),
    "desktop_env.providers.base": make_module("desktop_env.providers.base", Provider=FakeProviderBase),
    "desktop_env.providers.volume": make_module(
        "desktop_env.providers.volume",
        expand_guest_volume=lambda **kwargs: None,
        normalize_volume_size=lambda value: value,
    ),
}
policy = load_module("pinned_harbor_error_policy", POLICY_PATH)
with patch.dict(sys.modules, stubs):
    provider = load_module("pinned_osworld_provider", PROVIDER_PATH)


class ErrorPolicyTests(unittest.TestCase):
    def test_agent_timeout_is_valid_and_not_retried(self):
        p = policy.policy_for("AgentTimeoutError")
        self.assertEqual(p.cause, policy.FailureCause.AGENT_EXHAUSTED_BUDGET)
        self.assertEqual((p.reward_valid, p.retry, p.grade), (True, False, True))

    def test_oom_is_invalid_retryable_not_graded(self):
        p = policy.policy_for("MemoryLimitExceededError")
        self.assertEqual((p.reward_valid, p.retry, p.grade), (False, True, False))

    def test_provider_rate_limit_is_invalid_but_graded(self):
        p = policy.policy_for("ApiRateLimitError")
        self.assertEqual((p.reward_valid, p.retry, p.grade), (False, True, True))

    def test_verifier_failure_is_invalid_not_retried(self):
        p = policy.policy_for("VerifierTimeoutError")
        self.assertEqual((p.reward_valid, p.retry, p.grade), (False, False, True))

    def test_unknown_name_is_not_inferred_from_suffix(self):
        p = policy.policy_for("CustomAgentTimeoutError")
        self.assertEqual(p.cause, policy.FailureCause.UNCLASSIFIED)
        self.assertEqual((p.reward_valid, p.retry, p.grade), (False, True, True))

    def test_registry_is_immutable(self):
        with self.assertRaises(TypeError):
            policy.ERROR_POLICIES["NewError"] = policy.UNKNOWN_ERROR_POLICY

    def test_exclusion_set_matches_policy(self):
        exclude = policy.default_exclude_exceptions()
        self.assertIn("AgentTimeoutError", exclude)
        self.assertIn("VerifierTimeoutError", exclude)
        self.assertNotIn("MemoryLimitExceededError", exclude)


class ProviderControlFlowTests(unittest.TestCase):
    def setUp(self):
        self.p = provider.DockerProvider("test")
        self.client = self.p.client
        self.p._wait_for_vm_ready = lambda: True
        # Namespace replacement only affects the module under test, not global os.
        self.patched_os = types.SimpleNamespace(
            path=types.SimpleNamespace(exists=lambda path: False, abspath=os.path.abspath)
        )
        self.os_patch = patch.object(provider, "os", self.patched_os)
        self.os_patch.start()
        self.time_patch = patch.object(provider, "time", types.SimpleNamespace(sleep=lambda n: None))
        self.time_patch.start()

    def tearDown(self):
        self.time_patch.stop()
        self.os_patch.stop()

    def start(self):
        self.p.start_emulator("/tmp/fake-system.qcow2", True, "Ubuntu")
        return self.client.containers.calls[-1]

    def test_absent_kvm_selects_software_branch(self):
        _, options = self.start()
        self.assertEqual(options["environment"]["KVM"], "N")
        self.assertEqual(options["devices"], [])

    def test_present_kvm_passes_device(self):
        self.patched_os.path.exists = lambda path: path == "/dev/kvm"
        _, options = self.start()
        self.assertEqual(options["devices"], ["/dev/kvm"])
        self.assertNotIn("KVM", options["environment"])

    def test_runtime_digest_and_readonly_backing_disk(self):
        args, options = self.start()
        self.assertIn("@sha256:", args[0])
        self.assertEqual(options["volumes"]["/tmp/fake-system.qcow2"]["mode"], "ro")
        self.assertEqual(options["cap_add"], ["NET_ADMIN"])
        self.assertEqual(set(options["ports"]), {8006, 5000, 9222, 8080})

    def test_default_guest_resources_are_environment_variables(self):
        _, options = self.start()
        for key, value in {"DISK_SIZE": "32G", "RAM_SIZE": "4G", "CPU_CORES": "4"}.items():
            self.assertEqual(options["environment"][key], value)
        self.assertNotIn("mem_limit", options)
        self.assertNotIn("nano_cpus", options)

    def test_revert_stops_and_removes_container(self):
        self.start()
        c = self.client.containers.last_container
        self.p.revert_to_snapshot("ignored", "init_state")
        self.assertEqual((c.stopped, c.removed), (1, 1))
        self.assertIsNone(self.p.container)
        self.assertIsNone(self.p.server_port)

    def test_snapshot_save_is_unsupported(self):
        with self.assertRaises(NotImplementedError):
            self.p.save_state("ignored", "test")

    def test_start_failure_attempts_cleanup(self):
        def fail_ready():
            raise TimeoutError("injected readiness failure")
        self.p._wait_for_vm_ready = fail_ready
        with self.assertRaises(TimeoutError):
            self.start()
        c = self.client.containers.last_container
        self.assertEqual((c.stopped, c.removed), (1, 1))

    def test_readiness_accepts_status_200_without_body_validation(self):
        self.p.server_port = 5000
        fake_clock = types.SimpleNamespace(time=lambda: 0, sleep=lambda n: None)
        fake_http = types.SimpleNamespace(get=lambda *args, **kwargs: types.SimpleNamespace(status_code=200))
        with patch.object(provider, "time", fake_clock), patch.object(provider, "requests", fake_http):
            self.assertTrue(provider.DockerProvider._wait_for_vm_ready(self.p))


if __name__ == "__main__":
    manifest = []
    for path in (POLICY_PATH, PROVIDER_PATH):
        data = path.read_bytes()
        manifest.append({
            "file": path.name,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "git_blob_sha1": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(),
        })
    print(json.dumps({"python": sys.version.split()[0], "sources": manifest}, indent=2), flush=True)
    unittest.main(verbosity=2)
