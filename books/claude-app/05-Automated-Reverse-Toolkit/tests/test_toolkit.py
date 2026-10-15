"""Original synthetic fixtures only. Run with Python's standard unittest."""
from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from toolkit.diffing import diff_snapshots, readable
from toolkit.inventory import canonical, snapshot, verify_snapshot
from toolkit.literals import json_candidates, literal_candidates, load_rules
from toolkit.safeio import Limits, ToolkitError, extract_zip


class Temporary(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()


class SnapshotTests(Temporary):
    def test_deterministic_across_absolute_paths(self):
        source = ROOT / "tests/fixtures/v1"
        shutil.copytree(source, self.base / "copy")
        self.assertEqual(snapshot(source, "test"), snapshot(self.base / "copy", "test"))

    def test_mutation_detected(self):
        doc = snapshot(ROOT / "tests/fixtures/v1", "test")
        self.assertIs(verify_snapshot(doc), doc)
        doc["label"] = "forged"
        with self.assertRaises(ToolkitError): verify_snapshot(doc)

    def test_synthetic_diff_values_and_uncertainty(self):
        old = snapshot(ROOT / "tests/fixtures/v1", "v1")
        new = snapshot(ROOT / "tests/fixtures/v2", "v2")
        report = diff_snapshots(old, new)
        css = report["inventories"]["css_tokens"]
        self.assertEqual([x["key"] for x in css["added"]], ["--demo-gap"])
        self.assertEqual([x["key"] for x in css["removed"]], ["--demo-radius"])
        self.assertEqual([x["key"] for x in css["changed"]], ["--demo-gray-100"])
        flags = report["inventories"]["flags"]
        self.assertEqual(flags["added"][0]["key"], "demo_experiment")
        self.assertEqual(flags["added"][0]["interpretation"], "uncertain-candidate")
        self.assertEqual(len(flags["changed"]), 2)
        contract = report["inventories"]["tool_contracts"]["changed"][0]
        self.assertEqual(contract["key"], "demo_lookup")
        self.assertIn("新增旗标不代表未来产品承诺", readable(report))

    def test_css_byte_ranges_are_utf8_not_character_offsets(self):
        content = '/* 原创 */ :root { --tone: "a;b}"; --demo-red-10: #abc; }'.encode()
        (self.base / "theme.css").write_bytes(content)
        doc = snapshot(self.base, "synthetic")
        records = [x for x in doc["records"] if x["category"] == "css_tokens"]
        self.assertEqual(len(records), 2)
        for record in records:
            src = record["source"]
            self.assertTrue(content[src["byte_start"]:src["byte_end"]].startswith(record["key"].encode()))
        self.assertEqual(next(x for x in records if x["key"] == "--tone")["value"], '"a;b}"')

    def test_nested_scope_does_not_merge_dark_and_light(self):
        doc = snapshot(ROOT / "tests/fixtures/v1", "test")
        values = [x for x in doc["records"] if x["category"] == "css_tokens" and x["key"] == "--demo-gray-100"]
        self.assertEqual(len(values), 2)
        self.assertNotEqual(values[0]["scope"], values[1]["scope"])

    def test_quoted_selector_comment_is_preserved(self):
        (self.base / "theme.css").write_text('[data-name="/*literal*/"] { --x: #abc; }')
        doc = snapshot(self.base, "test")
        self.assertEqual(doc["records"][0]["scope"], ['[data-name="/*literal*/"]'])

    def test_unclosed_css_comment_and_excess_depth_report_gaps(self):
        (self.base / "one.css").write_text(':root { --x: #abc; } /* unclosed')
        (self.base / "two.css").write_text('@layer a {' * 65 + ':root { --x: #abc; }' + '}' * 65)
        doc = snapshot(self.base, "test")
        self.assertEqual(len(doc["coverage"]["issues"]), 2)

    def test_malformed_and_non_utf8_files_are_coverage_gaps(self):
        (self.base / "bad.json").write_text('{"a":1,"a":2}')
        (self.base / "bad.js").write_bytes(b"\xff")
        doc = snapshot(self.base, "test")
        self.assertFalse(doc["coverage"]["complete_within_declared_scope"])
        self.assertEqual(len(doc["coverage"]["issues"]), 2)

    def test_skipped_oversized_file(self):
        (self.base / "large.js").write_bytes(b"x"*20)
        doc = snapshot(self.base, "test", replace(Limits(), max_file_bytes=10))
        self.assertEqual(doc["files"][0]["status"], "skipped-file-size-bound")
        self.assertFalse(doc["coverage"]["complete_within_declared_scope"])

    def test_total_and_entry_bounds_fail_closed(self):
        (self.base / "a").write_bytes(b"123")
        (self.base / "b").write_bytes(b"123")
        with self.assertRaises(ToolkitError): snapshot(self.base, "test", replace(Limits(), max_total_bytes=5))
        with self.assertRaises(ToolkitError): snapshot(self.base, "test", replace(Limits(), max_files=1))

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlinks_not_followed(self):
        target = self.base / "outside.js"
        target.write_text('checkGate("secret_outside")')
        inside = self.base / "input"
        inside.mkdir()
        (inside / "link.js").symlink_to(target)
        doc = snapshot(inside, "test")
        self.assertFalse(doc["records"])
        self.assertEqual(doc["files"][0]["status"], "skipped-link-or-special")

    def test_hardlinks_not_scanned(self):
        target = self.base / "outside.js"
        target.write_text('checkGate("secret_outside")')
        inside = self.base / "input"
        inside.mkdir()
        os.link(target, inside / "hard.js")
        self.assertFalse(snapshot(inside, "test")["records"])

    def test_renamed_bundle_does_not_create_token_changes(self):
        old, new = self.base / "old", self.base / "new"
        old.mkdir(); new.mkdir()
        data = ':root { --x: #abc; }'
        (old / "old-hash.css").write_text(data)
        (new / "new-hash.css").write_text(data)
        report = diff_snapshots(snapshot(old, "old"), snapshot(new, "new"))
        self.assertFalse(report["inventories"]["css_tokens"]["added"])
        self.assertEqual(len(report["files"]["possible_moves"]), 1)

    def test_policy_difference_downgrades_css_change(self):
        old = snapshot(ROOT / "tests/fixtures/v1", "old")
        new = snapshot(ROOT / "tests/fixtures/v2", "new", replace(Limits(), max_files=1000))
        report = diff_snapshots(old, new)
        self.assertTrue(report["warnings"])
        self.assertEqual(report["inventories"]["css_tokens"]["changed"][0]["interpretation"], "uncertain-candidate")

    def test_markdown_neutralizes_html_and_links(self):
        old, new = self.base / "old", self.base / "new"
        old.mkdir(); new.mkdir()
        (new / "sample.js").write_text('track("<img src=x onerror=evil> [click](https://bad.invalid)")')
        text = readable(diff_snapshots(snapshot(old, "<script>"), snapshot(new, "new")))
        self.assertNotIn("<script>", text)
        self.assertNotIn("<img", text)
        self.assertNotIn("[click](", text)


class LiteralTests(unittest.TestCase):
    def scan(self, code): return literal_candidates(code.encode(), load_rules())

    def test_comments_strings_regex_and_dynamic_values_are_not_executed_or_named(self):
        records = self.scan('''// checkGate("comment")
/* track("comment") */
const text = 'checkGate("inside_string")';
const pattern = /checkGate("inside_regex")/;
checkGate(dynamicName); checkGate(`dynamic_${name}`);
checkGate("actual", false); track("sentinel");
''')
        self.assertEqual({r["key"] for r in records}, {"actual", "sentinel"})

    def test_concatenated_first_argument_not_claimed(self):
        self.assertFalse(self.scan('checkGate("prefix" + suffix);'))

    def test_escaped_names_are_explicitly_not_decoded(self):
        self.assertFalse(self.scan(r'checkGate("x\u0061");'))

    def test_event_field_literal_and_dynamic(self):
        records = self.scan('({event_key:"a"}); ({event_key:condition?"b":"c"});')
        self.assertEqual([r["key"] for r in records], ["a"])

    def test_unassociated_schema_is_not_attached_to_nearby_name(self):
        records = self.scan('const a={name:"unrelated"}; const b={inputSchema:generateSchema()};')
        self.assertEqual(records[0]["key"], "schema-marker:inputSchema")
        self.assertEqual(records[0]["kind"], "unassociated-schema-marker")

    def test_json_contract_and_pointer(self):
        data = b'{"tools":[{"name":"example","input_schema":{"type":"object","properties":{"q":{"type":"string"}},"required":["q"]}}]}'
        records = json_candidates(data, load_rules())
        self.assertEqual(records[0]["json_pointer"], "/tools/0/input_schema")
        self.assertEqual(records[0]["value"]["properties"], [{"name":"q","type":"string"}])
        self.assertEqual(records[0]["confidence"], "static-json-structure")

    def test_json_nonfinite_and_duplicate_members_rejected(self):
        for data in (b'{"flags":{"x":NaN}}', b'{"flags":{"x":1e400}}', b'{"a":1,"a":2}'):
            with self.subTest(data=data), self.assertRaises(ToolkitError):
                json_candidates(data, load_rules())

    def test_rule_configuration_is_literal_and_bounded(self):
        with self.assertRaises(ToolkitError): load_rules({"flag_calls": [".*"]})
        rules = load_rules(); rules["flag_calls"] = ["minifiedAlias"]
        records = literal_candidates(b'minifiedAlias("candidate")', load_rules(rules))
        self.assertEqual(records[0]["key"], "candidate")


class ArchiveTests(Temporary):
    def make(self, entries, compression=zipfile.ZIP_STORED):
        path = self.base / "input.zip"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with zipfile.ZipFile(path, "w", compression=compression) as z:
                for name, data in entries: z.writestr(name, data)
        return path

    def reject(self, entries, limits=Limits()):
        archive = self.make(entries)
        with self.assertRaises((ToolkitError, zipfile.BadZipFile)):
            extract_zip(archive, self.base / "output", limits)
        self.assertFalse((self.base / "output").exists())

    def test_valid_zip_and_non_executable_mode(self):
        path = self.make([("sub/", b""), ("sub/a.js", b'checkGate("test")')], zipfile.ZIP_DEFLATED)
        result = extract_zip(path, self.base / "output")
        target = self.base / "output/sub/a.js"
        self.assertEqual(target.read_bytes(), b'checkGate("test")')
        self.assertEqual(result["entries"], 2)
        self.assertEqual(target.stat().st_mode & 0o111, 0)

    def test_path_traversal_and_platform_aliases(self):
        for name in ("../escape", "/absolute", "a/../x", "a\\evil", "C:/evil", "a//b", "a/./b", "NUL.txt", "COM¹", "LPT².log", "bad*path", "bad|path", "a.", "a ", "x:stream", "a\x01b"):
            with self.subTest(name=name): self.reject([(name, b"x")])

    def test_link_and_special_modes(self):
        for mode in (stat.S_IFLNK, stat.S_IFIFO, stat.S_IFCHR, stat.S_IFSOCK):
            entry = zipfile.ZipInfo("evil")
            entry.create_system = 3
            entry.external_attr = (mode | 0o777) << 16
            with self.subTest(mode=mode): self.reject([(entry, b"target")])

    def test_duplicate_case_unicode_and_prefix_collisions(self):
        for names in (("a", "a"), ("A.txt", "a.txt"), ("é.txt", "e\u0301.txt"), ("a", "a/x")):
            with self.subTest(names=names): self.reject([(name, b"x") for name in names])

    def test_size_entry_depth_and_total_bounds(self):
        self.reject([("x", b"123")], replace(Limits(), max_file_bytes=2))
        self.reject([("x", b"12"), ("y", b"34")], replace(Limits(), max_total_bytes=3))
        self.reject([("x", b"1"), ("y", b"2")], replace(Limits(), max_files=1))
        self.reject([("a/b/c", b"1")], replace(Limits(), max_depth=2))

    def test_compression_ratio(self):
        archive = self.make([("bomb", b"0"*100000)], zipfile.ZIP_DEFLATED)
        with self.assertRaises(ToolkitError): extract_zip(archive, self.base / "output")
        self.assertFalse((self.base / "output").exists())

    def test_crc_failure_rolls_back(self):
        archive = self.make([("x", b"unique_payload_123")])
        data = archive.read_bytes().replace(b"unique_payload_123", b"Unique_payload_123")
        archive.write_bytes(data)
        with self.assertRaises(zipfile.BadZipFile): extract_zip(archive, self.base / "output")
        self.assertFalse((self.base / "output").exists())
        self.assertFalse(list(self.base.glob(".reverse-toolkit-*")))

    def test_existing_output_untouched(self):
        archive = self.make([("x", b"new")])
        out = self.base / "output"; out.mkdir()
        (out / "keep").write_text("old")
        with self.assertRaises(ToolkitError): extract_zip(archive, out)
        self.assertEqual((out / "keep").read_text(), "old")

    def test_non_zip_rejected(self):
        path = self.base / "archive.dmg"; path.write_bytes(b"not zip")
        with self.assertRaises(ToolkitError): extract_zip(path, self.base / "output")

    def test_unsupported_compression_rejected(self):
        path = self.make([("x", b"abc")], zipfile.ZIP_BZIP2)
        with self.assertRaises(ToolkitError): extract_zip(path, self.base / "output")

    def test_zip64_multidisk_and_encryption_headers_rejected(self):
        for kind in ("zip64", "multidisk", "encrypted"):
            path = self.make([("x", b"abc")])
            data = bytearray(path.read_bytes())
            eocd = data.rfind(b"PK\x05\x06")
            if kind == "zip64":
                struct.pack_into("<H", data, eocd+8, 65535)
                struct.pack_into("<H", data, eocd+10, 65535)
            elif kind == "multidisk": struct.pack_into("<H", data, eocd+4, 1)
            else:
                cd = data.index(b"PK\x01\x02")
                struct.pack_into("<H", data, cd+8, 1)
            path.write_bytes(data)
            with self.subTest(kind=kind), self.assertRaises(ToolkitError):
                extract_zip(path, self.base / "output")
            self.assertFalse((self.base / "output").exists())

    def test_archive_and_central_directory_bounds(self):
        path = self.make([("x", b"abc")])
        for limits in (replace(Limits(), max_archive_bytes=10), replace(Limits(), max_central_bytes=5)):
            with self.subTest(limits=limits), self.assertRaises(ToolkitError):
                extract_zip(path, self.base / "output", limits)

    def test_nul_in_original_zip_name_rejected(self):
        path = self.make([("abc", b"x")])
        path.write_bytes(path.read_bytes().replace(b"abc", b"a\x00c"))
        with self.assertRaises(ToolkitError): extract_zip(path, self.base / "output")

    def test_small_file_with_forced_zip64_local_header_rejected(self):
        path = self.base / "forced.zip"
        with zipfile.ZipFile(path, "w") as archive:
            with archive.open("small", "w", force_zip64=True) as file:
                file.write(b"small")
        with self.assertRaises(ToolkitError): extract_zip(path, self.base / "output")


class CliTests(Temporary):
    def run_cli(self, *args):
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run([sys.executable, "-B", str(ROOT / "reverse_toolkit.py"), *map(str, args)], cwd=self.base, env=env, text=True, capture_output=True)

    def test_one_command_and_snapshot_diff_roundtrip(self):
        output = self.base / "result with spaces"
        result = self.run_cli("compare", "--old", ROOT/"tests/fixtures/v1", "--new", ROOT/"tests/fixtures/v2", "--output", output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(sorted(p.name for p in output.iterdir()), ["after.json", "before.json", "diff.json", "diff.md"])
        second = self.base / "second"
        result = self.run_cli("diff", "--old-snapshot", output/"before.json", "--new-snapshot", output/"after.json", "--output", second)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((output/"diff.json").read_bytes(), (second/"diff.json").read_bytes())
        self.assertEqual((output/"diff.md").read_bytes(), (second/"diff.md").read_bytes())

    def test_no_overwrite_and_no_output_inside_input(self):
        source = self.base / "input"; source.mkdir()
        result = self.run_cli("snapshot", "--input", source, "--label", "x", "--output", source/"report.json")
        self.assertEqual(result.returncode, 2)
        output = self.base / "keep.json"; output.write_text("keep")
        result = self.run_cli("snapshot", "--input", source, "--label", "x", "--output", output)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(output.read_text(), "keep")

    def test_no_target_execution(self):
        source = self.base / "input"; source.mkdir()
        marker = self.base / "MUST_NOT_EXIST"
        (source / "payload.js").write_text(f'require("fs").writeFileSync({json.dumps(str(marker))}, "executed"); checkGate("safe_literal");')
        result = self.run_cli("snapshot", "--input", source, "--label", "x", "--output", self.base/"out.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists())


if __name__ == "__main__": unittest.main()
