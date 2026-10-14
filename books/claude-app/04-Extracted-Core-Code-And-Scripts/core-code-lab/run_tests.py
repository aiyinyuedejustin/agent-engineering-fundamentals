#!/usr/bin/env python3
"""运行原创实验室的离线测试；可选运行合成数据演示。"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demos', action='store_true', help='测试全部通过后，再运行四个离线演示')
    args = parser.parse_args()
    node = shutil.which('node')
    if node is None:
        parser.error('需要 Node.js 20+；请先确认 node 在 PATH 中。')
    if sys.version_info < (3, 10):
        parser.error('需要 Python 3.10 或更新版本。')
    try:
        version = subprocess.run([node, '--version'], check=True, text=True,
                                 capture_output=True).stdout.strip()
        major = int(version.lstrip('v').split('.')[0])
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        parser.error(f'无法读取 Node.js 版本：{error}')
    if major < 20:
        parser.error(f'需要 Node.js 20+；当前为 {version}。')

    python = sys.executable
    jobs = [
        ('protocol-tree', ROOT / 'protocol-tree',
         [node, '--test', *[str(p) for p in sorted((ROOT / 'protocol-tree/test').glob('*.test.mjs'))]]),
        ('loop-cowork', ROOT / 'loop-cowork', [python, '-B', '-m', 'unittest', 'discover', '-s', '.', '-p', 'test_*.py', '-v']),
        ('workspace-core', ROOT / 'workspace-core', [node, '--test', 'workspaces-model.test.mjs']),
        ('memory-flags', ROOT / 'memory-flags', [node, '--test', 'memory-flags-model.test.mjs']),
        ('color-tools', ROOT / 'color-tools', [python, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py', '-v']),
    ]
    # 不安装依赖，不写日志或缓存；各模块独立运行，任何失败都不能被后续成功掩盖。
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    failures = []
    for label, cwd, command in jobs:
        print(f'\n===== {label} =====', flush=True)
        result = subprocess.run(command, cwd=cwd, env=env, check=False)
        if result.returncode:
            failures.append(label)
    if failures:
        print('\n未通过：' + ', '.join(failures), file=sys.stderr)
        return 1
    print('\n五个离线测试模块全部通过。样本基线回归和可选 DOM 检查未运行。', flush=True)
    if args.demos:
        demos = [
            ('protocol-tree', [node, 'demo.mjs']),
            ('loop-cowork', [python, '-B', 'model.py']),
            ('workspace-core', [node, 'demo.mjs']),
            ('memory-flags', [node, 'demo.mjs']),
        ]
        for label, command in demos:
            print(f'\n===== {label} 演示 =====', flush=True)
            if subprocess.run(command, cwd=ROOT / label, env=env, check=False).returncode:
                print(f'演示未通过：{label}', file=sys.stderr)
                return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
