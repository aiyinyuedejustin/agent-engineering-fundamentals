#!/usr/bin/env python3
"""Reproduce a static UI comparison from three independently extracted resources roots.

Python 3.10+, standard library only. Each root must contain ion-dist/ and app.asar.
Reads files as inert bytes; never imports or runs inspected application code.
Verifies packed regular ASAR entries against their declared sizes, SHA-256s and
block hashes. Unpacked companions and ASAR links are inventoried but excluded.
The report is hashes/metadata only. No extracted proprietary content is written.

Example:
  python compare_ui_trees.py --linux-resources /sample/linux/resources \
    --windows-resources /sample/windows/resources \
    --macos-resources /sample/macos/Resources --output ui-comparison.json

Package extraction, download provenance and OS signature trust are separate steps.
Successful execution means a comparison was produced; inspect equality fields for
the result. Internal ASAR hash consistency is not publisher authentication.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import stat
import struct

FONT_SUFFIXES = {'.woff', '.woff2', '.ttf', '.otf'}
PLATFORMS = ('linux', 'windows', 'macos')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, 'Duplicate ASAR JSON key: ' + key)
        obj[key] = value
    return obj


def packed_entries(path):
    require(stat.S_ISREG(path.lstat().st_mode), 'ASAR must be a regular file')
    length = path.stat().st_size
    with path.open('rb') as f:
        header = f.read(16)
        require(len(header) == 16, 'Truncated ASAR header')
        pickle_size, header_size, payload_size, json_size = struct.unpack('<4I', header)
        require(pickle_size == 4 and header_size == payload_size + 4, 'Invalid ASAR pickle lengths')
        require(0 < json_size <= payload_size - 4 and json_size <= 64 * 1024**2, 'Invalid/bounded ASAR JSON size')
        data_start = 8 + header_size
        require(16 + json_size <= data_start <= length, 'ASAR header exceeds archive')
        tree = json.loads(f.read(json_size), object_pairs_hook=unique_object)

        def walk(node, prefix=''):
            for name, entry in node['files'].items():
                require(name not in ('', '.', '..') and '/' not in name and '\\' not in name,
                        'Unsafe ASAR path component')
                relative = prefix + name
                if 'files' in entry:
                    yield from walk(entry, relative + '/')
                else:
                    yield relative, entry

        for name, entry in walk(tree):
            if entry.get('unpacked') or 'link' in entry:
                yield name, entry, None
                continue
            size, offset = entry['size'], int(entry['offset'])
            require(isinstance(size, int) and 0 <= size <= 512 * 1024**2 and offset >= 0,
                    'Invalid/bounded packed ASAR size or offset: ' + name)
            require(data_start + offset + size <= length, 'Packed entry exceeds ASAR: ' + name)
            f.seek(data_start + offset)
            data = f.read(size)
            integrity = entry.get('integrity', {})
            require(len(data) == size and integrity.get('algorithm') == 'SHA256',
                    'Missing size or SHA256 integrity: ' + name)
            require(sha(data) == integrity.get('hash'), 'Packed file hash mismatch: ' + name)
            block_size = integrity.get('blockSize')
            require(isinstance(block_size, int) and block_size > 0, 'Invalid block size: ' + name)
            blocks = [sha(data[i:i+block_size]) for i in range(0, size, block_size)] or [sha(b'')]
            require(blocks == integrity.get('blocks'), 'Packed block hash mismatch: ' + name)
            yield name, entry, data


def read_platform(root):
    require(root.is_dir(), 'Missing resources root: ' + str(root))
    require((root / 'ion-dist').is_dir(), 'Missing ion-dist tree: ' + str(root))
    require(not (root / 'ion-dist').is_symlink(), 'ion-dist cannot be a symlink')
    ions, packed, css, fonts, unpacked, links = {}, {}, {}, {}, [], []
    for file in sorted((root / 'ion-dist').rglob('*')):
        mode = file.lstat().st_mode
        if stat.S_ISDIR(mode):
            continue
        require(stat.S_ISREG(mode), 'Non-regular ion-dist entry: ' + str(file))
        relative = file.relative_to(root).as_posix()
        ions[relative] = {'size': file.stat().st_size, 'sha256': file_sha(file)}
        if file.suffix == '.css':
            data = file.read_bytes()
            css[relative] = {'sha256': sha(data), 'crlf_to_lf_sha256': sha(data.replace(b'\r\n', b'\n')),
                             'crlf_count': data.count(b'\r\n'),
                             'bare_cr_count': data.replace(b'\r\n', b'').count(b'\r')}
        if file.suffix in FONT_SUFFIXES:
            fonts[relative] = ions[relative]
    for relative, entry, data in packed_entries(root / 'app.asar'):
        if entry.get('unpacked'):
            unpacked.append(relative)
            continue
        if 'link' in entry:
            links.append(relative)
            continue
        require(relative not in ions, 'Ambiguous combined resource path: ' + relative)
        packed[relative] = {'size': len(data), 'sha256': sha(data)}
        if Path(relative).suffix == '.css':
            css[relative] = {'sha256': sha(data), 'crlf_to_lf_sha256': sha(data.replace(b'\r\n', b'\n')),
                             'crlf_count': data.count(b'\r\n'),
                             'bare_cr_count': data.replace(b'\r\n', b'').count(b'\r')}
        if Path(relative).suffix in FONT_SUFFIXES:
            fonts[relative] = packed[relative]
    digest = sha('\n'.join(f'{p}\t{ions[p]["sha256"]}' for p in sorted(ions)).encode('utf-8'))
    return {'ion_dist': {'file_count': len(ions), 'tree_digest_sha256': digest,
                         'extension_counts': dict(sorted(Counter(Path(p).suffix for p in ions).items())),
                         'assets_v1_js_count': sum(p.startswith('ion-dist/assets/v1/') and p.endswith('.js') for p in ions),
                         'inventory': ions},
            'asar': {'sha256': file_sha(root / 'app.asar'), 'packed_file_count': len(packed),
                     'packed_integrity_verified': True, 'packed_inventory': packed,
                     'excluded_unpacked_entries': unpacked, 'excluded_link_entries': links},
            'css': css, 'fonts': fonts}


def compare(roots):
    samples = {p: read_platform(roots[p]) for p in PLATFORMS}
    ions = {p: samples[p]['ion_dist']['inventory'] for p in PLATFORMS}
    css_paths = sorted(set().union(*(samples[p]['css'] for p in PLATFORMS)))
    css = []
    for path in css_paths:
        present = {p: samples[p]['css'][path] for p in PLATFORMS if path in samples[p]['css']}
        all_present = len(present) == len(PLATFORMS)
        css.append({'path': path, 'platforms': present,
                    'byte_identical_all': all_present and len({r['sha256'] for r in present.values()}) == 1,
                    'crlf_to_lf_equal_all': all_present and len({r['crlf_to_lf_sha256'] for r in present.values()}) == 1})
    return {'scope': 'Fresh ion-dist regular-file trees plus packed regular app.asar entries; all counts computed from supplied roots.',
            'method': 'Python standard library; no inspected code executed; no unpacked companion or ASAR link followed.',
            'tree_digest_method': 'SHA256 of UTF-8 lexicographically path-sorted path + TAB + file SHA256 records joined with LF, no trailing LF.',
            'ion_dist': {'files_each': {p: len(v) for p,v in ions.items()},
                         'all_paths_sizes_and_hashes_equal': all(v == ions['linux'] for v in ions.values())},
            'css': {'files_each': {p: len(samples[p]['css']) for p in PLATFORMS},
                    'unique_raw_hashes_each': {p: len({x['sha256'] for x in samples[p]['css'].values()}) for p in PLATFORMS},
                    'byte_identical_count': sum(r['byte_identical_all'] for r in css),
                    'crlf_to_lf_equal_count': sum(r['crlf_to_lf_equal_all'] for r in css),
                    'inventory': css},
            'fonts': {'suffix_scope': sorted(FONT_SUFFIXES),
                      'files_each': {p: len(samples[p]['fonts']) for p in PLATFORMS},
                      'unique_hashes_each': {p: len({x['sha256'] for x in samples[p]['fonts'].values()}) for p in PLATFORMS},
                      'all_paths_sizes_and_hashes_equal': all(samples[p]['fonts'] == samples['linux']['fonts'] for p in PLATFORMS)},
            'platforms': samples,
            'limitations': ['Package download provenance, extraction lineage and OS signature trust are not validated by this script.',
                            'Archive-declared hash checks establish internal consistency, not publisher authentication.',
                            'Byte equality does not establish identical rendering, native behavior, feature flags, active fonts or remote content.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for platform in PLATFORMS:
        parser.add_argument('--' + platform + '-resources', type=Path, required=True)
    parser.add_argument('--output', type=Path, help='Write metadata JSON here instead of stdout')
    args = parser.parse_args()
    roots = {p: getattr(args, p + '_resources') for p in PLATFORMS}
    report = json.dumps(compare(roots), indent=2) + '\n'
    if args.output:
        args.output.write_text(report, encoding='utf-8')
    else:
        print(report, end='')


if __name__ == '__main__':
    main()
