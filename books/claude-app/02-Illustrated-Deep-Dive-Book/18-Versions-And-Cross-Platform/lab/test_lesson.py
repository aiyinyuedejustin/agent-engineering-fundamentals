"""Tests exercise the actual published comparator, not a duplicate algorithm."""
import tempfile
from pathlib import Path
import unittest
from lesson import CHANGED, CRLF, LF, classify, comparator, make_roots, write_asar


class ComparisonLessonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.roots = make_roots(Path(self.temp.name))
        self.report = comparator.compare(self.roots)
        self.rows = {r['path']: r for r in self.report['css']['inventory']}

    def test_four_outcomes(self):
        self.assertEqual({p: classify(r) for p, r in self.rows.items()}, {
            'ion-dist/same.css': '同字节', 'shell/newlines.css': '仅所定义归一化相同',
            'shell/changed.css': '内容不同', 'shell/missing.css': '集合不完整'})

    def test_normalization_retains_raw_evidence(self):
        row = self.rows['shell/newlines.css']
        self.assertFalse(row['byte_identical_all'])
        self.assertTrue(row['crlf_to_lf_equal_all'])
        win = row['platforms']['windows']
        self.assertEqual(win['sha256'], comparator.sha(CRLF))
        self.assertEqual(win['crlf_to_lf_sha256'], comparator.sha(LF))
        self.assertEqual(win['crlf_count'], 1)
        self.assertEqual(win['bare_cr_count'], 0)
        entries = {p: data for p, _, data in comparator.packed_entries(self.roots['windows'] / 'app.asar')}
        self.assertEqual(entries['shell/newlines.css'], CRLF)

    def test_missing_is_not_equal_even_when_present_hashes_match(self):
        row = self.rows['shell/missing.css']
        self.assertEqual(len({r['sha256'] for r in row['platforms'].values()}), 1)
        self.assertFalse(row['byte_identical_all'])
        self.assertFalse(row['crlf_to_lf_equal_all'])

    def test_content_change_survives_normalization(self):
        row = self.rows['shell/changed.css']
        self.assertFalse(row['byte_identical_all'])
        self.assertFalse(row['crlf_to_lf_equal_all'])
        self.assertEqual(row['platforms']['windows']['crlf_to_lf_sha256'], comparator.sha(CHANGED))

    def test_rename_changes_resource_tree_even_with_same_hash_multiset(self):
        ion = self.roots['windows'] / 'ion-dist'
        (ion / 'same.css').rename(ion / 'renamed.css')
        report = comparator.compare(self.roots)
        self.assertFalse(report['ion_dist']['all_paths_sizes_and_hashes_equal'])
        inventories = [report['platforms'][p]['ion_dist']['inventory'] for p in comparator.PLATFORMS]
        self.assertEqual(sorted(r['sha256'] for r in inventories[0].values()), sorted(r['sha256'] for r in inventories[1].values()))
        self.assertNotEqual(report['platforms']['linux']['ion_dist']['tree_digest_sha256'], report['platforms']['windows']['ion_dist']['tree_digest_sha256'])
        self.assertEqual(sum(classify(r) == '集合不完整' for r in report['css']['inventory']), 3)

    def test_three_font_instances_two_content_hashes(self):
        self.assertEqual(self.report['fonts']['files_each'], dict.fromkeys(comparator.PLATFORMS, 3))
        self.assertEqual(self.report['fonts']['unique_hashes_each'], dict.fromkeys(comparator.PLATFORMS, 2))
        self.assertTrue(self.report['fonts']['all_paths_sizes_and_hashes_equal'])

    def test_bare_cr_not_normalized(self):
        for platform, root in self.roots.items():
            (root / 'ion-dist/bare.css').write_bytes(LF.replace(b'\n', b'\r') if platform == 'windows' else LF)
        report = comparator.compare(self.roots)
        row = next(r for r in report['css']['inventory'] if r['path'] == 'ion-dist/bare.css')
        self.assertEqual(classify(row), '内容不同')
        self.assertEqual(row['platforms']['windows']['bare_cr_count'], 1)

    def test_bom_is_not_removed(self):
        for platform, root in self.roots.items():
            (root / 'ion-dist/bom.css').write_bytes((b'\xef\xbb\xbf' if platform == 'windows' else b'') + LF)
        row = next(r for r in comparator.compare(self.roots)['css']['inventory'] if r['path'] == 'ion-dist/bom.css')
        self.assertEqual(classify(row), '内容不同')

    def test_bad_packed_integrity_stops_comparison(self):
        archive = self.roots['windows'] / 'app.asar'
        data = archive.read_bytes()
        archive.write_bytes(data[:-1] + bytes([data[-1] ^ 1]))
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            comparator.compare(self.roots)

    def test_counts_are_per_path_and_presence(self):
        self.assertEqual(self.report['css']['files_each'], {'linux': 4, 'windows': 3, 'macos': 4})
        self.assertEqual(self.report['css']['byte_identical_count'], 1)
        self.assertEqual(self.report['css']['crlf_to_lf_equal_count'], 2)


if __name__ == '__main__':
    unittest.main()
