"""Original, synthetic-only acceptance tests for the strict DEB projection.

Run beside the installed toolkit: PYTHONDONTWRITEBYTECODE=1 python -m unittest -v test_projection
For staging, explicitly set PYTHONPATH to the reviewed toolkit root.
All archive bytes are made here; no real packages, tar extraction, shell scripts,
installer, or target source are executed. Filesystem fixtures stay beside this
file and are removed by TemporaryDirectory. These are envelope tests, not a
claim that the inner ASAR rules or transactional CLI have been revalidated.
"""
from __future__ import annotations

import copy
from dataclasses import replace
import gzip
import hashlib
import io
import lzma
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
import deb_projection as dp

HERE = Path(__file__).resolve().parent
ASAR = 'opt/example/resources/app.asar'
COMPANION = ASAR + '.unpacked'
SELECT = dp.Selection(ASAR, COMPANION)
ASAR_BYTES = b'original synthetic archive envelope payload\x00\x01'
CONTROL_BYTES = b'Package: synthetic-envelope-test\nVersion: 1\n'
ZERO = bytes(512)


def octal(value, width):
    out = format(value, 'o').encode('ascii')
    if len(out) >= width:
        raise ValueError('test number does not fit')
    return out.rjust(width - 1, b'0') + b'\0'


def checksum(header):
    h = bytearray(header)
    h[148:156] = b' ' * 8
    h[148:156] = format(sum(h), '06o').encode('ascii') + b'\0 '
    return bytes(h)


def header(name, body=b'', kind='0', link=b'', size=None, mode=0o644):
    """Emit basic GNU header explicitly; never use tarfile's default dialect."""
    if isinstance(name, str):
        name = name.encode('utf-8')
    if isinstance(link, str):
        link = link.encode('utf-8')
    if len(name) > 100 or len(link) > 100:
        raise ValueError('use GNU L for a long fixture path')
    h = bytearray(512)
    h[:len(name)] = name
    h[100:108] = octal(mode, 8)
    h[108:116] = octal(0, 8)
    h[116:124] = octal(0, 8)
    h[124:136] = octal(len(body) if size is None else size, 12)
    h[136:148] = octal(0, 12)
    h[156] = ord(kind)
    h[157:157 + len(link)] = link
    h[257:265] = b'ustar  \0'
    h[329:337] = octal(0, 8)
    h[337:345] = octal(0, 8)
    return checksum(h)


def entry(name, body=b'', kind='0', link=b'', *, size=None, mode=0o644):
    return header(name, body, kind, link, size, mode) + body + bytes((-len(body)) % 512)


def long_entry(name, body=b'', *, short='placeholder', mode=0o644):
    encoded = name.encode('utf-8') if isinstance(name, str) else name
    return entry('././@LongLink', encoded + b'\0', 'L') + entry(short, body, mode=mode)


def mutate_header(raw, start, end, value):
    h = bytearray(raw[:512])
    if len(value) != end - start:
        raise ValueError('test mutation has wrong width')
    h[start:end] = value
    return checksum(h) + raw[512:]


def tar(*entries, eof=2, tail=b''):
    return b''.join(entries) + ZERO * eof + tail


def xz(raw, *, check=lzma.CHECK_CRC64, **kwargs):
    return lzma.compress(raw, format=lzma.FORMAT_XZ, check=check, **kwargs)


def ar_member(name, body, *, declared=None, pad=b'\n', trailer=b'`\n'):
    if isinstance(name, str):
        name = name.encode('ascii')
    if len(name) > 16:
        raise ValueError('test AR name too long')
    h = (name.ljust(16, b' ') + b'0'.ljust(12) + b'0'.ljust(6)
         + b'0'.ljust(6) + b'100644'.ljust(8)
         + str(len(body) if declared is None else declared).encode().ljust(10)
         + trailer)
    return h + body + (pad if len(body) & 1 else b'')


def envelope(control=None, data=None, *, version=b'2.0\n', slash=False):
    suffix = '/' if slash else ''
    if control is None:
        control = xz(tar(entry('control', CONTROL_BYTES)))
    if data is None:
        data = xz(tar(*basic_data()))
    return (b'!<arch>\n' + ar_member('debian-binary' + suffix, version)
            + ar_member('control.tar.xz' + suffix, control)
            + ar_member('data.tar.xz' + suffix, data))


def basic_data():
    return [entry(ASAR, ASAR_BYTES), entry(COMPANION, kind='5'),
            entry(COMPANION + '/empty.txt'),
            entry(COMPANION + '/code.txt', b'original inert fixture\n')]


def scan(raw, *, selection=SELECT, limits=None, destination=None, expected=None):
    args = dict(destination=destination, expected=expected)
    if limits is not None:
        args['limits'] = limits
    return dp.scan(io.BytesIO(raw), len(raw), selection, **args)


def data_package(*extra, data_entries=None, tail=b'', eof=2):
    entries = basic_data() if data_entries is None else data_entries
    return envelope(data=xz(tar(*entries, *extra, tail=tail, eof=eof)))


