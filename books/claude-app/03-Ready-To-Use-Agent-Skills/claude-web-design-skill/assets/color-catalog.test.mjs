import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync, realpathSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve, relative, dirname, isAbsolute } from 'node:path';
const root = realpathSync(fileURLToPath(new URL('../', import.meta.url)));
const catalog = JSON.parse(readFileSync(new URL('../references/color-catalog.json', import.meta.url), 'utf8'));
const extension = catalog.resolution_extension;
const key = row => `${row[0]}:${row[1]}`;
const validHex = value => typeof value === 'string' && /^#[0-9a-f]{6}$/.test(value);
const validAlpha = value => typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 1;
const profiles = {raw: 315, cds_light: 349, cds_dark: 349, legacy_v1_light: 50, legacy_v1_dark: 50, legacy_v2_light: 50, legacy_v2_dark: 50, bridge: 128};

test('frozen catalog schema, unique profile/name keys and baseline statistics', () => {
  assert.equal(catalog.schema, 'claude.color-catalog.compact.v1');
  assert.equal(catalog.product, 'Claude Desktop Linux');
  assert.equal(catalog.version, '2.37337.1');
  assert.deepEqual(catalog.columns, ['profile', 'name', 'declared', 'hex', 'alpha', 'status']);
  assert.equal(catalog.records.length, 1341);
  assert.equal(new Set(catalog.records.map(key)).size, 1341);
  let resolved = 0;
  for (const row of catalog.records) {
    assert.equal(row.length, 6);
    assert.ok(Object.hasOwn(profiles, row[0]));
    assert.match(row[1], /^--[\w-]+$/);
    assert.equal(typeof row[2], 'string');
    assert.ok(['resolved', 'unresolved'].includes(row[5]));
    if (row[5] === 'resolved') {
      resolved++;
      assert.ok(validHex(row[3]), key(row));
      assert.ok(validAlpha(row[4]), key(row));
    } else {
      assert.equal(row[3], null);
      assert.equal(row[4], null);
    }
  }
  assert.equal(resolved, 1318);
  assert.equal(catalog.statistics.profile_records, 1341);
  assert.equal(catalog.statistics.resolved_records, resolved);
  assert.equal(catalog.statistics.unresolved_records, 23);
  assert.equal(catalog.statistics.raw_palette_entries, 315);
  assert.equal(catalog.statistics.families * catalog.statistics.shades_per_family, 315);
  assert.deepEqual(Object.keys(catalog.statistics.profiles).sort(), Object.keys(profiles).sort());
  for (const [profile, total] of Object.entries(profiles)) {
    const rows = catalog.records.filter(row => row[0] === profile);
    const count = rows.filter(row => row[5] === 'resolved').length;
    assert.equal(rows.length, total);
    assert.deepEqual(catalog.statistics.profiles[profile], {total, resolved: count, unresolved: total - count});
  }
  assert.equal(catalog.sources.length, 4);
  for (const source of catalog.sources) {
    assert.match(source.sha256, /^[0-9a-f]{64}$/);
    assert.ok(Number.isInteger(source.bytes) && source.bytes > 0);
    assert.equal(typeof source.path, 'string'); // Provenance identifier, not a file dependency.
  }
});

test('extension preserves 14 derived HEX, 5 extended sRGB and 4 contextual records', () => {
  assert.equal(extension.schema, 'claude.color-resolution-extension.v1');
  assert.equal(extension.provenance.browser_css_semantics.product_runtime_executed, false);
  assert.deepEqual(Object.keys(extension.records).sort(), catalog.records.filter(row => row[5] === 'unresolved').map(key).sort());
  const counts = Object.fromEntries(Object.keys(profiles).map(profile => [profile, {records: 0, baseline_resolved: 0, derived_static: 0, hex: 0, extended_srgb: 0, context_dependent: 0}]));
  for (const row of catalog.records) {
    const count = counts[row[0]];
    count.records++;
    if (row[5] === 'resolved') { count.baseline_resolved++; count.hex++; continue; }
    const entry = extension.records[key(row)];
    assert.equal(typeof entry.expanded_expression, 'string');
    if (entry.audit_status === 'context_dependent') {
      count.context_dependent++;
      assert.equal(entry.hex, null);
      assert.equal(entry.alpha, null);
      assert.equal(typeof entry.reason, 'string');
      assert.equal(typeof entry.dependency_kind, 'string');
      assert.equal(entry.srgb_channels, undefined);
      continue;
    }
    assert.equal(entry.audit_status, 'statically_resolved');
    count.derived_static++;
    assert.ok(validAlpha(entry.alpha));
    assert.equal(entry.srgb_channels.length, 3);
    assert.ok(entry.srgb_channels.every(Number.isFinite));
    const inGamut = entry.srgb_channels.every(value => value >= 0 && value <= 1);
    assert.equal(entry.srgb_in_gamut, inGamut);
    assert.match(entry.css_color_srgb, /^color\(srgb /);
    if (inGamut) { count.hex++; assert.ok(validHex(entry.hex)); }
    else {
      count.extended_srgb++;
      assert.equal(entry.hex, null, `${key(row)} must not invent HEX`);
      assert.ok(validHex(entry.clipped_preview.hex));
      assert.match(entry.clipped_preview.warning, /Preview only/);
    }
  }
  assert.deepEqual(extension.profiles, counts);
  assert.deepEqual(extension.statistics, {
    baseline_records: 1341, baseline_resolved_records: 1318, baseline_unresolved_records: 23,
    derived_static_records: 19, derived_hex_records: 14, extended_srgb_records: 5,
    context_dependent_records: 4, static_numeric_records: 1337, hex_records: 1332,
  });
  const sum = field => Object.values(counts).reduce((total, count) => total + count[field], 0);
  assert.equal(sum('derived_static'), 19);
  assert.equal(sum('extended_srgb'), 5);
  assert.equal(sum('context_dependent'), 4);
  assert.equal(sum('hex'), 1332);
});

test('Markdown relative file references resolve within the copied skill', () => {
  const walk = directory => readdirSync(directory).flatMap(name => {
    const path = resolve(directory, name);
    return statSync(path).isDirectory() ? walk(path) : [path];
  });
  const contained = path => {
    const rel = relative(root, path);
    return !isAbsolute(rel) && rel !== '..' && !rel.startsWith('../');
  };
  let links = 0;
  for (const file of walk(root).filter(path => path.endsWith('.md'))) {
    const text = readFileSync(file, 'utf8');
    for (const [, target] of text.matchAll(/\[[^\]]*\]\(([^\s)]+)\)/g)) {
      if (/^[a-z][a-z\d+.-]*:|^#/i.test(target)) continue;
      const path = resolve(dirname(file), decodeURIComponent(target.split('#')[0]));
      assert.ok(contained(path), `${file}: outside-skill reference ${target}`);
      assert.ok(statSync(path).isFile(), `${file}: missing ${target}`);
      assert.ok(contained(realpathSync(path)), `${file}: symlink escapes skill`);
      links++;
    }
  }
  assert.ok(links >= 10);
});
