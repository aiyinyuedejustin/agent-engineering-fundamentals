"""Original strict DEB envelope reader. Inert data only; no tarfile extraction."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
import lzma
import os
from pathlib import Path
import re
import sys
import unicodedata

# Install alongside reverse_toolkit.py and toolkit/. No research-tree path
# assumptions and no target-controlled import paths.
sys.dont_write_bytecode = True
from toolkit.safeio import Limits, ToolkitError, safe_member
from toolkit.asar import _source, _identity, _archive_hash

MIB = 1024**2
CHUNK = 65536
PROFILE = 'deb-xz-gnu-asar-projection/v1'

@dataclass(frozen=True)
class DebEnvelopeLimits:
    archive: int = 256*MIB
    stream: int = 768*MIB
    control: int = 16*MIB
    opaque_file: int = 256*MIB
    decoder: int = 128*MIB
    raw_headers: int = 20000
    entries: int = 20000
    representation: int = 16*MIB
    ratio: int = 200
    selected: int = 512*MIB

DEFAULTS = DebEnvelopeLimits()

def require(condition, message):
    if not condition:
        raise ToolkitError(message)

def exact(stream, n):
    data = stream.read(n)
    require(len(data) == n, 'Truncated envelope')
    return data

def number(raw, base=8):
    # Reject embedded terminators rather than repairing numeric spellings.
    pattern = rb' *[0-7]+[\0 ]*' if base == 8 else rb'[0-9]+ *'
    require(bool(re.fullmatch(pattern, raw)), 'Unsupported numeric field')
    text = raw.strip(b' \0')
    return int(text, base)

def cstring(raw):
    head, sep, tail = raw.partition(b'\0')
    require(not any(tail), 'Nonzero TAR string terminator tail')
    try:
        return head.decode('utf-8')
    except UnicodeError as e:
        raise ToolkitError('Invalid UTF-8 TAR field') from e

def path_name(raw, kind):
    if raw in ('.', './'):
        require(kind == '5', 'Root must be a directory')
        return ''
    name = raw[2:] if raw.startswith('./') else raw
    if kind == '5' and name.endswith('/'):
        name = name[:-1]
    require(not name.endswith('/'), 'Unexpected trailing slash')
    require(len(name.encode('utf-8')) <= 4096, 'Path byte budget')
    return safe_member(name, Limits())

@dataclass(frozen=True)
class Selection:
    asar: str
    companion: str | None = None
    def __post_init__(self):
        for value in (self.asar, self.companion):
            if value is not None:
                require(path_name(value, '0') == value, 'Selector must be canonical relative path')
        if self.companion:
            require(not self.contains(self.asar, self.companion) and not self.contains(self.companion, self.asar), 'Overlapping selectors')
    @staticmethod
    def contains(path, root):
        return path == root or path.startswith(root + '/')
    def selected(self, path):
        return path == self.asar or bool(self.companion and self.contains(path, self.companion))
    def ancestor(self, path):
        return any(value and value.startswith(path + '/') for value in (self.asar, self.companion))

class Budget:
    def __init__(self, limits):
        self.limits = limits
        self.stream = self.raw = self.entries = self.representation = self.selected = 0
    def charge(self, field, amount, limit):
        value = getattr(self, field) + amount
        require(value <= limit, field + ' budget exceeded')
        setattr(self, field, value)

class Namespace:
    def __init__(self, budget):
        self.nodes = {}
        self.budget = budget
    def add(self, path, kind):
        parts = path.split('/') if path else ['']
        for i in range(1, len(parts)+1):
            prefix = '/'.join(parts[:i])
            key = unicodedata.normalize('NFC', prefix.casefold())
            final = i == len(parts)
            old = self.nodes.get(key)
            if old:
                require(old[0] == prefix, 'Case/Unicode path collision')
                require(old[1] == '5', 'Non-directory ancestor or duplicate')
                if final:
                    require(kind == '5' and not old[2], 'Duplicate or conflicting logical path')
                    self.nodes[key] = (prefix, kind, True)
            else:
                self.budget.charge('representation', len(prefix.encode())+256, self.budget.limits.representation)
                self.nodes[key] = (prefix, kind if final else '5', final)

class XZ:
    def __init__(self, source, member, budget):
        self.source = source
        self.left = member['bytes']
        self.size = self.left
        self.control = member['name'] == 'control.tar.xz'
        self.budget = budget
        source.seek(member['offset'])
        self.decoder = lzma.LZMADecompressor(format=lzma.FORMAT_XZ, memlimit=budget.limits.decoder)
        self.buffer = b''
        self.total = self.position = 0
        self.done = False
        self.hashed = hashlib.sha256()
    def read(self, n):
        require(0 <= n <= CHUNK, 'Internal read bound')
        while len(self.buffer) < n and not self.done:
            if self.decoder.eof:
                require(not self.decoder.unused_data and not self.left, 'XZ trailing/concatenated bytes')
                require(self.decoder.check == lzma.CHECK_CRC64, 'XZ requires CRC64')
                self.done = True
                break
            if self.decoder.needs_input:
                require(self.left > 0, 'Truncated XZ stream')
                data = exact(self.source, min(CHUNK, self.left))
                self.left -= len(data)
                self.hashed.update(data)
            else:
                data = b''
            try:
                chunk = self.decoder.decompress(data, max_length=CHUNK)
            except lzma.LZMAError as e:
                raise ToolkitError('Invalid XZ stream or decoder memory budget') from e
            self.total += len(chunk)
            self.budget.charge('stream', len(chunk), self.budget.limits.stream)
            require(self.total <= self.size*self.budget.limits.ratio, 'XZ ratio budget')
            require(not self.control or self.total <= self.budget.limits.control, 'Control stream budget')
            self.buffer += chunk
        data, self.buffer = self.buffer[:n], self.buffer[n:]
        self.position += len(data)
        return data


def ar_members(source, size):
    source.seek(0)
    require(exact(source, 8) == b'!<arch>\n', 'Unsupported AR magic')
    members = []
    for expected in ('debian-binary', 'control.tar.xz', 'data.tar.xz'):
        header_offset = source.tell()
        header = exact(source, 60)
        require(header[58:] == b'`\n', 'Malformed AR header')
        raw = header[:16].rstrip(b' ')
        if raw.endswith(b'/'): raw = raw[:-1]
        require(raw == expected.encode(), 'AR member name/order outside profile')
        for a,b,base in ((16,28,10),(28,34,10),(34,40,10),(40,48,8)):
            require(b'\0' not in header[a:b], 'AR numeric NUL unsupported')
            number(header[a:b], base)
        length = number(header[48:58], 10)
        offset = source.tell()
        require(offset+length+(length & 1) <= size, 'AR member outside container')
        if expected == 'debian-binary':
            require(length == 4 and exact(source, 4) == b'2.0\n', 'Unsupported DEB version')
        source.seek(offset+length)
        if length & 1:
            require(exact(source, 1) == b'\n', 'Invalid AR padding')
        members.append(dict(name=expected, header_offset=header_offset, offset=offset, bytes=length))
    require(source.tell() == size, 'Extra AR member/trailing data')
    return members


def mkdir_private(path):
    if not path.exists():
        mkdir_private(path.parent)
        path.mkdir(mode=0o700)


def scan_tar(source, member, budget, selection, destination=None, expected=None):
    xz = XZ(source, member, budget)
    namespace = Namespace(budget)
    records, pending = [], None
    is_data = member['name'] == 'data.tar.xz'
    while True:
        offset = xz.position
        header = exact(xz, 512)
        if not any(header):
            require(not any(exact(xz, 512)), 'TAR requires consecutive double zero EOF')
            require(pending is None, 'Dangling GNU L')
            break
        budget.charge('raw', 1, budget.limits.raw_headers)
        require(number(header[148:156]) == sum(header[:148])+256+sum(header[156:]), 'TAR checksum mismatch')
        require(header[257:265] == b'ustar  \0', 'Only GNU basic TAR supported')
        # GNU atime/ctime/offset/sparse/extended area is not silently interpreted.
        require(not any(header[345:]), 'GNU extended header fields unsupported')
        for a,b in ((100,108),(108,116),(116,124),(124,136),(136,148)):
            number(header[a:b])
        for a,b in ((329,337),(337,345)):
            require(not any(header[a:b]) or number(header[a:b]) == 0, 'TAR device fields unsupported')
        cstring(header[265:297]); cstring(header[297:329])
        raw_name, link = cstring(header[:100]), cstring(header[157:257])
        size, kind = number(header[124:136]), chr(header[156])
        require(kind in ('0','5','2','L'), 'Unsupported TAR entry type')
        require(kind == '0' or pending is None, 'GNU L must precede one regular entry')
        require(kind == '2' or not link, 'Unexpected TAR linkname')
        if kind == 'L':
            require(raw_name == '././@LongLink' and 1 <= size <= 4097, 'Invalid GNU L header/size')
            budget.charge('representation', size+256, budget.limits.representation)
            body = exact(xz, size)
            require(body[-1:] == b'\0' and b'\0' not in body[:-1], 'Invalid GNU L terminator')
            try: pending = body[:-1].decode('utf-8')
            except UnicodeError as e: raise ToolkitError('Invalid GNU L UTF-8') from e
            require(not any(exact(xz, (-size)%512)), 'Nonzero TAR padding')
            continue
        if pending is not None:
            raw_name, pending = pending, None
        name = path_name(raw_name, kind)
        if not is_data:
            require((name == '' and kind == '5') or (kind == '0' and '/' not in name),
                    'Control supports only root and top-level regular files')
        require(kind == '0' or size == 0, 'Non-file with payload')
        require(size <= budget.limits.opaque_file, 'Opaque file budget')
        namespace.add(name, kind)
        budget.charge('entries', 1, budget.limits.entries)
        selected = is_data and selection.selected(name)
        if kind == '2':
            require(bool(link) and not (is_data and (selected or selection.ancestor(name))), 'Link in selected scope/ancestor')
        if selected:
            require(kind in ('0','5'), 'Selected nonregular entry')
            require(size <= Limits().max_file_bytes, 'Selected file budget')
            budget.charge('selected', size, budget.limits.selected)
        record = dict(path=name, kind=kind, bytes=size, header_offset=offset,
                      link=link if kind == '2' else None,
                      scope='selected' if selected else 'outside-selected-scope')
        index = len(records)
        if expected is not None:
            require(index < len(expected), 'Second pass extra entry')
            require(all(expected[index].get(k) == v for k,v in record.items()), 'Second pass metadata changed')
        target = None
        if destination is not None and selected:
            dest = destination / ('app.asar' if name == selection.asar else 'companion')
            if name != selection.asar and name != selection.companion:
                dest = destination / 'companion' / name[len(selection.companion)+1:]
            if kind == '5': mkdir_private(dest)
            else:
                mkdir_private(dest.parent)
                target = os.fdopen(os.open(dest, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600), 'wb')
        hashed = hashlib.sha256()
        try:
            left = size
            while left:
                chunk = exact(xz, min(CHUNK,left)); left -= len(chunk)
                hashed.update(chunk)
                if target: target.write(chunk)
        finally:
            if target: target.close()
        require(not any(exact(xz, (-size)%512)), 'Nonzero TAR padding')
        record['sha256'] = hashed.hexdigest() if kind == '0' else None
        if expected is not None: require(record == expected[index], 'Second pass payload changed')
        budget.charge('representation', len(json.dumps(record, ensure_ascii=True).encode())+256, budget.limits.representation)
        records.append(record)
    while True:
        tail = xz.read(CHUNK)
        if not tail: break
        require(not any(tail), 'Nonzero TAR trailing bytes')
    require(xz.position % 512 == 0, 'Partial TAR trailing block')
    if expected is not None: require(len(records) == len(expected), 'Second pass missing entry')
    paths = {r['path']:r for r in records}
    if is_data:
        require(paths.get(selection.asar, {}).get('kind') == '0', 'Selected ASAR missing/not regular')
        if selection.companion:
            require(paths.get(selection.companion, {}).get('kind') == '5', 'Companion needs explicit directory')
    else:
        require(paths.get('control', {}).get('kind') == '0', 'Control file missing/not regular')
    return dict(records=records, stream_bytes=xz.total, compressed_sha256=xz.hashed.hexdigest(), xz_check='CRC64')


def scan(source, size, selection, destination=None, expected=None, limits=DEFAULTS):
    require(size <= limits.archive, 'DEB archive budget')
    members = ar_members(source, size)
    budget = Budget(limits)
    for i, member in enumerate(members[1:], 1):
        prior = expected['members'][i]['tar']['records'] if expected else None
        member['tar'] = scan_tar(source, member, budget, selection, destination, prior)
    result = dict(profile=PROFILE, source_bytes=size, source_sha256=_archive_hash(source,size),
                  selection=asdict(selection), limits=asdict(limits), members=members,
                  selected_bytes=budget.selected, stream_bytes=budget.stream,
                  raw_headers=budget.raw, logical_entries=budget.entries,
                  outer_envelope_inventory_complete=True, outer_compressed_streams_verified=True,
                  selected_asar_declared_scope_complete=False, complete_package=False,
                  complete_application=False, publisher_authenticity_verified=False)
    if expected is not None: require(result == expected, 'Second pass envelope changed')
    return result


def inspect_deb(path, selection):
    require(hasattr(os, 'O_NOFOLLOW'), 'Host lacks no-follow primitive')
    with _source(Path(path), Limits()) as (source,size):
        return scan(source,size,selection)
