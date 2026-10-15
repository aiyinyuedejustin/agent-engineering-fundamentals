"""Dependency-free overlay tests using original synthetic facts, no product files."""
import copy
import importlib.util
import json
import os
import subprocess
import tempfile
from pathlib import Path
import sys
import unittest
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from resolution_overlay import apply_resolution_overlay, baseline_fingerprint, validate_extension, write_new_outputs
from apply_catalog_overlay import apply_or_verify


def fixtures():
    numeric = {'expanded_expression': 'rgb(from #fff calc(r / 2) g b / 50%)',
        'audit_status': 'statically_resolved', 'method': 'synthetic', 'math': ['r: 255 / (2) = 255/2'],
        'rgb_255_exact': ['255/2', '255', '255'], 'srgb_exact': ['1/2', '1', '1'],
        'srgb_channels': [.5, 1., 1.], 'alpha': .5, 'alpha_exact': '1/2', 'srgb_in_gamut': True,
        'hex': '#80ffff', 'css_color_srgb': 'color(srgb 0.5 1 1 / 0.5)'}
    context = {'expanded_expression': 'initial', 'audit_status': 'context_dependent',
        'dependency_kind': 'custom_property_initial', 'hex': None, 'alpha': None,
        'consumer_example': {'is_token_hex': False}}
    rows = [{'id': 'raw:--base', 'profile': 'raw', 'name': '--base', 'declared': '#fff', 'hex': '#ffffff', 'alpha': 1., 'status': 'resolved'},
        {'id': 'light:--derived', 'profile': 'light', 'name': '--derived', 'declared': numeric['expanded_expression'], 'resolved_expression': numeric['expanded_expression'], 'status': 'unresolved', 'reason': 'conservative'},
        {'id': 'light:--context', 'profile': 'light', 'name': '--context', 'declared': 'initial', 'resolved_expression': 'initial', 'status': 'unresolved', 'reason': 'context'}]
    catalog = {'version': 'synthetic', 'records': rows, 'statistics': {'profile_records': 3, 'resolved_records': 1, 'unresolved_records': 2}}
    overlay = {'schema': 'claude.color-gap-overlay.recommendation.v1', 'validation': {
        'version': 'synthetic', 'baseline_projection_sha256': baseline_fingerprint(catalog),
        'expected_statistics': {'baseline_records': 3, 'baseline_resolved_records': 1, 'baseline_unresolved_records': 2,
            'derived_static_records': 1, 'derived_hex_records': 1, 'extended_srgb_records': 0,
            'context_dependent_records': 1, 'static_numeric_records': 2, 'hex_records': 2}},
        'records': [{'id': rows[1]['id'], 'expected_declared': rows[1]['declared'], 'resolution_extension': numeric},
                    {'id': rows[2]['id'], 'expected_declared': 'initial', 'resolution_extension': context}]}
    return catalog, overlay


