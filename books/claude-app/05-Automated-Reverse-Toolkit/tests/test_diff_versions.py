"""Original generated fixtures only; no products, network or target execution."""
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
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SPEC = importlib.util.spec_from_file_location("diff_versions", ROOT / "diff-versions.py")
frontend = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(frontend)
from toolkit.safeio import Limits, ToolkitError


class VersionDiffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="version diff synthetic ")
        self.base = Path(self.temp.name)
        self.old = self.base / "old directory"
        self.new = self.base / "new directory"
        self.out = self.base / "new private run"
        self.sentinel = self.base / "TARGET_EXECUTED"
        for root, value in ((self.old, "#123456"), (self.new, "#654321")):
            (root / "assets").mkdir(parents=True)
            (root / "empty").mkdir()
            (root / "assets/theme.css").write_text(":root { --synthetic-tone: " + value + "; }", encoding="utf-8")
            (root / "flags.json").write_text(json.dumps({"feature_flags": {"synthetic_switch": value == "#654321"}}), encoding="utf-8")
            (root / "bundle.js").write_text('track("synthetic_' + value[1:] + '");', encoding="utf-8")
            (root / "do-not-run.py").write_text("from pathlib import Path\nPath(" + repr(str(self.sentinel)) + ").touch()\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def archive(self, source, name, compression=zipfile.ZIP_DEFLATED):
        path = self.base / name
        with zipfile.ZipFile(path, "w", compression=compression) as archive:
            for entry in sorted(source.rglob("*")):
                logical = entry.relative_to(source).as_posix()
                archive.writestr(logical + "/" if entry.is_dir() else logical,
                                 b"" if entry.is_dir() else entry.read_bytes())
        return path

    def run_cli(self, old=None, new=None, output=None, *extra):
        return subprocess.run(
            [sys.executable, "-B", str(ROOT / "diff-versions.py"), str(old or self.old),
             str(new or self.new), "--output", str(output or self.out),
             "--old-label", "synthetic-old", "--new-label", "synthetic-new", *extra],
            cwd=self.base, text=True, capture_output=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=20,
        )

    def assert_clean(self):
        self.assertFalse(self.out.exists())
        self.assertFalse(self.out.is_symlink())
        self.assertFalse(list(self.base.glob(".diff-versions-*")))
        self.assertFalse(list(self.base.glob(".reverse-toolkit-*")))
        self.assertFalse(self.sentinel.exists())

    def test_directories_end_to_end_match_existing_compare_exactly(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        response = json.loads(result.stdout)
        self.assertEqual(response["markdown_report"], str(self.out / "report/diff.md"))
        legacy = self.base / "existing compare"
        control = subprocess.run(
            [sys.executable, "-B", str(ROOT / "reverse_toolkit.py"), "compare", "--old", str(self.old),
             "--new", str(self.new), "--old-label", "synthetic-old", "--new-label", "synthetic-new",
             "--output", str(legacy)], cwd=self.base, text=True, capture_output=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=20,
        )
        self.assertEqual(control.returncode, 0, control.stderr)
        for name in ("before.json", "after.json", "diff.json", "diff.md"):
            self.assertEqual((self.out / "report" / name).read_bytes(), (legacy / name).read_bytes())
        self.assertFalse(list((self.out / "inputs").iterdir()))
        run = json.loads((self.out / "run.json").read_text())
        self.assertEqual(run["limits"], Limits().dictionary())
        self.assertEqual(run["inputs"]["old"], {"adapter": "unpacked-directory-v1", "copied": False})
        self.assertNotIn(str(self.base), (self.out / "run.json").read_text())
        self.assertFalse(self.sentinel.exists())

    def test_archives_and_mixed_inputs_are_byte_equivalent_to_directories(self):
        baseline = self.run_cli()
        self.assertEqual(baseline.returncode, 0, baseline.stderr)
        expected = {name: (self.out / "report" / name).read_bytes()
                    for name in ("before.json", "after.json", "diff.json", "diff.md")}
        for compression in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            oldzip = self.archive(self.old, f"old {compression}.zip", compression)
            newzip = self.archive(self.new, f"new {compression}.zip", compression)
            for index, (old, new) in enumerate(((oldzip, newzip), (self.old, newzip), (oldzip, self.new))):
                with self.subTest(compression=compression, combination=index):
                    output = self.base / f"comparison {compression} {index}"
                    result = self.run_cli(old, new, output)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    for name, data in expected.items():
                        self.assertEqual((output / "report" / name).read_bytes(), data)
                    run = json.loads((output / "run.json").read_text())
                    for side, source in (("old", old), ("new", new)):
                        extracted = output / "inputs" / side
                        self.assertEqual(extracted.exists(), source.is_file())
                        if source.is_file():
                            self.assertEqual(run["inputs"][side]["private_root"], f"inputs/{side}")
                            self.assertRegex(run["inputs"][side]["archive_sha256"], r"^[0-9a-f]{64}$")
                            original = self.old if side == "old" else self.new
                            self.assertEqual((extracted / "assets/theme.css").read_bytes(), (original / "assets/theme.css").read_bytes())
        self.assertFalse(self.sentinel.exists())

    def test_extension_is_not_format_validation(self):
        archive = self.archive(self.old, "actual zip without extension")
        result = self.run_cli(archive)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_custom_rules_use_existing_bounded_rule_loader(self):
        rules = frontend.load_rules()
        rules["telemetry_calls"] = ["customSyntheticEvent"]
        path = self.base / "rules.json"
        path.write_text(json.dumps(rules))
        result = self.run_cli(None, None, None, "--rules", str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        before = json.loads((self.out / "report/before.json").read_text())
        self.assertEqual(before["policy"]["rules"], rules)

    @unittest.skipUnless(os.name == "posix", "POSIX permission bits only")
    def test_all_private_boundaries_and_report_files(self):
        archive = self.archive(self.old, "old.zip")
        old_umask = os.umask(0)
        try:
            frontend.compare_versions(archive, self.new, self.out)
        finally:
            os.umask(old_umask)
        for directory in (self.out, self.out / "inputs", self.out / "inputs/old", self.out / "report"):
            self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o700)
        for path in (self.out / "run.json", *(self.out / "report").iterdir()):
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        for path in (self.out / "inputs/old").rglob("*"):
            if path.is_file():
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_repeat_run_does_not_overwrite(self):
        first = self.run_cli()
        self.assertEqual(first.returncode, 0, first.stderr)
        before = {p.relative_to(self.out): p.read_bytes() for p in self.out.rglob("*") if p.is_file()}
        second = self.run_cli()
        self.assertEqual(second.returncode, 2)
        self.assertIn("must not exist", second.stderr)
        self.assertEqual(before, {p.relative_to(self.out): p.read_bytes() for p in self.out.rglob("*") if p.is_file()})
        self.assertFalse(list(self.base.glob(".diff-versions-*")))

    def test_output_inside_either_input_is_rejected(self):
        for source in (self.old, self.new):
            with self.subTest(source=source):
                result = self.run_cli(output=source / "output")
                self.assertEqual(result.returncode, 2)
                self.assertIn("outside", result.stderr)
                self.assertFalse((source / "output").exists())
                self.assertFalse(list(source.glob(".diff-versions-*")))

    def test_output_parent_must_exist(self):
        result = self.run_cli(output=self.base / "absent/output")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.base / "absent").exists())

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlinked_input_roots_rejected(self):
        for source in (self.old, self.archive(self.old, "old.zip")):
            with self.subTest(source=source):
                link = self.base / (source.name + " link")
                link.symlink_to(source, target_is_directory=source.is_dir())
                result = self.run_cli(old=link)
                self.assertEqual(result.returncode, 2)
                self.assert_clean()

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_output_link_and_parent_alias_into_input_rejected(self):
        self.out.symlink_to(self.base / "not present")
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertTrue(self.out.is_symlink())
        self.assertFalse((self.base / "not present").exists())
        self.out.unlink()
        alias = self.base / "alias"
        alias.symlink_to(self.old, target_is_directory=True)
        result = self.run_cli(output=alias / "report")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.old / "report").exists())
        self.assert_clean()

    def test_unsupported_packaging_and_invalid_zip_fail_with_manual_guidance(self):
        for extension in ("asar", "dmg", "deb", "rpm", "7z", "tar", "exe", "zip"):
            with self.subTest(extension=extension):
                path = self.base / ("unsupported." + extension)
                path.write_bytes(b"synthetic non-ZIP bytes")
                result = self.run_cli(old=path)
                self.assertEqual(result.returncode, 2)
                self.assertIn("extract manually with a trusted tool", result.stderr)
                self.assert_clean()

    def test_bad_second_archive_cleans_successful_first_extraction(self):
        oldzip = self.archive(self.old, "old.zip")
        bad = self.base / "bad.zip"
        bad.write_bytes(b"not a ZIP")
        extracted = []
        original = frontend.extract_zip
        def observe(*args):
            result = original(*args)
            extracted.append(args[1])
            self.assertTrue((args[1] / "assets/theme.css").is_file())
            return result
        with mock.patch.object(frontend, "extract_zip", side_effect=observe):
            with self.assertRaises(ToolkitError):
                frontend.compare_versions(oldzip, bad, self.out)
        self.assertEqual(len(extracted), 1)
        self.assertFalse(extracted[0].exists())
        self.assert_clean()

    def test_crc_failure_removes_partial_extraction_and_run(self):
        archive = self.archive(self.old, "bad-crc.zip", zipfile.ZIP_STORED)
        data = archive.read_bytes()
        self.assertIn(b"#123456", data)
        archive.write_bytes(data.replace(b"#123456", b"#999999", 1))
        result = self.run_cli(new=archive)
        self.assertEqual(result.returncode, 2)
        self.assertIn("CRC", result.stderr)
        self.assert_clean()

    def test_traversal_and_zip_symlink_rejected_by_existing_adapter(self):
        link = zipfile.ZipInfo("link")
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        for name in ("../escape", link):
            with self.subTest(name=name):
                archive = self.base / "hostile.zip"
                with zipfile.ZipFile(archive, "w") as target:
                    target.writestr(name, b"synthetic")
                result = self.run_cli(new=archive)
                self.assertEqual(result.returncode, 2)
                self.assertFalse((self.base / "escape").exists())
                self.assert_clean()

    def test_default_compression_ratio_limit_is_not_bypassed(self):
        archive = self.base / "too-compressed.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as target:
            target.writestr("padding", b"x" * (1024 * 1024))
        result = self.run_cli(old=archive)
        self.assertEqual(result.returncode, 2)
        self.assertIn("compression-ratio", result.stderr)
        self.assert_clean()

    def test_limit_bypass_option_not_exposed(self):
        result = self.run_cli(None, None, None, "--max-file-mib", "9999")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unrecognized arguments", result.stderr)
        self.assert_clean()

    def test_snapshot_failure_cleans_extracted_inputs(self):
        archive = self.archive(self.old, "old.zip")
        with mock.patch.object(frontend, "snapshot", side_effect=ToolkitError("synthetic bound")):
            with self.assertRaisesRegex(ToolkitError, "synthetic bound"):
                frontend.compare_versions(archive, self.new, self.out)
        self.assert_clean()

    def test_report_write_failure_and_interrupt_clean_entire_run(self):
        archive = self.archive(self.old, "old.zip")
        for error in (OSError("synthetic disk error"), KeyboardInterrupt()):
            with self.subTest(error=type(error).__name__):
                with mock.patch.object(frontend, "write_report", side_effect=error):
                    with self.assertRaises(type(error)):
                        frontend.compare_versions(archive, self.new, self.out)
                self.assert_clean()

    def test_run_metadata_failure_cleans_finished_report(self):
        with mock.patch.object(frontend, "emit", side_effect=OSError("synthetic metadata failure")):
            with self.assertRaises(OSError):
                frontend.compare_versions(self.old, self.new, self.out)
        self.assert_clean()

    def test_output_appearing_during_run_is_preserved_on_rollback(self):
        original = frontend.emit
        def appear(*args):
            original(*args)
            self.out.mkdir()
            (self.out / "do-not-delete").write_text("synthetic unrelated content")
        with mock.patch.object(frontend, "emit", side_effect=appear):
            with self.assertRaisesRegex(ToolkitError, "appeared"):
                frontend.compare_versions(self.old, self.new, self.out)
        self.assertEqual((self.out / "do-not-delete").read_text(), "synthetic unrelated content")
        self.assertFalse(list(self.base.glob(".diff-versions-*")))

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_output_symlink_appearing_during_run_is_not_followed_or_removed(self):
        target = self.base / "unrelated directory"
        target.mkdir()
        sentinel = target / "do-not-delete"
        sentinel.write_text("synthetic unrelated content")
        original = frontend.emit
        def appear(*args):
            original(*args)
            self.out.symlink_to(target, target_is_directory=True)
        with mock.patch.object(frontend, "emit", side_effect=appear):
            with self.assertRaisesRegex(ToolkitError, "appeared"):
                frontend.compare_versions(self.old, self.new, self.out)
        self.assertTrue(self.out.is_symlink())
        self.assertEqual(sentinel.read_text(), "synthetic unrelated content")
        self.assertFalse(list(self.base.glob(".diff-versions-*")))

    def test_final_rename_failure_removes_staging(self):
        with mock.patch.object(frontend, "atomic_publish", side_effect=OSError("synthetic publish failure")):
            with self.assertRaisesRegex(OSError, "synthetic publish failure"):
                frontend.compare_versions(self.old, self.new, self.out)
        self.assert_clean()

    def test_empty_destination_appearing_at_publish_is_not_replaced(self):
        original = frontend.atomic_publish
        created_inode = []
        def appear(stage, destination):
            self.out.mkdir()
            created_inode.append(self.out.stat().st_ino)
            return original(stage, destination)
        with mock.patch.object(frontend, "atomic_publish", side_effect=appear):
            with self.assertRaisesRegex(ToolkitError, "nothing was replaced"):
                frontend.compare_versions(self.old, self.new, self.out)
        self.assertEqual(self.out.stat().st_ino, created_inode[0])
        self.assertEqual(list(self.out.iterdir()), [])
        self.assertFalse(list(self.base.glob(".diff-versions-*")))

    def test_directory_coverage_gaps_are_preserved(self):
        (self.old / "broken.json").write_text('{"duplicate":1,"duplicate":2}')
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.out / "report/diff.json").read_text())
        self.assertTrue(any("old scan has coverage gaps" in item for item in report["warnings"]))
        before = json.loads((self.out / "report/before.json").read_text())
        self.assertFalse(before["coverage"]["complete_within_declared_scope"])

    def test_no_target_or_external_command_is_executed(self):
        archive = self.archive(self.old, "old.zip")
        with mock.patch("subprocess.Popen", side_effect=AssertionError("must not launch a command")), \
             mock.patch("os.system", side_effect=AssertionError("must not invoke a shell")):
            frontend.compare_versions(archive, self.new, self.out)
        self.assertFalse(self.sentinel.exists())


if __name__ == "__main__":
    unittest.main()
