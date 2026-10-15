#!/usr/bin/env python3
"""Verify that overlay outputs preserve complete baseline facts and all 23 gaps."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from resolution_overlay import baseline_fingerprint, require


def payload(path):
    text = path.read_text(encoding='utf-8')
    match = re.search(r'<script type="application/json" id="color-data">(.*?)</script>', text, re.S)
    require(match is not None, 'Missing browser payload')
    return json.loads(match[1])


def without_extension(data):
    return {key: value for key, value in data.items() if key != 'resolution_extension'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('baseline', 'annotated', 'baseline-browser', 'annotated-browser'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--baseline-full', type=Path)
    p.add_argument('--annotated-full', type=Path)
    a = p.parse_args()
    old, new = [json.loads(path.read_text()) for path in (a.baseline, a.annotated)]
    old_ui, new_ui = payload(a.baseline_browser), payload(a.annotated_browser)
    require(without_extension(new) == old, 'Published baseline was modified')
    require(without_extension(new_ui) == old_ui, 'Original browser payload was modified')
    require(new['resolution_extension'] == new_ui['resolution_extension'], 'JSON/browser extension mismatch')
    require(baseline_fingerprint(new) == baseline_fingerprint(new_ui), 'JSON/browser baseline mismatch')
    if a.baseline_full or a.annotated_full:
        require(a.baseline_full and a.annotated_full, 'Both full catalog paths are required')
        old_full, new_full = [json.loads(path.read_text()) for path in (a.baseline_full, a.annotated_full)]
        for key in ('records', 'statistics', 'definition_inventory', 'sources', 'blocks', 'profiles'):
            require(old_full[key] == new_full[key], 'Full catalog changed ' + key)
        require(new_full['resolution_extension'] == new['resolution_extension'], 'Full/compact extension mismatch')
    extension = new['resolution_extension']
    require(len(extension['records']) == 23, 'Expected 23 classified records')
    require(sum(v['audit_status'] == 'statically_resolved' for v in extension['records'].values()) == 19, 'Expected 19 derived')
    require(sum(v.get('srgb_in_gamut') is False for v in extension['records'].values()) == 5, 'Expected 5 extended')
    require(all(v.get('hex') is None for v in extension['records'].values() if v.get('srgb_in_gamut') is False or v['audit_status'] == 'context_dependent'), 'Fabricated HEX')
    require(all(v.get('alpha') is None for v in extension['records'].values() if v['audit_status'] == 'context_dependent'), 'Fabricated contextual alpha')
    print(json.dumps({'status': 'passed', 'published_original_fields_identical': True,
        'browser_original_payload_identical': True, 'full_original_facts_identical': bool(a.baseline_full),
        'original_records': 1341, 'extension_records': 23,
        'statistics': extension['statistics'],
        'output_sha256': {'json': hashlib.sha256(a.annotated.read_bytes()).hexdigest(), 'html': hashlib.sha256(a.annotated_browser.read_bytes()).hexdigest()}}, indent=2))

if __name__ == '__main__':
    main()
