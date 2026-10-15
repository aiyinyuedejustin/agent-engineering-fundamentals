"""Original black-box audit. Every mutation is in a fresh owned TemporaryDirectory.

Uses the frozen runner only to own its child handles and fixture directories.
Expected bytes, digests, outcomes, and file snapshots are authored here.
No protocol helper functions are used as the test oracle.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lab

OLD = b'{"label":"old","revision":7}\n'
NEW = b'{"label":"new","revision":8}\n'
R9 = b'{"label":"independent-r9","revision":9}\n'
FIXTURES = ("settings.json", "candidate.json", "intent.json", "receipt.json")


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(box):
    """Independent raw bytes plus identity/time metadata, excluding access time."""
    out = {}
    for name in FIXTURES:
        path = box.root / name
        if path.exists():
            stat = path.stat()
            out[name] = (path.read_bytes(), stat.st_ino, stat.st_mtime_ns, stat.st_size)
    return out


def receipt():
    return {"schema": 1, "resource": "synthetic-settings", "operationId": "op-r7-r8",
            "nextHash": sha(NEW), "revision": 8}


class IndependentAudit(unittest.TestCase):
    def assert_rejected_stable(self, box, expected, repeats=3):
        before = snapshot(box)
        for _ in range(repeats):
            result = box.run("recover")["result"]
            self.assertEqual(result, {"status": "rejected", "action": expected,
                                    "target_replacements": 0, "receipt_writes": 0})
            self.assertEqual(snapshot(box), before)

    def test_01_all_eight_writer_cuts_use_actual_owned_child_termination(self):
        cases = {
            "C0": (OLD, "no-intent", 0),
            "C1": (OLD, "no-intent", 0),
            "C2": (OLD, "no-intent", 0),
            "C3": (OLD, "invalid-journal", 0),
            "C4": (OLD, "installed-candidate", 1),
            "C5": (NEW, "finalized-installed", 0),
            "C6": (NEW, "finalized-installed", 0),
            "C7": (NEW, "already-committed", 0),
        }
        for cut, (before_bytes, action, replace_count) in cases.items():
            with self.subTest(cut=cut), lab.Sandbox() as box:
                stopped = box.run("write", cut)
                if os.name == "posix":
                    self.assertEqual(stopped["exit_code"], -signal.SIGTERM)
                self.assertEqual(stopped["stop_method"], "Popen.terminate-after-checkpoint-handshake")
                self.assertEqual(box.read("settings.json"), before_bytes)
                before = snapshot(box)
                result = box.run("recover")["result"]
                self.assertEqual(result["action"], action)
                self.assertEqual(result["target_replacements"], replace_count)
                if cut in ("C0", "C1", "C2", "C3"):
                    self.assertNotEqual(result["status"], "committed")
                    self.assertEqual(snapshot(box), before)
                else:
                    self.assertEqual(box.read("settings.json"), NEW)
                    self.assertEqual(json.loads(box.read("receipt.json")), receipt())
                    self.assertFalse((box.root / "intent.json").exists())
                    committed = snapshot(box)
                    for _ in range(3):
                        repeated = box.run("recover")["result"]
                        self.assertEqual(repeated["action"], "already-committed")
                        self.assertEqual(snapshot(box), committed)

    def test_02_stale_intent_and_matching_receipt_cannot_overwrite_r9(self):
        for cut in ("C4", "C5", "C6"):
            for add_receipt in (False, True):
                with self.subTest(cut=cut, receipt=add_receipt), lab.Sandbox() as box:
                    box.run("write", cut)
                    box.put("settings.json", R9)
                    if add_receipt:
                        box.put("receipt.json", encode(receipt()))
                    self.assert_rejected_stable(box, "base-conflict")
                    self.assertEqual(box.read("settings.json"), R9)

    def test_03_installed_target_does_not_depend_on_lost_or_corrupt_candidate(self):
        for residue in (None, b"broken", b'{"revision":99}'):
            with self.subTest(residue=residue), lab.Sandbox() as box:
                box.run("write", "C5")
                if residue is not None:
                    box.put("candidate.json", residue)
                target = snapshot(box)["settings.json"]
                result = box.run("recover")["result"]
                self.assertEqual(result["action"], "finalized-installed")
                self.assertEqual(result["target_replacements"], 0)
                self.assertEqual(snapshot(box)["settings.json"], target)
                if residue is not None:
                    self.assertEqual(box.read("candidate.json"), residue)

    def test_04_rebinding_candidate_hash_and_journal_cannot_change_the_request(self):
        candidates = [
            {"revision": 8.0, "label": "new"},
            {"revision": True, "label": "new"},
            {"revision": "8", "label": "new"},
            {"revision": 8, "label": None},
            {"revision": 8, "label": "new", "extra": 1},
        ]
        for value in candidates:
            with self.subTest(value=value), lab.Sandbox() as box:
                box.run("write", "C4")
                candidate = encode(value)
                box.put("candidate.json", candidate)
                journal = json.loads(box.read("intent.json"))
                journal["nextHash"] = sha(candidate)
                box.put("intent.json", encode(journal))
                self.assert_rejected_stable(box, "operation-conflict")
                self.assertEqual(box.read("settings.json"), OLD)

    def test_05_missing_and_corrupt_candidates_preserve_all_evidence(self):
        for data in (None, b"", b"not-json", NEW + b"x", OLD):
            with self.subTest(data=data), lab.Sandbox() as box:
                box.run("write", "C4")
                if data is None:
                    (box.root / "candidate.json").unlink()
                else:
                    box.put("candidate.json", data)
                self.assert_rejected_stable(box, "invalid-material")

    def test_06_journal_identity_types_and_duplicate_keys_fail_closed(self):
        changes = [
            {"schema": True}, {"schema": 1.0}, {"nextRevision": 8.0},
            {"nextRevision": True}, {"nextRevision": -1}, {"operationId": []},
            {"operationId": "../outside"}, {"resource": "other-resource"},
            {"baseHash": "a" * 63}, {"nextHash": "A" * 64},
            {"candidatePath": "../outside"},
        ]
        for change in changes:
            with self.subTest(change=change), lab.Sandbox() as box:
                box.run("write", "C4")
                journal = json.loads(box.read("intent.json"))
                journal.update(change)
                box.put("intent.json", encode(journal))
                self.assert_rejected_stable(box, "invalid-journal")
        with lab.Sandbox() as box:
            box.run("write", "C4")
            raw = box.read("intent.json").strip()
            box.put("intent.json", raw[:-1] + b',"operationId":"op-r7-r8"}')
            self.assert_rejected_stable(box, "invalid-journal")

    def test_07_receipt_schema_types_rejected_with_and_without_journal(self):
        changes = [
            {"schema": True}, {"schema": 1.0}, {"revision": 8.0},
            {"revision": True}, {"revision": "8"}, {"revision": -1},
            {"operationId": None}, {"operationId": ""}, {"operationId": "x/y"},
            {"resource": "other-resource"}, {"nextHash": "A" * 64}, {"extra": 1},
        ]
        for cut in ("C6", "C7"):
            for change in changes:
                with self.subTest(cut=cut, change=change), lab.Sandbox() as box:
                    box.run("write", cut)
                    value = receipt()
                    value.update(change)
                    box.put("receipt.json", encode(value))
                    self.assert_rejected_stable(box, "invalid-receipt")
            for data in (b'{"schema":', b"\xff", encode(receipt()).strip()[:-1] + b',"schema":1}'):
                with self.subTest(cut=cut, raw=data), lab.Sandbox() as box:
                    box.run("write", cut)
                    box.put("receipt.json", data)
                    self.assert_rejected_stable(box, "invalid-receipt")

    def test_08_other_operation_receipt_cannot_authorize_live_journal(self):
        for cut in ("C4", "C5", "C6"):
            with self.subTest(cut=cut), lab.Sandbox() as box:
                box.run("write", cut)
                value = receipt()
                value["operationId"] = "other-operation"
                box.put("receipt.json", encode(value))
                self.assert_rejected_stable(box, "receipt-conflict")

    def test_09_three_consecutive_recovery_interruptions_preserve_installed_identity(self):
        with lab.Sandbox() as box:
            box.run("write", "C4")
            box.run("recover", "R_RENAME")
            target = snapshot(box)["settings.json"]
            box.run("recover", "R_RECEIPT")
            receipt_identity = snapshot(box)["receipt.json"]
            box.run("recover", "R_COMMIT")
            for _ in range(4):
                result = box.run("recover")["result"]
                self.assertEqual(result, {"status": "committed", "action": "already-committed",
                                        "target_replacements": 0, "receipt_writes": 0})
                self.assertEqual(snapshot(box)["settings.json"], target)
                self.assertEqual(snapshot(box)["receipt.json"], receipt_identity)

    def test_10_missing_receipt_and_journal_do_not_fabricate_a_commit(self):
        with lab.Sandbox() as box:
            box.run("write", "C7")
            (box.root / "receipt.json").unlink()
            before = snapshot(box)
            result = box.run("recover")["result"]
            self.assertEqual(result["status"], "idle")
            self.assertEqual(snapshot(box), before)

    def test_11_rename_refusal_has_no_in_place_fallback(self):
        with lab.Sandbox() as box:
            old_identity = snapshot(box)["settings.json"]
            result = box.run("write", deny_rename=True)["result"]
            self.assertEqual(result["action"], "rename-refused")
            self.assertEqual(snapshot(box)["settings.json"], old_identity)
            self.assertEqual(box.read("candidate.json"), NEW)
            self.assertFalse((box.root / "receipt.json").exists())

    def test_12_foreign_sentinel_child_and_temp_directory_survive_cleanup(self):
        # The sentinel is also ours. We never enumerate system processes or use a PID.
        with tempfile.TemporaryDirectory(prefix="independent-audit-sentinel-") as temp:
            marker = Path(temp) / "sentinel.txt"
            marker.write_bytes(b"owned independent sentinel")
            child = subprocess.Popen([sys.executable, "-B", "-c", "import time; time.sleep(60)"],
                                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
            observed = []
            original_popen = subprocess.Popen
            def capture(*args, **kwargs):
                process = original_popen(*args, **kwargs)
                observed.append(process)
                return process
            try:
                with mock.patch.object(lab.subprocess, "Popen", side_effect=capture):
                    with lab.Sandbox() as box:
                        owned_root = box.root
                        box.run("write", "C0")
                    self.assertFalse(owned_root.exists())
                self.assertEqual(len(observed), 1)
                for process in observed:
                    self.assertIsNotNone(process.poll())
                    self.assertTrue(process.stdin.closed)
                    self.assertTrue(process.stdout.closed)
                    self.assertTrue(process.stderr.closed)
                self.assertIsNone(child.poll())
                self.assertEqual(marker.read_bytes(), b"owned independent sentinel")
            finally:
                if child.poll() is None:
                    child.terminate()
                    try:
                        child.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        child.kill()
                        child.wait(timeout=5)

    def test_13_fixed_paths_and_symlink_guard_do_not_mutate_external_fixture(self):
        with tempfile.TemporaryDirectory(prefix="independent-audit-link-") as temp:
            unrelated = Path(temp) / "owned-sentinel.txt"
            unrelated.write_bytes(b"do not mutate")
            with lab.Sandbox() as box:
                with self.assertRaises(ValueError):
                    box.put("../owned-sentinel.txt", b"x")
                (box.root / "candidate.json").symlink_to(unrelated)
                with self.assertRaisesRegex(RuntimeError, "symlinks are outside this experiment"):
                    box.run("write")
                self.assertEqual(box.read("settings.json"), OLD)
            self.assertEqual(unrelated.read_bytes(), b"do not mutate")

    def test_14_duplicate_candidate_keys_cannot_be_hidden_by_rebinding_request_hash(self):
        with lab.Sandbox() as box:
            box.run("write", "C4")
            data = b'{"revision":8,"revision":8,"label":"new"}\n'
            journal = json.loads(box.read("intent.json"))
            journal["nextHash"] = sha(data)
            box.put("intent.json", encode(journal))
            box.put("candidate.json", data)
            self.assert_rejected_stable(box, "operation-conflict")

    def test_15_no_journal_receipt_must_describe_the_exact_request(self):
        for value in (
            {**receipt(), "operationId": "other-operation"},
            {**receipt(), "nextHash": sha(OLD), "revision": 7},
            {**receipt(), "nextHash": sha(R9), "revision": 9},
        ):
            with self.subTest(receipt=value), lab.Sandbox() as box:
                if value["revision"] == 8:
                    box.run("write", "C7")
                elif value["revision"] == 9:
                    box.put("settings.json", R9)
                box.put("receipt.json", encode(value))
                self.assert_rejected_stable(box, "operation-conflict")

    def test_16_target_and_candidate_are_byte_identity_not_revision_only(self):
        cases = (("C4", "settings.json", b'{"revision":7,"label":"old"}'),
                 ("C4", "candidate.json", b'{"revision":8,"label":"new"}'),
                 ("C5", "settings.json", b'{"revision":8,"label":"new"}'))
        for cut, name, data in cases:
            with self.subTest(cut=cut, name=name), lab.Sandbox() as box:
                box.run("write", cut)
                box.put(name, data)
                self.assert_rejected_stable(box, "invalid-material" if name == "candidate.json" else "base-conflict")

    def test_17_writer_refusals_do_not_touch_preexisting_evidence(self):
        for condition in ("newer-target", "intent-exists", "receipt-exists"):
            with self.subTest(condition=condition), lab.Sandbox() as box:
                box.put("candidate.json", b"owned orphan evidence")
                if condition == "newer-target":
                    box.put("settings.json", R9)
                elif condition == "intent-exists":
                    box.put("intent.json", b"owned old journal evidence")
                else:
                    box.put("receipt.json", b"owned receipt evidence")
                before = snapshot(box)
                result = box.run("write")["result"]
                self.assertEqual(result["status"], "rejected")
                self.assertEqual(result["action"], "base-conflict" if condition == "newer-target" else "existing-operation")
                self.assertEqual(snapshot(box), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