class EnvelopeCase(unittest.TestCase):
    def assertRejected(self, raw, *, contains=None, **kwargs):
        before = hashlib.sha256(raw).digest()
        with self.assertRaises(dp.ToolkitError) as caught:
            scan(raw, **kwargs)
        self.assertEqual(hashlib.sha256(raw).digest(), before)
        if contains:
            self.assertIn(contains, str(caught.exception))
        return str(caught.exception)

    def assertBudgetBoundary(self, raw, field, used):
        """Admit usage at limit and limit-1; reject usage at limit+1."""
        for limit in (used + 1, used):
            with self.subTest(field=field, allowed_limit=limit):
                scan(raw, limits=replace(dp.DEFAULTS, **{field: limit}))
        with self.subTest(field=field, allowed_limit=used - 1):
            self.assertRejected(raw, limits=replace(dp.DEFAULTS, **{field: used - 1}))


class PositiveEnvelopeTests(EnvelopeCase):
    def test_minimal_exact_three_member_envelope(self):
        raw = envelope()
        result = scan(raw)
        self.assertEqual(result['source_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual([m['name'] for m in result['members']],
                         ['debian-binary', 'control.tar.xz', 'data.tar.xz'])
        self.assertEqual(result['raw_headers'], 5)
        self.assertEqual(result['logical_entries'], 5)
        self.assertTrue(result['outer_envelope_inventory_complete'])
        self.assertTrue(result['outer_compressed_streams_verified'])
        for key in ('selected_asar_declared_scope_complete', 'complete_package',
                    'complete_application', 'publisher_authenticity_verified'):
            self.assertFalse(result[key])

    def test_single_trailing_slash_ar_names(self):
        self.assertEqual(scan(envelope(slash=True))['logical_entries'], 5)

    def test_single_leading_dot_slash_names(self):
        rows = [entry('./' + ASAR, ASAR_BYTES), entry('./' + COMPANION + '/', kind='5')]
        records = scan(data_package(data_entries=rows))['members'][2]['tar']['records']
        self.assertEqual([r['path'] for r in records], [ASAR, COMPANION])

    def test_explicit_root_directory_and_zero_tail_are_allowed(self):
        raw = data_package(entry('./', kind='5'), tail=ZERO * 3)
        result = scan(raw)
        self.assertIn('', [r['path'] for r in result['members'][2]['tar']['records']])
        self.assertEqual(result['members'][2]['tar']['stream_bytes'] % 512, 0)

    def test_control_allows_one_root_and_multiple_inert_top_level_files(self):
        control = tar(entry('./', kind='5'), entry('./control', CONTROL_BYTES),
                      entry('postinst', b'original inert script-like bytes', mode=0o755),
                      entry('md5sums', b'original inert metadata'))
        result = scan(envelope(control=xz(control)))
        self.assertEqual([r['path'] for r in result['members'][1]['tar']['records']],
                         ['', 'control', 'postinst', 'md5sums'])

    def test_nonselected_symlink_is_recorded_without_following(self):
        raw = data_package(entry('usr/bin/unrelated', kind='2', link='../../private/sentinel'))
        record = scan(raw)['members'][2]['tar']['records'][-1]
        self.assertEqual(record['kind'], '2')
        self.assertEqual(record['link'], '../../private/sentinel')
        self.assertEqual(record['scope'], 'outside-selected-scope')

    def test_child_before_one_explicit_parent_directory(self):
        raw = data_package(entry('outside/child', b'x'), entry('outside', kind='5'))
        self.assertEqual(scan(raw)['logical_entries'], 7)

    def test_gnu_longname_affects_exactly_one_regular_entry(self):
        name = 'long/' + 'q' * 150
        raw = data_package(long_entry(name, b'first'), entry('second', b'second'))
        result = scan(raw)
        records = result['members'][2]['tar']['records']
        self.assertEqual([r['path'] for r in records[-2:]], [name, 'second'])
        self.assertEqual(result['raw_headers'] - result['logical_entries'], 1)

    def test_prefix_neighbor_is_outside_selected_scope(self):
        neighbor = COMPANION + '-extra/file'
        raw = data_package(entry(neighbor, b'leave outside'))
        record = scan(raw)['members'][2]['tar']['records'][-1]
        self.assertEqual(record['path'], neighbor)
        self.assertEqual(record['scope'], 'outside-selected-scope')

    def test_no_companion_is_valid_when_not_selected(self):
        selection = dp.Selection(ASAR)
        raw = data_package(data_entries=[entry(ASAR, ASAR_BYTES)])
        self.assertEqual(scan(raw, selection=selection)['selection'],
                         {'asar': ASAR, 'companion': None})

    def test_projection_writes_only_regular_private_selected_files(self):
        raw = data_package(entry('outside/script', b'#!/bin/sh\nexit 1\n', mode=0o4755),
                           entry('outside/link', kind='2', link='/never-open'))
        expected = scan(raw)
        with tempfile.TemporaryDirectory(prefix='.test-projection-', dir=HERE) as temporary:
            root = Path(temporary)
            result = scan(raw, destination=root, expected=expected)
            self.assertEqual(result, expected)
            self.assertEqual((root / 'app.asar').read_bytes(), ASAR_BYTES)
            self.assertEqual((root / 'companion/empty.txt').read_bytes(), b'')
            self.assertFalse((root / 'outside').exists())
            for p in root.rglob('*'):
                self.assertFalse(p.is_symlink())
                mode = stat.S_IMODE(p.stat().st_mode)
                self.assertEqual(mode, 0o700 if p.is_dir() else 0o600)


class ARTests(EnvelopeCase):
    def test_wrong_or_truncated_ar_magic(self):
        raw = envelope()
        for magic in (b'!<thin>\n', b'!<arch>X', b'PK\x03\x04xxxx', b'0.939000'):
            with self.subTest(magic=magic):
                self.assertRejected(magic + raw[8:])
        self.assertRejected(raw[:7])

    def test_header_truncated_at_every_field_boundary(self):
        for size in (8, 24, 36, 42, 48, 56, 66, 67):
            with self.subTest(size=size):
                self.assertRejected(envelope()[:size])

    def test_invalid_ar_header_terminator(self):
        raw = envelope()
        for trailer in (b'\x00\n', b'`\x00', b'\n`'):
            with self.subTest(trailer=trailer):
                self.assertRejected(raw[:66] + trailer + raw[68:])

    def test_ar_decimal_size_is_strict_ascii(self):
        raw = envelope()
        for value in (b'-4', b'+4', b'4e0', b'', b'4\x00', b'\xff4', b'4 0', b' 4'):
            with self.subTest(value=value):
                self.assertRejected(raw[:56] + value.ljust(10, b' ') + raw[66:])

    def test_ar_metadata_numeric_fields_are_validated(self):
        raw = envelope()
        for start, stop, bad in ((24, 36, b'-1'), (36, 42, b'1\x00'),
                                 (42, 48, b'+0'), (48, 56, b'888')):
            with self.subTest(start=start):
                self.assertRejected(raw[:start] + bad.ljust(stop - start) + raw[stop:])

    def test_ar_declared_payload_cannot_cross_container(self):
        raw = envelope()
        self.assertRejected(raw[:56] + b'9999999999' + raw[66:])
        for count in (1, 2, 17, 60):
            with self.subTest(short_by=count):
                self.assertRejected(raw[:-count])

    def test_ar_odd_payload_padding_is_required_and_newline_only(self):
        # Direct AR parser isolates pad validation from the deliberately invalid XZ bytes.
        for pad in (b'', b'\0', b'X'):
            raw = (b'!<arch>\n' + ar_member('debian-binary', b'2.0\n')
                   + ar_member('control.tar.xz', b'x', pad=pad)
                   + ar_member('data.tar.xz', b'xx'))
            with self.subTest(pad=pad), self.assertRaises(dp.ToolkitError):
                dp.ar_members(io.BytesIO(raw), len(raw))
        raw = (b'!<arch>\n' + ar_member('debian-binary', b'2.0\n')
               + ar_member('control.tar.xz', b'x') + ar_member('data.tar.xz', b'xx'))
        self.assertEqual(len(dp.ar_members(io.BytesIO(raw), len(raw))), 3)

    def test_ar_names_do_not_accept_extensions_or_case_repair(self):
        raw = envelope()
        names = (b'debian-binary//', b'/debian-binary', b'Debian-binary', b'debian binary',
                 b'#1/20', b'/', b'//', b'/123', b'/SYM64/', b'debian-binary\0')
        for name in names:
            with self.subTest(name=name):
                self.assertRejected(raw[:8] + name.ljust(16) + raw[24:])

    def test_member_order_and_required_roles_are_exact(self):
        c, d = xz(tar(entry('control', CONTROL_BYTES))), xz(tar(*basic_data()))
        version = ar_member('debian-binary', b'2.0\n')
        control, data = ar_member('control.tar.xz', c), ar_member('data.tar.xz', d)
        for members in ((version, data, control), (version, control),
                        (control, version, data), (version, control, control),
                        (version, data, data)):
            with self.subTest(lengths=[len(m) for m in members]):
                self.assertRejected(b'!<arch>\n' + b''.join(members))

    def test_other_compression_suffixes_are_not_in_profile(self):
        raw = envelope()
        members = dp.ar_members(io.BytesIO(raw), len(raw))
        start = members[1]['header_offset']
        for name in (b'control.tar.gz', b'control.tar.zst', b'control.tar'):
            with self.subTest(name=name):
                self.assertRejected(raw[:start] + name.ljust(16) + raw[start + 16:])

    def test_extra_ar_members_second_archive_and_trailing_bytes(self):
        raw = envelope()
        for tail in (b'X', b'\0', ar_member('_gpgorigin', b'signature'), raw):
            with self.subTest(tail_size=len(tail)):
                self.assertRejected(raw + tail)

    def test_version_payload_is_exact(self):
        for version in (b'2.1\n', b'3.0\n', b'2.0', b'2.0\0', b'2.0\n\n', b'2.0\nextra'):
            with self.subTest(version=version):
                self.assertRejected(envelope(version=version))


class XZTests(EnvelopeCase):
    def test_wrong_compression_format(self):
        data = tar(*basic_data())
        for compressed in (gzip.compress(data), lzma.compress(data, format=lzma.FORMAT_ALONE), data):
            with self.subTest(prefix=compressed[:8]):
                self.assertRejected(envelope(data=compressed))

    def test_crc64_is_the_only_allowed_check(self):
        for check in (lzma.CHECK_NONE, lzma.CHECK_CRC32, lzma.CHECK_SHA256):
            if lzma.is_check_supported(check):
                with self.subTest(check=check):
                    self.assertRejected(envelope(data=xz(tar(*basic_data()), check=check)),
                                        contains='CRC64')

    def test_corrupt_xz_footer_after_complete_tar_is_rejected(self):
        good = xz(tar(*basic_data()))
        for index in (-1, -4, -8, -12, -20):
            corrupt = bytearray(good)
            corrupt[index] ^= 0x80
            with self.subTest(index=index):
                self.assertRejected(envelope(data=bytes(corrupt)))

    def test_xz_truncation_at_header_body_and_footer(self):
        good = xz(tar(*basic_data()))
        for stop in (0, 1, 6, 12, len(good) // 2, len(good) - 12, len(good) - 1):
            with self.subTest(stop=stop):
                self.assertRejected(envelope(data=good[:stop]))

    def test_single_xz_stream_has_exact_eof(self):
        good = xz(tar(*basic_data()))
        for tail in (b'\0', b'\0' * 4, b'junk', good, xz(b'')):
            with self.subTest(tail_size=len(tail)):
                self.assertRejected(envelope(data=good + tail), contains='trailing')

    def test_member_boundary_prevents_decoder_reading_next_ar_bytes(self):
        # A valid control XZ is declared short; decoder must not consume the following AR header.
        good = xz(tar(entry('control', CONTROL_BYTES)))
        raw = (b'!<arch>\n' + ar_member('debian-binary', b'2.0\n')
               + ar_member('control.tar.xz', good[:-4])
               + ar_member('data.tar.xz', xz(tar(*basic_data()))))
        self.assertRejected(raw)

    def test_large_dictionary_small_output_hits_decoder_memory_budget(self):
        compressed = xz(tar(*basic_data()), filters=[{'id': lzma.FILTER_LZMA2, 'dict_size': 32 * 1024**2}])
        self.assertRejected(envelope(data=compressed),
                            limits=replace(dp.DEFAULTS, decoder=2 * 1024**2), contains='memory')

    def test_multiple_bounded_decoder_drains_keep_all_payload(self):
        body = b''.join(hashlib.sha256(str(i).encode()).digest() for i in range(10000))
        raw = data_package(entry(COMPANION + '/blocks.bin', body))
        expected = scan(raw)
        with mock.patch.object(dp, 'CHUNK', 1024):
            actual = scan(raw)
        self.assertEqual(actual, expected)
        self.assertEqual(actual['members'][2]['tar']['records'][-1]['sha256'], hashlib.sha256(body).hexdigest())

    def test_exact_64k_xz_boundary_does_not_consume_following_stream(self):
        payload = b''.join(hashlib.sha256(str(i).encode()).digest() for i in range(2100))[:65470]
        compressed = xz(payload, preset=0)
        self.assertEqual(len(compressed), 65536, 'fixture must end exactly on the input chunk boundary')
        following = xz(b'a second stream outside the AR member slice')
        source = io.BytesIO(compressed + following)
        decoder = dp.XZ(source, {'name': 'data.tar.xz', 'offset': 0, 'bytes': len(compressed)},
                        dp.Budget(dp.DEFAULTS))
        self.assertEqual(decoder.read(dp.CHUNK), payload)
        self.assertEqual(decoder.read(dp.CHUNK), b'')
        self.assertEqual(source.tell(), len(compressed))
        self.assertEqual(source.read(), following)

    def test_decoder_output_calls_are_bounded_before_stream_budget_failure(self):
        original_decoder = lzma.LZMADecompressor
        requested = []

        class ObservedDecoder:
            def __init__(self, *args, **kwargs):
                self.real = original_decoder(*args, **kwargs)
            def __getattr__(self, name):
                return getattr(self.real, name)
            def decompress(self, data, max_length=-1):
                requested.append(max_length)
                if not (0 < max_length <= dp.CHUNK):
                    raise AssertionError('unbounded decoder allocation')
                return self.real.decompress(data, max_length=max_length)

        raw = data_package(entry('outside-large', b'z' * 150000))
        with mock.patch.object(dp.lzma, 'LZMADecompressor', ObservedDecoder):
            self.assertRejected(raw, limits=replace(dp.DEFAULTS, stream=8192), contains='stream')
        self.assertTrue(requested)
        self.assertLessEqual(max(requested), 65536)

    def test_total_stream_budget_counts_headers_padding_and_tail(self):
        raw = data_package(tail=ZERO * 2)
        used = scan(raw)['stream_bytes']
        self.assertGreater(used, scan(raw)['selected_bytes'])
        self.assertBudgetBoundary(raw, 'stream', used)

    def test_control_stream_has_an_independent_budget(self):
        raw = envelope()
        used = scan(raw)['members'][1]['tar']['stream_bytes']
        self.assertBudgetBoundary(raw, 'control', used)

    def test_ratio_uses_full_compressed_member_bytes(self):
        raw = envelope()
        result = scan(raw)
        needed = max((m['tar']['stream_bytes'] + m['bytes'] - 1) // m['bytes']
                     for m in result['members'][1:])
        scan(raw, limits=replace(dp.DEFAULTS, ratio=needed))
        scan(raw, limits=replace(dp.DEFAULTS, ratio=needed + 1))
        self.assertRejected(raw, limits=replace(dp.DEFAULTS, ratio=needed - 1), contains='ratio')


class TARTests(EnvelopeCase):
    def test_non_gnu_dialects_are_rejected(self):
        original = entry('outside', b'data')
        for magic in (b'ustar\00000', b'ustar\0 \0', b'notatar!', bytes(8)):
            with self.subTest(magic=magic):
                self.assertRejected(data_package(mutate_header(original, 257, 265, magic)))

    def test_nonzero_gnu_reserved_extension_area_is_rejected(self):
        original = entry('outside', b'data')
        for position in (345, 369, 386, 482, 495, 511):
            with self.subTest(position=position):
                self.assertRejected(data_package(mutate_header(original, position, position + 1, b'1')))

    def test_unsigned_checksum_is_mandatory(self):
        original = entry('outside', b'data')
        corrupt = bytearray(original)
        corrupt[1] ^= 1
        self.assertRejected(data_package(bytes(corrupt)), contains='checksum')
        high = bytearray(entry('caf\u00e9', b'data'))
        high[148:156] = b' ' * 8
        signed = sum(byte if byte < 128 else byte - 256 for byte in high[:512])
        high[148:156] = format(signed, '06o').encode() + b'\0 '
        self.assertRejected(data_package(bytes(high)), contains='checksum')

    def test_tar_size_requires_unsigned_octal_encoding(self):
        original = entry('outside')
        for spelling in (b'-1', b'+1', b'8', b'0x1', b'1 1', b'1\x001', b''):
            with self.subTest(spelling=spelling):
                field = spelling.ljust(12, b'\0')
                self.assertRejected(data_package(mutate_header(original, 124, 136, field)))
        self.assertRejected(data_package(mutate_header(original, 124, 136, b'\x80' + bytes(11))))

    def test_padding_must_be_all_zero(self):
        original = bytearray(entry('outside', b'x'))
        original[513] = 1
        self.assertRejected(data_package(bytes(original)), contains='padding')

    def test_payload_declared_size_cannot_move_header_boundary(self):
        # Claimed 513 B consumes the first byte of the subsequent TAR header.
        malformed = entry('outside', b'x' * 512, size=513) + entry('after', b'y')
        self.assertRejected(data_package(malformed))

    def test_directory_and_symlink_cannot_have_payload(self):
        for kind, link in (('5', ''), ('2', 'target')):
            with self.subTest(kind=kind):
                self.assertRejected(data_package(entry('outside', b'x', kind, link)))

    def test_non_symlink_cannot_have_linkname(self):
        for kind in ('0', '5', 'L'):
            with self.subTest(kind=kind):
                self.assertRejected(data_package(entry('outside', kind=kind, link='target')))

    def test_hardlinks_devices_fifo_contiguous_sparse_unknown_are_rejected(self):
        for kind in ('1', '3', '4', '6', '7', 'S', 'Z', '\0', 'K'):
            with self.subTest(kind=repr(kind)):
                self.assertRejected(data_package(entry('outside', kind=kind)))

    def test_pax_headers_are_rejected_before_applying_overrides(self):
        payloads = (b'25 path=../../escape.txt\n', b'18 GNU.sparse.size=9\n', b'14 unknown=x\n')
        for kind in ('x', 'g', 'X'):
            for payload in payloads:
                with self.subTest(kind=kind, payload=payload):
                    self.assertRejected(data_package(entry('pax', payload, kind)))

    def test_gnu_longname_header_and_size_are_bounded(self):
        self.assertRejected(data_package(entry('not-longlink', b'x\0', 'L'), entry('x')))
        for size in (0, 4098):
            with self.subTest(size=size):
                self.assertRejected(data_package(entry('././@LongLink', b'a' * size, 'L'), entry('x')))

    def test_gnu_longname_has_exactly_one_final_nul_and_valid_utf8(self):
        for body in (b'no-nul', b'x\0\0', b'x\0hidden\0', b'\xff\0'):
            with self.subTest(body=body):
                self.assertRejected(data_package(entry('././@LongLink', body, 'L'), entry('x')))

    def test_gnu_longname_successor_must_be_regular(self):
        prefix = entry('././@LongLink', b'effective-name\0', 'L')
        for kind in ('L', 'K', 'x', '5', '2'):
            with self.subTest(kind=kind):
                self.assertRejected(data_package(prefix, entry('next', kind=kind)))
        self.assertRejected(data_package(prefix), contains='Dangling')

    def test_gnu_longname_effective_name_controls_collisions_and_safety(self):
        for name in (ASAR, '../escape', 'safe/../escape', '/absolute'):
            with self.subTest(name=name):
                self.assertRejected(data_package(long_entry(name, b'data', short='safe-short-name')))

    def test_two_zero_eof_blocks_are_required(self):
        for eof in (0, 1):
            with self.subTest(eof=eof):
                self.assertRejected(data_package(eof=eof))
        self.assertRejected(data_package(eof=1, tail=entry('after-zero', b'x') + ZERO * 2))

    def test_after_eof_only_complete_zero_blocks_are_allowed(self):
        for tail in (b'\0', bytes(511), ZERO + b'\0', b'X' + bytes(511), tar(entry('hidden', b'x'))):
            with self.subTest(tail_size=len(tail)):
                self.assertRejected(data_package(tail=tail))

    def test_string_terminator_tail_is_not_silently_discarded(self):
        original = entry('outside')
        self.assertRejected(data_package(mutate_header(original, 0, 100, b'safe\0hidden'.ljust(100, b'\0'))))
        self.assertRejected(data_package(mutate_header(original, 265, 297, b'user\0hidden'.ljust(32, b'\0'))))

    def test_invalid_utf8_name_and_linkname_are_rejected(self):
        self.assertRejected(data_package(entry(b'bad\xff')))
        self.assertRejected(data_package(entry('outside', kind='2', link=b'bad\xff')))

    def test_nonzero_device_fields_are_rejected_for_regular_file(self):
        original = entry('outside')
        for a, b in ((329, 337), (337, 345)):
            with self.subTest(field=(a, b)):
                self.assertRejected(data_package(mutate_header(original, a, b, octal(1, 8))))


class PathsAndScopeTests(EnvelopeCase):
    def test_absolute_windows_unc_backslash_and_ads_paths_are_rejected(self):
        for name in ('/absolute', '//server/share', 'C:/drive', 'C:relative', r'\\server\share',
                     r'a\b', 'file:stream'):
            with self.subTest(name=name):
                self.assertRejected(data_package(entry(name)))

    def test_dot_segments_empty_segments_and_multiple_prefixes_are_rejected(self):
        for name in ('../x', 'a/../x', 'a/./x', '././x', 'a//x', '', './', 'a/'):
            with self.subTest(name=name):
                self.assertRejected(data_package(entry(name)))

    def test_duplicate_root_and_root_as_file_are_rejected(self):
        self.assertRejected(data_package(entry('.', kind='5'), entry('./', kind='5')))
        self.assertRejected(data_package(entry('.')))

    def test_duplicate_effective_names_and_directory_spellings_are_rejected(self):
        for entries in ((entry('dup'), entry('./dup')),
                        (entry('dup/', kind='5'), entry('dup', kind='5')),
                        (entry('dup'), entry('dup'))):
            with self.subTest(entries=len(entries)):
                self.assertRejected(data_package(*entries))

    def test_casefold_collisions_include_implicit_parents(self):
        for names in (('A/x', 'a/y'), ('Stra\u00dfe/x', 'STRASSE/y'), ('A', 'a')):
            with self.subTest(names=names):
                self.assertRejected(data_package(*(entry(name) for name in names)))

    def test_unicode_nfc_collisions_include_implicit_parents(self):
        for names in (('caf\u00e9/x', 'cafe\u0301/y'), ('caf\u00e9', 'cafe\u0301')):
            with self.subTest(names=names):
                self.assertRejected(data_package(*(entry(name) for name in names)))

    def test_nondirectory_ancestor_conflicts_are_order_independent(self):
        for kind, link in (('0', ''), ('2', 'somewhere')):
            first, second = entry('outside', kind=kind, link=link), entry('outside/child')
            for entries in ((first, second), (second, first)):
                with self.subTest(kind=kind, reversed=entries[0] == second):
                    self.assertRejected(data_package(*entries))

    def test_same_path_different_types_never_replace(self):
        entries = [entry('outside'), entry('outside', kind='5'), entry('outside', kind='2', link='target')]
        for i in range(3):
            for j in range(3):
                if i != j:
                    with self.subTest(first=i, second=j):
                        self.assertRejected(data_package(entries[i], entries[j]))

    def test_second_explicit_confirmation_of_implicit_parent_is_rejected(self):
        self.assertRejected(data_package(entry('outside/child'), entry('outside', kind='5'),
                                         entry('outside', kind='5')))

    def test_reserved_names_controls_and_nonportable_components_are_rejected(self):
        for name in ('CON', 'LPT\u00b9', 'aux.txt', 'tail.', 'tail ', 'a\nb', 'a\x7fb',
                     'a?b', 'a<b', 'a"b', 'a|b'):
            with self.subTest(name=name):
                self.assertRejected(data_package(entry(name)))

    def test_component_utf8_bytes_not_character_count(self):
        for length in (254, 255):
            scan(data_package(long_entry('p/' + 'x' * length)))
        self.assertRejected(data_package(long_entry('p/' + 'x' * 256)))
        scan(data_package(long_entry('p/' + '\u00e9' * 127)))
        self.assertRejected(data_package(long_entry('p/' + '\u00e9' * 128)))

    def test_path_depth_bound(self):
        for depth in (63, 64):
            scan(data_package(long_entry('/'.join(['a'] * depth))))
        self.assertRejected(data_package(long_entry('/'.join(['a'] * 65))))

    def test_total_path_byte_bound(self):
        # 16 components of 255 bytes + separators = 4095; extend the final component safely.
        name4095 = '/'.join(['x' * 255] * 16)
        self.assertEqual(len(name4095.encode()), 4095)
        scan(data_package(long_entry(name4095)))
        name4096 = '/'.join(['x' * 240] * 17)  # 4080 + 16
        self.assertEqual(len(name4096.encode()), 4096)
        scan(data_package(long_entry(name4096)))
        with self.assertRaises(dp.ToolkitError):
            dp.path_name(name4096 + 'y', '0')

    def test_selectors_must_already_be_canonical_and_disjoint(self):
        for path in ('./app.asar', '/app.asar', 'a/../app.asar', 'app.asar/'):
            with self.subTest(path=path), self.assertRaises(dp.ToolkitError):
                dp.Selection(path)
        for asar, companion in (('a', 'a'), ('a/b', 'a'), ('a', 'a/b')):
            with self.subTest(asar=asar, companion=companion), self.assertRaises(dp.ToolkitError):
                dp.Selection(asar, companion)

    def test_selected_asar_must_exist_and_be_regular(self):
        for rows in ([entry(COMPANION, kind='5')],
                     [entry(ASAR, kind='5'), entry(COMPANION, kind='5')],
                     [entry(ASAR, kind='2', link='elsewhere'), entry(COMPANION, kind='5')]):
            with self.subTest(first=rows[0][:50]):
                self.assertRejected(data_package(data_entries=rows))

    def test_selected_companion_must_be_explicit_directory(self):
        for rows in ([entry(ASAR, ASAR_BYTES)],
                     [entry(ASAR, ASAR_BYTES), entry(COMPANION)],
                     [entry(ASAR, ASAR_BYTES), entry(COMPANION + '/child')]):
            with self.subTest(count=len(rows)):
                self.assertRejected(data_package(data_entries=rows))

    def test_selected_companion_and_ancestors_cannot_be_symlinks(self):
        for name in (COMPANION, COMPANION + '/link', 'opt', 'opt/example/resources'):
            rows = [e for e in basic_data() if not (name == COMPANION and e[156:157] == b'5')]
            rows.insert(0, entry(name, kind='2', link='somewhere'))
            with self.subTest(name=name):
                self.assertRejected(data_package(data_entries=rows))

    def test_empty_symlink_target_is_rejected_even_outside_selection(self):
        self.assertRejected(data_package(entry('outside-link', kind='2')))

    def test_control_rejects_links_nested_files_and_nonroot_directories(self):
        cases = (entry('alias', kind='2', link='control'), entry('subdir', kind='5'),
                 entry('subdir/file', b'x'), entry('hard', kind='1', link='control'))
        for extra in cases:
            with self.subTest(name=extra[:100].rstrip(bytes(1))):
                self.assertRejected(envelope(control=xz(tar(entry('control', CONTROL_BYTES), extra))))

    def test_control_must_contain_one_regular_control_file(self):
        for rows in ([], [entry('control', kind='5')], [entry('other', b'x')],
                     [entry('control', CONTROL_BYTES), entry('./control', CONTROL_BYTES)]):
            with self.subTest(count=len(rows)):
                self.assertRejected(envelope(control=xz(tar(*rows))))


class BudgetAndReplayTests(EnvelopeCase):
    def test_archive_byte_budget_boundary(self):
        raw = envelope()
        self.assertBudgetBoundary(raw, 'archive', len(raw))

    def test_opaque_nonselected_file_size_budget_boundary(self):
        raw = data_package(entry('outside-large', b'x' * 83))
        self.assertBudgetBoundary(raw, 'opaque_file', 83)

    def test_selected_per_file_budget_boundary_uses_small_test_limit(self):
        raw = data_package(entry(COMPANION + '/bounded.bin', b'x' * 83))
        original_limits = dp.Limits()
        for maximum in (84, 83, 82):
            with self.subTest(maximum=maximum):
                with mock.patch.object(dp, 'Limits', return_value=replace(original_limits, max_file_bytes=maximum)):
                    if maximum >= 83:
                        scan(raw)
                    else:
                        self.assertRejected(raw, contains='Selected file budget')

    def test_selected_total_budget_boundary(self):
        raw = envelope()
        self.assertBudgetBoundary(raw, 'selected', scan(raw)['selected_bytes'])

    def test_raw_and_logical_header_budgets_are_independent(self):
        raw = data_package(long_entry('outside/' + 'q' * 101, b'x'))
        result = scan(raw)
        self.assertGreater(result['raw_headers'], result['logical_entries'])
        self.assertBudgetBoundary(raw, 'raw_headers', result['raw_headers'])
        self.assertBudgetBoundary(raw, 'entries', result['logical_entries'])

    def test_representation_budget_includes_implicit_parents_and_longnames(self):
        raw = data_package(long_entry('a/b/c/' + 'q' * 101, b'x'))
        stream = io.BytesIO(raw)
        members = dp.ar_members(stream, len(raw))
        budget = dp.Budget(dp.DEFAULTS)
        for member in members[1:]:
            dp.scan_tar(stream, member, budget, SELECT)
        self.assertBudgetBoundary(raw, 'representation', budget.representation)

    def test_replay_matches_the_entire_envelope(self):
        raw = envelope()
        expected = scan(raw)
        self.assertEqual(scan(raw, expected=expected), expected)

    def test_replay_rejects_payload_same_size_hash_change(self):
        original = envelope()
        expected = scan(original)
        altered = basic_data()
        altered[0] = entry(ASAR, b'X' + ASAR_BYTES[1:])
        self.assertRejected(data_package(data_entries=altered), expected=expected, contains='payload')

    def test_replay_rejects_metadata_extra_and_missing_entries(self):
        raw = envelope()
        expected = scan(raw)
        for altered in (data_package(entry('extra', b'x')),
                        data_package(data_entries=basic_data()[:-1]),
                        data_package(data_entries=[entry('different-asar', ASAR_BYTES)] + basic_data()[1:])):
            with self.subTest(size=len(altered)):
                self.assertRejected(altered, expected=expected)

    def test_replay_rejects_compressed_change_with_identical_tar(self):
        raw = envelope()
        expected = scan(raw)
        altered = envelope(data=xz(tar(*basic_data()), preset=0))
        self.assertNotEqual(altered, raw)
        self.assertRejected(altered, expected=expected, contains='envelope')

    def test_replay_rejects_tampered_expected_payload_hash(self):
        raw = envelope()
        expected = copy.deepcopy(scan(raw))
        expected['members'][2]['tar']['records'][0]['sha256'] = '0' * 64
        self.assertRejected(raw, expected=expected, contains='payload')

    def test_script_like_bytes_are_hashed_but_never_executed(self):
        with tempfile.TemporaryDirectory(prefix='.test-inert-', dir=HERE) as temporary:
            sentinel = Path(temporary) / 'sentinel'
            sentinel.write_bytes(b'untouched')
            script = ('#!/bin/sh\nprintf modified > ' + str(sentinel) + '\n').encode()
            raw = envelope(control=xz(tar(entry('control', CONTROL_BYTES),
                                           entry('postinst', script, mode=0o755))))
            with (mock.patch('os.system', side_effect=AssertionError('execution forbidden')) as system,
                  mock.patch('subprocess.run', side_effect=AssertionError('execution forbidden')) as run,
                  mock.patch('subprocess.Popen', side_effect=AssertionError('execution forbidden')) as popen):
                result = scan(raw)
            self.assertEqual(sentinel.read_bytes(), b'untouched')
            self.assertEqual(result['members'][1]['tar']['records'][1]['sha256'], hashlib.sha256(script).hexdigest())
            system.assert_not_called()
            run.assert_not_called()
            popen.assert_not_called()

    def test_inspect_rejects_symlink_hardlink_and_fifo_without_opening(self):
        with tempfile.TemporaryDirectory(prefix='.test-source-', dir=HERE) as temporary:
            root = Path(temporary)
            original = root / 'synthetic.deb'
            original.write_bytes(envelope())
            symlink = root / 'link.deb'
            symlink.symlink_to(original.name)
            with self.assertRaises(dp.ToolkitError):
                dp.inspect_deb(symlink, SELECT)
            os.link(original, root / 'hardlink.deb')
            with self.assertRaises(dp.ToolkitError):
                dp.inspect_deb(original, SELECT)
            if hasattr(os, 'mkfifo'):
                fifo = root / 'fifo.deb'
                os.mkfifo(fifo)
                with self.assertRaises(dp.ToolkitError):
                    dp.inspect_deb(fifo, SELECT)

    def test_filename_suffix_never_authenticates_container(self):
        with tempfile.TemporaryDirectory(prefix='.test-suffix-', dir=HERE) as temporary:
            path = Path(temporary) / 'synthetic.bin'
            path.write_bytes(envelope())
            self.assertTrue(dp.inspect_deb(path, SELECT)['outer_envelope_inventory_complete'])
            path = Path(temporary) / 'fake.deb'
            path.write_bytes(b'PK\x03\x04not a DEB')
            with self.assertRaises(dp.ToolkitError):
                dp.inspect_deb(path, SELECT)


if __name__ == '__main__':
    unittest.main(verbosity=2)
