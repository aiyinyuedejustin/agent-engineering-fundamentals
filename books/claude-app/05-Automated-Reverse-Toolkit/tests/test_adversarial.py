"""Offline synthetic regressions from the independent bounded-I/O audit."""
from dataclasses import replace
from copy import deepcopy
import binascii
import io
import json
import os
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import unittest
from unittest import mock
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from toolkit.safeio import Limits, ToolkitError, extract_zip, digest
from toolkit.inventory import snapshot, canonical, verify_snapshot
from toolkit.diffing import diff_snapshots, readable
from reverse_toolkit import prepare_output


class AdversarialArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.archive = self.base / "input.zip"
        self.output = self.base / "output"

    def tearDown(self):
        self.temp.cleanup()

    def make(self, entries, compression=zipfile.ZIP_STORED):
        with zipfile.ZipFile(self.archive, "w", compression=compression) as archive:
            for name, payload in entries:
                archive.writestr(name, payload)
        return bytearray(self.archive.read_bytes())

    def reject(self, data=None, limits=Limits()):
        if data is not None:
            self.archive.write_bytes(data)
        try:
            with self.assertRaises((ToolkitError, zipfile.BadZipFile)):
                extract_zip(self.archive, self.output, limits)
            self.assertFalse(self.output.exists())
            self.assertFalse(list(self.base.glob(".reverse-toolkit-*")))
        finally:
            # Keep failure reproductions independent when several corrupt
            # inputs are subtests of one method on the unpatched baseline.
            if self.output.is_dir():
                shutil.rmtree(self.output)

    def test_implicit_parent_case_and_unicode_collisions(self):
        for names in (("Dir/a", "dir/b"), ("é/a", "e\u0301/b"), ("Dir/", "dir/a"), ("ΐ/a", "Ι\u0308\u0301/b")):
            with self.subTest(names=names):
                self.make([(name, b"" if name.endswith("/") else b"x") for name in names])
                self.reject()

    def test_extra_trailing_separators_rejected(self):
        self.make([("dir//", b"")])
        self.reject()

    def test_understated_stored_and_deflated_sizes_fail_closed(self):
        for compression in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            with self.subTest(compression=compression):
                data = self.make([("file", b"ABC" + b"tail" * 100)], compression)
                cd = data.index(b"PK\x01\x02")
                for base, crc_offset, size_offset in ((0, 14, 22), (cd, 16, 24)):
                    struct.pack_into("<I", data, base+crc_offset, binascii.crc32(b"ABC"))
                    struct.pack_into("<I", data, base+size_offset, 3)
                self.reject(data, replace(Limits(), max_file_bytes=3, max_total_bytes=3))

    def test_directory_crc_checked_and_rolled_back(self):
        data = self.make([("safe/", b"")])
        cd = data.index(b"PK\x01\x02")
        struct.pack_into("<I", data, 14, 1)
        struct.pack_into("<I", data, cd+16, 1)
        self.reject(data)

    def test_directory_local_path_must_match(self):
        data = self.make([("safe/", b"")])
        data[30:35] = b"../x/"
        self.reject(data)

    def test_central_entry_disk_number_rejected(self):
        data = self.make([("file", b"abc")])
        cd = data.index(b"PK\x01\x02")
        struct.pack_into("<H", data, cd+34, 1)
        self.reject(data)

    def test_local_method_size_crc_and_flags_must_match(self):
        for offset, fmt, value in ((8, "<H", 12), (22, "<I", 1), (14, "<I", 0), (6, "<H", 1)):
            with self.subTest(offset=offset):
                data = self.make([("file", b"abc")])
                struct.pack_into(fmt, data, offset, value)
                self.reject(data)

    def test_disguised_zip64_extra_rejected(self):
        info = zipfile.ZipInfo("file")
        info.extra = struct.pack("<HH", 1, 0)
        self.make([(info, b"abc")])
        self.reject()

    def test_false_eocd_count_rejected_before_zipfile_allocation(self):
        data = self.make([("one", b"a"), ("two", b"b")])
        end = data.rfind(b"PK\x05\x06")
        struct.pack_into("<2H", data, end+8, 1, 1)
        self.archive.write_bytes(data)
        with mock.patch("toolkit.safeio.zipfile.ZipFile", side_effect=AssertionError("must preflight actual entry count")):
            self.reject()

    def test_overlapping_local_headers_rejected(self):
        data = self.make([("same", b"one"), ("next", b"two")])
        first = data.index(b"PK\x01\x02")
        second = data.index(b"PK\x01\x02", first+4)
        data[second+46:second+50] = b"same"
        # Distinct central name still rejects overlapping local headers before
        # any writes, whether by the header match or overlap validation.
        struct.pack_into("<I", data, second+42, 0)
        self.reject(data)

    def test_deflate_end_marker_and_trailing_payload_checked(self):
        # Two handcrafted ordinary deflate records: one unfinished stream and
        # one complete stream followed by bytes inside its compressed extent.
        payload = b"small synthetic payload"
        compressor = zlib.compressobj(wbits=-15)
        incomplete = compressor.compress(payload) + compressor.flush(zlib.Z_SYNC_FLUSH)
        compressor = zlib.compressobj(wbits=-15)
        complete = compressor.compress(payload) + compressor.flush()
        for compressed in (incomplete, complete+b"junk"):
            with self.subTest(compressed=compressed):
                name = b"file"
                crc = binascii.crc32(payload)
                local = struct.pack("<4s5H3I2H", b"PK\x03\x04", 20, 0, 8, 0, 0, crc, len(compressed), len(payload), len(name), 0) + name + compressed
                central = struct.pack("<4s6H3I5H2I", b"PK\x01\x02", 20, 20, 0, 8, 0, 0, crc, len(compressed), len(payload), len(name), 0, 0, 0, 0, 0, 0) + name
                end = struct.pack("<4s4H2IH", b"PK\x05\x06", 0, 0, 1, 1, len(central), len(local), 0)
                self.reject(local+central+end)

    def test_supported_data_descriptors_still_extract(self):
        class Unseekable(io.BytesIO):
            def seekable(self): return False
            def seek(self, *args): raise io.UnsupportedOperation
        buffer = Unseekable()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("dir/", b"")
            archive.writestr("dir/file", b"payload")
        self.archive.write_bytes(buffer.getvalue())
        extract_zip(self.archive, self.output)
        self.assertEqual((self.output / "dir/file").read_bytes(), b"payload")

    def test_explicit_directory_after_child_and_multichunk_deflate(self):
        payload = b"abcdefghijklmnop" * (256*1024)
        self.make([("dir/file", payload), ("dir/", b"")], zipfile.ZIP_DEFLATED)
        extract_zip(self.archive, self.output, replace(Limits(), max_ratio=1000))
        self.assertEqual((self.output / "dir/file").read_bytes(), payload)

    def test_write_failure_rolls_back(self):
        self.make([("file", b"abc")])
        with mock.patch("toolkit.safeio.os.chmod", side_effect=OSError("synthetic disk error")):
            with self.assertRaises(OSError):
                extract_zip(self.archive, self.output)
        self.assertFalse(self.output.exists())
        self.assertFalse(list(self.base.glob(".reverse-toolkit-*")))


