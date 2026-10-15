"""Independent black-box assertions against child-process files and results.

Expected bytes, hashes, revisions and actions below do not call protocol's
writer/recovery functions, validators, serializers or decision helpers.
"""
import hashlib
import json
import unittest

from lab import Sandbox


OLD = b'{"label":"old","revision":7}\n'
NEW = b'{"label":"new","revision":8}\n'
R9 = b'{"label":"third-party","revision":9}\n'


def dump(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


class CrashCuts(unittest.TestCase):
    def assert_committed(self, box):
        self.assertEqual(box.read("settings.json"), NEW)
        self.assertFalse((box.root / "intent.json").exists())
        receipt = json.loads(box.read("receipt.json"))
        self.assertEqual(receipt, {"schema": 1, "resource": "synthetic-settings",
                         "operationId": "op-r7-r8", "revision": 8,
                         "nextHash": hashlib.sha256(NEW).hexdigest()})

    def assert_stable_recovery(self, box, action):
        before = box.snapshot()
        result = box.run("recover")["result"]
        self.assertEqual(result["action"], action)
        self.assertEqual(result["target_replacements"], 0)
        self.assertEqual(result["receipt_writes"], 0)
        # Includes bytes' hashes, lengths, inode, mtime and decoded content.
        self.assertEqual(box.snapshot(), before)

    def test_eight_cuts_and_repeated_recovery(self):
        expected = {
            "C0": (7, {"settings.json"}, "no-intent", 0, 0),
            "C1": (7, {"settings.json", "candidate.json"}, "no-intent", 0, 0),
            "C2": (7, {"settings.json", "candidate.json"}, "no-intent", 0, 0),
            "C3": (7, {"settings.json", "candidate.json", "intent.json"}, "invalid-journal", 0, 0),
            "C4": (7, {"settings.json", "candidate.json", "intent.json"}, "installed-candidate", 1, 1),
            "C5": (8, {"settings.json", "intent.json"}, "finalized-installed", 0, 1),
            "C6": (8, {"settings.json", "intent.json", "receipt.json"}, "finalized-installed", 0, 0),
            "C7": (8, {"settings.json", "receipt.json"}, "already-committed", 0, 0),
        }
        for cut, (revision, names, action, replaces, receipts) in expected.items():
            with self.subTest(cut=cut), Sandbox() as box:
                stopped = box.run("write", cut)
                self.assertNotEqual(stopped["exit_code"], 0)
                self.assertEqual(stopped["checkpoint"], cut)
                self.assertEqual(stopped["state"]["target"]["revision"], revision)
                self.assertEqual(set(stopped["state"]["files"]), names)
                self.assertEqual(box.read("settings.json"), OLD if revision == 7 else NEW)
                if cut == "C1":
                    self.assertEqual(box.read("candidate.json"), NEW[:len(NEW) // 2])
                if cut == "C2":
                    self.assertEqual(box.read("candidate.json"), NEW)
                if cut == "C3":
                    with self.assertRaises(ValueError):
                        json.loads(box.read("intent.json"))
                before = box.snapshot()
                recovered = box.run("recover")["result"]
                self.assertEqual(recovered["action"], action)
                self.assertEqual(recovered["target_replacements"], replaces)
                self.assertEqual(recovered["receipt_writes"], receipts)
                if cut in ("C0", "C1", "C2", "C3"):
                    self.assertNotEqual(recovered["status"], "committed")
                    self.assertEqual(box.snapshot(), before)
                    self.assert_stable_recovery(box, action)
                else:
                    self.assertEqual(recovered["status"], "committed")
                    self.assert_committed(box)
                    self.assert_stable_recovery(box, "already-committed")

    def test_old_journal_cannot_overwrite_r9(self):
        with Sandbox() as box:
            box.run("write", "C4")
            box.put("settings.json", R9)
            self.assert_stable_recovery(box, "base-conflict")
            self.assert_stable_recovery(box, "base-conflict")
            self.assertEqual(box.read("settings.json"), R9)
            self.assertFalse((box.root / "receipt.json").exists())

    def test_corrupt_candidate_cannot_be_installed(self):
        for bad in (b'{"broken":', b'{"label":"tampered","revision":8}\n'):
            with self.subTest(candidate=bad), Sandbox() as box:
                box.run("write", "C4")
                box.put("candidate.json", bad)
                self.assert_stable_recovery(box, "invalid-material")
                self.assertEqual(box.read("settings.json"), OLD)

    def test_missing_candidate_is_rejected(self):
        with Sandbox() as box:
            box.run("write", "C4")
            (box.root / "candidate.json").unlink()
            self.assert_stable_recovery(box, "invalid-material")

    def test_journal_cannot_rebind_this_operation_to_another_payload(self):
        for bad in (b"not-json", b'{"revision":8}', b'{"revision":9,"label":"new"}'):
            with self.subTest(candidate=bad), Sandbox() as box:
                box.run("write", "C4")
                box.put("candidate.json", bad)
                journal = json.loads(box.read("intent.json"))
                journal["nextHash"] = hashlib.sha256(bad).hexdigest()
                box.put("intent.json", dump(journal))
                self.assert_stable_recovery(box, "operation-conflict")

    def test_receipt_must_match_this_operation(self):
        for cut in ("C4", "C5", "C6"):
            with self.subTest(cut=cut), Sandbox() as box:
                box.run("write", cut)
                box.put("receipt.json", dump({"schema": 1, "resource": "synthetic-settings",
                    "operationId": "some-other-operation", "revision": 8,
                    "nextHash": hashlib.sha256(NEW).hexdigest()}))
                self.assert_stable_recovery(box, "receipt-conflict")

    def test_torn_receipt_requires_inspection(self):
        with Sandbox() as box:
            box.run("write", "C5")
            box.put("receipt.json", b'{"operationId":')
            self.assert_stable_recovery(box, "invalid-receipt")

    def test_recovery_knows_the_expected_operation_even_without_journal(self):
        for cut, name in (("C4", "intent.json"), ("C7", "receipt.json")):
            with self.subTest(cut=cut), Sandbox() as box:
                box.run("write", cut)
                record = json.loads(box.read(name))
                record["operationId"] = "another-valid-looking-operation"
                box.put(name, dump(record))
                self.assert_stable_recovery(box, "operation-conflict")

    def test_same_operation_id_with_old_payload_is_not_completion(self):
        with Sandbox() as box:
            box.put("receipt.json", dump({"schema": 1, "resource": "synthetic-settings",
                "operationId": "op-r7-r8", "revision": 7,
                "nextHash": hashlib.sha256(OLD).hexdigest()}))
            self.assert_stable_recovery(box, "operation-conflict")
            self.assertEqual(box.read("settings.json"), OLD)

    def test_receipt_types_cannot_use_python_boolean_integer_equality(self):
        for cut in ("C6", "C7"):
            for change in ({"schema": True}, {"revision": 8.0}):
                with self.subTest(cut=cut, change=change), Sandbox() as box:
                    box.run("write", cut)
                    receipt = json.loads(box.read("receipt.json"))
                    receipt.update(change)
                    box.put("receipt.json", dump(receipt))
                    self.assert_stable_recovery(box, "invalid-receipt")

    def test_bad_journal_schema_and_paths_are_rejected(self):
        for change in ({"schema": 2}, {"schema": True}, {"resource": "../other"},
                       {"nextHash": "no"}, {"candidatePath": "/tmp/unrelated"}):
            with self.subTest(change=change), Sandbox() as box:
                box.run("write", "C4")
                journal = json.loads(box.read("intent.json"))
                journal.update(change)
                box.put("intent.json", dump(journal))
                self.assert_stable_recovery(box, "invalid-journal")

    def test_duplicate_journal_keys_are_rejected(self):
        with Sandbox() as box:
            box.run("write", "C4")
            journal = box.read("intent.json").rstrip()
            box.put("intent.json", journal[:-1] + b',"schema":1}')
            self.assert_stable_recovery(box, "invalid-journal")

    def test_recovery_itself_can_stop_then_restart_twice(self):
        for cut in ("R_RENAME", "R_RECEIPT", "R_COMMIT"):
            with self.subTest(cut=cut), Sandbox() as box:
                box.run("write", "C4")
                box.run("recover", cut)
                target_before = box.snapshot()["files"]["settings.json"]
                self.assertEqual(box.read("settings.json"), NEW)
                resumed = box.run("recover")["result"]
                self.assertEqual(resumed["target_replacements"], 0)
                self.assertEqual(resumed["receipt_writes"], 1 if cut == "R_RENAME" else 0)
                self.assert_committed(box)
                self.assertEqual(box.snapshot()["files"]["settings.json"], target_before)
                self.assert_stable_recovery(box, "already-committed")

    def test_recovery_survives_two_consecutive_interruptions(self):
        with Sandbox() as box:
            box.run("write", "C4")
            box.run("recover", "R_RENAME")
            installed = box.snapshot()["files"]["settings.json"]
            box.run("recover", "R_RECEIPT")
            receipt = box.snapshot()["files"]["receipt.json"]
            result = box.run("recover")["result"]
            self.assertEqual(result["target_replacements"], 0)
            self.assertEqual(result["receipt_writes"], 0)
            self.assertEqual(box.snapshot()["files"]["settings.json"], installed)
            self.assertEqual(box.snapshot()["files"]["receipt.json"], receipt)
            self.assert_committed(box)
            self.assert_stable_recovery(box, "already-committed")

    def test_rename_refusal_preserves_old_target(self):
        with Sandbox() as box:
            result = box.run("write", deny_rename=True)["result"]
            self.assertEqual(result["action"], "rename-refused")
            self.assertEqual(result["status"], "rejected")
            self.assertEqual(box.read("settings.json"), OLD)
            self.assertEqual(box.read("candidate.json"), NEW)
            self.assertTrue((box.root / "intent.json").exists())
            self.assertFalse((box.root / "receipt.json").exists())
            self.assertEqual(box.run("recover")["result"]["action"], "installed-candidate")
            self.assert_committed(box)
            self.assert_stable_recovery(box, "already-committed")

    def test_success_without_interruption(self):
        with Sandbox() as box:
            result = box.run("write")["result"]
            self.assertEqual(result["action"], "writer-committed")
            self.assertEqual(result["status"], "committed")
            self.assert_committed(box)
            self.assert_stable_recovery(box, "already-committed")

    def test_stale_receipt_without_journal_is_not_commit_proof(self):
        with Sandbox() as box:
            box.run("write")
            box.put("settings.json", R9)
            self.assert_stable_recovery(box, "invalid-receipt")

    def test_runner_restricts_filenames_and_checkpoint_enums(self):
        with Sandbox() as box:
            with self.assertRaises(ValueError):
                box.put("../not-a-fixture", b"x")
            with self.assertRaises(ValueError):
                box.run("write", "unknown")
            self.assertEqual(box.read("settings.json"), OLD)
            owned_root = box.root
        self.assertFalse(owned_root.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
