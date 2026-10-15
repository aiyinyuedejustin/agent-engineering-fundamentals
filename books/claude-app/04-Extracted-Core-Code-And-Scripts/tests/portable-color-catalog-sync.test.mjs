// Book-only integrity gate. Deliberately outside the portable skill.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

test('published catalog and portable skill copy are byte-identical', () => {
  const source = readFileSync(new URL('../evidence/data/color-catalog.json', import.meta.url));
  const copy = readFileSync(new URL('../../03-Ready-To-Use-Agent-Skills/claude-web-design-skill/references/color-catalog.json', import.meta.url));
  assert.ok(source.equals(copy), 'Catalog drift: copy the published catalog byte-for-byte into skill references, review statistics, and rerun both test groups.');
});
