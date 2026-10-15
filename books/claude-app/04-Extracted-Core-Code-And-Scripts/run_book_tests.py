#!/usr/bin/env python3
"""运行本书原创模型；不安装依赖、不运行 Claude、不请求网络。"""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
BOOK = ROOT.parent

def commands(include_skills=False):
    node = shutil.which('node')
    if not node:
        raise RuntimeError('需要 Node.js 22+，请先把 node 放入 PATH。')
    version = subprocess.check_output([node, '--version'], text=True).strip()
    if int(version.lstrip('v').split('.')[0]) < 22:
        raise RuntimeError('完整测试集合需要 Node.js 22+；预览超时实验使用内置虚拟定时器接口。')
    jobs = [('core-code-lab', ROOT / 'core-code-lab', [sys.executable, '-B', 'run_tests.py'])]
    for folder, pattern in [('worked-cases/sandbox-timeout', '*.test.mjs'), ('worked-cases/state-transitions', '*.test.mjs'), ('async-reading-primer', '*.test.mjs'), ('shell-lifecycle', '*.test.mjs'), ('tool-contracts', 'test/*.test.mjs'),
                            ('streaming-performance', 'test/*.test.mjs'), ('security-guardrails', '*.test.mjs'), ('native-voice-geometry', '*.test.mjs'), ('resilience-quota', 'test/*.test.mjs')]:
        location = ROOT / folder
        files = sorted(location.glob(pattern))
        if not files:
            raise RuntimeError(f'缺少已声明的测试：{folder}/{pattern}')
        jobs.append((folder, location, [node, '--test', *map(str, files)]))
    jobs.append(('worked-cases-python', ROOT / 'worked-cases', [sys.executable, '-B', '-m', 'unittest', '-v', 'test_worked_cases.py']))
    jobs.append(('worked-cases-node', ROOT / 'worked-cases', [node, '--test', 'context_budget.test.mjs']))
    jobs.append(('telemetry-metrics', BOOK / '02-Illustrated-Deep-Dive-Book/12-Telemetry-And-Product-Metrics/metrics-lab', [sys.executable, '-B', '-m', 'unittest', '-v', 'test_metrics_lab.py']))
    if include_skills:
        location = BOOK / '03-Ready-To-Use-Agent-Skills'
        files = sorted(location.rglob('*.test.mjs'))
        if not files:
            raise RuntimeError('未找到 skills 的独立复制测试。')
        jobs.append(('portable-skills', location, [node, '--test', *map(str, files)]))
    return jobs

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills', action='store_true', help='同时运行 skills 内独立副本的测试；不把重复模型算作新增实现')
    parser.add_argument('--list', action='store_true', help='只列出各测试组，不执行')
    args = parser.parse_args()
    try:
        jobs = commands(args.skills)
    except RuntimeError as error:
        parser.error(str(error))
    if args.list:
        for name, directory, _ in jobs:
            print(f'{name}: {directory.relative_to(BOOK)}')
        return 0
    failed = []
    for name, directory, command in jobs:
        print(f'\n===== {name} =====', flush=True)
        result = subprocess.run(command, cwd=directory, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, check=False)
        if result.returncode:
            failed.append(name)
    if failed:
        print('\n失败组：' + ', '.join(failed), file=sys.stderr)
        return 1
    print('\n所列原创模型均通过。浏览器绘制、目标产品运行及可选 DOM/样本检查不在本命令范围。')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
