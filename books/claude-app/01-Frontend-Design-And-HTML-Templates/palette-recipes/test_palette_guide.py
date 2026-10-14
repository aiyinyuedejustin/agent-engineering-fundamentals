"""Source agreement, color math, threshold checks, and SVG/output regression tests."""
import colorsys
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('guide', HERE/'generate_palette_guide.py')
guide=importlib.util.module_from_spec(spec)
spec.loader.exec_module(guide)
SOURCE=next((p for p in (HERE.parent/'frontend-templates'/'shared',HERE.parent/'styles') if (p/'claude-tokens.css').exists()),None)


class ColorMathTests(unittest.TestCase):
    def test_known_color_vectors(self):
        cases={'#000000':(0,0,0),'#ffffff':(0,0,100),'#ff0000':(0,100,50),'#00ff00':(120,100,50),'#0000ff':(240,100,50),'#ffff00':(60,100,50),'#00ffff':(180,100,50),'#ff00ff':(300,100,50)}
        for raw,expected in cases.items():
            c=guide.color(raw)
            self.assertEqual(tuple(Fraction(v) for v in c['hslExact'].values()),expected)

    def test_alpha_is_eight_bit_not_guessed_percentage(self):
        self.assertEqual(guide.color('#26251f40')['alphaExact'],'64/255')
        self.assertEqual(guide.color('#00000080')['alphaExact'],'128/255')
        self.assertNotEqual(float(Fraction(guide.color('#00000080')['alphaExact'])),.5)
        self.assertEqual(guide.color('#00000000')['alphaExact'],'0')
        self.assertEqual(guide.color('#000000ff')['alphaExact'],'1')
        self.assertIn('/ calc(64 / 255)',guide.color('#26251f40')['rgbCss'])

    def test_roundtrip_dense_rgb_grid(self):
        for r in range(0,256,17):
            for g in range(0,256,17):
                for b in range(0,256,17):
                    c=guide.color(f'#{r:02x}{g:02x}{b:02x}')
                    h,s,l=(Fraction(v) for v in c['hslExact'].values())
                    actual=tuple(round(v*255) for v in colorsys.hls_to_rgb(float(h)/360,float(l)/100,float(s)/100))
                    self.assertEqual(actual,(r,g,b))
                    actual_rounded=tuple(round(v*255) for v in colorsys.hls_to_rgb(float(guide.decimal(h))/360,float(guide.decimal(l))/100,float(guide.decimal(s))/100))
                    self.assertEqual(actual_rounded,(r,g,b))

    def test_contrast_reference_vectors_and_alpha(self):
        self.assertAlmostEqual(guide.contrast('#000000','#ffffff'),21)
        self.assertAlmostEqual(guide.contrast('#ffffff','#ffffff'),1)
        self.assertAlmostEqual(guide.contrast('#00000080','#ffffff'),guide.contrast('#7f7f7f','#ffffff'))
        self.assertAlmostEqual(guide.contrast('#00000000','#ffffff'),1)
        with self.assertRaises(ValueError): guide.contrast('#000000','#ffffff80')

    def test_invalid_values_are_rejected(self):
        for value in ('red','#fff','#abcdefghi','#1234567','hsl(0 0% 0%)'):
            with self.assertRaises(ValueError): guide.color(value)


class GuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=guide.load_sources(SOURCE)
        cls.files=guide.outputs(cls.source,HERE)

    def test_css_json_agree_and_roles_present(self):
        self.assertEqual(len(self.source['data']['palettes']),5)
        for palette in self.source['data']['palettes'].values():
            for mode in ('light','dark'):
                self.assertEqual(set(palette[mode]),set(guide.ROLES))
                for raw in palette[mode].values(): self.assertEqual(guide.color(raw)['alphaByte'],255)

    def test_detects_source_drift(self):
        with tempfile.TemporaryDirectory() as folder:
            for p in self.source['paths'].values(): (Path(folder)/p.name).write_bytes(p.read_bytes())
            p=Path(folder)/'claude-tokens.css'
            p.write_text(p.read_text().replace('#f8f7f3','#f8f7f2',1))
            with self.assertRaisesRegex(AssertionError,'JSON/CSS drift'): guide.load_sources(Path(folder))

    def test_all_actual_values_roundtrip(self):
        expanded=json.loads(self.files['tokens-expanded.json'])
        records=[c for p in expanded['palettes'].values() for mode in ('light','dark') for c in p[mode].values()]
        records += [c for v in expanded['common'].values() for c in v.values()]
        records += [c for v in expanded['shadows'].values() for c in v['colors']]
        self.assertEqual(len(records),108)
        for c in records:
            h,s,l=(Fraction(v) for v in c['hslExact'].values())
            actual=[round(v*255) for v in colorsys.hls_to_rgb(float(h)/360,float(l)/100,float(s)/100)]
            self.assertEqual(actual,c['rgb'])
            self.assertEqual(Fraction(c['alphaExact']),Fraction(c['alphaByte'],255))

    def test_contrast_thresholds_and_decorative_boundary(self):
        report=json.loads(self.files['contrast-report.json'])
        checks=[c for p in report['palettes'] for c in p['checks']]
        self.assertEqual(len(checks),190)
        self.assertTrue(report['allPassed'])
        self.assertTrue(all(c['ratio'] >= c['threshold'] and c['passed'] for c in checks))
        self.assertTrue(all(v<3 for p in report['palettes'] for v in p['decorativeLineRatios'].values()))

    def test_generated_files_match(self):
        for path,body in self.files.items(): self.assertEqual((HERE/path).read_text(),body,path)

    def test_svg_accessible_and_no_network_assets(self):
        ns={'s':'http://www.w3.org/2000/svg'}
        for name,body in self.files.items():
            if not name.endswith('.svg'): continue
            root=ET.fromstring(body)
            self.assertEqual(root.attrib['role'],'img')
            self.assertTrue(root.find('s:title',ns).text)
            self.assertTrue(root.find('s:desc',ns).text)
            self.assertFalse(root.findall('.//s:image',ns))
            self.assertFalse(root.findall('.//s:script',ns))
            self.assertTrue(len(root.findall('.//s:rect',ns))>10)

    def test_palette_svg_contains_each_role_and_source_hex(self):
        for pid,palette in self.source['data']['palettes'].items():
            body=self.files[f'swatches/{pid}.svg']
            for role in guide.ROLES: self.assertEqual(body.count(f'--ui-{role}&lt;'),0)
            root=ET.fromstring(body)
            text=' '.join(root.itertext())
            for mode in ('light','dark'):
                for role,raw in palette[mode].items():
                    self.assertIn(f'--ui-{role}',text)
                    self.assertIn(raw.upper(),text)
                    self.assertIn(f'fill="{raw}"',body)

    def test_readme_local_links_exist(self):
        for link in re.findall(r'\]\(([^)]+)\)',self.files['README.md']):
            if '://' not in link: self.assertTrue((HERE/link).exists(),link)


if __name__=='__main__': unittest.main()
