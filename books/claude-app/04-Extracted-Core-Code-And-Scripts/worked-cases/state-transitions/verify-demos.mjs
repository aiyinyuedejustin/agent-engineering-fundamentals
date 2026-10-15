import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
for (const name of ['tree', 'settings']) {
  const result = spawnSync(process.execPath, [fileURLToPath(new URL(`${name}-case.mjs`, import.meta.url))], { encoding: 'utf8', env: process.env });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stderr, '');
  assert.equal(result.stdout, readFileSync(new URL(`${name}.expected.txt`, import.meta.url), 'utf8'));
}
console.log('PASS: 2 deterministic demo outputs match expected snapshots');
