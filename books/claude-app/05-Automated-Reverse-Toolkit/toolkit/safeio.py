"""Bounded local reads and conservative ZIP extraction. Never execute input."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import binascii
import hashlib
import os
from pathlib import Path
import re
import shutil
import stat
import struct
import tempfile
import unicodedata
import zipfile
import zlib


class ToolkitError(ValueError):
    pass


@dataclass(frozen=True)
class Limits:
    max_files: int = 20000
    max_file_bytes: int = 64 * 1024 * 1024
    max_total_bytes: int = 512 * 1024 * 1024
    max_archive_bytes: int = 256 * 1024 * 1024
    max_central_bytes: int = 16 * 1024 * 1024
    max_ratio: int = 200
    max_depth: int = 64
    max_records: int = 200000

    def dictionary(self):
        return asdict(self)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def bounded_read(path, limit):
    """Reject final-component links, non-regular files and concurrent changes."""
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise ToolkitError(f"Not a regular file: {path.name}")
    if before.st_size > limit:
        raise ToolkitError(f"File exceeds byte bound: {path.name}")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    fd = os.open(path, flags)
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise ToolkitError("Input changed while opening")
        data = stream.read(limit + 1)
        after = os.fstat(stream.fileno())
    if len(data) > limit or len(data) != before.st_size or (after.st_size, after.st_mtime_ns) != (before.st_size, before.st_mtime_ns):
        raise ToolkitError("Input changed or exceeds byte bound")
    return data


def safe_member(raw, limits):
    if not raw or raw.startswith("/") or "\\" in raw or any(ord(c) < 32 or ord(c) == 127 for c in raw):
        raise ToolkitError("Unsafe ZIP path")
    parts = (raw[:-1] if raw.endswith("/") else raw).split("/")
    if len(parts) > limits.max_depth:
        raise ToolkitError("ZIP path exceeds depth bound")
    for part in parts:
        if part in ("", ".", "..") or len(part.encode("utf-8")) > 255 or any(c in part for c in '<>:"|?*') or part.endswith((".", " ")):
            raise ToolkitError("Unsafe or nonportable ZIP path")
        if re.match(r"^(?:CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\.|$)", part, re.I):
            raise ToolkitError("Reserved ZIP path")
    return "/".join(parts)


def check_extra(extra):
    """Reject ZIP64 even if its version/sentinel fields have been disguised."""
    offset = 0
    while offset < len(extra):
        if offset + 4 > len(extra):
            raise ToolkitError("Malformed ZIP extra field")
        kind, size = struct.unpack_from("<HH", extra, offset)
        offset += 4 + size
        if kind == 1 or offset > len(extra):
            raise ToolkitError("ZIP64 or malformed ZIP extra field")


def preflight_eocd(data, limits):
    # Reject ZIP64/multi-disk and bound the central directory before zipfile
    # allocates an object per entry. This intentionally supports a ZIP subset.
    start = max(0, len(data) - 65557)
    pos = data.rfind(b"PK\x05\x06", start)
    if pos < 0 or pos + 22 > len(data):
        raise ToolkitError("Not a supported ZIP archive")
    _, disk, cd_disk, on_disk, count, cd_size, cd_offset, comment = struct.unpack_from("<4s4H2LH", data, pos)
    if pos + 22 + comment != len(data) or disk or cd_disk or on_disk != count:
        raise ToolkitError("Multi-disk or malformed ZIP is unsupported")
    if count == 65535 or cd_size == 0xFFFFFFFF or cd_offset == 0xFFFFFFFF or b"PK\x06\x07" == data[max(0, pos-20):max(0, pos-16)]:
        raise ToolkitError("ZIP64 is unsupported")
    if count > limits.max_files or cd_size > limits.max_central_bytes or cd_offset + cd_size != pos:
        raise ToolkitError("ZIP central directory exceeds bounds or is malformed")
    # Count the actual records before ZipFile creates Python objects. The EOCD
    # count is untrusted and zipfile itself does not use it as an allocation cap.
    offset, actual = cd_offset, 0
    while offset < pos:
        if offset + 46 > pos or data[offset:offset+4] != b"PK\x01\x02":
            raise ToolkitError("Malformed ZIP central directory")
        name_size, extra_size, comment_size, disk_start = struct.unpack_from("<4H", data, offset+28)
        end = offset + 46 + name_size + extra_size + comment_size
        actual += 1
        if end > pos or actual > count or disk_start:
            raise ToolkitError("ZIP entry count, disk or central directory mismatch")
        check_extra(data[offset+46+name_size:offset+46+name_size+extra_size])
        offset = end
    if actual != count:
        raise ToolkitError("ZIP entry count mismatch")
    return count


def member_span(data, info):
    """Validate each local header, including directory entries never opened before."""
    start = info.header_offset
    if start < 0 or start + 30 > len(data):
        raise ToolkitError("Truncated ZIP local header")
    header = struct.unpack_from("<4s5H3I2H", data, start)
    signature, version, flags, method, _, _, crc, compressed, size, name_size, extra_size = header
    begin = start + 30 + name_size + extra_size
    if signature != b"PK\x03\x04" or version >= 45 or flags != info.flag_bits or method != info.compress_type:
        raise ToolkitError("Unsupported or inconsistent ZIP local header")
    if begin > len(data):
        raise ToolkitError("Truncated ZIP local header")
    name = data[start+30:start+30+name_size].decode("utf-8" if flags & 0x800 else "cp437")
    if name != info.orig_filename:
        raise ToolkitError("ZIP local and central names differ")
    check_extra(data[start+30+name_size:begin])
    if not flags & 8 and (crc, compressed, size) != (info.CRC, info.compress_size, info.file_size):
        raise ToolkitError("ZIP local and central sizes/CRC differ")
    return begin, begin + info.compress_size


def member_chunks(data, info, span):
    """Check the complete stream, not ZipExtFile's size-truncated output view."""
    begin, end = span
    total = crc = 0
    inflater = zlib.decompressobj(-15) if info.compress_type == zipfile.ZIP_DEFLATED else None
    if inflater is None and end - begin != info.file_size:
        raise ToolkitError("Stored ZIP size mismatch")
    try:
        for position in range(begin, end, 65536):
            pending = data[position:min(position+65536, end)]
            while pending:
                chunk = inflater.decompress(pending, 1024 * 1024) if inflater else pending
                pending = inflater.unconsumed_tail if inflater else b""
                total += len(chunk)
                if total > info.file_size:
                    raise ToolkitError("Actual ZIP member bytes exceed declared size")
                crc = binascii.crc32(chunk, crc)
                if chunk:
                    yield chunk
                if inflater and inflater.eof:
                    if inflater.unused_data or position + 65536 < end:
                        raise ToolkitError("Trailing data in ZIP compressed member")
                    break
        if inflater and not inflater.eof:
            raise ToolkitError("Truncated ZIP deflate stream")
    except zlib.error as exc:
        raise ToolkitError("Invalid ZIP deflate stream") from exc
    if total != info.file_size:
        raise ToolkitError("ZIP member size mismatch")
    if crc != info.CRC:
        raise zipfile.BadZipFile("ZIP member CRC mismatch")


