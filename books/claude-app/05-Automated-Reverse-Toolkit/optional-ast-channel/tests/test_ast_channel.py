"""Original synthetic regressions. Fixture JavaScript is parsed, never run."""
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import ast_candidates as channel

FIXTURES = json.loads((ROOT / 'tests/fixtures.json').read_text())

class FixtureTests(unittest.TestCase):
    pass


def make_fixture_test(fixture):
    def test(self):
        data = fixture['source'].encode('utf-8')
        result = channel.analyze_bytes(data, test_node_bundled=True)
        self.assertEqual(result['status'], fixture['expected_status'], result['coverage']['issues'])
        self.assertEqual(Counter((r['category'], r['key']) for r in result['records']),
                         Counter((r['category'], r['key']) for r in fixture['expected_candidates']))
        self.assertIs(result['semantic_completeness_proven'], False)
        self.assertIs(result['coverage']['legacy_coverage_modified'], False)
        for record in result['records']:
            anchor = record['source']
            self.assertEqual(anchor['sha256'], hashlib.sha256(data).hexdigest())
            self.assertTrue(0 <= anchor['byte_start'] <= anchor['byte_end'] <= len(data))
            self.assertEqual(anchor['line'], 1 + data[:anchor['byte_start']].count(b'\n'))
            self.assertTrue(data[anchor['byte_start']:anchor['byte_end']].decode('utf-8'))
    return test


for fixture in FIXTURES:
    setattr(FixtureTests, 'test_' + fixture['id'].replace('-', '_'), make_fixture_test(fixture))


