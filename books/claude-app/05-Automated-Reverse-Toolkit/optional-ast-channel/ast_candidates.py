#!/usr/bin/env python3
"""Original opt-in AST channel. Standard-library launcher; no target execution."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import selectors
import shutil
import stat
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
SCHEMA = 'original-ast-candidate-snapshot/v1'
DEFAULT_LIMITS = {
    'max_input_bytes': 64 * 1024 * 1024,
    'max_tokens': 1000000,
    'max_nodes': 200000,
    'max_depth': 64,
    'max_records': 200000,
    'max_output_bytes': 8 * 1024 * 1024,
    'wall_seconds': 15,
    'cpu_seconds': 10,
    'v8_old_space_mib': 128,
}

class ChannelError(ValueError):
    pass


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def limits_with(overrides=None):
    limits = dict(DEFAULT_LIMITS)
    if overrides is not None and not isinstance(overrides, dict):
        raise ChannelError('ast-limit-configuration-rejected')
    for key, value in (overrides or {}).items():
        if key not in limits or type(value) is not int or not 0 < value <= limits[key]:
            raise ChannelError('ast-limit-configuration-rejected')
        if key == 'max_output_bytes' and value < 4096:
            raise ChannelError('ast-limit-configuration-rejected')
        limits[key] = value
    return limits


def bounded_read(path, limit):
    path = Path(path)
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ChannelError('ast-input-not-regular-single-link')
    if before.st_size > limit:
        raise ChannelError('ast-input-byte-bound-exceeded')
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    with os.fdopen(os.open(path, flags), 'rb') as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise ChannelError('ast-input-changed')
        data = stream.read(limit + 1)
        after = os.fstat(stream.fileno())
    if len(data) > limit or len(data) != before.st_size or (after.st_size, after.st_mtime_ns) != (before.st_size, before.st_mtime_ns):
        raise ChannelError('ast-input-changed')
    return data


def dependency_config(module_path=None, test_node_bundled=False):
    if bool(module_path) == bool(test_node_bundled):
        raise ChannelError('ast-parser-dependency-required')
    if test_node_bundled:
        return {'kind': 'node-internal-test-only', 'sha256': None}
    module_path = Path(module_path).absolute()
    if module_path.name != 'acorn.js' or module_path.parent.name != 'dist':
        raise ChannelError('ast-parser-layout-unsupported')
    # Read metadata before loading the explicitly trusted tool dependency.
    # Name/version/hash identify it, but cannot authenticate a hostile package.
    try:
        package_bytes = bounded_read(module_path.parent.parent / 'package.json', 65536)
        package = json.loads(package_bytes)
        module_bytes = bounded_read(module_path, 2 * 1024 * 1024)
    except (OSError, ValueError, RecursionError):
        raise ChannelError('ast-parser-dependency-unavailable') from None
    if not isinstance(package, dict) or package.get('name') != 'acorn' or package.get('version') != '8.17.0' or package.get('main') != 'dist/acorn.js':
        raise ChannelError('ast-parser-version-or-layout-unsupported')
    return {'kind': 'explicit-installed-acorn', 'module_path': str(module_path),
            'sha256': sha256(module_bytes), 'package_sha256': sha256(package_bytes)}


def valid_source_name(name):
    return (isinstance(name, str) and len(name) <= 255 and
            not any(ord(c) < 32 or 0xD800 <= ord(c) <= 0xDFFF for c in name))


def incomplete(code, data=None, source_name='input.js', limits=None, dependency=None):
    return {
        'schema': SCHEMA, 'analysis_kind': 'ast_syntax_candidate_inventory',
        'semantic_completeness_proven': False,
        'input': {'name': source_name if valid_source_name(source_name) else 'input.js',
                  'identity_available': data is not None,
                  'bytes': len(data) if data is not None else None,
                  'sha256': sha256(data) if data is not None else None},
        'status': 'scan-incomplete',
        'policy': {'adapter': 'original-acorn-ast-candidate/v1', 'limits': limits or dict(DEFAULT_LIMITS),
                   'dependency': {'source': (dependency or {}).get('kind'),
                                  'testing_only': (dependency or {}).get('kind') == 'node-internal-test-only'}},
        'metrics': {},
        'coverage': {'complete_within_ast_declared_scope': False, 'legacy_coverage_modified': False,
                     'issues': [{'code': code, 'phase': 'ast-candidate-channel', 'input_validity': 'not-determined'}]},
        'records': [],
        'limitations': ['AST syntax candidates only; semantic completeness is not proven.',
                        'Legacy snapshot schema, statuses and counts are not modified or merged.'],
    }


def encode_report(report):
    """Canonical UTF-8 wire representation; the output cap includes LF."""
    return (json.dumps(report, sort_keys=True, ensure_ascii=False,
                       separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')


def finalize(report, data, source_name, limits, dependency):
    try:
        report['identity'] = {'channel_sha256': sha256(encode_report(report))}
    except (ValueError, TypeError, UnicodeError, RecursionError):
        report = incomplete('ast-worker-protocol-rejected', data, source_name, limits, dependency)
        report['identity'] = {'channel_sha256': sha256(encode_report(report))}
    if len(encode_report(report)) > limits['max_output_bytes']:
        report = incomplete('ast-output-bound-exceeded', data, source_name, limits, dependency)
        report['identity'] = {'channel_sha256': sha256(encode_report(report))}
    return report


def _child_limits(cpu_seconds):
    # Supported launcher platform: POSIX with resource limits. No RSS sandbox
    # claim: V8 old-space is bounded separately; source/output allocations also
    # have explicit byte limits. Only this newly created child is constrained.
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def _bounded_worker(command, data, limits):
    if os.name != 'posix':
        raise ChannelError('ast-process-limits-unavailable')
    try:
        import resource  # noqa: F401: presence required before child creation
    except ImportError:
        raise ChannelError('ast-process-limits-unavailable') from None
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               cwd=HERE, env={}, close_fds=True,
                               preexec_fn=lambda: _child_limits(limits['cpu_seconds']))
    output, errors, offset = bytearray(), bytearray(), 0
    deadline = time.monotonic() + limits['wall_seconds']
    selector = selectors.DefaultSelector()
    try:
        for stream in (process.stdin, process.stdout, process.stderr):
            os.set_blocking(stream.fileno(), False)
        selector.register(process.stdin, selectors.EVENT_WRITE, 'input')
        selector.register(process.stdout, selectors.EVENT_READ, 'output')
        selector.register(process.stderr, selectors.EVENT_READ, 'error')
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ChannelError('ast-worker-time-bound-exceeded')
            for key, _ in selector.select(min(remaining, 0.2)):
                stream = key.fileobj
                if key.data == 'input':
                    if offset == len(data):
                        selector.unregister(stream); stream.close(); continue
                    try:
                        offset += os.write(stream.fileno(), memoryview(data)[offset:offset + 65536])
                    except BrokenPipeError:
                        selector.unregister(stream); stream.close()
                else:
                    chunk = os.read(stream.fileno(), 65536)
                    if not chunk:
                        selector.unregister(stream); stream.close(); continue
                    destination = output if key.data == 'output' else errors
                    destination.extend(chunk)
                    maximum = limits['max_output_bytes'] + 1 if key.data == 'output' else 65536
                    if len(destination) > maximum:
                        raise ChannelError('ast-worker-output-bound-exceeded')
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ChannelError('ast-worker-time-bound-exceeded')
        try:
            exit_code = process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            raise ChannelError('ast-worker-time-bound-exceeded') from None
        if exit_code != 0:
            raise ChannelError('ast-worker-resource-or-process-failed')
        return bytes(output)
    finally:
        # Never signal a process group or discover/kill unrelated processes.
        if process.poll() is None:
            process.kill()
        process.wait()
        selector.close()
        for stream in (process.stdin, process.stdout, process.stderr):
            if not stream.closed:
                stream.close()


def analyze_bytes(data, *, source_name='input.js', source_type='module', acorn_module=None,
                  test_node_bundled=False, node_binary=None, limit_overrides=None):
    limits, dependency = dict(DEFAULT_LIMITS), None
    try:
        limits = limits_with(limit_overrides)
        if not isinstance(data, bytes):
            raise ChannelError('ast-input-must-be-bytes')
        if source_type not in ('module', 'script'):
            raise ChannelError('ast-source-type-unsupported')
        if not valid_source_name(source_name):
            raise ChannelError('ast-source-name-rejected')
        if len(data) > limits['max_input_bytes']:
            raise ChannelError('ast-input-byte-bound-exceeded')
        try:
            data.decode('utf-8')
        except UnicodeError:
            raise ChannelError('ast-input-not-utf8') from None
        dependency = dependency_config(acorn_module, test_node_bundled)
        node = node_binary or shutil.which('node')
        if not node:
            raise ChannelError('ast-node-unavailable')
        node = str(Path(node).absolute())
        config = {'source_name': source_name, 'source_type': source_type, 'dependency': dependency, 'limits': limits}
        command = [node, '--max-old-space-size=' + str(limits['v8_old_space_mib']), '--max-semi-space-size=16', '--stack-size=512']
        if test_node_bundled:
            command.append('--expose-internals')
        command += [str(HERE / 'ast_worker.cjs'), json.dumps(config, separators=(',', ':'), ensure_ascii=True)]
        payload = _bounded_worker(command, data, limits)
        try:
            report = json.loads(payload)
        except (ValueError, UnicodeError, RecursionError):
            raise ChannelError('ast-worker-protocol-rejected') from None
        if (not isinstance(report, dict) or report.get('schema') != SCHEMA or
                report.get('analysis_kind') != 'ast_syntax_candidate_inventory' or
                report.get('semantic_completeness_proven') is not False or
                report.get('status') not in ('scanned', 'scan-incomplete') or
                not isinstance(report.get('records'), list) or
                not isinstance(report.get('input'), dict) or
                not isinstance(report.get('coverage'), dict) or
                not isinstance(report.get('policy'), dict) or
                (report['status'] == 'scan-incomplete' and report['records'])):
            raise ChannelError('ast-worker-protocol-rejected')
        if report['input'].get('sha256') != sha256(data) or report['input'].get('bytes') != len(data):
            raise ChannelError('ast-worker-input-identity-mismatch')
    except ChannelError as error:
        report = incomplete(str(error), data if isinstance(data, bytes) else None, source_name, limits, dependency)
    except (OSError, subprocess.SubprocessError):
        report = incomplete('ast-worker-or-file-unavailable', data, source_name, limits, dependency)
    return finalize(report, data if isinstance(data, bytes) else None, source_name, limits, dependency)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Opt-in AST syntax candidates; no target execution; legacy toolkit unchanged')
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--source-type', choices=['module', 'script'], required=True)
    dependency = parser.add_mutually_exclusive_group(required=True)
    dependency.add_argument('--acorn-module', type=Path, help='Explicit trusted Acorn 8.17.0 dist/acorn.js; not a target file')
    dependency.add_argument('--test-node-bundled-acorn', action='store_true', help='TEST ONLY: unstable Node-internal Acorn, marked in policy')
    parser.add_argument('--node', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.acorn_module and args.input.resolve() == args.acorn_module.resolve():
            raise ChannelError('ast-target-dependency-collision')
        data = bounded_read(args.input, DEFAULT_LIMITS['max_input_bytes'])
        report = analyze_bytes(data, source_name=args.input.name, source_type=args.source_type,
                               acorn_module=args.acorn_module, test_node_bundled=args.test_node_bundled_acorn,
                               node_binary=args.node)
    except (OSError, ChannelError) as error:
        code = str(error) if isinstance(error, ChannelError) else 'ast-input-unavailable'
        report = incomplete(code, source_name=args.input.name)
        report = finalize(report, None, args.input.name, DEFAULT_LIMITS, None)
    sys.stdout.buffer.write(encode_report(report))
    return 0 if report['status'] == 'scanned' else 2


if __name__ == '__main__':
    raise SystemExit(main())
