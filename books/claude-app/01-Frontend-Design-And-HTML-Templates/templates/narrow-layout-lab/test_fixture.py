#!/usr/bin/env python3
"""Original static/build tests. No browser, package install, network or source edits."""
import base64
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import build_fixture as build


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.data = {}
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == 'script':
            self.current = attrs.get('id', 'runtime')
            self.data[self.current] = ''

    def handle_data(self, data):
        if self.current:
            self.data[self.current] += data

    def handle_endtag(self, tag):
        if tag == 'script':
            self.current = None


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lock, cls.payloads, cls.hashes = build.load_sources()
        cls.output = build.render_fixture(cls.lock, cls.payloads, cls.hashes)
        cls.markup = Markup()
        cls.markup.feed(cls.output.decode())

    def test_01_fixed_sources_and_bundle(self):
        self.assertEqual(len(self.payloads), 6)
        self.assertEqual(self.lock['bundleSha256'], hashlib.sha256(build.canonical(self.lock['templates'])).hexdigest())

    def test_02_embedded_source_byte_identity(self):
        payload = json.loads(self.markup.data['fixture-data'])
        for item in payload['templates']:
            with self.subTest(source=item['filename']):
                data = base64.b64decode(item['base64'], validate=True)
                self.assertEqual(data, (build.ROOT / build.SOURCE_REL / item['filename']).read_bytes())
                self.assertEqual(len(data), item['bytes'])
                self.assertEqual(hashlib.sha256(data).hexdigest(), item['sha256'])

    def test_03_generated_artifact_reproducible(self):
        self.assertEqual((build.HERE / 'fixture.html').read_bytes(), self.output)
        self.assertEqual(self.output, build.render_fixture(self.lock, self.payloads, self.hashes))

    def test_04_outer_sandbox_has_only_scripts(self):
        frames = [attrs for tag, attrs in self.markup.tags if tag == 'iframe']
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0]['sandbox'], 'allow-scripts')
        self.assertEqual(frames[0]['referrerpolicy'], 'no-referrer')
        self.assertNotIn('src', frames[0])
        self.assertNotIn('allow', frames[0])

    def test_05_inner_preview_sandbox_is_unchanged(self):
        source = base64.b64decode(self.payloads[2]['base64']).decode()
        self.assertIn('sandbox=""', source)
        self.assertIn("script-src 'none'", source)
        self.assertIn("frame-src 'none'", source)
        self.assertIn('function sanitizeStatic(source)', source)
        self.assertIn('current.cloneNode(false)', source)

    def test_06_csp_hashes_exact_scripts_and_denies_network(self):
        policies = [a['content'] for t, a in self.markup.tags if t == 'meta' and a.get('http-equiv') == 'Content-Security-Policy']
        self.assertEqual(len(policies), 1)
        policy = policies[0]
        expected = self.hashes | {base64.b64encode(hashlib.sha256(build.RUNTIME.encode()).digest()).decode()}
        self.assertEqual(set(re.findall(r"'sha256-([^']+)'", policy)), expected)
        self.assertEqual(len(expected), 7)
        self.assertIn("default-src 'none'", policy)
        self.assertIn("connect-src 'none'", policy)
        self.assertIn("frame-src about:", policy)
        self.assertIn("form-action 'none'", policy)
        self.assertNotIn("script-src 'unsafe-inline'", policy)
        self.assertNotIn('unsafe-eval', policy)
        self.assertNotIn('https:', policy)

    def test_07_fixture_has_no_external_or_arbitrary_source_input(self):
        self.assertFalse(any(t in ('input', 'textarea', 'form', 'object', 'embed', 'link', 'base') for t, _ in self.markup.tags))
        self.assertFalse(any('src' in a or 'href' in a for _, a in self.markup.tags))
        self.assertNotRegex(build.RUNTIME, r'\b(fetch|XMLHttpRequest|WebSocket|eval)\s*\(')
        self.assertNotIn('location.search', build.RUNTIME)
        self.assertNotIn('location.hash', build.RUNTIME)
        self.assertNotIn('postMessage', build.RUNTIME)

    def test_08_three_fixed_widths_and_no_scaling(self):
        buttons = [a['data-width'] for t, a in self.markup.tags if t == 'button' and 'data-width' in a]
        self.assertEqual(buttons, ['375', '768', '1024'])
        self.assertIn('height: 900px', build.SHELL)
        self.assertIn('max-width: none', build.SHELL)
        self.assertIn('overflow-x: auto', build.SHELL)
        self.assertNotRegex(build.SHELL, r'\b(transform|zoom)\s*:')

    def test_09_output_traversal_and_non_html_rejected(self):
        for name in ['../outside.html', '/tmp/outside.html', 'sub/out.html', '.hidden.html', 'x.txt', 'file.html/../file.html', 'x\\y.html']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                build.valid_output(name)

    def test_10_existing_output_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'safe.html'
            path.write_bytes(b'keep me')
            with self.assertRaises(FileExistsError):
                build.create_new('safe.html', b'replace', directory)
            self.assertEqual(path.read_bytes(), b'keep me')

    def test_11_output_symlink_never_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / 'target').write_bytes(b'keep me')
            (path / 'out.html').symlink_to(path / 'target')
            with self.assertRaises(FileExistsError):
                build.create_new('out.html', b'replace', directory)
            self.assertEqual((path / 'target').read_bytes(), b'keep me')
            self.assertTrue((path / 'out.html').is_symlink())

    def test_12_new_output_only(self):
        with tempfile.TemporaryDirectory() as directory:
            build.create_new('fresh.html', b'new', directory)
            self.assertEqual((Path(directory) / 'fresh.html').read_bytes(), b'new')

    def inputs(self, directory):
        path = Path(directory)
        for item in self.payloads:
            (path / item['filename']).write_bytes(base64.b64decode(item['base64']))
        lock = path / 'source-lock.json'
        lock.write_text(json.dumps(self.lock))
        return path, lock

    def test_13_source_drift_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path, lock = self.inputs(directory)
            (path / build.FILES[0][0]).write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'Source drift'):
                build.load_sources(path, lock)

    def test_14_lock_digest_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path, lock = self.inputs(directory)
            changed = json.loads(lock.read_text())
            changed['templates'][0]['sha256'] = '0' * 64
            lock.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, 'bundle digest mismatch'):
                build.load_sources(path, lock)

    def test_15_source_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path, lock = self.inputs(directory)
            target = path / build.FILES[0][0]
            target.unlink()
            target.symlink_to(build.ROOT / build.SOURCE_REL / target.name)
            with self.assertRaisesRegex(ValueError, 'non-symlink'):
                build.load_sources(path, lock)

    def test_16_extra_or_reordered_sources_rejected(self):
        for mutate in [lambda x: x.reverse(), lambda x: x.append(x[0])]:
            with self.subTest(mutate=mutate), tempfile.TemporaryDirectory() as directory:
                path, lock = self.inputs(directory)
                changed = json.loads(lock.read_text())
                mutate(changed['templates'])
                lock.write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError, 'exactly the six'):
                    build.load_sources(path, lock)

    def test_17_check_cli_read_only(self):
        before = (build.HERE / 'fixture.html').stat().st_mtime_ns
        result = subprocess.run([sys.executable, str(build.HERE / 'build_fixture.py'), '--check', 'fixture.html'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASS: six sources', result.stdout)
        self.assertEqual((build.HERE / 'fixture.html').stat().st_mtime_ns, before)

    def test_18_cli_refuses_default_overwrite(self):
        before = (build.HERE / 'fixture.html').read_bytes()
        result = subprocess.run([sys.executable, str(build.HERE / 'build_fixture.py')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual((build.HERE / 'fixture.html').read_bytes(), before)

    def test_19_contract_discloses_actual_scope(self):
        for claim in ['无设备仿真', '200% 缩放', '不是独立读取子页面 innerWidth', 'localStorage 会被拒绝', '不把静态检查算作执行证据']:
            self.assertIn(claim, build.SHELL)

    def test_20_runtime_script_matches_csp_hash_bytes(self):
        self.assertEqual(self.markup.data['runtime'], build.RUNTIME)
        self.assertNotIn('</script', build.RUNTIME.lower())


if __name__ == '__main__':
    unittest.main(verbosity=2)