class ContractTests(unittest.TestCase):
    def scan(self, text, **kwargs):
        data = text if isinstance(text, bytes) else text.encode('utf-8')
        return channel.analyze_bytes(data, test_node_bundled=True, **kwargs)

    def code(self, result):
        self.assertEqual(result['status'], 'scan-incomplete')
        self.assertEqual(result['records'], [])
        self.assertFalse(result['coverage']['complete_within_ast_declared_scope'])
        return result['coverage']['issues'][0]['code']

    def test_separate_schema_policy_and_determinism(self):
        data = 'checkGate("stable");'
        one, two = self.scan(data), self.scan(data)
        self.assertEqual(one, two)
        self.assertEqual(one['schema'], 'original-ast-candidate-snapshot/v1')
        self.assertNotEqual(one['schema'], 'original-static-snapshot/v1')
        self.assertEqual(one['analysis_kind'], 'ast_syntax_candidate_inventory')
        self.assertIs(one['semantic_completeness_proven'], False)
        self.assertTrue(one['policy']['dependency']['testing_only'])
        self.assertEqual(one['policy']['dependency']['version'], '8.17.0')
        self.assertEqual(one['policy']['ecma_version'], 2025)
        self.assertEqual(one['policy']['limits']['max_tokens'], 1000000)

    def test_utf8_bom_and_astral_prefix_exact_bytes(self):
        data = '\ufeff/* 中文 🧪 */\ncheckGate("方向🧭");'.encode()
        result = self.scan(data)
        anchor = result['records'][0]['source']
        literal = '"方向🧭"'.encode()
        self.assertEqual(anchor['byte_start'], data.index(literal))
        self.assertEqual(anchor['byte_end'], data.index(literal) + len(literal))
        self.assertEqual(anchor['line'], 2)

    def test_real_call_inside_interpolation_separate_scope(self):
        result = self.scan('const x = `${checkGate("actual_expression")}`;')
        self.assertEqual([r['key'] for r in result['records']], ['actual_expression'])
        self.assertFalse(result['coverage']['legacy_coverage_modified'])

    def test_nonfinite_second_literal_fails_whole_file(self):
        result = self.scan('checkGate("before"); track("too_big",1e400);')
        self.assertEqual(self.code(result), 'ast-nonfinite-candidate-literal')

    def test_static_second_values_are_bounded(self):
        result = self.scan('checkGate("a",false); track("b",null); track("c",2.5); track("d",0xff);')
        by_key = {r['key']: r['value'] for r in result['records']}
        self.assertIs(by_key['a']['second_literal'], False)
        self.assertIsNone(by_key['b']['second_literal'])
        self.assertEqual(by_key['c']['second_literal'], 2.5)
        self.assertNotIn('second_literal', by_key['d'])

    def test_invalid_utf8_rejected_before_process(self):
        with mock.patch.object(channel, '_bounded_worker', side_effect=AssertionError('must not spawn')):
            self.assertEqual(self.code(self.scan(b'\xff')), 'ast-input-not-utf8')

    def test_larger_limits_rejected_before_process(self):
        with mock.patch.object(channel, '_bounded_worker', side_effect=AssertionError('must not spawn')):
            result = self.scan('x', limit_overrides={'max_tokens': 1000001})
        self.assertEqual(self.code(result), 'ast-limit-configuration-rejected')

    def test_input_bound_preserved_and_lowerable(self):
        self.assertEqual(channel.DEFAULT_LIMITS['max_input_bytes'], 64 * 1024 * 1024)
        self.assertEqual(self.code(self.scan('abcd', limit_overrides={'max_input_bytes': 3})), 'ast-input-byte-bound-exceeded')

    def test_token_bound_exact_and_over(self):
        self.assertEqual(self.scan('checkGate("x");', limit_overrides={'max_tokens': 5})['status'], 'scanned')
        result = self.scan('checkGate("x");', limit_overrides={'max_tokens': 4})
        self.assertEqual(self.code(result), 'ast-token-bound-exceeded')
        self.assertEqual(result['metrics']['tokens'], 5)

    def test_real_default_million_token_boundary(self):
        # Parentheses add parser tokens without enough AST nodes to hit the
        # independently tighter node bound before the original token ceiling.
        source = 'const a=[' + ('(' * 8 + '0' + ')' * 8 + ',') * 55555 + '];' + ';' * 4
        exact = self.scan(source)
        self.assertEqual(exact['status'], 'scanned', exact['coverage']['issues'])
        self.assertEqual(exact['metrics']['tokens'], 1000000)
        over = self.scan(source + ';')
        self.assertEqual(self.code(over), 'ast-token-bound-exceeded')
        self.assertEqual(over['metrics']['tokens'], 1000001)

    def test_node_bound_during_allocation(self):
        result = self.scan('checkGate("x");', limit_overrides={'max_nodes': 3})
        self.assertEqual(self.code(result), 'ast-node-bound-exceeded')
        self.assertEqual(result['metrics']['node_allocations'], 4)

    def test_shorthand_copy_node_counts_toward_node_bound(self):
        result = self.scan('const a={x};', limit_overrides={'max_nodes': 7})
        self.assertEqual(self.code(result), 'ast-node-bound-exceeded')
        exact = self.scan('const a={x};', limit_overrides={'max_nodes': 8})
        self.assertEqual(exact['status'], 'scanned')
        self.assertEqual(exact['metrics']['node_allocations'], 8)
        self.assertEqual(exact['metrics']['visited_nodes'], 8)

    def test_all_ecmascript_line_terminators(self):
        for ending in ['\r', '\n', '\r\n', '\u2028', '\u2029']:
            data = ('/* 🧭 */' + ending + 'checkGate("two");').encode()
            result = self.scan(data)
            self.assertEqual(result['records'][0]['source']['line'], 2, repr(ending))
            self.assertEqual(result['records'][0]['source']['byte_start'], data.index(b'"two"'))

    def test_invalid_source_names_are_bounded_fixed_labels(self):
        for name in ['x'*20000, '\udcff.js', b'bytes.js', 'control\x00.js']:
            result = self.scan('x', source_name=name)
            self.assertEqual(self.code(result), 'ast-source-name-rejected')
            self.assertEqual(result['input']['name'], 'input.js')
            self.assertLess(len(channel.encode_report(result)), 4096)

    def test_posix_non_utf8_filename_has_structured_cli_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(os.fsdecode(os.fsencode(temp) + b'/\xff.js'))
            path.write_bytes(b'checkGate("x");')
            completed = subprocess.run([sys.executable, str(ROOT/'ast_candidates.py'),
                '--input', str(path), '--source-type', 'module', '--test-node-bundled-acorn'],
                capture_output=True, timeout=20)
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(completed.stderr, b'')
            self.assertEqual(self.code(json.loads(completed.stdout)), 'ast-source-name-rejected')

    def test_output_budget_includes_final_identity_and_newline(self):
        result = self.scan('checkGate("x");'*30, limit_overrides={'max_output_bytes': 16384})
        self.assertEqual(result['status'], 'scanned')
        self.assertLessEqual(len(channel.encode_report(result)), 16384)
        self.assertTrue(channel.encode_report(result).endswith(b'\n'))
        original = channel.incomplete('synthetic', b'x')
        original['padding'] = 'x'*4096
        result = channel.finalize(original, b'x', 'input.js', channel.limits_with({'max_output_bytes': 4096}), None)
        self.assertEqual(self.code(result), 'ast-output-bound-exceeded')
        self.assertLessEqual(len(channel.encode_report(result)), 4096)

    def test_shipping_output_cap_and_cli_compact_serialization(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'calls.js';path.write_text('checkGate("x");'*20000)
            completed=subprocess.run([sys.executable,str(ROOT/'ast_candidates.py'),
                '--input',str(path),'--source-type','module','--test-node-bundled-acorn'],
                cwd=temp,capture_output=True,timeout=25)
            self.assertEqual(completed.returncode,0,completed.stderr)
            self.assertLessEqual(len(completed.stdout),channel.DEFAULT_LIMITS['max_output_bytes'])
            report=json.loads(completed.stdout)
            self.assertEqual(len(report['records']),20000)
            self.assertEqual(completed.stdout,channel.encode_report(report))

    def test_limit_configuration_wrong_types_rejected(self):
        for limits in [[1],1,'bad',{'max_tokens':True}]:
            self.assertEqual(self.code(self.scan('x',limit_overrides=limits)), 'ast-limit-configuration-rejected')

    def test_nested_package_json_normalizes_recursion_error(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'dist').mkdir()
            module=root/'dist/acorn.js';module.write_text('throw 1;')
            (root/'package.json').write_text('['*10000+'0'+']'*10000)
            with mock.patch.object(channel,'_bounded_worker',side_effect=AssertionError('must not spawn')):
                result=channel.analyze_bytes(b'x',acorn_module=module)
            self.assertEqual(self.code(result),'ast-parser-dependency-unavailable')

    def test_worker_protocol_missing_input_identity_is_controlled(self):
        report=self.scan('x')
        del report['input']
        with mock.patch.object(channel,'_bounded_worker',return_value=json.dumps(report).encode()):
            result=self.scan('x')
        self.assertEqual(self.code(result),'ast-worker-protocol-rejected')

    def test_depth_bound_discards_already_collected_candidates(self):
        self.assertEqual(self.code(self.scan('checkGate("x");', limit_overrides={'max_depth': 2})), 'ast-depth-bound-exceeded')

    def test_record_bound_discards_partial_candidates(self):
        result = self.scan('checkGate("one");checkGate("two");', limit_overrides={'max_records': 1})
        self.assertEqual(self.code(result), 'ast-record-bound-exceeded')

    def test_output_bound_discards_partial_candidates(self):
        result = self.scan('checkGate("one");', limit_overrides={'max_output_bytes': 4096})
        self.assertEqual(self.code(result), 'ast-output-bound-exceeded')

    def test_no_target_execution_and_no_import_resolution(self):
        with tempfile.TemporaryDirectory() as temp:
            sentinel = Path(temp) / 'NEVER_WRITTEN'
            target = ('import "./nonexistent-side-effect-module.js";\n'
                      'require("node:fs").writeFileSync(' + json.dumps(str(sentinel)) + ',"executed");\n'
                      'process.exit(99); throw new Error("target-executed");\ncheckGate("syntactic_only");')
            result = self.scan(target)
            self.assertEqual(result['status'], 'scanned')
            self.assertFalse(sentinel.exists())
            self.assertEqual([r['key'] for r in result['records']], ['syntactic_only'])

    def test_parser_error_has_no_source_or_exception_text(self):
        result = self.scan('const SECRET_FIXTURE_MARKER = ;')
        self.assertEqual(self.code(result), 'ast-syntax-rejected')
        self.assertNotIn('SECRET_FIXTURE_MARKER', json.dumps(result))
        self.assertNotIn('Unexpected token', json.dumps(result))
        self.assertLessEqual(result['coverage']['issues'][0]['byte_offset'], result['input']['bytes'])

    def test_source_type_explicit_no_fallback(self):
        result = self.scan('export const x=1;', source_type='script')
        self.assertEqual(self.code(result), 'ast-syntax-rejected')
        self.assertEqual(self.code(self.scan('x', source_type='unambiguous')), 'ast-source-type-unsupported')

    def test_missing_dependency_is_not_silent_fallback(self):
        result = channel.analyze_bytes(b'checkGate("x");')
        self.assertEqual(self.code(result), 'ast-parser-dependency-required')

    def test_wrong_dependency_metadata_never_loaded(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'dist').mkdir()
            module = root / 'dist/acorn.js'; module.write_text('throw new Error("MUST_NOT_LOAD");')
            for metadata in [[], {'name': 'acorn', 'version': '8.16.0', 'main': 'dist/acorn.js'}]:
                (root / 'package.json').write_text(json.dumps(metadata))
                with mock.patch.object(channel, '_bounded_worker', side_effect=AssertionError('must not spawn')):
                    result = channel.analyze_bytes(b'checkGate("x");', acorn_module=module)
                self.assertEqual(self.code(result), 'ast-parser-version-or-layout-unsupported')

    def test_dependency_export_version_checked_again(self):
        # This is an original synthetic TOOL dependency stub, not target input
        # and not a bundled third-party parser. It tests rejection, not support.
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); (root/'dist').mkdir()
            (root/'package.json').write_text(json.dumps({'name':'acorn','version':'8.17.0','main':'dist/acorn.js'}))
            module=root/'dist/acorn.js';module.write_text('module.exports={version:"wrong",Parser:class{}};')
            result=channel.analyze_bytes(b'checkGate("x");',acorn_module=module)
            self.assertEqual(self.code(result),'ast-parser-version-unsupported')

    def test_symlinks_and_hardlinks_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);target=root/'target.js';target.write_bytes(b'x')
            link=root/'link.js';link.symlink_to(target)
            with self.assertRaises(channel.ChannelError):channel.bounded_read(link,100)
            hard=root/'hard.js';os.link(target,hard)
            with self.assertRaises(channel.ChannelError):channel.bounded_read(hard,100)

    def test_worker_protocol_bad_json_never_leaks_text(self):
        with mock.patch.object(channel,'_bounded_worker',return_value=b'SECRET_PROTOCOL_MARKER'):
            result=self.scan('x')
        self.assertEqual(self.code(result),'ast-worker-protocol-rejected')
        self.assertNotIn('SECRET_PROTOCOL_MARKER',json.dumps(result))


