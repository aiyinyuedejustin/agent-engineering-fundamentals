#!/usr/bin/env python3
"""Optional full-baseline regression using private inputs supplied explicitly."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_color_catalog import build_catalog, write_outputs
from extract_design_tokens import extract_inventory


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', required=True, type=Path)
    parser.add_argument('--baseline', required=True, type=Path, help='Existing, locally held 1341-record color-catalog.json')
    parser.add_argument('--resources', required=True, type=Path)
    parser.add_argument('--asar-root', required=True, type=Path)
    parser.add_argument('--primary-source')
    parser.add_argument('--output', type=Path, help='Optional destination for regenerated catalog and HTML')
    args = parser.parse_args()
    baseline = json.loads(args.baseline.read_text(encoding='utf-8'))
    kwargs = dict(primary_source=args.primary_source, product=baseline['product'], version=baseline['version'])
    original = build_catalog(args.inventory, args.resources, args.asar_root, **kwargs)
    fresh_inventory = extract_inventory(args.resources, args.asar_root)
    prior_inventory = json.loads(args.inventory.read_text(encoding='utf-8'))
    for field in ('sources', 'blocks', 'tokens', 'statistics'):
        require(fresh_inventory[field] == prior_inventory[field], f'Fresh extraction differs in {field}')
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'inventory.json'
        path.write_text(json.dumps(fresh_inventory, ensure_ascii=False), encoding='utf-8')
        fresh = build_catalog(path, args.resources, args.asar_root, **kwargs)
    for label, catalog in [('original inventory', original), ('fresh inventory', fresh)]:
        for field in ('records', 'statistics', 'definition_inventory', 'sources', 'blocks'):
            require(catalog[field] == baseline[field], f'{label}: mismatch in {field}')
        require(len(catalog['records']) == 1341, f'{label}: expected 1341 records')
        require(catalog['statistics']['unresolved_records'] == 23, f'{label}: expected 23 unresolved records')
        expected_profiles = {'raw': 315, 'cds_light': 349, 'cds_dark': 349,
                             'legacy_v1_light': 50, 'legacy_v1_dark': 50,
                             'legacy_v2_light': 50, 'legacy_v2_dark': 50, 'bridge': 128}
        require({key: profile['record_count'] for key, profile in catalog['profiles'].items()} == expected_profiles,
                f'{label}: profile counts differ from the documented baseline')
        require(catalog['verification']['source_hash_checks'] == baseline['verification']['source_hash_checks'], f'{label}: source verification differs')
        require(catalog['verification']['byte_anchors_checked'] == 3234, f'{label}: expected 3234 checked anchors')
        require(all('hex' not in r and 'alpha' not in r for r in catalog['records'] if r['status'] == 'unresolved'), 'Unresolved color was fabricated')
    if args.output:
        write_outputs(fresh, args.output, Path(__file__).resolve().parents[1] / 'color_catalog_template.html')
    print(json.dumps({'status': 'passed', 'original_inventory_records_identical': True,
                      'fresh_extraction_records_identical': True, 'profile_records': 1341,
                      'resolved_records': 1318, 'unresolved_records': 23,
                      'verified_source_hashes': len(fresh['verification']['source_hash_checks']),
                      'declarations_in_inventory': 3234}, indent=2))


if __name__ == '__main__':
    main()
