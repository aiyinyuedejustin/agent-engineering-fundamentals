#!/usr/bin/env python3
"""Validate and append a reviewed resolution overlay without editing baseline facts.

Accepts full, compact-column, and browser catalogs. The overlay is specific to a
verified six-column baseline fingerprint, not a general-purpose CSS evaluator.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
import re
from fractions import Fraction
from pathlib import Path

COLUMNS = ('profile', 'name', 'declared', 'hex', 'alpha', 'status')
SCHEMA = 'claude.color-resolution-extension.v1'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def baseline_records(catalog):
    rows = catalog.get('records', [])
    is_compact = 'columns' in catalog
    if is_compact:
        columns = catalog['columns']
        require(all(key in columns for key in COLUMNS), 'Missing baseline columns')
        require(all(len(row) == len(columns) for row in rows), 'Malformed compact row')
        rows = [dict(zip(columns, row)) for row in rows]
    require(all(isinstance(row, dict) for row in rows), 'Malformed catalog records')
    for row in rows:
        expected_id = row['profile'] + ':' + row['name']
        require((is_compact and 'id' not in row) or row.get('id') == expected_id,
                'Object record id is required and must match profile:name')
    return rows


def baseline_fingerprint(catalog):
    projection = []
    for row in baseline_records(catalog):
        values = [row.get(key) for key in COLUMNS]
        if values[4] is not None:
            values[4] = float(values[4])
        projection.append(values)
    raw = json.dumps(projection, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def validate_extension(value):
    require(isinstance(value.get('expanded_expression'), str), 'Missing expanded expression')
    status = value.get('audit_status')
    if status == 'context_dependent':
        require(value.get('dependency_kind') in ('custom_property_initial', 'element_currentcolor'), 'Unknown context dependency')
        require(value.get('hex') is None and value.get('alpha') is None, 'Context has fabricated HEX/alpha')
        require(not value.get('css_color_srgb') and not value.get('srgb_channels'), 'Context has fabricated numeric color')
        if value['dependency_kind'] == 'custom_property_initial':
            require(value['expanded_expression'] == 'initial', 'Unexpected initial expression')
            example = value.get('consumer_example', {})
            require(example.get('is_token_hex') is False, 'Fallback must not be described as token HEX')
        else:
            weight = value.get('currentcolor_alpha_multiplier')
            require(weight in (.18, .22), 'Unexpected currentColor mix')
        return
    require(status == 'statically_resolved', 'Unsupported resolution extension status')
    channels = value.get('srgb_channels', [])
    require(len(channels) == 3 and all(isinstance(c, (int, float)) and math.isfinite(c) for c in channels), 'Invalid sRGB channels')
    alpha = value.get('alpha')
    require(isinstance(alpha, (int, float)) and math.isfinite(alpha) and 0 <= alpha <= 1, 'Invalid derived alpha')
    require(len(value.get('srgb_exact', [])) == 3 and len(value.get('rgb_255_exact', [])) == 3, 'Missing exact channels')
    for actual, exact, rgb in zip(channels, value['srgb_exact'], value['rgb_255_exact']):
        require(math.isclose(actual, float(Fraction(exact)), rel_tol=0, abs_tol=1e-14), 'Exact sRGB channel mismatch')
        require(Fraction(rgb) / 255 == Fraction(exact), 'Exact RGB/sRGB mismatch')
    require(float(Fraction(value['alpha_exact'])) == alpha, 'Exact alpha mismatch')
    in_gamut = all(0 <= c <= 1 for c in channels)
    require(value.get('srgb_in_gamut') is in_gamut, 'Incorrect gamut label')
    require((value.get('hex') is not None) == in_gamut, 'Extended sRGB must not have a clipped HEX')
    if in_gamut:
        expected = '#' + ''.join(f'{math.floor(c * 255 + .5):02x}' for c in channels)
        require(value['hex'] == expected, 'Derived HEX mismatch')
    css = re.fullmatch(r'color\(srgb ([^ ]+) ([^ ]+) ([^ ]+) / ([^ ]+)\)', value.get('css_color_srgb', ''))
    require(css is not None, 'Missing derived color(srgb)')
    require(all(math.isclose(float(x), y, rel_tol=0, abs_tol=1e-11) for x, y in zip(css.groups(), channels + [alpha])), 'Derived color(srgb) mismatch')


def apply_resolution_overlay(catalog, overlay):
    """Return a new catalog with one top-level extension; preserve every old key."""
    require('resolution_extension' not in catalog, 'Catalog already has a resolution extension')
    require(overlay.get('schema') == 'claude.color-gap-overlay.recommendation.v1', 'Unknown overlay schema')
    validation = overlay.get('validation', {})
    require(baseline_fingerprint(catalog) == validation.get('baseline_projection_sha256'), 'Overlay baseline fingerprint mismatch')
    require(catalog.get('version') == validation.get('version'), 'Overlay version mismatch')
    rows = baseline_records(catalog)
    by_id = {row['profile'] + ':' + row['name']: row for row in rows}
    require(len(by_id) == len(rows), 'Duplicate baseline record id')
    resolved = sum(row['status'] == 'resolved' for row in rows)
    require(catalog['statistics']['profile_records'] == len(rows), 'Baseline statistics record mismatch')
    require(catalog['statistics']['resolved_records'] == resolved, 'Baseline resolved statistics mismatch')
    require(catalog['statistics']['unresolved_records'] == len(rows) - resolved, 'Baseline unresolved statistics mismatch')
    extensions = {}
    for item in overlay.get('records', []):
        record_id = item['id']
        require(record_id not in extensions, 'Duplicate extension id')
        require(record_id in by_id, 'Extension id missing from baseline')
        record = by_id[record_id]
        require(record['status'] == 'unresolved', 'Overlay cannot replace a resolved baseline record')
        require(record['declared'] == item['expected_declared'], 'Overlay declaration mismatch')
        value = item['resolution_extension']
        if 'resolved_expression' in record:
            require(record['resolved_expression'] == value['expanded_expression'], 'Expanded expression mismatch')
        validate_extension(value)
        extensions[record_id] = copy.deepcopy(value)
    require(set(extensions) == {key for key, row in by_id.items() if row['status'] == 'unresolved'}, 'Overlay must classify every baseline unresolved record')
    derived = [v for v in extensions.values() if v['audit_status'] == 'statically_resolved']
    in_gamut = sum(v['srgb_in_gamut'] for v in derived)
    stats = {'baseline_records': len(rows), 'baseline_resolved_records': resolved,
             'baseline_unresolved_records': len(rows) - resolved,
             'derived_static_records': len(derived), 'derived_hex_records': in_gamut,
             'extended_srgb_records': len(derived) - in_gamut,
             'context_dependent_records': len(extensions) - len(derived),
             'static_numeric_records': resolved + len(derived),
             'hex_records': resolved + in_gamut}
    require(stats == validation.get('expected_statistics'), 'Extension statistics do not match reviewed overlay')
    profile_stats = {}
    for profile in dict.fromkeys(row['profile'] for row in rows):
        selected = [row for row in rows if row['profile'] == profile]
        baseline_count = sum(row['status'] == 'resolved' for row in selected)
        added = [extensions[row['profile'] + ':' + row['name']] for row in selected if row['profile'] + ':' + row['name'] in extensions]
        static = [v for v in added if v['audit_status'] == 'statically_resolved']
        profile_stats[profile] = {'records': len(selected), 'baseline_resolved': baseline_count,
                                 'derived_static': len(static), 'hex': baseline_count + sum(v['srgb_in_gamut'] for v in static),
                                 'extended_srgb': sum(not v['srgb_in_gamut'] for v in static),
                                 'context_dependent': sum(v['audit_status'] == 'context_dependent' for v in added)}
    result = copy.deepcopy(catalog)
    result['resolution_extension'] = {
        'schema': SCHEMA,
        'evidence_status': 'packaged_static_and_derived; no_logged_in_product_observation',
        'scope': 'Additive derivation under original named static profiles. Original declarations, statuses, and statistics remain unchanged. Extended sRGB is not clipped to HEX. Contextual values need their consumer.',
        'baseline_projection_sha256': validation['baseline_projection_sha256'],
        'provenance': copy.deepcopy(overlay.get('provenance', {})),
        'statistics': stats, 'profiles': profile_stats, 'records': extensions,
    }
    return result


def load_resolution_overlay(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_new_outputs(output, files):
    """Create a new output directory and exclusive files; never truncate paths.

    Existing directories, files, and symlinks are rejected. A mid-write error
    leaves any newly created output for inspection; no existing data is removed.
    """
    output = Path(output)
    require(all(Path(name).name == name and name not in ('.', '..') for name in files),
            'Output names must be plain filenames')
    require(all(isinstance(value, str) for value in files.values()), 'Output content must be text')
    try:
        output.mkdir(parents=True, exist_ok=False)
    except FileExistsError as error:
        raise ValueError('Output directory already exists; choose a new, non-existing directory. No existing output was changed.') from error
    for name, value in files.items():
        with (output / name).open('x', encoding='utf-8') as handle:
            handle.write(value)
