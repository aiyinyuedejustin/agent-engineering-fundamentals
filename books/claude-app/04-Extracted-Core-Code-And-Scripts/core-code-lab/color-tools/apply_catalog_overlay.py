#!/usr/bin/env python3
"""Append a reviewed overlay to a published JSON catalog and offline browser.

Does not read or execute product source. No network or third-party dependencies.
"""
import argparse
import json
from pathlib import Path
import re
from resolution_overlay import apply_resolution_overlay, baseline_fingerprint, load_resolution_overlay, require, write_new_outputs


def apply_or_verify(catalog, overlay):
    """Rebuild baseline or verify an identical existing extension before reuse."""
    baseline = {key: value for key, value in catalog.items() if key != 'resolution_extension'}
    result = apply_resolution_overlay(baseline, overlay)
    if 'resolution_extension' in catalog:
        require(catalog['resolution_extension'] == result['resolution_extension'],
                'Existing resolution extension differs from reviewed overlay')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    book = Path(__file__).resolve().parents[3]
    p.add_argument('--catalog', type=Path, default=book / '04-Extracted-Core-Code-And-Scripts/evidence/data/color-catalog.json', help='Defaults to this book’s published compact catalog')
    p.add_argument('--browser', type=Path, default=book / '01-Frontend-Design-And-HTML-Templates/color-catalog/index.html', help='Defaults to this book’s published offline catalog')
    p.add_argument('--overlay', type=Path, default=Path(__file__).with_name('reviewed-resolution-overlay.json'))
    p.add_argument('--template', type=Path, default=Path(__file__).with_name('color_catalog_template.html'))
    p.add_argument('--output', type=Path, required=True, help='New, non-existing output directory; existing paths are never replaced')
    a = p.parse_args()
    try:
        inputs = {x.resolve() for x in [a.catalog, a.browser, a.overlay, a.template]}
        require(all((a.output / n).resolve() not in inputs for n in ('color-catalog.json', 'index.html')), 'Refuse input overwrite')
        catalog = json.loads(a.catalog.read_text(encoding='utf-8'))
        html = a.browser.read_text(encoding='utf-8')
        matches = re.findall(r'<script type="application/json" id="color-data">(.*?)</script>', html, re.S)
        require(len(matches) == 1, 'Expected one embedded browser color payload')
        ui = json.loads(matches[0])
        require(baseline_fingerprint(catalog) == baseline_fingerprint(ui), 'JSON/browser baseline mismatch')
        overlay = load_resolution_overlay(a.overlay)
        result = apply_or_verify(catalog, overlay)
        ui_result = apply_or_verify(ui, overlay)
        template = a.template.read_text(encoding='utf-8')
        require(template.count('__COLOR_DATA__') == 1, 'Expected one template placeholder')
        payload = json.dumps(ui_result, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
        payload = payload.replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
        output_html = template.replace('__COLOR_DATA__', payload)
        write_new_outputs(a.output, {
            'color-catalog.json': json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n',
            'index.html': output_html,
        })
        print(json.dumps({'status': 'passed', 'baseline_unchanged': True, 'statistics': result['resolution_extension']['statistics']}, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as error:
        p.exit(2, f'error: {error}\n')

if __name__ == '__main__':
    main()
