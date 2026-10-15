#!/usr/bin/env python3
"""Replay the 52 published original fixtures through the formal external CLI.
No network, installation, target execution, or private metadata/cache access.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acorn-module', required=True, type=Path,
                        help='Trusted installed Acorn 8.17.0 dist/acorn.js')
    parser.add_argument('--tool-dir', type=Path,
                        default=Path(__file__).resolve().parent.parent,
                        help='Published optional-ast-channel directory; defaults to parent of this script directory')
    parser.add_argument('--node', type=Path, help='Trusted Node executable; defaults to PATH node')
    args = parser.parse_args()
    tool = args.tool_dir.resolve()
    module = args.acorn_module.absolute()
    node = str(args.node.absolute()) if args.node else shutil.which('node')
    require(node is not None, 'Node unavailable')
    fixtures = json.loads((tool / 'tests/fixtures.json').read_text(encoding='utf-8'))
    require(isinstance(fixtures, list) and len(fixtures) == 52, 'Expected exactly 52 published fixtures')
    require(len({f['id'] for f in fixtures}) == 52, 'Fixture IDs must be unique')
    module_sha256 = hashlib.sha256(module.read_bytes()).hexdigest()
    counts = Counter()
    with tempfile.TemporaryDirectory(prefix='original-ast-formal-fixtures-') as temp:
        root = Path(temp)
        for index, fixture in enumerate(fixtures):
            data = fixture['source'].encode('utf-8')
            source = root / ('fixture-%02d.js' % index)
            source.write_bytes(data)
            expected = fixture['expected_status']
            require(expected in ('scanned', 'scan-incomplete'), 'Unsupported expected status')
            command = [sys.executable, '-B', str(tool / 'ast_candidates.py'),
                       '--input', str(source), '--source-type', 'module',
                       '--node', node, '--acorn-module', str(module)]
            result = subprocess.run(command, cwd=root, capture_output=True, timeout=25)
            label = fixture['id']
            require(result.returncode == (0 if expected == 'scanned' else 2), label + ': exit code mismatch')
            require(not result.stderr, label + ': unexpected stderr')
            report = json.loads(result.stdout)
            (root / ('report-%02d.json' % index)).write_bytes(result.stdout)
            require(report['status'] == expected, label + ': status mismatch')
            observed = Counter((r['category'], r['key']) for r in report['records'])
            wanted = Counter((r['category'], r['key']) for r in fixture['expected_candidates'])
            require(observed == wanted, label + ': candidate multiset mismatch')
            dependency = report['policy']['dependency']
            require(dependency['source'] == 'explicit-installed-acorn', label + ': not external mode')
            require(dependency['testing_only'] is False, label + ': testing-only mode')
            require(dependency['sha256'] == module_sha256, label + ': dependency hash mismatch')
            identity = report['identity']['channel_sha256']
            body = {key: value for key, value in report.items() if key != 'identity'}
            wire = (json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')
            require(identity == hashlib.sha256(wire).hexdigest(), label + ': report identity mismatch')
            require(dependency['name'] == 'acorn' and dependency['version'] == '8.17.0', label + ': dependency version mismatch')
            require(report['input']['identity_available'] is True, label + ': missing input identity')
            require(report['input']['bytes'] == len(data), label + ': input size mismatch')
            require(report['input']['sha256'] == hashlib.sha256(data).hexdigest(), label + ': input hash mismatch')
            require(report['semantic_completeness_proven'] is False, label + ': semantic claim changed')
            require(report['coverage']['legacy_coverage_modified'] is False, label + ': legacy coverage changed')
            require(report['coverage']['complete_within_ast_declared_scope'] is (expected == 'scanned'), label + ': coverage mismatch')
            if expected == 'scan-incomplete':
                require(report['records'] == [], label + ': partial records after rejection')
            counts[expected] += 1
    require(hashlib.sha256(module.read_bytes()).hexdigest() == module_sha256, 'Parser module changed during validation')
    require(counts == Counter({'scanned': 45, 'scan-incomplete': 7}), 'Unexpected fixture status totals')
    print(json.dumps({'result': 'PASS', 'fixture_count': 52, 'scanned': 45,
                      'expected_scan_incomplete': 7, 'testing_only': False,
                      'scope': 'Replay of the existing 52 original fixtures, not additional distinct tests'},
                     ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('Fixture verification failed: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
