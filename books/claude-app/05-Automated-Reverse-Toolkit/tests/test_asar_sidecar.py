"""Original synthetic sidecar fixtures. Never inspect native target materials."""
from dataclasses import replace
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from toolkit import asar, asar_sidecar
from toolkit.safeio import Limits, ToolkitError
from test_asar import archive_bytes, integrity


class SidecarTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.archive = self.base / "input.asar"
        self.companion = self.base / "explicit companion"
        self.companion.mkdir()
        self.output = self.base / "output"

    def tearDown(self):
        self.temp.cleanup()

    def fixture(self, data=b"abc", declared=True, inherited=False, packed=b"packed"):
        node = {"size": len(data)}
        if declared:
            node["integrity"] = integrity(data)
        if inherited:
            files = {"native": {"unpacked": True, "files": {"data.bin": node, "empty": {"files": {}}}}}
        else:
            node["unpacked"] = True
            files = {"native": {"files": {"data.bin": node}}}
        files["packed.txt"] = {"size": len(packed), "offset": "0", "integrity": integrity(packed)}
        self.archive.write_bytes(archive_bytes({"files": files}, packed))
        (self.companion / "native").mkdir()
        target = self.companion / "native/data.bin"
        target.write_bytes(data)
        if inherited:
            (self.companion / "native/empty").mkdir()
        return target

    def extract(self, **kwargs):
        return asar.extract_asar(self.archive, self.output, unpacked_dir=self.companion, **kwargs)

    def assert_rolled_back(self):
        self.assertFalse(self.output.exists())
        self.assertFalse(list(self.base.glob(".reverse-toolkit-asar-*")))
        self.assertFalse(list(self.base.glob(".diff-versions-*")))

    def rejects(self, pattern=None, **kwargs):
        with self.assertRaisesRegex(ToolkitError, pattern or "ASAR") as caught:
            self.extract(**kwargs)
        self.assert_rolled_back()
        return caught.exception

    def test_mixed_members_exact_metadata_and_permissions(self):
        self.fixture(inherited=True)
        result = self.extract()
        self.assertEqual((self.output / "native/data.bin").read_bytes(), b"abc")
        self.assertEqual((self.output / "packed.txt").read_bytes(), b"packed")
        self.assertTrue((self.output / "native/empty").is_dir())
        self.assertEqual(result["expanded_bytes"], 9)
        self.assertEqual(result["files_with_declared_integrity"], 2)
        self.assertTrue(result["declared_member_integrity_verified"])
        self.assertFalse(result["complete_application"])
        self.assertFalse(result["publisher_authenticity_verified"])
        self.assertEqual(result["exclusions"], [])
        self.assertNotEqual(result["container_exclusions"], [])
        side = result["sidecar"]
        self.assertEqual(side["files"], 1)
        self.assertEqual(side["bytes"], 3)
        self.assertEqual(side["members"], [{"path": "native/data.bin", "size": 3,
            "sha256": hashlib.sha256(b"abc").hexdigest(), "declared_integrity": True}])
        self.assertEqual([side[k] for k in ("missing", "extra", "invalid")], [[], [], []])
        self.assertTrue(side["complete_asar_declared_scope"])
        self.assertNotIn(str(self.companion), json.dumps(result))
        self.assertEqual(stat.S_IMODE((self.output / "native/data.bin").stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE((self.output / "native").stat().st_mode), 0o700)

    def test_metadata_deterministic_without_absolute_paths_or_file_identity(self):
        self.fixture()
        first = self.extract()
        self.output = self.base / "second output"
        second = self.extract()
        self.assertEqual(first, second)

    def test_no_integrity_is_explicit_and_hash_still_recorded(self):
        self.fixture(declared=False)
        result = self.extract()["sidecar"]
        self.assertEqual(result["files_with_declared_integrity"], 0)
        self.assertFalse(result["members"][0]["declared_integrity"])
        self.assertEqual(result["members"][0]["sha256"], hashlib.sha256(b"abc").hexdigest())

    def test_zero_and_multichunk_files(self):
        for index, data in enumerate((b"", b"a", b"z"*(asar.CHUNK*2+7))):
            with self.subTest(size=len(data)):
                self.companion = self.base / str(index)
                self.companion.mkdir()
                self.output = self.base / ("out" + str(index))
                self.fixture(data)
                self.extract()
                self.assertEqual((self.output / "native/data.bin").read_bytes(), data)

    def test_default_rejects_without_opening_any_companion(self):
        self.fixture()
        guessed = self.base / "input.asar.unpacked"
        guessed.symlink_to(self.companion, target_is_directory=True)
        with mock.patch.object(asar, "Sidecar", side_effect=AssertionError("companion touched")):
            with self.assertRaisesRegex(ToolkitError, "sidecar"):
                asar.extract_asar(self.archive, self.output)
            metadata = asar.inspect_asar(self.archive)
        self.assertFalse(metadata["extractable_within_subset"])
        self.assert_rolled_back()

    def test_inspect_rejects_companion_option_instead_of_silently_reading(self):
        self.fixture()
        result = self.cli("inspect-asar", "--input", self.archive, "--unpacked-dir", self.companion)
        self.assertEqual(result.returncode, 2)
        self.assertIn("unrecognized arguments", result.stderr)

    def test_missing_and_extra_reported_together_before_stage(self):
        self.fixture().unlink()
        (self.companion / "wrong.bin").write_bytes(b"extra")
        with mock.patch.object(asar.tempfile, "mkdtemp", side_effect=AssertionError("stage created")):
            exc = self.rejects("coverage-mismatch")
        self.assertEqual(exc.coverage["missing"], ["native/data.bin"])
        self.assertEqual(exc.coverage["extra"], ["wrong.bin"])
        self.assertFalse(exc.coverage["complete_asar_declared_scope"])

    def test_extra_empty_directory_is_not_ignored(self):
        self.fixture()
        (self.companion / "unrelated").mkdir()
        exc = self.rejects("coverage-mismatch")
        self.assertEqual(exc.coverage["extra"], ["unrelated"])

    def test_missing_declared_empty_directory_rejects(self):
        self.fixture(inherited=True)
        (self.companion / "native/empty").rmdir()
        exc = self.rejects("coverage-mismatch")
        self.assertEqual(exc.coverage["missing"], ["native/empty"])

    def test_companion_cannot_override_packed_member(self):
        self.fixture()
        (self.companion / "packed.txt").write_bytes(b"replacement")
        exc = self.rejects("coverage-mismatch")
        self.assertEqual(exc.coverage["extra"], ["packed.txt"])

    def test_declared_size_mismatch_is_fatal_without_payload_read(self):
        self.fixture().write_bytes(b"abcd")
        with mock.patch.object(asar_sidecar.Sidecar, "source", side_effect=AssertionError("payload read")):
            exc = self.rejects("declared-size-mismatch")
        self.assertEqual(exc.coverage["invalid"], [{"path": "native/data.bin", "reason": "declared-size-mismatch"}])

    def test_matching_size_wrong_hash_is_fatal(self):
        self.fixture().write_bytes(b"xyz")
        exc = self.rejects("integrity-failure")
        self.assertEqual(exc.coverage["failure_path"], "native/data.bin")

    def test_whole_block_empty_hash_checks_all_mandatory(self):
        for index, field in enumerate(("hash", "blocks", "empty")):
            with self.subTest(field=field):
                self.companion = self.base / str(index); self.companion.mkdir()
                data = b"" if field == "empty" else b"abc"
                self.fixture(data)
                bad = integrity(data)
                bad["hash" if field == "hash" else "blocks"] = "0"*64 if field == "hash" else ["0"*64]*len(bad["blocks"])
                tree = {"files": {"native": {"files": {"data.bin": {
                    "size": len(data), "unpacked": True, "integrity": bad}}}}}
                self.archive.write_bytes(archive_bytes(tree, b""))
                self.rejects("integrity-failure")

    def test_root_symlink_and_non_directory_rejected(self):
        self.fixture()
        link = self.base / "linked"; link.symlink_to(self.companion, target_is_directory=True)
        original = self.companion
        self.companion = link
        self.rejects("root-not-real-directory")
        self.companion = original / "native/data.bin"
        self.rejects("root-not-real-directory")

    def test_intermediate_symlink_rejected_without_follow(self):
        self.fixture()
        native = self.companion / "native"
        outside = self.base / "outside"
        native.rename(outside)
        native.symlink_to(outside, target_is_directory=True)
        exc = self.rejects("type-or-link-mismatch")
        self.assertEqual(exc.coverage["missing"], ["native/data.bin"])

    def test_final_symlink_and_hardlink_rejected(self):
        target = self.fixture()
        saved = self.base / "saved"; target.rename(saved)
        target.symlink_to(saved)
        self.rejects("type-or-link-mismatch")
        target.unlink(); os.link(saved, target)
        self.rejects("type-or-link-mismatch")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX FIFO required")
    def test_fifo_is_rejected_before_open(self):
        target = self.fixture(); target.unlink(); os.mkfifo(target)
        with mock.patch.object(asar_sidecar.Sidecar, "source", side_effect=AssertionError("FIFO opened")):
            self.rejects("type-or-link-mismatch")

    def test_extra_symlink_is_an_error_not_silently_skipped(self):
        self.fixture()
        (self.companion / "extra-link").symlink_to(self.base / "not-present")
        exc = self.rejects("type-or-link-mismatch")
        self.assertEqual(exc.coverage["extra"], ["extra-link"])

    def test_case_and_unicode_collisions_are_rejected(self):
        self.fixture()
        for first, second in (("A", "a"), ("é", "e\u0301")):
            a, b = self.companion / first, self.companion / second
            a.write_bytes(b""); b.write_bytes(b"")
            self.rejects("case-unicode-collision")
            a.unlink(); b.unlink()

    def test_unsafe_names_rejected(self):
        self.fixture()
        for name in ("NUL", "bad\\name", "bad:name", "bad\nname", "trail."):
            path = self.companion / name; path.write_bytes(b"")
            self.rejects("unsafe-path")
            path.unlink()

    def test_exact_path_binding_does_not_guess_case(self):
        self.fixture().rename(self.companion / "native/Data.bin")
        exc = self.rejects("coverage-mismatch")
        self.assertEqual(exc.coverage["missing"], ["native/data.bin"])
        self.assertEqual(exc.coverage["extra"], ["native/Data.bin"])

    def test_combined_size_budget_includes_packed_and_unpacked(self):
        self.fixture()
        self.rejects("combined-packed-unpacked-byte-bound", limits=replace(Limits(), max_total_bytes=8))

    def test_inventory_count_and_listing_budget(self):
        self.fixture()
        for index in range(4):
            (self.companion / str(index)).write_bytes(b"")
        self.rejects("entry-count-bound", limits=replace(Limits(), max_files=3))
        with mock.patch.object(asar_sidecar, "MAX_LISTING_BYTES", 1):
            self.rejects("listing-byte-bound")

    def test_only_declared_empty_unpacked_directory(self):
        self.archive.write_bytes(archive_bytes({"files": {"empty": {"unpacked": True, "files": {}}}}, b""))
        (self.companion / "empty").mkdir()
        result = self.extract()
        self.assertTrue((self.output / "empty").is_dir())
        self.assertEqual(result["sidecar"]["files"], 0)
        self.assertEqual(result["expanded_bytes"], 0)
        self.assertTrue(result["sidecar"]["complete_asar_declared_scope"])

    def test_depth_budget_for_extra_tree(self):
        self.fixture()
        (self.companion / "extra/deep/leaf").mkdir(parents=True)
        self.rejects("unsafe-path", limits=replace(Limits(), max_depth=2))

    def test_file_directory_type_conflict(self):
        target = self.fixture()
        target.unlink(); target.mkdir()
        exc = self.rejects("type-or-link-mismatch")
        self.assertEqual(exc.coverage["invalid"], [{"path": "native/data.bin", "reason": "type-or-link-mismatch"}])

    def test_extra_contents_are_not_opened(self):
        self.fixture()
        (self.companion / "extra.bin").write_bytes(b"inert extra")
        with mock.patch.object(asar_sidecar.Sidecar, "source", side_effect=AssertionError("read extra")):
            self.rejects("coverage-mismatch")

    def test_partial_stage_write_error_cleans_up(self):
        self.fixture()
        with mock.patch.object(asar, "_copy_entry", side_effect=OSError("synthetic write error")):
            self.rejects("read-failure")

    def test_unavailable_root_has_unknown_coverage_and_no_absolute_path(self):
        self.fixture()
        self.companion = self.base / "absent-root"
        exc = self.rejects("root-io-failure")
        self.assertFalse(exc.coverage["inventory_complete"])
        self.assertIsNone(exc.coverage["missing"])
        self.assertNotIn(str(self.base), str(exc))

    def test_inventory_io_failure_has_stable_unknown_coverage(self):
        self.fixture()
        with mock.patch.object(asar_sidecar.Sidecar, "_scan", side_effect=PermissionError("synthetic permission failure")):
            exc = self.rejects("inventory-io-failure")
        self.assertFalse(exc.coverage["inventory_complete"])
        self.assertIsNone(exc.coverage["extra"])
        self.assertEqual(exc.coverage["failure_path"], ".")

    def test_cli_missing_root_has_structured_error_only(self):
        self.fixture()
        absent = self.base / "absent-root"
        result = self.cli("unpack-asar", "--input", self.archive, "--output", self.output,
                          "--unpacked-dir", absent)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn('"inventory_complete":false', result.stderr)
        self.assertIn('"missing":null', result.stderr)
        self.assertNotIn(str(absent), result.stderr)
        self.assert_rolled_back()

    def test_no_declared_unpacked_means_companion_argument_rejected(self):
        self.archive.write_bytes(archive_bytes())
        self.rejects("unexpected-companion-no-unpacked-declarations")

    def test_asar_links_still_reject_before_companion_read(self):
        self.fixture()
        self.archive.write_bytes(archive_bytes({"files": {"link": {"link": "ignored"}}}, b""))
        with mock.patch.object(asar, "Sidecar", side_effect=AssertionError("opened companion")):
            self.rejects("link exclusions")

    def test_missing_host_primitives_fail_closed(self):
        self.fixture()
        with mock.patch.object(asar_sidecar.os, "supports_fd", set()):
            self.rejects("unsupported-host")

    def test_output_inside_companion_is_rejected(self):
        self.fixture()
        self.output = self.companion / "out"
        self.rejects("output-inside-companion")

    def test_mutation_during_read_is_fatal_without_declared_hash(self):
        target = self.fixture(declared=False)
        original = asar._copy_entry
        def mutate(stream, entry, destination):
            digest = original(stream, entry, destination)
            if entry["unpacked"]:
                target.write_bytes(b"xyz")
            return digest
        with mock.patch.object(asar, "_copy_entry", side_effect=mutate):
            self.rejects("source-changed")

    def test_mutation_of_previous_sidecar_after_read_is_caught_at_close(self):
        target = self.fixture(declared=False)
        original = asar._copy_entry
        def mutate(stream, entry, destination):
            digest = original(stream, entry, destination)
            if not entry["unpacked"]:
                target.write_bytes(b"xyz")
            return digest
        with mock.patch.object(asar, "_copy_entry", side_effect=mutate):
            self.rejects("source-changed")

    def test_added_extra_after_file_read_is_caught_at_close(self):
        self.fixture()
        original = asar._copy_entry
        def mutate(stream, entry, destination):
            digest = original(stream, entry, destination)
            if not entry["unpacked"]:
                (self.companion / "late-extra").write_bytes(b"x")
            return digest
        with mock.patch.object(asar, "_copy_entry", side_effect=mutate):
            exc = self.rejects("root-changed")
            self.assertFalse(exc.coverage["inventory_complete"])
            self.assertIsNone(exc.coverage["extra"])

    def test_replacement_before_file_open_is_rejected(self):
        target = self.fixture(declared=False)
        original = asar_sidecar.Sidecar.source
        def replace_before(sidecar, entry):
            target.unlink(); target.write_bytes(b"abc")
            return original(sidecar, entry)
        with mock.patch.object(asar_sidecar.Sidecar, "source", replace_before):
            self.rejects("source-changed")

    def test_root_replacement_before_publication_is_rejected(self):
        self.fixture()
        original = asar._copy_entry
        def replace_after(stream, entry, destination):
            digest = original(stream, entry, destination)
            if not entry["unpacked"]:
                self.companion.rename(self.base / "moved-root")
                self.companion.mkdir()
            return digest
        with mock.patch.object(asar, "_copy_entry", side_effect=replace_after):
            self.rejects("root-changed")

    def test_publish_failure_rolls_back(self):
        self.fixture()
        with mock.patch.object(asar, "atomic_publish", side_effect=OSError("synthetic publish error")):
            with self.assertRaises(OSError): self.extract()
        self.assert_rolled_back()

    def test_existing_output_untouched(self):
        self.fixture()
        self.output.mkdir()
        with self.assertRaisesRegex(ToolkitError, "must not exist"):
            self.extract()
        self.assertTrue(self.output.is_dir())
        self.assertEqual(list(self.output.iterdir()), [])

    def test_target_script_bytes_never_execute(self):
        marker = self.base / "executed"
        data = ('require("fs").writeFileSync('+json.dumps(str(marker))+',"bad");').encode()
        self.fixture(data)
        self.extract()
        self.assertFalse(marker.exists())

    def cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(ROOT / "reverse_toolkit.py"),
            *map(str, args)], cwd=self.base, text=True, capture_output=True)

    def diff_cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(ROOT / "diff-versions.py"),
            *map(str, args)], cwd=self.base, text=True, capture_output=True)

    def test_unpack_cli_success(self):
        self.fixture()
        result = self.cli("unpack-asar", "--input", self.archive, "--output", self.output,
                          "--unpacked-dir", self.companion)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["sidecar"]["files"], 1)

    def test_cli_failure_has_no_success_json_or_output(self):
        self.fixture().unlink()
        result = self.cli("unpack-asar", "--input", self.archive, "--output", self.output,
                          "--unpacked-dir", self.companion)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn('"missing":["native/data.bin"]', result.stderr)
        self.assert_rolled_back()

    def test_two_versions_combined_complete_declared_scope(self):
        self.fixture()
        other = self.base / "new.ASAR"; other.write_bytes(self.archive.read_bytes())
        result = self.diff_cli(self.archive, other, "--old-unpacked-dir", self.companion,
            "--new-unpacked-dir", self.companion, "--output", self.output)
        self.assertEqual(result.returncode, 0, result.stderr)
        run = json.loads((self.output / "run.json").read_text())
        for side in ("old", "new"):
            self.assertTrue(run["inputs"][side]["sidecar"]["complete_asar_declared_scope"])
            self.assertEqual((self.output / "inputs" / side / "native/data.bin").read_bytes(), b"abc")
        report = json.loads((self.output / "report/diff.json").read_text())
        self.assertEqual(report["files"]["removed"], [])

    def test_two_versions_missing_sidecar_rejects_entire_run(self):
        self.fixture()
        other = self.base / "new.asar"; other.write_bytes(self.archive.read_bytes())
        result = self.diff_cli(self.archive, other, "--old-unpacked-dir", self.companion,
                              "--output", self.output)
        self.assertEqual(result.returncode, 2)
        self.assertIn("new input rejected", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assert_rolled_back()

    def test_two_versions_extra_companion_content_produces_no_removed_report(self):
        self.fixture()
        other = self.base / "new.asar"; other.write_bytes(self.archive.read_bytes())
        wrong = self.base / "wrong companion"; wrong.mkdir()
        (wrong / "extra.txt").write_bytes(b"not a product removal")
        result = self.diff_cli(self.archive, other, "--old-unpacked-dir", self.companion,
            "--new-unpacked-dir", wrong, "--output", self.output)
        self.assertEqual(result.returncode, 2)
        self.assertIn('"extra":["extra.txt"]', result.stderr)
        self.assertIn("missing/extra/invalid paths", result.stderr)
        self.assertNotIn("extract manually", result.stderr)
        self.assert_rolled_back()

    def test_integrity_failure_cli_never_suggests_manual_extraction_bypass(self):
        target = self.fixture()
        target.write_bytes(b"xyz")
        for kind in ("sidecar", "packed"):
            with self.subTest(kind=kind):
                flags = ["--old-unpacked-dir", self.companion, "--new-unpacked-dir", self.companion]
                if kind == "packed":
                    self.archive.write_bytes(archive_bytes({"files": {"packed.bin": {
                        "size": 3, "offset": "0", "integrity": integrity(b"abc")}}}, b"xyz"))
                    flags = []
                result = self.diff_cli(self.archive, self.archive, *flags, "--output", self.output)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("trusted source", result.stderr)
                self.assertIn("Never bypass integrity checks", result.stderr)
                self.assertNotIn("extract manually", result.stderr)
                self.assertNotIn("trusted tool", result.stderr)
                self.assert_rolled_back()

    def test_two_versions_companion_argument_for_directory_is_error(self):
        self.fixture()
        result = self.diff_cli(self.companion, self.companion, "--old-unpacked-dir", self.companion,
                              "--output", self.output)
        self.assertEqual(result.returncode, 2)
        self.assertIn("requires an ASAR input", result.stderr)
        self.assert_rolled_back()


if __name__ == "__main__":
    unittest.main()