class ProcessTests(unittest.TestCase):
    def limits(self, **kw):
        return channel.limits_with(kw)

    def test_wall_timeout_kills_only_owned_handle(self):
        real_popen=subprocess.Popen;handles=[]
        def create(*args,**kwargs):
            handle=real_popen(*args,**kwargs);handles.append(handle);return handle
        with mock.patch.object(channel.subprocess,'Popen',side_effect=create):
            with self.assertRaisesRegex(channel.ChannelError,'ast-worker-time-bound-exceeded'):
                channel._bounded_worker([sys.executable,'-c','import time;time.sleep(10)'],b'',self.limits(wall_seconds=1))
        self.assertEqual(len(handles),1)
        self.assertIsNotNone(handles[0].poll())

    def test_stdout_capture_is_bounded(self):
        with self.assertRaisesRegex(channel.ChannelError,'ast-worker-output-bound-exceeded'):
            channel._bounded_worker([sys.executable,'-c','import sys;sys.stdout.write("x"*100000)'],b'',self.limits(max_output_bytes=4096))

    def test_stderr_capture_is_bounded(self):
        with self.assertRaisesRegex(channel.ChannelError,'ast-worker-output-bound-exceeded'):
            channel._bounded_worker([sys.executable,'-c','import sys;sys.stderr.write("x"*100000)'],b'',self.limits())

    def test_worker_environment_is_clean(self):
        program='import os,json;print(json.dumps(dict(os.environ)))'
        with mock.patch.dict(os.environ,{'NODE_OPTIONS':'--unwanted','NODE_PATH':'/unwanted'}):
            output=channel._bounded_worker([sys.executable,'-c',program],b'',self.limits())
        env=json.loads(output)
        self.assertNotIn('NODE_OPTIONS',env);self.assertNotIn('NODE_PATH',env)

    def test_nonzero_worker_has_fixed_failure_code(self):
        with self.assertRaisesRegex(channel.ChannelError,'ast-worker-resource-or-process-failed'):
            channel._bounded_worker([sys.executable,'-c','import sys;sys.exit(7)'],b'',self.limits())

    def test_cpu_limit_reaps_owned_busy_child(self):
        with self.assertRaisesRegex(channel.ChannelError,'ast-worker-resource-or-process-failed'):
            channel._bounded_worker([sys.executable,'-c','while True: pass'],b'',self.limits(cpu_seconds=1,wall_seconds=5))


if __name__ == '__main__':
    unittest.main(verbosity=2)