class AdditionalBoundaryTests(unittest.TestCase):
    def resign(self, doc):
        doc = deepcopy(doc)
        doc["identity"]["tree_sha256"] = digest(canonical(doc["files"]).encode())
        doc["identity"]["policy_sha256"] = digest(canonical(doc["policy"]).encode())
        doc["identity"].pop("snapshot_sha256", None)
        doc["identity"]["snapshot_sha256"] = digest(canonical(doc).encode())
        return doc

    def test_rehashed_snapshot_cannot_inject_source_digest_markup(self):
        doc = snapshot(ROOT / "tests/fixtures/v1", "test")
        doc["records"][0]["source"]["sha256"] = "x\n\n[click](https://example.invalid)"
        with self.assertRaises(ToolkitError):
            verify_snapshot(self.resign(doc))

    def test_malformed_rehashed_snapshot_shapes_rejected(self):
        original = snapshot(ROOT / "tests/fixtures/v1", "test")
        for mutation in ("scope", "value", "source", "coverage", "path", "digest"):
            with self.subTest(mutation=mutation):
                doc = deepcopy(original)
                if mutation == "scope": doc["records"][0]["scope"] = [None]
                elif mutation == "value": del doc["records"][0]["value"]
                elif mutation == "source": doc["records"][0]["source"] = {}
                elif mutation == "coverage": del doc["coverage"]
                elif mutation == "path": doc["files"][0]["path"] = 123
                else: doc["files"][0]["sha256"] = "<script>"
                with self.assertRaises(ToolkitError):
                    diff_snapshots(original, self.resign(doc))

    def test_record_source_ranges_must_reference_inventory_bytes(self):
        original = snapshot(ROOT / "tests/fixtures/v1", "test")
        for mutation in ("path", "end", "line"):
            with self.subTest(mutation=mutation):
                doc = deepcopy(original)
                source = next(record["source"] for record in doc["records"] if "byte_end" in record["source"])
                if mutation == "path": source["path"] = "missing"
                elif mutation == "end": source["byte_end"] = 10**9
                else: source["line"] = 0
                with self.assertRaises(ToolkitError):
                    verify_snapshot(self.resign(doc))

    def test_nonfinite_js_number_is_a_coverage_gap(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp)
            (source / "x.js").write_text('checkGate("number", 1e400)')
            doc = snapshot(source, "test")
            self.assertFalse(doc["coverage"]["complete_within_declared_scope"])
            self.assertEqual(doc["files"][0]["status"], "scan-incomplete")
            self.assertFalse(doc["records"])
            self.assertIs(verify_snapshot(doc), doc)

    def test_output_alias_into_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / "input"; source.mkdir()
            alias = base / "alias"; alias.symlink_to(source, target_is_directory=True)
            with self.assertRaises(ToolkitError):
                prepare_output(alias / "report.json", [source])

    def test_dangling_output_link_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            output = base / "output"; output.symlink_to(base / "missing")
            with self.assertRaises(ToolkitError):
                prepare_output(output, [])

    def test_symlink_directory_entries_are_counted_but_not_followed(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            outside = base / "outside"; outside.mkdir()
            (outside / "secret.js").write_text('track("outside")')
            source = base / "input"; source.mkdir()
            (source / "link").symlink_to(outside, target_is_directory=True)
            doc = snapshot(source, "test")
            self.assertEqual(doc["coverage"]["entry_count"], 1)
            self.assertFalse(doc["records"])
            with self.assertRaises(ToolkitError):
                snapshot(source, "test", replace(Limits(), max_files=0))

    def test_identical_duplicate_content_is_not_guessed_as_moves(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            old = base / "old"; old.mkdir()
            new = base / "new"; new.mkdir()
            for name in ("a", "b"): (old / name).write_bytes(b"same")
            for name in ("c", "d"): (new / name).write_bytes(b"same")
            first = diff_snapshots(snapshot(old, "old"), snapshot(new, "new"))
            second = diff_snapshots(snapshot(old, "old"), snapshot(new, "new"))
            self.assertFalse(first["files"]["possible_moves"])
            self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
