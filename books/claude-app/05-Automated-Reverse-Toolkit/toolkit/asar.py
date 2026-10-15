"""Original inert ASAR subset reader. No target import or execution; explicit, exact sidecar opt-in only.

Canonical Electron Pickle framing only. Quiescent inputs and a trusted, stable
output parent are required. All archive-derived names and ranges are validated
before creating output. Atomic no-replace publication fails closed when the
host does not expose an appropriate primitive. See SUPPORT.md for exclusions.
"""
from __future__ import annotations

from contextlib import contextmanager, nullcontext
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import struct
import sys
import tempfile
import unicodedata

from .safeio import Limits, ToolkitError, safe_member
from .asar_sidecar import Sidecar

CHUNK = 64 * 1024
MAX_PATH_BYTES = 4096
MAX_LISTING_BYTES = 16 * 1024 * 1024
_HEX = re.compile(r"[0-9a-fA-F]{64}\Z")
_DECIMAL = re.compile(r"(?:0|[1-9][0-9]{0,19})\Z")


def _identity(s):
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size,
            s.st_mtime_ns, s.st_ctime_ns)


def _validate_limits(limits):
    for name in ("max_files", "max_file_bytes", "max_total_bytes",
                 "max_archive_bytes", "max_central_bytes", "max_depth", "max_records"):
        value = getattr(limits, name)
        if type(value) is not int or value <= 0:
            raise ToolkitError("ASAR limits must be positive integers")
    # Avoid Python parser recursion and excessive nesting even with custom limits.
    if limits.max_depth > 128:
        raise ToolkitError("ASAR depth limit cannot exceed 128")


