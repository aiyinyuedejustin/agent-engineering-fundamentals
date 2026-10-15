#!/usr/bin/env python3
"""Original inert fixtures exercising the published comparator; Python 3.10+."""
import importlib.util
import json
import os
from pathlib import Path
import struct
import sys
import tempfile

sys.dont_write_bytecode = True
DEFAULT_SCRIPT = Path(__file__).resolve().parents[3] / '04-Extracted-Core-Code-And-Scripts/scripts/compare_ui_trees.py'
spec = importlib.util.spec_from_file_location('ui_comparator', os.environ.get('COMPARE_UI_SCRIPT', DEFAULT_SCRIPT))
comparator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparator)

LF = b'.demo { color: teal; }\n'
CRLF = LF.replace(b'\n', b'\r\n')
CHANGED = b'.demo { color: plum; }\n'


def write_asar(path, files):
    """Tiny original ASAR fixture, never a product archive or executable."""
    tree, chunks, offset = {'files': {}}, [], 0
    for name, data in sorted(files.items()):
        node = tree
        parts = name.split('/')
        for part in parts[:-1]:
            node = node['files'].setdefault(part, {'files': {}})
        node['files'][parts[-1]] = {
            'size': len(data), 'offset': str(offset),
            'integrity': {'algorithm': 'SHA256', 'hash': comparator.sha(data),
                          'blockSize': 1024,
                          'blocks': [comparator.sha(data[i:i+1024]) for i in range(0, len(data), 1024)] or [comparator.sha(b'')]}}
        offset += len(data)
        chunks.append(data)
    header = json.dumps(tree, separators=(',', ':')).encode()
    padding = b'\0' * ((-(4 + len(header))) % 4)
    payload_size = 4 + len(header) + len(padding)
    path.write_bytes(struct.pack('<4I', 4, payload_size + 4, payload_size, len(header)) + header + padding + b''.join(chunks))


def make_roots(base):
    roots = {}
    for platform in comparator.PLATFORMS:
        root = base / platform
        ion = root / 'ion-dist'
        ion.mkdir(parents=True)
        (ion / 'same.css').write_bytes(LF)
        # These bytes intentionally are NOT valid fonts. Only suffix/hash counting is tested.
        (ion / 'font-a.woff2').write_bytes(b'ORIGINAL MOCK A - not a font')
        (ion / 'font-a-copy.woff2').write_bytes(b'ORIGINAL MOCK A - not a font')
        (ion / 'font-b.woff2').write_bytes(b'ORIGINAL MOCK B - not a font')
        shell = {'shell/newlines.css': CRLF if platform == 'windows' else LF,
                 'shell/changed.css': CHANGED if platform == 'windows' else LF}
        if platform != 'windows':
            shell['shell/missing.css'] = LF
        write_asar(root / 'app.asar', shell)
        roots[platform] = root
    return roots


def classify(row):
    # Presence must be decided first: false/false alone cannot distinguish missing/content.
    if len(row['platforms']) != len(comparator.PLATFORMS):
        return '集合不完整'
    if row['byte_identical_all']:
        return '同字节'
    if row['crlf_to_lf_equal_all']:
        return '仅所定义归一化相同'
    return '内容不同'


def summary(report):
    return {'cases': [{'path': r['path'], 'result': classify(r),
                       'raw_equal': r['byte_identical_all'],
                       'crlf_to_lf_equal': r['crlf_to_lf_equal_all']}
                      for r in report['css']['inventory']],
            'css_counts': {key: report['css'][key] for key in ('files_each', 'byte_identical_count', 'crlf_to_lf_equal_count')},
            'fonts': report['fonts'],
            'scope': 'Original synthetic bytes only; mock suffixes are not usable fonts.'}


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='ui-comparison-lesson-') as directory:
        report = comparator.compare(make_roots(Path(directory)))
        print(json.dumps(summary(report), indent=2, ensure_ascii=False))
