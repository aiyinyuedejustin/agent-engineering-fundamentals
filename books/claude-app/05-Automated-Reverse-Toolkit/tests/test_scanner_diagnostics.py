"""Original synthetic fixtures. Executes Python scanner only, never target JS."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from toolkit.literals import literal_candidates, load_rules, tokens
from toolkit.inventory import snapshot, verify_snapshot, canonical
from toolkit.safeio import ToolkitError, digest
from toolkit.diffing import diff_snapshots, readable

class DiagnosticTests(unittest.TestCase):
    def caught(self, data):
        with self.assertRaises(ToolkitError) as result:
            tokens(data)
        self.assertIs(type(result.exception), ToolkitError)
        return result.exception.scan_diagnostic

    def test_nested_template_rejection_remains_explicit(self):
        data = b"const t = `${`don't`}`;"
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / 'nested.js').write_bytes(data)
            doc = snapshot(Path(folder), 'synthetic')
        self.assertEqual(doc['coverage']['file_status_counts'], {'scan-incomplete': 1})
        self.assertFalse(doc['coverage']['complete_within_declared_scope'])
        self.assertEqual(doc['records'], [])
        issue = doc['coverage']['issues'][0]
        self.assertEqual(issue['error_type'], 'ToolkitError')
        self.assertEqual(issue['diagnostic']['code'], 'js-quoted-state-unclosed')
        self.assertEqual(issue['diagnostic']['input_validity'], 'not-determined')

    def test_source_and_token_values_are_never_serialized(self):
        diagnostic = self.caught(b"const marker='PRIVATE_SENTINEL")
        encoded = json.dumps(diagnostic)
        self.assertNotIn('PRIVATE_SENTINEL', encoded)
        self.assertNotIn('marker', encoded)
        self.assertNotIn('message', diagnostic)
        self.assertEqual(diagnostic['quote_kind'], 'single')

    def test_offset_is_bytes_and_cursor_bounded(self):
        data = '/* 原创 🧪 */ const q = "private\\'.encode()
        diagnostic = self.caught(data)
        self.assertEqual(diagnostic['byte_start'], data.index(b'"'))
        self.assertEqual(diagnostic['byte_cursor'], len(data))
        self.assertNotEqual(diagnostic['byte_start'], data.decode('utf-8').index(chr(34)))

    def test_unclosed_comment_has_static_code(self):
        diagnostic = self.caught(b'/* synthetic')
        self.assertEqual(diagnostic['code'], 'js-comment-state-unclosed')
        self.assertNotIn('quote_kind', diagnostic)
        self.assertEqual(diagnostic['byte_cursor'], 12)

    def test_token_budget_unchanged_and_explicit(self):
        diagnostic = self.caught(b';' * 1000001)
        self.assertEqual(diagnostic['code'], 'js-token-bound-exceeded')
        self.assertEqual(diagnostic['category'], 'resource-bound')
        self.assertEqual(diagnostic['token_limit'], 1000000)
        self.assertEqual(diagnostic['tokens_observed'], 1000001)
        self.assertEqual(diagnostic['byte_cursor'], 1000001)

    def test_budget_cursor_is_bounded_after_regex_escape_overshoot(self):
        data = b';' * 1000000 + bytes([47, 92])
        diagnostic = self.caught(data)
        self.assertEqual(diagnostic['code'], 'js-token-bound-exceeded')
        self.assertEqual(diagnostic['tokens_observed'], 1000001)
        self.assertEqual(diagnostic['byte_cursor'], len(data))
        self.assertLessEqual(diagnostic['byte_start'], len(data))

    def test_simple_interpolation_remains_opaque(self):
        self.assertEqual(literal_candidates(b'const t = `${checkGate("synthetic_real")}`;', load_rules()), [])

    def test_valid_plain_literal_is_unchanged(self):
        records = literal_candidates(b'checkGate("synthetic_visible", false)', load_rules())
        self.assertEqual(records[0]['key'], 'synthetic_visible')
        self.assertEqual(records[0]['value']['second_literal'], False)

    def test_successful_pipeline_does_not_claim_semantic_completeness(self):
        # Even a successful ordinary candidate scan cannot establish full
        # semantics. Unresolved false-positive probes live outside this suite.
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / 'ordinary.js').write_bytes(b'checkGate("synthetic_visible");')
            doc = snapshot(Path(folder), 'synthetic')
        self.assertTrue(doc['coverage']['complete_within_declared_scope'])
        self.assertEqual([record['key'] for record in doc['records']], ['synthetic_visible'])
        self.assertEqual(doc['analysis_kind'], 'lexical_candidate_inventory')
        self.assertIs(doc['semantic_completeness_proven'], False)
        self.assertIs(verify_snapshot(doc), doc)

    def test_diff_reports_candidates_and_explicit_unproven_semantics(self):
        with tempfile.TemporaryDirectory() as folder:
            doc = snapshot(Path(folder), 'synthetic')
        report = diff_snapshots(doc, doc)
        self.assertEqual(report['analysis_kind'], 'lexical_candidate_inventory')
        self.assertIs(report['semantic_completeness_proven'], False)
        text = readable(report)
        self.assertTrue(text.startswith('# 静态候选版本差分'))
        self.assertIn('不证明 JS 语义完整', text)
        self.assertNotIn('声明范围内的静态事实', text)

    def test_legacy_snapshot_remains_readable_without_semantic_claim(self):
        with tempfile.TemporaryDirectory() as folder:
            doc = snapshot(Path(folder), 'synthetic')
        doc.pop('analysis_kind')
        doc.pop('semantic_completeness_proven')
        doc['identity'].pop('snapshot_sha256')
        doc['identity']['snapshot_sha256'] = digest(canonical(doc).encode())
        self.assertIs(verify_snapshot(doc), doc)
        self.assertIs(diff_snapshots(doc, doc)['semantic_completeness_proven'], False)

    def test_semantic_complete_claim_cannot_be_promoted(self):
        with tempfile.TemporaryDirectory() as folder:
            doc = snapshot(Path(folder), 'synthetic')
        doc['semantic_completeness_proven'] = True
        doc['identity'].pop('snapshot_sha256')
        doc['identity']['snapshot_sha256'] = digest(canonical(doc).encode())
        with self.assertRaises(ToolkitError):
            verify_snapshot(doc)

    def test_json_exception_does_not_leak_parser_message(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / 'bad.json').write_bytes(b'{"PRIVATE_SENTINEL":')
            doc = snapshot(Path(folder), 'synthetic')
        issue = doc['coverage']['issues'][0]
        self.assertNotIn('PRIVATE_SENTINEL', json.dumps(issue))
        self.assertNotIn('diagnostic', issue)
        self.assertEqual(doc['records'], [])

if __name__ == '__main__':
    unittest.main(verbosity=2)
