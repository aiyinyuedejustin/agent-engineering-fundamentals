"""Original explicit ASAR sidecar contract; filesystem bytes are never executed.

POSIX no-follow, descriptor-relative traversal only. Quiescent trusted ancestors
remain required; this is not a hostile concurrent-process sandbox.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat
import unicodedata

from .safeio import ToolkitError, safe_member

MAX_PATH_BYTES = 4096
MAX_LISTING_BYTES = 16 * 1024 * 1024


def _identity(s):
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size,
            s.st_mtime_ns, s.st_ctime_ns)


class SidecarError(ToolkitError):
    """Machine-readable coverage accompanies a failed, never partial, operation."""
    def __init__(self, code, coverage=None, path=None):
        self.code = code
        self.coverage = {"complete_asar_declared_scope": False, "inventory_complete": False,
                         "missing": None, "extra": None, "invalid": None,
                         **(coverage or {})}
        if path is not None:
            self.coverage["failure_path"] = path
        super().__init__("ASAR sidecar " + code + ": " + json.dumps(
            self.coverage, ensure_ascii=True, sort_keys=True, separators=(",", ":")))


def _require_primitives():
    if (os.name != "posix" or not getattr(os, "O_NOFOLLOW", 0)
            or not getattr(os, "O_DIRECTORY", 0) or not getattr(os, "O_NONBLOCK", 0)
            or os.open not in os.supports_dir_fd or os.stat not in os.supports_dir_fd
            or os.stat not in os.supports_follow_symlinks or os.scandir not in os.supports_fd):
        raise SidecarError("unsupported-host-no-follow-primitives")


def _flags(directory=False):
    return (os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
            | (os.O_DIRECTORY if directory else 0))


def _directory(fd, expected, path):
    observed = os.fstat(fd)
    if not stat.S_ISDIR(observed.st_mode) or _identity(observed) != expected:
        raise SidecarError("source-changed", path=path)


class Sidecar:
    """Bind an explicit root to exactly the archive's unpacked declaration."""
    def __init__(self, root, entries, packed_bytes, limits, output):
        self.root = Path(root).absolute()
        self.limits = limits
        self.output = output
        self.fd = None
        self.records = {}
        self.observed_hashes = {}
        self.expected = {}
        self.files = {e["path"]: e for e in entries if e["kind"] == "file" and e["unpacked"]}
        for entry in entries:
            if entry["unpacked"] and entry["kind"] in ("file", "directory"):
                self.expected[entry["path"]] = entry["kind"]
                parts = entry["path"].split("/")
                for n in range(1, len(parts)):
                    self.expected["/".join(parts[:n])] = "directory"
        if not self.expected:
            raise SidecarError("unexpected-companion-no-unpacked-declarations")
        self.unpacked_bytes = sum(e["size"] for e in self.files.values())
        if packed_bytes + self.unpacked_bytes > limits.max_total_bytes:
            raise SidecarError("combined-packed-unpacked-byte-bound")

    def __enter__(self):
        _require_primitives()
        phase = "root-io-failure"
        try:
            before = self.root.lstat()
            if not stat.S_ISDIR(before.st_mode):
                raise SidecarError("root-not-real-directory", path=".")
            self.root_identity = _identity(before)
            self.fd = os.open(self.root, _flags(directory=True))
            _directory(self.fd, self.root_identity, ".")
            # resolve is used only for output containment after no-follow root
            # admission; it does not authorize symlink traversal of descendants.
            resolved = self.root.resolve()
            if self.output == resolved or resolved in self.output.parents:
                raise SidecarError("output-inside-companion")
            phase = "inventory-io-failure"
            self.records = self._scan()
            coverage = {"missing": sorted(set(self.expected) - set(self.records)),
                        "extra": sorted(set(self.records) - set(self.expected)), "invalid": []}
            for path, record in self.records.items():
                expected = self.expected.get(path)
                if record["kind"] == "invalid" or (expected and record["kind"] != expected):
                    coverage["invalid"].append({"path": path, "reason": "type-or-link-mismatch"})
                elif path in self.files and record["size"] != self.files[path]["size"]:
                    coverage["invalid"].append({"path": path, "reason": "declared-size-mismatch"})
            coverage["invalid"].sort(key=lambda row: row["path"])
            if any(coverage.values()):
                raise SidecarError("coverage-mismatch", {**coverage, "inventory_complete": True})
            return self
        except OSError as exc:
            self.close()
            raise SidecarError(phase, path=".") from exc
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def __exit__(self, kind, value, traceback):
        try:
            if kind is None:
                self.verify_unchanged()
        finally:
            self.close()

    def _scan(self):
        """Bounded metadata inventory; never open regular-file contents here."""
        records, canonical = {}, set()
        listing_bytes = 0

        def walk(fd, parent, expected):
            nonlocal listing_bytes
            _directory(fd, expected, parent or ".")
            with os.scandir(fd) as children:
                for child in children:
                    path = parent + "/" + child.name if parent else child.name
                    try:
                        safe_member(path, self.limits)
                        path_bytes = len(path.encode("utf-8"))
                    except (ToolkitError, UnicodeError) as exc:
                        raise SidecarError("unsafe-path", path=path) from exc
                    listing_bytes += path_bytes + 256
                    if path_bytes > MAX_PATH_BYTES or listing_bytes > MAX_LISTING_BYTES:
                        raise SidecarError("listing-byte-bound", path=path)
                    key = unicodedata.normalize("NFC", path.casefold())
                    if key in canonical:
                        raise SidecarError("case-unicode-collision", path=path)
                    canonical.add(key)
                    if len(canonical) > self.limits.max_files:
                        raise SidecarError("entry-count-bound")
                    before = os.stat(child.name, dir_fd=fd, follow_symlinks=False)
                    if stat.S_ISDIR(before.st_mode):
                        kind = "directory"
                    elif stat.S_ISREG(before.st_mode) and before.st_nlink == 1:
                        kind = "file"
                    else:
                        kind = "invalid"
                    records[path] = {"kind": kind, "size": before.st_size,
                                     "identity": _identity(before)}
                    if kind == "directory":
                        nested = os.open(child.name, _flags(directory=True), dir_fd=fd)
                        try:
                            walk(nested, path, _identity(before))
                        finally:
                            os.close(nested)
            _directory(fd, expected, parent or ".")

        walk(self.fd, "", self.root_identity)
        return records

    @contextmanager
    def _parent(self, path):
        opened = []
        fd = self.fd
        try:
            _directory(fd, self.root_identity, ".")
            parts = path.split("/")
            for index, name in enumerate(parts[:-1], 1):
                fd = os.open(name, _flags(directory=True), dir_fd=fd)
                opened.append(fd)
                relative = "/".join(parts[:index])
                _directory(fd, self.records[relative]["identity"], relative)
            yield fd, parts[-1]
        finally:
            for descriptor in reversed(opened):
                os.close(descriptor)

    @contextmanager
    def source(self, entry):
        path = entry["path"]
        expected = self.records[path]["identity"]
        try:
            with self._parent(path) as (parent, name):
                before = os.stat(name, dir_fd=parent, follow_symlinks=False)
                if _identity(before) != expected:
                    raise SidecarError("source-changed", path=path)
                fd = os.open(name, _flags(), dir_fd=parent)
                with os.fdopen(fd, "rb") as stream:
                    if _identity(os.fstat(stream.fileno())) != expected:
                        raise SidecarError("source-changed-while-opening", path=path)
                    yield stream
                    if (stream.read(1) or _identity(os.fstat(stream.fileno())) != expected
                            or _identity(os.stat(name, dir_fd=parent, follow_symlinks=False)) != expected):
                        raise SidecarError("source-changed-during-reading", path=path)
        except SidecarError:
            raise
        except ToolkitError as exc:
            code = "declared-integrity-failure" if "integrity mismatch" in str(exc) else "read-failure"
            raise SidecarError(code, path=path) from exc
        except OSError as exc:
            raise SidecarError("read-failure", path=path) from exc

    def verify_unchanged(self):
        try:
            if _identity(self.root.lstat()) != self.root_identity:
                raise SidecarError("root-changed", path=".")
            if self._scan() != self.records:
                raise SidecarError("source-changed-before-publication")
        except OSError as exc:
            raise SidecarError("source-changed-before-publication") from exc

    def metadata(self):
        members = [{"path": path, "size": self.files[path]["size"],
                    "sha256": self.observed_hashes[path],
                    "declared_integrity": self.files[path]["integrity"] is not None}
                   for path in sorted(self.files)]
        listing = json.dumps({"members": members, "directories": sorted(
            path for path, kind in self.expected.items() if kind == "directory")},
            ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return {"contract": "explicit-exact-asar-sidecar/v1", "files": len(members),
                "bytes": self.unpacked_bytes, "members": members,
                "manifest_sha256": hashlib.sha256(listing).hexdigest(),
                "complete_asar_declared_scope": True, "inventory_complete": True,
                "missing": [], "extra": [], "invalid": [],
                "files_with_declared_integrity": sum(row["declared_integrity"] for row in members),
                "publisher_authenticity_verified": False}