class OverlayTests(unittest.TestCase):
    def setUp(self):
        self.catalog, self.overlay = fixtures()

    def test_append_only_and_no_input_mutation(self):
        original, overlay = copy.deepcopy(self.catalog), copy.deepcopy(self.overlay)
        result = apply_resolution_overlay(self.catalog, self.overlay)
        self.assertEqual({k: v for k, v in result.items() if k != 'resolution_extension'}, original)
        self.assertEqual(self.catalog, original)
        self.assertEqual(self.overlay, overlay)
        self.assertEqual(result['resolution_extension']['statistics']['static_numeric_records'], 2)

    def test_compact_projection_identical(self):
        compact = copy.deepcopy(self.catalog)
        compact['columns'] = ['profile', 'name', 'declared', 'hex', 'alpha', 'status']
        compact['records'] = [[row.get(k) for k in compact['columns']] for row in self.catalog['records']]
        self.assertEqual(baseline_fingerprint(compact), baseline_fingerprint(self.catalog))
        self.assertEqual(apply_resolution_overlay(compact, self.overlay)['records'], compact['records'])

    def test_explicit_record_id_mismatch_rejected(self):
        self.catalog['records'][1]['id'] = 'tampered:--not-the-token'
        with self.assertRaisesRegex(ValueError, 'record id'):
            apply_resolution_overlay(self.catalog, self.overlay)

    def test_unresolved_object_id_is_required(self):
        del self.catalog['records'][1]['id']
        with self.assertRaisesRegex(ValueError, 'record id is required'):
            apply_resolution_overlay(self.catalog, self.overlay)

    def test_resolved_object_id_is_required(self):
        del self.catalog['records'][0]['id']
        with self.assertRaisesRegex(ValueError, 'record id is required'):
            apply_resolution_overlay(self.catalog, self.overlay)

    def test_new_output_directory_and_exclusive_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'new'
            write_new_outputs(out, {'index.html': 'first', 'color-catalog.json': '{}'})
            self.assertEqual((out / 'index.html').read_text(), 'first')
            with self.assertRaisesRegex(ValueError, 'already exists'):
                write_new_outputs(out, {'index.html': 'second'})
            self.assertEqual((out / 'index.html').read_text(), 'first')

    def test_existing_empty_output_directory_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'already exists'):
                write_new_outputs(Path(tmp), {'index.html': 'value'})
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_output_directory_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'target'
            target.mkdir()
            link = Path(tmp) / 'link'
            link.symlink_to(target, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'already exists'):
                write_new_outputs(link, {'index.html': 'value'})
            self.assertEqual(list(target.iterdir()), [])
            self.assertTrue(link.is_symlink())

    def test_existing_regular_file_output_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'existing-file'
            out.write_text('original')
            with self.assertRaisesRegex(ValueError, 'already exists'):
                write_new_outputs(out, {'index.html': 'new'})
            self.assertEqual(out.read_text(), 'original')

    def test_existing_output_symlink_file_cannot_truncate_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / 'input.html'
            original.write_text('original')
            out = Path(tmp) / 'existing'
            out.mkdir()
            (out / 'index.html').symlink_to(original)
            with self.assertRaisesRegex(ValueError, 'already exists'):
                write_new_outputs(out, {'index.html': 'new'})
            self.assertEqual(original.read_text(), 'original')
            self.assertTrue((out / 'index.html').is_symlink())

    def test_exclusive_file_creation_rejects_late_hardlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / 'input.html'
            original.write_text('original')
            out = Path(tmp) / 'new'
            mkdir = Path.mkdir
            def interposed(path, *args, **kwargs):
                result = mkdir(path, *args, **kwargs)
                if path == out:
                    os.link(original, out / 'index.html')
                return result
            with mock.patch.object(Path, 'mkdir', interposed):
                with self.assertRaises(FileExistsError):
                    write_new_outputs(out, {'index.html': 'new'})
            self.assertEqual(original.read_text(), 'original')
            self.assertEqual((out / 'index.html').read_text(), 'original')

    def test_output_hardlink_cannot_truncate_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / 'input.html'
            original.write_text('keep input bytes')
            out = Path(tmp) / 'existing'
            out.mkdir()
            os.link(original, out / 'index.html')
            with self.assertRaisesRegex(ValueError, 'already exists'):
                write_new_outputs(out, {'color-catalog.json': '{}', 'index.html': 'bad'})
            self.assertEqual(original.read_text(), 'keep input bytes')
            self.assertEqual((out / 'index.html').read_text(), 'keep input bytes')
            self.assertFalse((out / 'color-catalog.json').exists())

    def test_public_cli_rejects_hardlink_output_without_changing_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paths = {name: base / name for name in ('catalog.json', 'browser.html', 'overlay.json', 'template.html')}
            paths['catalog.json'].write_text(json.dumps(self.catalog))
            paths['browser.html'].write_text('<script type="application/json" id="color-data">' + json.dumps(self.catalog) + '</script>')
            paths['overlay.json'].write_text(json.dumps(self.overlay))
            paths['template.html'].write_text('__COLOR_DATA__')
            old = {name: path.read_bytes() for name, path in paths.items()}
            out = base / 'existing'
            out.mkdir()
            os.link(paths['browser.html'], out / 'index.html')
            command = [sys.executable, str(Path(__file__).resolve().parents[1] / 'apply_catalog_overlay.py'),
                '--catalog', str(paths['catalog.json']), '--browser', str(paths['browser.html']),
                '--overlay', str(paths['overlay.json']), '--template', str(paths['template.html']), '--output', str(out)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn('already exists', result.stderr)
            self.assertEqual({name: path.read_bytes() for name, path in paths.items()}, old)
            self.assertEqual(list(out.iterdir()), [out / 'index.html'])

    def test_full_builder_rejects_hardlink_output(self):
        import build_color_catalog as builder
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            template = base / 'template.html'
            template.write_text('__COLOR_DATA__')
            minimal = {'product': 'Synthetic', 'version': 'test', 'families': [], 'profiles': {},
                       'statistics': {}, 'blocks': [], 'sources': [], 'records': []}
            out = base / 'existing'
            out.mkdir()
            os.link(template, out / 'index.html')
            with self.assertRaisesRegex(ValueError, 'already exists'):
                builder.write_outputs(minimal, out, template)
            self.assertEqual(template.read_text(), '__COLOR_DATA__')
            self.assertFalse((out / 'color-catalog.json').exists())

    def test_baseline_mismatch_rejected(self):
        self.catalog['records'][0]['hex'] = '#000000'
        with self.assertRaisesRegex(ValueError, 'fingerprint'):
            apply_resolution_overlay(self.catalog, self.overlay)

    def test_version_mismatch_rejected(self):
        self.catalog['version'] = 'other'
        with self.assertRaisesRegex(ValueError, 'version'):
            apply_resolution_overlay(self.catalog, self.overlay)

    def test_duplicate_overlay_rejected(self):
        self.overlay['records'].append(self.overlay['records'][0])
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            apply_resolution_overlay(self.catalog, self.overlay)

    def test_missing_overlay_rejected(self):
        self.overlay['records'].pop()
        with self.assertRaisesRegex(ValueError, 'every baseline'):
            apply_resolution_overlay(self.catalog, self.overlay)

    def test_wrong_declaration_rejected(self):
        self.overlay['records'][0]['expected_declared'] = '#000'
        with self.assertRaisesRegex(ValueError, 'declaration'):
            apply_resolution_overlay(self.catalog, self.overlay)

    def test_wrong_expanded_expression_rejected(self):
        self.catalog['records'][1]['resolved_expression'] = '#000'
        with self.assertRaisesRegex(ValueError, 'Expanded expression'):
            apply_resolution_overlay(self.catalog, self.overlay)

    def test_baseline_statistics_mismatch_rejected(self):
        self.catalog['statistics']['resolved_records'] = 99
        with self.assertRaisesRegex(ValueError, 'statistics'):
            apply_resolution_overlay(self.catalog, self.overlay)

    def test_summary_mismatch_rejected(self):
        self.overlay['validation']['expected_statistics']['hex_records'] = 99
        with self.assertRaisesRegex(ValueError, 'statistics'):
            apply_resolution_overlay(self.catalog, self.overlay)

    def test_public_cli_can_rebuild_identical_extension(self):
        annotated = apply_or_verify(self.catalog, self.overlay)
        self.assertEqual(apply_or_verify(annotated, self.overlay), annotated)

    def test_public_cli_rejects_changed_existing_extension(self):
        annotated = apply_or_verify(self.catalog, self.overlay)
        annotated['resolution_extension']['records']['light:--derived']['hex'] = '#ffffff'
        with self.assertRaisesRegex(ValueError, 'Existing resolution extension differs'):
            apply_or_verify(annotated, self.overlay)

    def test_reapplying_rejected(self):
        applied = apply_resolution_overlay(self.catalog, self.overlay)
        with self.assertRaisesRegex(ValueError, 'already'):
            apply_resolution_overlay(applied, self.overlay)

    def test_context_has_no_numeric_color(self):
        self.overlay['records'][1]['resolution_extension']['alpha'] = .1
        with self.assertRaisesRegex(ValueError, 'fabricated'):
            apply_resolution_overlay(self.catalog, self.overlay)

    def test_context_fallback_is_not_token_hex(self):
        self.overlay['records'][1]['resolution_extension']['consumer_example']['is_token_hex'] = True
        with self.assertRaisesRegex(ValueError, 'Fallback'):
            apply_resolution_overlay(self.catalog, self.overlay)

    def test_extended_channels_preserved(self):
        v = self.overlay['records'][0]['resolution_extension']
        v.update(srgb_channels=[-1., 2., .5], srgb_exact=['-1', '2', '1/2'], rgb_255_exact=['-255', '510', '255/2'],
                 srgb_in_gamut=False, hex=None, css_color_srgb='color(srgb -1 2 0.5 / 0.5)')
        validate_extension(v)
        v['hex'] = '#00ff80'
        with self.assertRaisesRegex(ValueError, 'clipped HEX'):
            validate_extension(v)

    def test_rounded_hex_consistency(self):
        v = self.overlay['records'][0]['resolution_extension']
        v['hex'] = '#7fffff'
        with self.assertRaisesRegex(ValueError, 'HEX mismatch'):
            validate_extension(v)

    def test_serialized_color_preserves_channels(self):
        v = self.overlay['records'][0]['resolution_extension']
        v['css_color_srgb'] = 'color(srgb 0.4 1 1 / 0.5)'
        with self.assertRaisesRegex(ValueError, 'color\\(srgb\\) mismatch'):
            validate_extension(v)

    def test_exact_rational_consistency(self):
        v = self.overlay['records'][0]['resolution_extension']
        v['rgb_255_exact'][0] = '127'
        with self.assertRaisesRegex(ValueError, 'RGB/sRGB mismatch'):
            validate_extension(v)

    def test_nonfinite_channels_rejected(self):
        v = self.overlay['records'][0]['resolution_extension']
        v['srgb_channels'][0] = float('nan')
        with self.assertRaisesRegex(ValueError, 'Invalid sRGB'):
            validate_extension(v)


if __name__ == '__main__':
    unittest.main()
