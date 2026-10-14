#!/usr/bin/env python3
"""核验交付清单；拒绝缺失、改写或未列入清单的文件。"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent


def main():
    try:
        manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
        listed = set()
        for item in manifest['files']:
            relative = item['path']
            path = ROOT / relative
            if relative in listed or not path.resolve().is_relative_to(ROOT) or path.is_symlink():
                raise ValueError(f'不合法或重复的路径：{relative}')
            listed.add(relative)
            raw = path.read_bytes()
            if len(raw) != item['bytes'] or hashlib.sha256(raw).hexdigest() != item['sha256']:
                raise ValueError(f'字节数或 SHA-256 不一致：{relative}')
        actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()}
        unexpected = actual - listed - {'manifest.json'}
        if unexpected:
            raise ValueError('存在未列入清单的文件：' + ', '.join(sorted(unexpected)))
        print(f'完整性核验通过：{len(listed)} 个文件。清单本身不参与递归哈希。')
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'完整性核验失败：{error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
