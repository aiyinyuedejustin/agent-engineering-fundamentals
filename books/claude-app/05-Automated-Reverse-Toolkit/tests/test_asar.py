"""Original synthetic ASAR fixtures only. No upstream/target code is executed."""
from dataclasses import replace
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from toolkit import asar
from toolkit.asar import extract_asar, inspect_asar
from toolkit.safeio import Limits, ToolkitError


def archive_bytes(tree=None, payload=b"abc", raw=None):
    if raw is None:
        raw = json.dumps(tree or {"files": {"a.txt": {"size": 3, "offset": "0"}}},
                         ensure_ascii=False, separators=(",", ":")).encode()
    padded = raw + b"\0" * (-len(raw) % 4)
    return struct.pack("<4I", 4, 8 + len(padded), 4 + len(padded), len(raw)) + padded + payload


def integrity(data, block=2):
    h = lambda value: hashlib.sha256(value).hexdigest()
    return {"algorithm": "SHA256", "hash": h(data), "blockSize": block,
            "blocks": [h(data[n:n+block]) for n in range(0, len(data), block)] or [h(b"")]}


class AsarTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.source = self.base / "input.asar"
        self.output = self.base / "output"

    def tearDown(self):
        self.temp.cleanup()

    def make(self, tree=None, payload=b"abc", raw=None):
        self.source.write_bytes(archive_bytes(tree, payload, raw))

    def rejects(self, data=None, limits=Limits(), pattern=None):
        if data is not None:
            self.source.write_bytes(data)
        context = self.assertRaisesRegex(ToolkitError, pattern) if pattern else self.assertRaises(ToolkitError)
        with context:
            extract_asar(self.source, self.output, limits)
        self.assertFalse(self.output.exists())
        self.assertFalse(list(self.base.glob(".reverse-toolkit-asar-*")))

    def test_happy_path_private_permissions_and_digest(self):
        self.make({"files": {"sub": {"files": {"a.txt": {"size": 3, "offset": "0", "executable": True,
                        "integrity": integrity(b"abc")}}}, "empty": {"files": {}},
                        "zero": {"size": 0, "offset": "3", "integrity": integrity(b"")}}})
        result = extract_asar(self.source, self.output)
        self.assertEqual((self.output / "sub/a.txt").read_bytes(), b"abc")
        self.assertTrue((self.output / "empty").is_dir())
        self.assertEqual((self.output / "zero").read_bytes(), b"")
        self.assertEqual(result["archive_sha256"], hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.assertEqual(result["files_with_declared_integrity"], 2)
        self.assertTrue(result["declared_member_integrity_verified"])
        self.assertFalse(result["publisher_authenticity_verified"])
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE(self.output.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE((self.output / "sub/a.txt").stat().st_mode), 0o600)

    def test_multichunk_and_boundary_integrity(self):
        for size in (0, 1, 2, 4, asar.CHUNK * 3 + 17):
            with self.subTest(size=size):
                data = b"x" * size
                self.make({"files": {"a": {"size": size, "offset": "0", "integrity": integrity(data, 90001)}}}, data)
                out = self.base / str(size)
                extract_asar(self.source, out)
                self.assertEqual((out / "a").read_bytes(), data)

    def test_empty_archive(self):
        self.make({"files": {}}, b"")
        result = extract_asar(self.source, self.output)
        self.assertEqual(result["entries"], 0)

    def test_missing_integrity_explicit_count(self):
        self.make()
        result = extract_asar(self.source, self.output)
        self.assertEqual(result["files_with_declared_integrity"], 0)

    def test_truncated_prefix_and_data(self):
        valid = archive_bytes()
        for end in (0, 1, 7, 8, 15, 16, len(valid)-1):
            with self.subTest(end=end): self.rejects(valid[:end])

    def test_pickle_lengths_and_padding(self):
        valid = archive_bytes()
        for index, value in ((0, 0), (1, 4), (1, 0xffffffff), (2, 0), (3, 0xffffffff), (3, 0)):
            with self.subTest(index=index, value=value):
                data = bytearray(valid)
                struct.pack_into("<I", data, index*4, value)
                self.rejects(data)
        raw = b'{"files":{}} '
        while len(raw) % 4 == 0: raw += b' '
        data = bytearray(archive_bytes(raw=raw, payload=b""))
        data[16+len(raw)] = 1
        self.rejects(data)

    def test_header_bound_before_allocating_declared_length(self):
        stream = io.BytesIO(struct.pack("<4I", 4, 64*1024*1024, 64*1024*1024-4, 64*1024*1024-8))
        with mock.patch.object(stream, "read", wraps=stream.read) as read:
            with self.assertRaisesRegex(ToolkitError, "header exceeds"):
                asar._header(stream, 128*1024*1024, Limits())
            self.assertEqual(read.call_args_list, [mock.call(16)])

    def test_archive_bound_before_open(self):
        self.make()
        with mock.patch.object(os, "open", side_effect=AssertionError("must not open")):
            self.rejects(limits=replace(Limits(), max_archive_bytes=16))

    def test_json_invalid_duplicate_keys_nonfinite_and_large_numbers(self):
        for raw in (b'{"files":{},"files":{}}', b'{"files":{"a":{"size":1,"size":2,"offset":"0"}}}',
                    b'{"files":{},"f":NaN}', b'{"files":{},"f":Infinity}',
                    b'{"files":{},"f":1.0}', b'{"files":{},"f":'+b'9'*100+b'}',
                    b'{"files":{}} garbage', b'{"files":{"\xff":{}}}', b'[]', b'null'):
            with self.subTest(raw=raw[:55]): self.rejects(archive_bytes(raw=raw))

    def test_json_token_and_depth_bounds_before_json_loads(self):
        for raw, limits in ((b'{"files":{"a":{"size":3,"offset":"0"}}}', replace(Limits(), max_records=3)),
                            (b'['*150+b']'*150, Limits())):
            with mock.patch.object(asar.json, "loads", side_effect=AssertionError("must not decode")):
                self.rejects(archive_bytes(raw=raw), limits)

    def test_unsafe_components_at_root_and_nested(self):
        for name in ("", ".", "..", "../escape", "/abs", "x/y", "x\\y", "C:drive", "NUL", "a\0b", "a\nb",
                     "trail.", "trail ", "COM1", "x"*256, "\ud800"):
            for nested in (False, True):
                with self.subTest(name=name, nested=nested):
                    files = {name: {"size": 3, "offset": "0"}}
                    if nested: files = {"parent": {"files": files}}
                    raw = json.dumps({"files": files}, ensure_ascii=True).encode()
                    self.rejects(archive_bytes(raw=raw))

    def test_case_and_unicode_collision(self):
        for names in (("A", "a"), ("é", "e\u0301"), ("Dir", "dir")):
            self.make({"files": {n: {"files": {}} for n in names}})
            self.rejects(pattern="colliding")

    def test_file_and_directory_conflict(self):
        self.make({"files": {"a": {"files": {}, "size": 3, "offset": "0"}}})
        self.rejects()

    def test_links_inventory_but_no_extraction(self):
        self.make({"files": {"link": {"link": "../../outside"}}}, b"")
        result = inspect_asar(self.source)
        self.assertEqual(result["exclusions"], [{"path": "link", "reason": "link-not-followed"}])
        self.assertNotIn("../../outside", json.dumps(result))
        self.rejects(pattern="exclusions")

    def test_unpacked_sidecar_is_never_read_or_used(self):
        self.make({"files": {"x.node": {"size": 3, "unpacked": True}}}, b"")
        sidecar = self.base / "input.asar.unpacked"
        sidecar.symlink_to(self.base / "missing")
        result = inspect_asar(self.source)
        self.assertFalse(result["extractable_within_subset"])
        self.assertFalse(result["complete_application"])
        self.assertEqual(result["exclusions"][0]["reason"], "unpacked-sidecar-not-read")
        self.rejects(pattern="sidecar")

    def test_unpacked_directory_propagates(self):
        self.make({"files": {"n": {"unpacked": True, "files": {"x": {"size": 3}}}}}, b"")
        result = inspect_asar(self.source)
        self.assertEqual(len(result["exclusions"]), 2)
        self.rejects()

    def test_ambiguous_unpacked_offset(self):
        self.make({"files": {"x": {"unpacked": True, "size": 3, "offset": "0"}}})
        self.rejects()

    def test_special_hardlink_and_unknown_metadata(self):
        for field, value in (("hardlink", "a"), ("symlink", "a"), ("type", "fifo"), ("mode", 0o120777), ("device", 0)):
            self.make({"files": {"x": {"size": 3, "offset": "0", field: value}}})
            self.rejects()

    def test_exact_shared_ranges_copied_not_hardlinked(self):
        self.make({"files": {"a": {"size": 3, "offset": "0"}, "b": {"size": 3, "offset": "0"}}})
        result = inspect_asar(self.source)
        self.assertEqual(result["packed_bytes"], 6)
        self.assertEqual(result["unique_payload_bytes"], 3)
        self.assertEqual(result["unreferenced_payload_bytes"], 0)
        self.assertEqual(result["shared_range_aliases"], 1)
        self.assertEqual(result["exclusions"], [])
        extract_asar(self.source, self.output)
        a, b = self.output / "a", self.output / "b"
        self.assertEqual(a.read_bytes(), b.read_bytes())
        self.assertNotEqual(a.stat().st_ino, b.stat().st_ino)
        self.assertEqual(a.stat().st_nlink, 1)
        self.assertEqual(b.stat().st_nlink, 1)

    def test_shared_ranges_charge_logical_expansion(self):
        self.make({"files": {"a": {"size": 3, "offset": "0"}, "b": {"size": 3, "offset": "0"}}})
        self.rejects(limits=replace(Limits(), max_total_bytes=5), pattern="total packed")

    def test_shared_ranges_integrity_must_agree(self):
        declared = integrity(b"abc")
        for other in (None, {**declared, "hash": "0"*64}, integrity(b"abc", 3)):
            nodes = {"a": {"size": 3, "offset": "0", "integrity": declared},
                     "b": {"size": 3, "offset": "0"}}
            if other is not None: nodes["b"]["integrity"] = other
            self.make({"files": nodes})
            self.rejects(pattern="inconsistent integrity")
        self.make({"files": {n: {"size": 3, "offset": "0", "integrity": declared} for n in ("a", "b")}})
        result = extract_asar(self.source, self.output)
        self.assertTrue(result["declared_member_integrity_verified"])
        self.assertEqual(result["shared_range_aliases"], 1)

    def test_zero_length_alias_integrity_and_embedded_zero_range(self):
        good = integrity(b"")
        bad = {**good, "hash": "0"*64}
        self.make({"files": {"a": {"size": 0, "offset": "0", "integrity": good},
                                  "b": {"size": 0, "offset": "0", "integrity": bad}}}, b"")
        self.rejects(pattern="inconsistent integrity")
        self.make({"files": {"a": {"size": 3, "offset": "0"},
                                  "zero": {"size": 0, "offset": "1", "integrity": good},
                                  "zero2": {"size": 0, "offset": "1", "integrity": good}}})
        result = extract_asar(self.source, self.output)
        self.assertEqual(result["shared_range_aliases"], 1)
        self.assertEqual(result["unique_payload_bytes"], 3)

    def test_partial_overlap_rejected_even_for_inspection(self):
        self.make({"files": {"a": {"size": 2, "offset": "0"}, "b": {"size": 2, "offset": "1"}}})
        with self.assertRaisesRegex(ToolkitError, "overlapping"): inspect_asar(self.source)
        self.rejects()

    def test_ranges_order_zero_length_and_unreferenced_bytes(self):
        self.make({"files": {"b": {"size": 1, "offset": "2"}, "a": {"size": 1, "offset": "0"},
                                      "zero": {"size": 0, "offset": "1"}}}, b"abc!")
        result = extract_asar(self.source, self.output)
        self.assertEqual(result["unreferenced_payload_bytes"], 2)
        self.assertEqual((self.output / "b").read_bytes(), b"c")

    def test_offsets_and_sizes(self):
        for value in (-1, 0, True, None, "-1", "+1", "01", "1.0", "1e3", "١", "9"*100, str(2**64), "3"):
            self.make({"files": {"x": {"size": 1, "offset": value}}})
            self.rejects()
        for size in (-1, True, None, "1", 4, 2**53):
            self.make({"files": {"x": {"size": size, "offset": "0"}}})
            self.rejects()

    def test_limits_total_files_depth_and_invalid_configuration(self):
        self.make()
        for changes in ({"max_file_bytes": 2}, {"max_total_bytes": 2}, {"max_files": 0}, {"max_depth": 129},
                        {"max_records": True}, {"max_central_bytes": 4}):
            self.rejects(limits=replace(Limits(), **changes))
        self.make({"files": {"a": {"files": {"b": {"size": 3, "offset": "0"}}}}})
        self.rejects(limits=replace(Limits(), max_depth=1))
        self.rejects(limits=replace(Limits(), max_files=1))

    def test_expanded_path_budget(self):
        self.make()
        with mock.patch.object(asar, "MAX_LISTING_BYTES", 1): self.rejects()
        with mock.patch.object(asar, "MAX_PATH_BYTES", 1): self.rejects()

    def test_integrity_structure_rejects(self):
        base = integrity(b"abc")
        for key, value in (("algorithm", "MD5"), ("hash", "z"*64), ("blockSize", True), ("blockSize", 0),
                           ("blockSize", 2**40), ("blocks", []), ("blocks", ["z"*64]*2)):
            bad = {**base, key: value}
            self.make({"files": {"x": {"size": 3, "offset": "0", "integrity": bad}}})
            self.rejects()

    def test_integrity_mismatch_rolls_back(self):
        for field in ("hash", "blocks"):
            bad = integrity(b"abc")
            bad[field] = "0"*64 if field == "hash" else ["0"*64]*2
            self.make({"files": {"x": {"size": 3, "offset": "0", "integrity": bad}}})
            self.rejects(pattern="integrity mismatch")

    def test_empty_file_block_integrity_mismatch(self):
        bad = integrity(b""); bad["blocks"] = ["0"*64]
        self.make({"files": {"x": {"size": 0, "offset": "0", "integrity": bad}}}, b"")
        self.rejects(pattern="integrity mismatch")

    def test_existing_output_empty_file_directory_and_symlink_preserved(self):
        self.make()
        for kind in ("file", "directory", "symlink"):
            output = self.base / kind
            if kind == "file": output.write_text("keep")
            elif kind == "directory": output.mkdir()
            else: output.symlink_to(self.base / "missing")
            with self.assertRaisesRegex(ToolkitError, "must not exist"): extract_asar(self.source, output)
            self.assertTrue(output.exists() or output.is_symlink())

    def test_output_appears_at_publication_not_overwritten(self):
        self.make()
        original = asar.atomic_publish
        def appear(stage, output):
            output.mkdir()
            return original(stage, output)
        with mock.patch.object(asar, "atomic_publish", side_effect=appear):
            with self.assertRaisesRegex(ToolkitError, "nothing was replaced"): extract_asar(self.source, self.output)
        self.assertTrue(self.output.is_dir())
        self.assertEqual(list(self.output.iterdir()), [])
        self.assertFalse(list(self.base.glob(".reverse-toolkit-asar-*")))

    def test_output_parent_must_exist(self):
        self.make()
        with self.assertRaises(ToolkitError): extract_asar(self.source, self.base / "missing/out")

    def test_symlink_and_hardlinked_inputs_rejected(self):
        self.make()
        link = self.base / "link.asar"; link.symlink_to(self.source)
        with self.assertRaises(ToolkitError): extract_asar(link, self.output)
        hard = self.base / "hard.asar"; os.link(self.source, hard)
        self.rejects()

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO unavailable")
    def test_fifo_input_rejected_without_open(self):
        os.mkfifo(self.source)
        self.rejects()

    def test_input_mutation_before_commit_rolls_back(self):
        self.make()
        original = asar._copy_entry
        def mutate(*args):
            original(*args)
            with self.source.open("ab") as stream: stream.write(b"!")
        with mock.patch.object(asar, "_copy_entry", side_effect=mutate): self.rejects(pattern="changed")

    def test_write_and_publish_failures_roll_back(self):
        self.make()
        for method in ("_copy_entry", "atomic_publish"):
            with mock.patch.object(asar, method, side_effect=OSError("synthetic failure")):
                with self.assertRaises(OSError): extract_asar(self.source, self.output)
            self.assertFalse(self.output.exists())
            self.assertFalse(list(self.base.glob(".reverse-toolkit-asar-*")))

    def test_unsupported_atomic_host_fails_closed(self):
        self.make()
        with mock.patch.object(asar.sys, "platform", "unsupported"):
            self.rejects(pattern="atomic no-replace")

    def test_target_javascript_never_runs(self):
        marker = self.base / "EXECUTED"
        data = ('require("fs").writeFileSync('+json.dumps(str(marker))+',"bad");').encode()
        self.make({"files": {"app.js": {"size": len(data), "offset": "0", "executable": True}}}, data)
        extract_asar(self.source, self.output)
        self.assertFalse(marker.exists())

    def test_cli_inventory_and_extract(self):
        self.make()
        for command in ("inspect-asar", "unpack-asar"):
            args = [sys.executable, "-B", str(ROOT / "reverse_toolkit.py"), command, "--input", str(self.source)]
            if command == "unpack-asar": args += ["--output", str(self.output)]
            result = subprocess.run(args, cwd=self.base, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["adapter"], "bounded-asar-v1")

    def test_one_line_asar_diff_and_exclusions_fail_whole_run(self):
        self.make({"files": {"app.js": {"size": 18, "offset": "0"}}}, b'checkGate("old");  ')
        other = self.base / "new.asar"
        other.write_bytes(archive_bytes({"files": {"app.js": {"size": 18, "offset": "0"}}}, b'checkGate("new");  '))
        args = [sys.executable, "-B", str(ROOT / "diff-versions.py"), str(self.source), str(other), "--output", str(self.output)]
        result = subprocess.run(args, cwd=self.base, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        run = json.loads((self.output / "run.json").read_text())
        self.assertEqual(run["inputs"]["old"]["adapter"], "bounded-asar-v1")
        self.assertEqual(run["inputs"]["old"]["exclusions"], [])
        other.write_bytes(archive_bytes({"files": {"external": {"size": 1, "unpacked": True}}}, b""))
        second = self.base / "second"
        args[-1] = str(second)
        result = subprocess.run(args, cwd=self.base, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("exclusions", result.stderr)
        self.assertFalse(second.exists())
        self.assertFalse(list(self.base.glob(".diff-versions-*")))


if __name__ == "__main__":
    unittest.main()