@contextmanager
def _source(archive, limits):
    before = archive.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ToolkitError("ASAR input must be a regular non-link, single-link file")
    if before.st_size > limits.max_archive_bytes:
        raise ToolkitError("ASAR archive exceeds byte bound")
    fd = os.open(archive, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                 | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(fd, "rb") as stream:
        if _identity(os.fstat(stream.fileno())) != _identity(before):
            raise ToolkitError("ASAR input changed while opening")
        yield stream, before.st_size
        if (_identity(os.fstat(stream.fileno())) != _identity(before)
                or _identity(archive.lstat()) != _identity(before)):
            raise ToolkitError("ASAR input changed during reading")


def _read_exact(stream, amount):
    # Callers admit lengths first. Header <= max_central_bytes, payload <= CHUNK.
    data = stream.read(amount)
    if len(data) != amount:
        raise ToolkitError("Truncated ASAR data")
    return data


def _budget_json(raw, limits):
    """Bound structure before json.loads allocates lists/dictionaries/integers."""
    depth = tokens = 0
    string = escape = atom = False
    for byte in raw:
        if string:
            if escape:
                escape = False
            elif byte == 92:
                escape = True
            elif byte == 34:
                string = False
            continue
        if byte == 34:
            string, atom = True, False
            tokens += 1
        elif byte in (123, 91):
            depth += 1
            tokens += 1
            atom = False
            if depth > 2 * limits.max_depth + 8:
                raise ToolkitError("ASAR JSON nesting exceeds bound")
        elif byte in (125, 93):
            depth -= 1
            atom = False
            if depth < 0:
                raise ToolkitError("Malformed ASAR JSON structure")
        elif byte in b" \t\r\n,:":
            atom = False
        elif not atom:
            tokens += 1
            atom = True
        if tokens > limits.max_records:
            raise ToolkitError("ASAR JSON token count exceeds bound")
    if string or depth:
        raise ToolkitError("Unterminated ASAR JSON structure")


def _integer(raw):
    if len(raw) > 21:
        raise ToolkitError("ASAR integer exceeds decode bound")
    return int(raw)


def _noninteger(_):
    raise ToolkitError("ASAR floating/nonfinite numbers are unsupported")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ToolkitError("Duplicate ASAR JSON key")
        result[key] = value
    return result


def _header(stream, archive_bytes, limits):
    if archive_bytes < 16:
        raise ToolkitError("Truncated ASAR Pickle prefix")
    prefix = _read_exact(stream, 16)
    size_payload, header_bytes, payload_bytes, json_bytes = struct.unpack("<4I", prefix)
    if (size_payload != 4 or header_bytes < 8 or header_bytes % 4
            or payload_bytes != header_bytes - 4
            or header_bytes != 8 + ((json_bytes + 3) // 4) * 4
            or json_bytes > 0x7fffffff or 8 + header_bytes > archive_bytes):
        raise ToolkitError("Invalid ASAR Pickle lengths")
    if header_bytes > limits.max_central_bytes:
        raise ToolkitError("ASAR header exceeds byte bound")
    raw = _read_exact(stream, json_bytes)
    if any(_read_exact(stream, header_bytes - 8 - json_bytes)):
        raise ToolkitError("Noncanonical ASAR Pickle padding")
    _budget_json(raw, limits)
    try:
        root = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                          parse_int=_integer, parse_float=_noninteger,
                          parse_constant=_noninteger)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ToolkitError("Invalid ASAR JSON") from exc
    if type(root) is not dict or set(root) != {"files"} or type(root["files"]) is not dict:
        raise ToolkitError("ASAR root must contain only a files object")
    return root, 8 + header_bytes, hashlib.sha256(raw).hexdigest()


def _integrity(value, size, limits):
    if type(value) is not dict or set(value) != {"algorithm", "hash", "blockSize", "blocks"}:
        raise ToolkitError("Unsupported ASAR integrity metadata")
    if value["algorithm"] != "SHA256" or type(value["hash"]) is not str or not _HEX.fullmatch(value["hash"]):
        raise ToolkitError("ASAR integrity must use SHA256 with a hex digest")
    block = value["blockSize"]
    if type(block) is not int or not 0 < block <= limits.max_file_bytes:
        raise ToolkitError("ASAR integrity block size exceeds bound")
    hashes = value["blocks"]
    if (type(hashes) is not list or len(hashes) != max(1, (size + block - 1) // block)
            or any(type(h) is not str or not _HEX.fullmatch(h) for h in hashes)):
        raise ToolkitError("ASAR integrity block count/hash mismatch")
    return value


def _listing(root, base, archive_bytes, limits):
    entries, exclusions, canonical = [], [], set()
    pending = [("", iter(root["files"].items()), False, 0)]
    total = listing_bytes = 0
    while pending:
        parent, children, inherited_unpacked, depth = pending[-1]
        child = next(children, None)
        if child is None:
            pending.pop()
            continue
        name, node = child
        if name in ("", ".", "..") or "/" in name or "\\" in name:
            raise ToolkitError("ASAR entry name must be one path component")
        path = parent + "/" + name if parent else name
        if depth >= limits.max_depth:
            raise ToolkitError("ASAR path exceeds depth bound")
        try:
            safe_member(path, limits)
            path_bytes = len(path.encode("utf-8"))
        except (ToolkitError, UnicodeError) as exc:
            raise ToolkitError("Unsafe or nonportable ASAR path") from exc
        listing_bytes += path_bytes + 256
        if path_bytes > MAX_PATH_BYTES or listing_bytes > MAX_LISTING_BYTES:
            raise ToolkitError("ASAR expanded path representation exceeds bound")
        key = unicodedata.normalize("NFC", path.casefold())
        if key in canonical:
            raise ToolkitError("Duplicate or case/Unicode-colliding ASAR path")
        canonical.add(key)
        if len(canonical) > limits.max_files:
            raise ToolkitError("ASAR entry count exceeds bound")
        if type(node) is not dict:
            raise ToolkitError("ASAR entry must be an object")
        for flag in ("unpacked", "executable"):
            if flag in node and type(node[flag]) is not bool:
                raise ToolkitError("ASAR flags must be boolean")
        unpacked = inherited_unpacked or node.get("unpacked", False)
        if "files" in node:
            if set(node) - {"files", "unpacked"} or type(node["files"]) is not dict:
                raise ToolkitError("Ambiguous/unsupported ASAR directory")
            entry = {"path": path, "kind": "directory", "size": 0, "unpacked": unpacked}
            pending.append((path, iter(node["files"].items()), unpacked, depth + 1))
            if node.get("unpacked", False) and not inherited_unpacked:
                exclusions.append({"path": path, "reason": "unpacked-directory"})
        elif "link" in node:
            if set(node) - {"link", "unpacked"} or type(node["link"]) is not str or not node["link"]:
                raise ToolkitError("Ambiguous/unsupported ASAR link")
            entry = {"path": path, "kind": "link", "size": 0, "unpacked": unpacked}
            exclusions.append({"path": path, "reason": "link-not-followed"})
        else:
            if set(node) - {"size", "offset", "integrity", "executable", "unpacked"}:
                raise ToolkitError("Unknown ASAR file metadata; special/hard links unsupported")
            size = node.get("size")
            if type(size) is not int or not 0 <= size <= limits.max_file_bytes:
                raise ToolkitError("ASAR member size exceeds bound or is invalid")
            integrity = _integrity(node["integrity"], size, limits) if "integrity" in node else None
            entry = {"path": path, "kind": "file", "size": size,
                     "unpacked": unpacked, "integrity": integrity}
            if unpacked:
                if "offset" in node:
                    raise ToolkitError("Unpacked ASAR entry also contains a packed offset")
                exclusions.append({"path": path, "reason": "unpacked-sidecar-not-read"})
            else:
                raw_offset = node.get("offset")
                if type(raw_offset) is not str or not _DECIMAL.fullmatch(raw_offset):
                    raise ToolkitError("ASAR offset must be a bounded canonical decimal string")
                offset = int(raw_offset)
                if offset > 2**64 - 1 or offset > archive_bytes - base or size > archive_bytes - base - offset:
                    raise ToolkitError("ASAR member range leaves archive")
                entry["start"] = base + offset
                total += size
                if total > limits.max_total_bytes:
                    raise ToolkitError("ASAR total packed bytes exceed bound")
        entries.append(entry)
    end = base
    spans = {}
    unique_bytes = shared_ranges = 0
    for entry in sorted((e for e in entries if "start" in e), key=lambda e: e["start"]):
        span = (entry["start"], entry["start"] + entry["size"])
        integrity = entry["integrity"]
        identity = None if integrity is None else (
            integrity["algorithm"], integrity["hash"].lower(), integrity["blockSize"],
            tuple(h.lower() for h in integrity["blocks"]))
        if span in spans:
            if spans[span] != identity:
                raise ToolkitError("Shared ASAR range has inconsistent integrity metadata")
            # Exact aliases are copied independently. Logical bytes have already
            # been charged once per destination above; no hard links are made.
            shared_ranges += 1
            continue
        if entry["size"] and entry["start"] < end:
            raise ToolkitError("Partially overlapping ASAR ranges are invalid")
        spans[span] = identity
        unique_bytes += entry["size"]
        end = max(end, span[1])
    return entries, exclusions, total, unique_bytes, shared_ranges


def _archive_hash(stream, size):
    stream.seek(0)
    remaining, hashed = size, hashlib.sha256()
    while remaining:
        chunk = _read_exact(stream, min(CHUNK, remaining))
        hashed.update(chunk)
        remaining -= len(chunk)
    return hashed.hexdigest()


def _admit(stream, size, limits):
    root, base, header_hash = _header(stream, size, limits)
    entries, exclusions, total, unique_bytes, shared_ranges = _listing(root, base, size, limits)
    metadata = {"adapter": "bounded-asar-v1", "archive_sha256": _archive_hash(stream, size),
                "header_json_sha256": header_hash, "archive_bytes": size,
                "entries": len(entries), "packed_files": sum("start" in e for e in entries),
                "packed_bytes": total, "unique_payload_bytes": unique_bytes,
                "shared_range_aliases": shared_ranges,
                "unreferenced_payload_bytes": size - base - unique_bytes,
                "exclusions": exclusions, "extractable_within_subset": not exclusions,
                "complete_application": False, "publisher_authenticity_verified": False,
                "declared_member_integrity_verified": False}
    return entries, metadata


def inspect_asar(archive: Path, limits=Limits()):
    """Read-only compatibility summary; exclusions are explicit, never followed.

    This is not a snapshot of application functionality and cannot be diffed as
    one. Hashing the container does not authenticate a publisher. Member hashes
    are checked on extraction, not by this metadata-only operation.
    """
    _validate_limits(limits)
    with _source(Path(archive), limits) as (stream, size):
        _, result = _admit(stream, size, limits)
    return result


def atomic_publish(source: Path, destination: Path):
    """Atomically rename a completed directory without replacing any pathname.

    ctypes calls only the operating system's libc, never a target binary.
    A check-then-rename fallback is deliberately forbidden on POSIX.
    """
    if sys.platform == "win32":
        os.rename(source, destination)  # Windows refuses existing destinations.
        return
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        method = libc.renameat2
        method.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        method.restype = ctypes.c_int
        result = method(-100, os.fsencode(source), -100, os.fsencode(destination), 1)  # RENAME_NOREPLACE
    elif sys.platform == "darwin" and hasattr(libc, "renamex_np"):
        method = libc.renamex_np
        method.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        method.restype = ctypes.c_int
        result = method(os.fsencode(source), os.fsencode(destination), 4)  # RENAME_EXCL
    else:
        raise ToolkitError("Host has no supported atomic no-replace directory rename")
    if result:
        error = ctypes.get_errno()
        if error in (errno.EEXIST, errno.ENOTEMPTY):
            raise ToolkitError("Extraction output appeared; nothing was replaced")
        if error in (errno.ENOSYS, errno.EINVAL, getattr(errno, "ENOTSUP", errno.EINVAL)):
            raise ToolkitError("Filesystem lacks atomic no-replace directory rename")
        raise OSError(error, os.strerror(error), str(destination))


def _copy_entry(stream, entry, destination):
    stream.seek(entry.get("start", 0))
    remaining = entry["size"]
    whole = hashlib.sha256()
    block_hash = hashlib.sha256()
    block_bytes = block_index = 0
    integrity = entry["integrity"]
    block_size = integrity["blockSize"] if integrity else CHUNK
    with destination.open("xb") as target:
        os.chmod(destination, 0o600)  # Never preserve executable bits.
        while remaining:
            chunk = _read_exact(stream, min(CHUNK, remaining, block_size - block_bytes))
            target.write(chunk)
            whole.update(chunk)
            block_hash.update(chunk)
            remaining -= len(chunk)
            block_bytes += len(chunk)
            if block_bytes == block_size or not remaining:
                if integrity and block_hash.hexdigest() != integrity["blocks"][block_index].lower():
                    raise ToolkitError("ASAR member block integrity mismatch")
                block_index += 1
                block_hash, block_bytes = hashlib.sha256(), 0
    if integrity:
        if entry["size"] == 0 and hashlib.sha256(b"").hexdigest() != integrity["blocks"][0].lower():
            raise ToolkitError("ASAR empty-member block integrity mismatch")
        if whole.hexdigest() != integrity["hash"].lower():
            raise ToolkitError("ASAR member integrity mismatch")
    return whole.hexdigest()


def extract_asar(archive: Path, output: Path, limits=Limits(), *, unpacked_dir=None):
    """Strict default; explicit companion opts into exact declared scope only."""
    _validate_limits(limits)
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise ToolkitError("Extraction output must not exist")
    if not output.parent.is_dir():
        raise ToolkitError("Extraction output parent must already exist")
    output = output.parent.resolve() / output.name
    temporary = None
    try:
        with _source(Path(archive), limits) as (stream, size):
            entries, metadata = _admit(stream, size, limits)
            if metadata["exclusions"] and unpacked_dir is None:
                reasons = sorted({e["reason"] for e in metadata["exclusions"]})
                raise ToolkitError("ASAR exclusions prevent complete extraction: " + ", ".join(reasons)
                                   + ". Use inspect-asar for explicit coverage; no sidecars were read")
            if any(e["kind"] == "link" for e in entries):
                raise ToolkitError("ASAR link exclusions prevent complete extraction even with an explicit sidecar")
            companion = (Sidecar(unpacked_dir, entries, metadata["packed_bytes"], limits, output)
                         if unpacked_dir is not None else nullcontext(None))
            with companion as sidecar:
                temporary = Path(tempfile.mkdtemp(prefix=".reverse-toolkit-asar-", dir=output.parent))
                for entry in entries:
                    destination = temporary / entry["path"]
                    if entry["kind"] == "directory":
                        destination.mkdir(mode=0o700, parents=True, exist_ok=True)
                    else:
                        destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                        if entry["unpacked"]:
                            with sidecar.source(entry) as source:
                                sidecar.observed_hashes[entry["path"]] = _copy_entry(source, entry, destination)
                        else:
                            _copy_entry(stream, entry, destination)
                if sidecar is not None:
                    metadata.update({"sidecar": sidecar.metadata(),
                                     "extraction_scope": "asar-declared-packed-and-unpacked-v1",
                                     "container_exclusions": metadata["exclusions"],
                                     "exclusions": [], "extractable_within_subset": True})
        # Source identity is rechecked by _source BEFORE any publication.
        atomic_publish(temporary, output)
        temporary = None
        metadata.update({"expanded_bytes": metadata["packed_bytes"] + metadata.get("sidecar", {}).get("bytes", 0),
                         "declared_member_integrity_verified": True,
                         "files_with_declared_integrity": sum(e.get("integrity") is not None for e in entries)})
        return metadata
    finally:
        if temporary is not None:
            shutil.rmtree(temporary)
