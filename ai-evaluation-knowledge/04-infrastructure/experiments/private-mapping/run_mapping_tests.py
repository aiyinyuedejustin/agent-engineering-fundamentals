#!/usr/bin/env python3
"""Real local mmap experiments, not a Firecracker or VM reproduction.

Uses only the Python standard library and files created in a temporary directory.
The backing-file mutation observation is explicitly scoped to the measured Linux
host: POSIX does not promise portable MAP_PRIVATE visibility after file writes.
"""
import datetime
import json
import mmap
import os
import platform
import sys
import tempfile
import unittest


class PrivateMappingTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="eval-mmap-contract-")
        self.addCleanup(self.directory.cleanup)
        self.path = os.path.join(self.directory.name, "baseline.bin")
        self.page_size = mmap.PAGESIZE
        self.original = b"A" * self.page_size + b"B" * self.page_size
        with open(self.path, "wb") as file:
            file.write(self.original)
        self.file = open(self.path, "r+b", buffering=0)
        self.addCleanup(self.file.close)

    def clone(self):
        result = mmap.mmap(self.file.fileno(), 0, access=mmap.ACCESS_COPY)
        self.addCleanup(result.close)
        return result

    def test_private_write_is_not_shared_or_persisted(self):
        first, second = self.clone(), self.clone()
        first[0:5] = b"TRIAL"
        self.assertEqual(first[:5], b"TRIAL")
        self.assertEqual(second[:5], b"AAAAA")
        self.file.seek(0)
        self.assertEqual(self.file.read(), self.original)

    @unittest.skipUnless(platform.system() == "Linux", "Linux-specific observation")
    def test_backing_write_affects_unprivatized_page_on_this_host(self):
        clone = self.clone()
        # Dirty only page zero. Page one remains backed by the shared file.
        clone[0:1] = b"X"
        os.pwrite(self.file.fileno(), b"Y", 0)
        os.pwrite(self.file.fileno(), b"Z", self.page_size)
        os.fsync(self.file.fileno())
        self.assertEqual(clone[0:1], b"X")
        self.assertEqual(clone[self.page_size:self.page_size + 1], b"Z")
        self.assertEqual(os.pread(self.file.fileno(), 1, 0), b"Y")

    def test_new_clone_requires_accessible_backing_path(self):
        first = self.clone()
        # Real Linux mappings can outlive unlink. This does NOT mean a VM
        # snapshot service may ignore its documented backing-file lifetime.
        os.unlink(self.path)
        self.assertEqual(first[:5], b"AAAAA")
        with self.assertRaises(FileNotFoundError):
            open(self.path, "rb")


if __name__ == "__main__":
    print(json.dumps({
        "started_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "python": platform.python_version(),
        "system": platform.system(),
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "page_size": mmap.PAGESIZE,
        "scope": "actual host mmap calls; no VM, network, dependencies or privilege changes",
    }, sort_keys=True), flush=True)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PrivateMappingTests)
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(suite)
    sys.exit(not result.wasSuccessful())