def extract_zip(archive: Path, output: Path, limits=Limits()):
    import io
    data = bounded_read(archive, limits.max_archive_bytes)
    expected = preflight_eocd(data, limits)
    output = output.absolute()
    if output.exists() or output.is_symlink():
        raise ToolkitError("Extraction output must not exist")
    if not output.parent.is_dir():
        raise ToolkitError("Extraction output parent must already exist")
    # Resolve the existing parent, but never follow links inside an archive.
    output = output.parent.resolve() / output.name
    entries, kinds, spellings, total = [], {}, {}, 0
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if len(z.infolist()) != expected:
            raise ToolkitError("ZIP entry count mismatch")
        for info in z.infolist():
            name = safe_member(info.orig_filename, limits)
            key = unicodedata.normalize("NFC", name.casefold())
            if key in kinds:
                raise ToolkitError("Duplicate or case/Unicode-colliding ZIP path")
            mode = info.external_attr >> 16
            kind = stat.S_IFMT(mode)
            directory = info.is_dir()
            if kind not in (0, stat.S_IFDIR if directory else stat.S_IFREG):
                raise ToolkitError("ZIP links/special files are unsupported")
            if info.flag_bits & ~0x80E:
                raise ToolkitError("Encrypted or unsupported ZIP flags")
            if info.extract_version >= 45:
                raise ToolkitError("ZIP64 or higher-version ZIP entries are unsupported")
            if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                raise ToolkitError("Only stored/deflated ZIP entries are supported")
            if directory and info.file_size:
                raise ToolkitError("ZIP directory contains data")
            if info.file_size > limits.max_file_bytes or info.file_size > max(1, info.compress_size) * limits.max_ratio:
                raise ToolkitError("ZIP member exceeds size/compression-ratio bound")
            total += info.file_size
            if total > limits.max_total_bytes:
                raise ToolkitError("ZIP total expanded bytes exceed bound")
            kinds[key] = directory
            # Implicit parents can collide even when the full member names do
            # not, e.g. Dir/a and dir/b or two normalization forms of a parent.
            parts = name.split("/")
            for i in range(1, len(parts)+1):
                prefix = "/".join(parts[:i])
                normalized = unicodedata.normalize("NFC", prefix.casefold())
                if spellings.setdefault(normalized, prefix) != prefix:
                    raise ToolkitError("Case/Unicode-colliding ZIP parent path")
            entries.append((name, info, member_span(data, info)))
        for key in kinds:
            parts = key.split("/")
            if any(kinds.get("/".join(parts[:i])) is False for i in range(1, len(parts))):
                raise ToolkitError("ZIP file/directory collision")
        # Local headers and payloads cannot overlap other members or the
        # central directory. Sort independently of the archive's entry order.
        ordered = sorted(entries, key=lambda entry: entry[1].header_offset)
        central_start = struct.unpack_from("<I", data, data.rfind(b"PK\x05\x06")+16)[0]
        for i, (_, info, span) in enumerate(ordered):
            next_start = ordered[i+1][1].header_offset if i+1 < len(ordered) else central_start
            if span[1] > next_start or info.header_offset >= next_start:
                raise ToolkitError("Overlapping ZIP member data")
        temp = Path(tempfile.mkdtemp(prefix=".reverse-toolkit-", dir=output.parent))
        observed = 0
        try:
            for name, info, span in entries:
                dest = temp / name
                if info.is_dir():
                    for _ in member_chunks(data, info, span):
                        raise ToolkitError("ZIP directory contains data")
                    dest.mkdir(parents=True, exist_ok=True)
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                written = 0
                with dest.open("xb") as dst:
                    os.chmod(dest, 0o600)
                    for chunk in member_chunks(data, info, span):
                        written += len(chunk)
                        observed += len(chunk)
                        if written > limits.max_file_bytes or written > info.file_size or observed > limits.max_total_bytes:
                            raise ToolkitError("Actual extracted bytes exceed bound")
                        dst.write(chunk)
                if written != info.file_size:
                    raise ToolkitError("ZIP member size mismatch")
            if output.exists() or output.is_symlink():
                raise ToolkitError("Extraction output appeared during operation")
            temp.rename(output)
        except BaseException:
            shutil.rmtree(temp)
            raise
    return {"adapter": "bounded-zip-v1", "archive_sha256": digest(data), "entries": len(entries), "expanded_bytes": observed}
