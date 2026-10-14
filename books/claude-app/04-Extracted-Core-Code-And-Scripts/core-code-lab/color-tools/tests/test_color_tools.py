"""Portable tests: only generated, original fixtures; no product files needed."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import build_color_catalog as build
import extract_design_tokens as extract
from inventory_inputs import source_bases, source_path, validate_inventory


def fixture_css():
    palette = ';'.join(f'--cds-{family}-{shade}:#123456' for family in build.FAMILIES for shade in build.SHADES)
    return ('/* 原创测试数据，不是产品样式 */\n:where(:root,:host){' + palette + ';'
            '--cds-hsl-gray-0:0 0% 100%;--_gray-0:var(--cds-hsl-gray-0);--text-body:16px;'
            '--cds-text-primary:#123456;--cds-bg-unsupported:currentColor;'
            '--cds-bg-relative:rgb(from #fff calc(r / 2) g b);'
            '--cds-bg-fallback:var(--missing, #fff);--cds-bg-keyword:initial;'
            '--cds-bg-cycle:var(--cycle);--cycle:var(--cds-bg-cycle);'
            '--cds-bg-missing:var(--missing);--alias:#abcdef;--cds-text-alias:var(--alias)}'
            '@font-face{font-family:Fixture;src:url(do-not-read.woff2)}'
            '.cds-root{--cds-surface-0:#fff;--cds-fill-field:#ffffff80;--cds-backdrop:#0006}'
            '@layer components{.cds-root{--cds-surface-0:#eee;--cds-button-on-content:#123456}}'
            '@media screen{' + build.DARK + '{--cds-surface-0:#000}}'
            '@media(prefers-color-scheme:dark){.cds-root{--cds-surface-0:#f00}}'
            '@supports(color:light-dark(white,black)){.cds-root{--cds-surface-0:#0f0}}'
            '.cds-dark-scope[data-mode=dark]{--cds-surface-0:#00f}'
            '@layer base{[data-theme=claude],[data-theme=claude][data-mode=light]{--bg-000:0 0% 90%}'
            '[data-theme=claude][data-mode=dark]{--bg-000:0 0% 10%}}'
            '[data-color-version=v2][data-theme=claude],[data-color-version=v2][data-theme=claude][data-mode=light]{--bg-000:var(--_gray-0)}')


class ParserTests(unittest.TestCase):
    def test_hex_alpha_rounding_and_hsl(self):
        for expression, color, alpha in [('#123', '#112233', 1), ('#0006', '#000000', .4),
                                         ('#ffffff80', '#ffffff', 128 / 255), ('transparent', '#000000', 0),
                                         ('120 100% 50%', '#00ff00', 1), ('rgb(255 0 0 / 20%)', '#ff0000', .2)]:
            result = build.color_fields(expression)
            self.assertEqual(result['hex'], color)
            self.assertEqual(result['alpha'], alpha)

    def test_relative_alpha_and_transparent_mix(self):
        self.assertEqual(build.color_fields('hsl(from #12345680 h s l / 10%)')['alpha'], .1)
        self.assertEqual(build.color_fields('color-mix(in srgb, #12345680 10%, transparent)')['alpha'], (128 / 255) * .1)

    def test_unknown_invalid_non_color_rejected(self):
        for expression in ['#12345', '#1234567', '#123456789', 'currentColor', 'initial', '10px',
                           'var(--missing)', 'rgb(from #fff calc(r / 2) g b)', 'color-mix(in oklab, red, blue)',
                           'hsl(5 10% 30%)', 'rgb(256 0 0)', '0 101% 50%', 'rgba(1,2,3,2)']:
            with self.subTest(expression=expression), self.assertRaises(build.Unresolved):
                build.parse_color(expression)

    def test_variable_cycle_missing_fallback(self):
        for env in [{'--a': {'value': 'var(--b)'}, '--b': {'value': 'var(--a)'}},
                    {'--a': {'value': 'var(--missing)'}}, {'--a': {'value': 'var(--b, #fff)'}}]:
            with self.assertRaises(build.Unresolved):
                build.expanded('--a', env)

    def test_scanner_preserves_utf8_byte_ranges_and_nesting(self):
        raw = '/* 注释 */ @media screen { :root { /* 色 */ --x: "a;{中}";--y:rgb(1 2 3 / .5) } }'.encode()
        nodes, validation = extract.scan(raw)
        self.assertFalse(any(validation.values()))
        node = nodes[1]
        self.assertEqual(extract.contexts(nodes, 1), ['@media screen'])
        for declaration in node['decl']:
            actual = raw[declaration['start']:declaration['end']].decode().strip()
            self.assertEqual(re.sub(r'\s*:\s*', ':', actual, count=1), declaration['name'] + ':' + declaration['value'])


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.resources = self.root / 'source resources'
        self.ion = self.resources / 'ion-dist'
        self.ion.mkdir(parents=True)
        self.css = self.ion / 'renamed-main.css'
        self.css.write_text(fixture_css(), encoding='utf-8')
        self.inventory = self.root / 'private inventory.json'
        self.data = extract.extract_inventory(self.resources)
        self.save()

    def save(self):
        self.inventory.write_text(json.dumps(self.data, ensure_ascii=False), encoding='utf-8')

    def build(self, **kwargs):
        return build.build_catalog(self.inventory, self.resources, None, **kwargs)

    def test_generated_fixture_has_all_raw_palette_names(self):
        catalog = self.build()
        raw = [r for r in catalog['records'] if r['kind'] == 'raw']
        self.assertEqual(len(raw), 315)
        self.assertEqual({r['name'] for r in raw}, {f'--cds-{f}-{s}' for f in build.FAMILIES for s in build.SHADES})
        self.assertTrue(all(r['status'] == 'resolved' for r in raw))
        self.assertNotIn('--text-body', catalog['definition_inventory'])

    def test_unsupported_raw_value_is_counted_as_unresolved(self):
        self.css.write_text(fixture_css().replace('--cds-gray-0:#123456', '--cds-gray-0:currentColor'), encoding='utf-8')
        self.data = extract.extract_inventory(self.resources)
        self.save()
        catalog = self.build()
        self.assertEqual(catalog['profiles']['raw']['resolved_count'], 314)
        self.assertEqual(catalog['statistics']['profiles']['raw']['unresolved'], 1)
        record = next(r for r in catalog['records'] if r['id'] == 'raw:--cds-gray-0')
        self.assertEqual(record['status'], 'unresolved')
        self.assertNotIn('hex', record)

    def test_profiles_keep_layer_order_legacy_and_contexts_separate(self):
        records = {(r['profile'], r['name']): r for r in self.build()['records']}
        self.assertEqual(records['cds_light', '--cds-surface-0']['hex'], '#ffffff')
        self.assertEqual(records['cds_dark', '--cds-surface-0']['hex'], '#000000')
        self.assertNotEqual(records['legacy_v1_light', '--bg-000']['hex'], records['legacy_v2_light', '--bg-000']['hex'])
        self.assertEqual(records['cds_light', '--cds-fill-field']['alpha'], 128 / 255)
        self.assertEqual(records['cds_light', '--cds-backdrop']['alpha'], .4)

    def test_unresolved_expressions_never_get_fabricated_color(self):
        catalog = self.build()
        unresolved = [r for r in catalog['records'] if r['status'] == 'unresolved']
        self.assertEqual(len(unresolved), 12)
        for record in unresolved:
            self.assertIn('declared', record)
            self.assertIn('reason', record)
            self.assertNotIn('hex', record)
            self.assertNotIn('alpha', record)
        expanded = [r for r in unresolved if r['name'] == '--cds-bg-relative']
        self.assertEqual(expanded[0]['resolved_expression'], 'rgb(from #fff calc(r / 2) g b)')

    def test_inventory_does_not_open_fonts_or_copy_source(self):
        (self.ion / 'do-not-read.woff2').write_bytes(b'not a font')
        data = extract.extract_inventory(self.resources)
        self.assertEqual(data, self.data)
        self.assertNotIn('font_assets', data)
        self.assertNotIn('nodes', data)
        self.assertTrue(any(b['selector'] == '@font-face' for b in data['blocks']))

    def test_duplicate_sources_are_hashed_and_analyzed_once(self):
        shutil.copyfile(self.css, self.ion / 'z-duplicate.css')
        data = extract.extract_inventory(self.resources)
        self.assertEqual(len(data['sources']), 2)
        self.assertEqual(len(data['statistics']), 1)
        self.assertEqual(data['sources'][1]['duplicate_of'], data['sources'][0]['id'])
        self.assertEqual(data['tokens'], self.data['tokens'])

    def test_hash_mismatch_is_rejected(self):
        self.css.write_text(fixture_css() + '/* changed */', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            self.build()

    def test_color_anchor_tampering_is_rejected(self):
        self.data['tokens']['--cds-text-primary']['definitions'][0]['value'] = '#ffffff'
        self.save()
        with self.assertRaisesRegex(ValueError, 'anchor mismatch'):
            self.build()

    def test_noncolor_resolution_dependency_is_also_verified(self):
        self.data['tokens']['--alias']['definitions'][0]['value'] = '#ffffff'
        self.save()
        with self.assertRaisesRegex(ValueError, 'anchor mismatch'):
            self.build()

    def test_bad_byte_ranges_are_rejected_even_if_hash_matches(self):
        self.data['tokens']['--cds-text-primary']['definitions'][0]['byte_end'] = 10**9
        self.save()
        with self.assertRaisesRegex(ValueError, 'byte bounds'):
            self.build()

    def test_missing_palette_and_ambiguous_sources_fail(self):
        self.data['tokens'].pop('--cds-gray-0')
        self.save()
        with self.assertRaisesRegex(ValueError, 'unique complete ion palette'):
            self.build()
        with self.assertRaisesRegex(ValueError, 'missing required root palette'):
            self.build(primary_source='f000')

    def test_explicit_primary_source_id_or_path(self):
        self.assertEqual(self.build(primary_source='f000')['records'], self.build(primary_source='ion/renamed-main.css')['records'])
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            self.build(primary_source='unrecognized.css')

    def test_multiple_full_ion_sources_require_selection(self):
        (self.ion / 'other.css').write_text(fixture_css() + '/* distinct */', encoding='utf-8')
        self.data = extract.extract_inventory(self.resources)
        self.save()
        with self.assertRaisesRegex(ValueError, 'unique complete ion palette'):
            self.build()
        self.assertEqual(self.build(primary_source='ion/renamed-main.css')['statistics']['raw_palette_entries'], 315)

    def test_source_traversal_and_symlink_escape_are_rejected(self):
        bases = source_bases(self.resources)
        for path in ['/etc/passwd', 'ion/../../outside.css', 'unknown/a.css', 'ion\\..\\outside.css']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                source_path(path, bases)
        outside = self.root / 'outside.css'
        outside.write_text(':root{--x:#fff}')
        try:
            (self.ion / 'escape.css').symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest('Symlinks are unavailable on this platform')
        with self.assertRaisesRegex(ValueError, 'leaves its declared directory'):
            extract.extract_inventory(self.resources)

    def test_missing_asar_root_has_actionable_error(self):
        with self.assertRaisesRegex(ValueError, 'supply --asar-root'):
            source_path('asar/main.css', source_bases(self.resources))

    def test_malformed_css_is_rejected(self):
        self.css.write_text(':root{--x:#fff', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Unclosed CSS syntax'):
            extract.extract_inventory(self.resources)

    def test_schema_rejects_duplicate_ids_and_unknown_blocks(self):
        broken = copy.deepcopy(self.data)
        broken['sources'].append(broken['sources'][0])
        with self.assertRaisesRegex(ValueError, 'unique'):
            validate_inventory(broken)
        broken = copy.deepcopy(self.data)
        broken['tokens']['--cds-gray-0']['definitions'][0]['block'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'known block'):
            validate_inventory(broken)

    def test_schema_rejects_nonobject_entries_without_traceback(self):
        for field in ('sources', 'blocks', 'tokens', 'definitions'):
            broken = copy.deepcopy(self.data)
            if field in ('sources', 'blocks'):
                broken[field][0] = None
            elif field == 'tokens':
                broken['tokens']['--cds-gray-0'] = None
            else:
                broken['tokens']['--cds-gray-0']['definitions'][0] = None
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'must be an object'):
                validate_inventory(broken)

    def test_browser_payload_is_compact_offline_and_escaped(self):
        catalog = self.build(product='Example </script><script>bad()</script>', version='test-1')
        payload = build.browser_payload(catalog)
        self.assertNotIn('blocks', payload)
        self.assertNotIn('definition_inventory', payload)
        self.assertTrue(all('resolution_chain' not in r and 'byte_start' not in r for r in payload['records']))
        template = (TOOLS / 'color_catalog_template.html').read_text(encoding='utf-8')
        html = build.render_html(catalog, template)
        for forbidden in ('src="http', 'href="http', '@font-face', 'fetch(', '__COLOR_DATA__', '<script>bad()'):
            self.assertNotIn(forbidden, html)
        embedded = re.search(r'<script type="application/json" id="color-data">(.*?)</script>', html, re.S)[1]
        self.assertEqual(json.loads(embedded), payload)
        self.assertEqual(payload['records'][0]['source_label'], 'ion/renamed-main.css')

    def test_bad_template_fails_before_output(self):
        for template in ('missing marker', '__COLOR_DATA____COLOR_DATA__'):
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                build.render_html(self.build(), template)
        bad = self.root / 'bad.html'
        bad.write_text('invalid')
        output = self.root / 'not-created'
        with self.assertRaises(ValueError):
            build.write_outputs(self.build(), output, bad)
        self.assertFalse(output.exists())

    def test_cli_is_portable_after_copy_and_works_from_unrelated_cwd(self):
        moved = self.root / 'copied tools'
        shutil.copytree(TOOLS, moved, ignore=shutil.ignore_patterns('__pycache__', 'node_modules'))
        elsewhere = self.root / 'unrelated cwd'
        elsewhere.mkdir()
        inventory = self.root / 'fresh' / 'inventory.json'
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        command = [sys.executable, str(moved / 'extract_design_tokens.py'), '--resources', str(self.resources), '--output', str(inventory)]
        result = subprocess.run(command, cwd=elsewhere, env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = self.root / 'output with spaces'
        command = [sys.executable, '-O', str(moved / 'build_color_catalog.py'), '--inventory', str(inventory), '--resources', str(self.resources), '--output', str(output), '--product', 'Fixture Product', '--version', 'custom-42']
        result = subprocess.run(command, cwd=elsewhere, env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        catalog = json.loads((output / 'color-catalog.json').read_text())
        self.assertEqual(catalog['version'], 'custom-42')
        self.assertEqual(catalog['product'], 'Fixture Product')
        self.assertTrue((output / 'index.html').is_file())
        self.css.write_text(fixture_css() + '/* changed */', encoding='utf-8')
        result = subprocess.run(command, cwd=elsewhere, env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('hash mismatch', result.stderr)

    def test_record_expectation_fails_before_output(self):
        output = self.root / 'not-created'
        command = [sys.executable, str(TOOLS / 'build_color_catalog.py'), '--inventory', str(self.inventory), '--resources', str(self.resources), '--output', str(output), '--expect-records', '1341']
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('Expected 1341 records', result.stderr)
        self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
