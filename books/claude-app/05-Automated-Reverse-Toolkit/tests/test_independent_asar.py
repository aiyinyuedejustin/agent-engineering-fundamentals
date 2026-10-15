"""Independent synthetic ASAR audit. No upstream code, packages, or app execution.

Point ASAR_AUDIT_ROOT at another complete toolkit directory to retest a patch.
"""
from dataclasses import replace
import hashlib
import importlib.util
import io
import itertools
import json
import os
from pathlib import Path
import random
import stat
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get("ASAR_AUDIT_ROOT", Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(ROOT))
from toolkit import asar
from toolkit.safeio import Limits, ToolkitError


def fixture(files=None, data=b"DATA", raw=None):
    """Independent framing: length Pickle, string Pickle, inert bytes."""
    if raw is None:
        raw = json.dumps({"files": files if files is not None else {
            "data.bin": {"size": len(data), "offset": "0"}
        }}, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    string_payload = struct.pack("<i", len(raw)) + raw + bytes((-len(raw)) % 4)
    header = struct.pack("<I", len(string_payload)) + string_payload
    return struct.pack("<II", 4, len(header)) + header + data


def integrity(data, block=3):
    sha = lambda b: hashlib.sha256(b).hexdigest()
    return {"algorithm": "SHA256", "hash": sha(data), "blockSize": block,
            "blocks": [sha(data[i:i+block]) for i in range(0, len(data), block)] or [sha(b"")]}


class IndependentAsarAudit(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.src, self.dst = self.base / "input.asar", self.base / "out"

    def tearDown(self):
        self.temp.cleanup()

    def admit(self, data, limits=Limits()):
        self.src.write_bytes(data)
        return asar.inspect_asar(self.src, limits)

    def deny_before_stage(self, data, limits=Limits()):
        self.src.write_bytes(data)
        with patch.object(asar.tempfile, "mkdtemp", side_effect=AssertionError("created output stage")):
            with self.assertRaises(ToolkitError):
                asar.extract_asar(self.src, self.dst, limits)
        self.assertFalse(self.dst.exists())
        self.assertEqual(set(self.base.iterdir()), {self.src})

    def test_utf8_byte_length_and_all_four_pickle_alignments(self):
        for n in range(4):
            raw = json.dumps({"files": {"é" + "x" * n: {"size": 4, "offset": "0"}}},
                             ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            meta = self.admit(fixture(raw=raw))
            self.assertEqual(meta["header_json_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(meta["unique_payload_bytes"], 4)

    def test_every_truncation_is_rejected_before_stage(self):
        blob = fixture()
        for length in range(len(blob)):
            with self.subTest(length=length):
                self.deny_before_stage(blob[:length])

    def test_pickle_field_boundary_mutations(self):
        blob = fixture()
        original = struct.unpack("<4I", blob[:16])
        for field, value in itertools.product(range(4), (0, 1, 3, 4, 7, 8, 15, 16, 31,
                                                         2**31-1, 2**31, 2**32-4, 2**32-1)):
            if original[field] == value:
                continue
            mutated = bytearray(blob)
            struct.pack_into("<I", mutated, field*4, value)
            with self.subTest(field=field, value=value):
                self.deny_before_stage(mutated)

    def test_header_length_bounds_before_variable_read(self):
        for raw_len in (2**24, 2**31-1, 2**31):
            aligned = (raw_len + 3) // 4 * 4
            stream = io.BytesIO(struct.pack("<4I", 4, aligned+8, aligned+4, raw_len))
            with patch.object(stream, "read", wraps=stream.read) as reader:
                with self.assertRaises(ToolkitError):
                    asar._header(stream, 2**32+16, Limits())
                self.assertEqual([call.args for call in reader.call_args_list], [(16,)])

    def test_invalid_utf8_and_json_surrogates(self):
        raws = [b'{"files":{"' + bad + b'":{"size":0,"offset":"0"}}}'
                for bad in (b"\xff", b"\xc0\xaf", b"\xed\xa0\x80", b"\xf4\x90\x80\x80")]
        raws += [b'{"files":{"\\ud800":{"size":0,"offset":"0"}}}',
                 b'\xef\xbb\xbf{"files":{}}', b'{"files":{}}\x00']
        for raw in raws:
            with self.subTest(raw=raw):
                self.deny_before_stage(fixture(raw=raw))

    def test_duplicate_json_escaped_keys_every_level(self):
        for raw in (b'{"files":{},"f\\u0069les":{}}',
                    b'{"files":{"x":{},"\\u0078":{}}}',
                    b'{"files":{"x":{"size":1,"s\\u0069ze":1,"offset":"0"}}}',
                    b'{"files":{"x":{"size":1,"offset":"0","integrity":{"hash":"a","hash":"b"}}}}'):
            self.deny_before_stage(fixture(raw=raw))

    def test_noninteger_nonfinite_huge_number_and_bool_sizes(self):
        for token in (b"NaN", b"Infinity", b"-Infinity", b"1e309", b"0.0", b"-0.0",
                      b"1e-999", b"true", b"false", b"null", b"-1", b"9"*10000):
            raw = b'{"files":{"x":{"size":' + token + b',"offset":"0"}}}'
            self.deny_before_stage(fixture(raw=raw))

    def test_json_record_and_nesting_budget_precedes_decode(self):
        for raw, limits in ((b'{"files":{"x":{"size":0,"offset":"0"}}}', replace(Limits(), max_records=5)),
                            (b'[' * 140 + b']' * 140, Limits())):
            with patch.object(asar.json, "loads", side_effect=AssertionError("decoded before budget")):
                self.deny_before_stage(fixture(raw=raw), limits)

    def test_offset_canonicality_and_uint64_range(self):
        for offset in ("00", "01", "-0", "+0", " 0", "0 ", "0\n", "0x0", "1e0", "١",
                       "０", "1.0", str(2**64-1), str(2**64), "9"*10000, 0, True):
            self.deny_before_stage(fixture({"x": {"size": 0, "offset": offset}}))
        self.deny_before_stage(fixture({"x": {"size": 2, "offset": "3"}}))
        self.deny_before_stage(fixture({"x": {"size": 0, "offset": "5"}}))

    def test_all_small_ranges_against_independent_interval_oracle(self):
        # Both insertion orders; exact aliases allowed, empty ranges do not overlap.
        for a_start, a_size, b_start, b_size in itertools.product(range(5), range(4), range(5), range(4)):
            intervals = ((a_start, a_size), (b_start, b_size))
            invalid = any(start+size > 4 for start, size in intervals)
            overlap = a_size and b_size and max(a_start, b_start) < min(a_start+a_size, b_start+b_size)
            invalid = invalid or bool(overlap and intervals[0] != intervals[1])
            for reverse in (False, True):
                pairs = [("a", {"size": a_size, "offset": str(a_start)}),
                         ("b", {"size": b_size, "offset": str(b_start)})]
                if reverse:
                    pairs.reverse()
                data = fixture(dict(pairs))
                with self.subTest(intervals=intervals, reverse=reverse):
                    if invalid:
                        with self.assertRaises(ToolkitError):
                            self.admit(data)
                    else:
                        meta = self.admit(data)
                        covered = set()
                        for start, size in intervals:
                            covered.update(range(start, start+size))
                        self.assertEqual(meta["packed_bytes"], a_size+b_size)
                        self.assertEqual(meta["unique_payload_bytes"], len(covered))
                        self.assertEqual(meta["unreferenced_payload_bytes"], 4-len(covered))

    def test_shared_range_alias_amplification_charged_per_output(self):
        files = {str(n): {"size": 4, "offset": "0"} for n in range(8)}
        self.deny_before_stage(fixture(files), replace(Limits(), max_total_bytes=31))
        meta = self.admit(fixture(files), replace(Limits(), max_total_bytes=32))
        self.assertEqual((meta["packed_bytes"], meta["unique_payload_bytes"], meta["shared_range_aliases"]),
                         (32, 4, 7))
        asar.extract_asar(self.src, self.dst, replace(Limits(), max_total_bytes=32))
        outputs = list(self.dst.iterdir())
        self.assertEqual(len({p.stat().st_ino for p in outputs}), 8)
        self.assertTrue(all(p.stat().st_nlink == 1 for p in outputs))

    def test_shared_integrity_normalizes_hex_and_disallows_disagreement(self):
        first = integrity(b"DATA")
        upper = {**first, "hash": first["hash"].upper(), "blocks": [h.upper() for h in first["blocks"]]}
        files = {"a": {"size": 4, "offset": "0", "integrity": first},
                 "b": {"size": 4, "offset": "0", "integrity": upper}}
        self.admit(fixture(files))
        asar.extract_asar(self.src, self.dst)
        files["b"]["integrity"] = integrity(b"DATA", 4)
        self.src.write_bytes(fixture(files))
        with self.assertRaises(ToolkitError):
            asar.inspect_asar(self.src)

    def test_zero_length_aliases_count_and_require_consistent_integrity(self):
        empty = integrity(b"")
        files = {"data": {"size": 4, "offset": "0"},
                 "a": {"size": 0, "offset": "1", "integrity": empty},
                 "b": {"size": 0, "offset": "1", "integrity": empty}}
        meta = self.admit(fixture(files))
        self.assertEqual(meta["shared_range_aliases"], 1)
        self.assertEqual(meta["unique_payload_bytes"], 4)
        self.assertEqual(meta["unreferenced_payload_bytes"], 0)
        del files["b"]["integrity"]
        self.deny_before_stage(fixture(files))

    def test_sidecars_links_and_inherited_unpacked_fail_before_any_write(self):
        for excluded in ({"link": "../../DO_NOT_READ"}, {"unpacked": True, "size": 1},
                         {"unpacked": True, "files": {}},
                         {"unpacked": True, "files": {"y": {"size": 1}}}):
            files = {"first": {"size": 4, "offset": "0"}, "last": excluded}
            self.deny_before_stage(fixture(files))
            meta = asar.inspect_asar(self.src)
            self.assertFalse(meta["extractable_within_subset"])
            self.assertTrue(meta["exclusions"])
            self.assertNotIn("DO_NOT_READ", json.dumps(meta))

    def test_sidecar_fifo_is_not_opened(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("no fifo support")
        sidecar = self.base / "input.asar.unpacked"
        os.mkfifo(sidecar)
        self.src.write_bytes(fixture({"x": {"size": 1, "unpacked": True}}))
        real_open = asar.os.open
        opened = []
        def open_spy(path, *args, **kwargs):
            opened.append(Path(path))
            return real_open(path, *args, **kwargs)
        with patch.object(asar.os, "open", side_effect=open_spy):
            meta = asar.inspect_asar(self.src)
        self.assertEqual(opened, [self.src])
        self.assertFalse(meta["extractable_within_subset"])

    def test_ambiguous_nodes_unknown_metadata_and_nonbool_flags(self):
        invalid = [{"files": {}, "link": "x"}, {"files": {}, "size": 1},
                   {"link": "x", "size": 0}, {"size": 1, "offset": "0", "unpacked": True},
                   {"size": 1, "offset": "0", "executable": 1},
                   {"size": 1, "offset": "0", "unpacked": 0},
                   {"size": 1, "offset": "0", "hardlink": "z"}, [], None, "str"]
        for node in invalid:
            self.deny_before_stage(fixture({"x": node}))

    def test_path_portability_and_nested_collisions(self):
        for name in ("..", "/tmp/escape", "x/y", "x\\y", "C:", "a:", "a ", "a.",
                     "CON.txt", "lpt².log", "x\x7f", "x\x00", "x"*256):
            self.deny_before_stage(fixture({name: {"files": {}}}))
        for a, b in (("A", "a"), ("é", "e\u0301"), ("ß", "ss")):
            self.deny_before_stage(fixture({"parent": {"files": {a: {"files": {}}, b: {"files": {}}}}}))

    def test_zero_files_gaps_and_member_integrity_reporting(self):
        files = {"empty": {"size": 0, "offset": "4", "integrity": integrity(b"")},
                 "b": {"size": 1, "offset": "2"},
                 "a": {"size": 1, "offset": "0", "integrity": integrity(b"D")}}
        meta = self.admit(fixture(files))
        self.assertFalse(meta["declared_member_integrity_verified"])
        self.assertEqual(meta["unreferenced_payload_bytes"], 2)
        meta = asar.extract_asar(self.src, self.dst)
        self.assertEqual((meta["files_with_declared_integrity"], meta["packed_files"]), (2, 3))
        self.assertTrue(meta["declared_member_integrity_verified"])
        self.assertFalse(meta["publisher_authenticity_verified"])
        self.assertFalse(meta["complete_application"])

    def test_corrupt_late_member_rolls_back_earlier_output(self):
        bad = integrity(b"DATA")
        bad["hash"] = "0"*64
        self.src.write_bytes(fixture({"earlier": {"size": 0, "offset": "0"},
                                      "later": {"size": 4, "offset": "0", "integrity": bad}}))
        with self.assertRaises(ToolkitError):
            asar.extract_asar(self.src, self.dst)
        self.assertFalse(self.dst.exists())
        self.assertEqual(set(self.base.iterdir()), {self.src})

    def test_keyboard_interrupt_and_oserror_roll_back_stage(self):
        self.src.write_bytes(fixture())
        original = asar._copy_entry
        for failure in (KeyboardInterrupt, OSError):
            def partial(*args):
                original(*args)
                raise failure("synthetic")
            with patch.object(asar, "_copy_entry", side_effect=partial):
                with self.assertRaises(failure):
                    asar.extract_asar(self.src, self.dst)
            self.assertEqual(set(self.base.iterdir()), {self.src})

    def test_destination_appearing_at_commit_preserves_all_kinds(self):
        self.src.write_bytes(fixture())
        original = asar.atomic_publish
        for kind in ("empty-directory", "nonempty-directory", "file", "dangling-symlink"):
            output = self.base / kind
            def appear(stage, target):
                if kind.endswith("directory"):
                    target.mkdir()
                    if kind == "nonempty-directory":
                        (target / "KEEP").write_bytes(b"keep")
                elif kind == "file":
                    target.write_bytes(b"keep")
                else:
                    target.symlink_to("DO_NOT_FOLLOW")
                return original(stage, target)
            with patch.object(asar, "atomic_publish", side_effect=appear):
                with self.assertRaises((ToolkitError, OSError)):
                    asar.extract_asar(self.src, output)
            self.assertTrue(output.exists() or output.is_symlink())
            if kind == "file":
                self.assertEqual(output.read_bytes(), b"keep")
            elif kind == "nonempty-directory":
                self.assertEqual((output / "KEEP").read_bytes(), b"keep")
            elif kind == "dangling-symlink":
                self.assertEqual(os.readlink(output), "DO_NOT_FOLLOW")
            else:
                self.assertEqual(list(output.iterdir()), [])
            self.assertFalse(list(self.base.glob(".reverse-toolkit-asar-*")))

    def test_source_replacement_and_same_size_mutation_rollback(self):
        original = asar._copy_entry
        for replacement in (False, True):
            self.src.write_bytes(fixture())
            def mutate(*args):
                original(*args)
                if replacement:
                    substitute = self.base / "substitute"
                    substitute.write_bytes(self.src.read_bytes())
                    substitute.replace(self.src)
                else:
                    with self.src.open("r+b") as file:
                        file.seek(-1, 2)
                        file.write(b"!")
            with patch.object(asar, "_copy_entry", side_effect=mutate):
                with self.assertRaises(ToolkitError):
                    asar.extract_asar(self.src, self.dst)
            self.assertFalse(self.dst.exists())
            self.assertFalse(list(self.base.glob(".reverse-toolkit-asar-*")))

    def test_cli_reports_hash_and_rejects_exclusions_cleanly(self):
        self.src.write_bytes(fixture({"a": {"size": 4, "offset": "0"}, "external": {"size": 1, "unpacked": True}}))
        cmd = [sys.executable, "-B", str(ROOT / "reverse_toolkit.py")]
        inspect = subprocess.run(cmd + ["inspect-asar", "--input", str(self.src)], capture_output=True, text=True)
        self.assertEqual(inspect.returncode, 0, inspect.stderr)
        result = json.loads(inspect.stdout)
        self.assertEqual(result["archive_sha256"], hashlib.sha256(self.src.read_bytes()).hexdigest())
        self.assertFalse(result["extractable_within_subset"])
        extract = subprocess.run(cmd + ["unpack-asar", "--input", str(self.src), "--output", str(self.dst)],
                                 capture_output=True, text=True)
        self.assertEqual(extract.returncode, 2)
        self.assertEqual(extract.stdout, "")
        self.assertNotIn("Traceback", extract.stderr)
        self.assertFalse(self.dst.exists())

    def test_seeded_mutations_reject_or_produce_self_consistent_summary(self):
        rng = random.Random(207701)
        original = fixture()
        for _ in range(500):
            blob = bytearray(original)
            for _ in range(rng.randint(1, 3)):
                blob[rng.randrange(len(blob))] ^= rng.randrange(1, 256)
            try:
                meta = self.admit(blob)
            except ToolkitError:
                continue
            self.assertEqual(meta["archive_sha256"], hashlib.sha256(blob).hexdigest())
            self.assertGreaterEqual(meta["unreferenced_payload_bytes"], 0)
            self.assertGreaterEqual(meta["packed_bytes"], meta["unique_payload_bytes"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
