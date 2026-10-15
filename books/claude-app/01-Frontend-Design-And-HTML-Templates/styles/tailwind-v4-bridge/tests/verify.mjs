/** Compile exactly one v4 + one v3; no installs, network, or browser; writes only new report/work directories. */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import { cpSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
if (!process.env.TAILWIND_V4_DIR || !process.env.TAILWIND_V3_DIR) {
  throw new Error('Set TAILWIND_V4_DIR and TAILWIND_V3_DIR to your separate, installed toolchain directories.');
}
const v4 = path.resolve(process.env.TAILWIND_V4_DIR);
const v3 = path.resolve(process.env.TAILWIND_V3_DIR);
const read = p => readFileSync(p, 'utf8');
const hash = p => createHash('sha256').update(readFileSync(p)).digest('hex');
const args = process.argv.slice(2);
if (args.length && (args.length !== 2 || args[0] !== '--output')) {
  throw new Error('Usage: node tests/verify.mjs [--output /path/to/new-report-directory]');
}
// An explicit destination must not exist. The default is a fresh sibling directory.
const output = args.length ? path.resolve(args[1]) : mkdtempSync(path.join(root, 'verification-run-'));
if (args.length) mkdirSync(output);
const tests = [];
const check = (name, fn) => { fn(); tests.push({ name, status: 'passed' }); };
const pkg = (dir, name) => JSON.parse(read(path.join(dir, 'node_modules', name, 'package.json')));
check('Fixed compiler versions', () => {
  assert.equal(pkg(v4, 'tailwindcss').version, '4.3.3');
  assert.equal(pkg(v4, '@tailwindcss/cli').version, '4.3.3');
  assert.equal(pkg(v3, 'tailwindcss').version, '3.4.19');
});
const postcss = createRequire(path.join(v3, 'package.json'))('postcss');
// Keep package lookup under the installed toolchain, but never reuse its files.
const work = mkdtempSync(path.join(v4, '.bridge-verify-'));
try {
for (const name of ['styles', 'tests']) cpSync(path.join(root, name), path.join(work, name), { recursive: true });
const sources = ['tailwind.config.js', 'claude-tokens.css', 'claude-reset-and-base.css', 'design-tokens.json'];
const snapshots = Object.fromEntries(sources.map(name => [name, hash(path.join(root, 'tests/reference', name))]));
function compile(name, dir, packageName, args) {
  const packageInfo = pkg(dir, packageName);
  const cli = path.join(dir, 'node_modules', packageName, packageInfo.bin.tailwindcss);
  const result = spawnSync(process.execPath, [cli, ...args], { cwd: dir, encoding: 'utf8' });
  writeFileSync(path.join(output, `${name}.cli.log`), `$ node ${cli} ${args.join(' ')}\n${result.stdout || ''}${result.stderr || ''}\nexit=${result.status}\n`);
  check(`${name}: CLI exit 0`, () => assert.equal(result.status, 0, result.stderr));
}
for (const kind of ['base', 'dark']) compile(kind, v4, '@tailwindcss/cli', ['-i', path.join(work, 'tests', `${kind}.input.css`), '-o', path.join(output, `${kind}.compiled.css`)]);
compile('v3', v3, 'tailwindcss', ['-c', path.join(root, 'tests/reference/tailwind.config.js'), '-i', path.join(root, 'tests/v3.input.css'), '--content', path.join(root, 'tests/v3.fixture.html'), '-o', path.join(output, 'v3.compiled.css')]);
const trees = Object.fromEntries(['base', 'dark', 'v3'].map(name => [name, postcss.parse(read(path.join(output, `${name}.compiled.css`)))]));
const declarations = (tree, selector, property) => {
  const found = [];
  tree.walkRules(selector, rule => rule.walkDecls(property, decl => found.push(decl.value)));
  return found;
};
const expected = {
  '.bg-canvas': ['background-color', 'var(--ui-canvas)'],
  '.bg-surface': ['background-color', 'var(--ui-surface)'],
  '.text-ink': ['color', 'var(--ui-ink)'],
  '.font-sans': ['font-family', 'var(--ui-font)'],
  '.font-serif': ['font-family', 'var(--ui-reading)'],
  '.font-mono': ['font-family', 'var(--ui-mono)'],
  '.rounded-control': ['border-radius', 'var(--ui-radius)'],
  '.rounded-card': ['border-radius', 'var(--ui-card-radius)'],
  '.rounded-composer': ['border-radius', 'var(--ui-composer-radius)'],
  '.min-h-control': ['min-height', 'var(--ui-control)'],
  '.shadow-float': ['--tw-shadow', 'var(--ui-shadow)']
};
for (const name of ['base', 'v3']) for (const [selector, [property, value]] of Object.entries(expected)) check(`${name}: ${selector} directly reads local token`, () => assert.ok(declarations(trees[name], selector, property).includes(value)));
check('v4 semantic spacing reads local variables', () => {
  for (const [selector, token] of [['.p-gutter', '5'], ['.p-section', '7'], ['.p-editorial', '8']]) assert.deepEqual(declarations(trees.base, selector, 'padding'), [`var(--ui-space-${token})`]);
});
check('Default bridge has no custom dark variant or @scope', () => {
  const source = read(path.join(root, 'styles/claude-tailwind-v4.css')).replace(/\/\*[\s\S]*?\*\//g, '');
  assert.doesNotMatch(source, /@custom-variant|@scope|@config/);
  assert.doesNotMatch(read(path.join(output, 'base.compiled.css')), /@scope|prefers-color-scheme|\.dark\\:/);
});
check('Optional v4 dark compiles into bounded atelier scope', () => {
  let count = 0;
  trees.dark.walkAtRules('scope', rule => {
    assert.equal(rule.params, '([data-ui="atelier"][data-theme="dark"]) to ([data-ui="atelier"])');
    assert.equal(rule.parent.selector, '.dark\\:bg-danger');
    assert.ok(rule.nodes.some(n => n.type === 'decl' && n.prop === 'background-color' && n.value === 'var(--ui-danger)'));
    count++;
  });
  assert.equal(count, 1);
  assert.doesNotMatch(read(path.join(output, 'dark.compiled.css')), /prefers-color-scheme/);
});
check('v3 selector dark compiles from original config snapshot', () => {
  const candidates = [];
  trees.v3.walkRules(rule => { if (rule.selector.includes('.dark\\:bg-danger')) candidates.push(rule); });
  assert.equal(candidates.length, 1);
  assert.match(candidates[0].selector, /:where\(\[data-theme="dark"\], \[data-theme="dark"\] \*\)/);
  assert.equal(candidates[0].nodes.find(n => n.prop === 'background-color').value, 'var(--ui-danger)');
  const config = createRequire(import.meta.url)(path.join(root, 'tests/reference/tailwind.config.js'));
  assert.deepEqual(config.corePlugins, { preflight: false });
});
for (const [name, tree] of Object.entries(trees)) check(`${name}: no global Preflight reset rules`, () => {
  tree.walkRules(rule => {
    const normal = (rule.nodes || []).filter(n => n.type === 'decl' && !n.prop.startsWith('--'));
    if (!normal.length || rule.selector.includes('[data-ui="atelier"]') || rule.selector.includes('.')) return;
    assert.fail(`Global non-class style rule: ${rule.selector}: ${normal.map(n => n.prop).join(', ')}`);
  });
  assert.doesNotMatch(read(path.join(output, `${name}.compiled.css`)), /-webkit-text-size-adjust|font-feature-settings:\s*normal|tab-size:\s*4|list-style:\s*none/);
});
check('Every inline bridge token exists in reviewed token CSS', () => {
  const bridge = read(path.join(root, 'styles/claude-tailwind-v4.css'));
  const tokens = read(path.join(root, 'tests/reference/claude-tokens.css'));
  for (const [, token] of bridge.matchAll(/var\((--ui-[\w-]+)\)/g)) assert.match(tokens, new RegExp(`${token}\\s*:`));
});
check('JSON palette values agree with CSS snapshots', () => {
  const palette = JSON.parse(read(path.join(root, 'tests/reference/design-tokens.json'))).palettes;
  const css = postcss.parse(read(path.join(root, 'tests/reference/claude-tokens.css')));
  for (const [name, record] of Object.entries(palette)) for (const theme of ['light', 'dark']) {
    let matched = null;
    css.walkRules(rule => { if (rule.selector.includes(`[data-palette="${name}"][data-theme="${theme}"]`)) matched = rule; });
    assert.ok(matched, `${name}/${theme}`);
    for (const [role, value] of Object.entries(record[theme])) assert.ok(matched.nodes.some(n => n.type === 'decl' && n.prop === `--ui-${role}` && n.value === value), `${name}/${theme}/${role}`);
  }
});
check('Reviewed source snapshots unchanged by tests', () => {
  for (const name of sources) assert.equal(hash(path.join(root, 'tests/reference', name)), snapshots[name]);
});
for (const name of ['base', 'dark']) {
  const html = read(path.join(root, 'tests', `${name}.fixture.html`));
  const css = read(path.join(output, `${name}.compiled.css`));
  check(`${name}: compiler MIT banner retained`, () => assert.ok(css.startsWith('/*! tailwindcss v4.3.3 | MIT License | https://tailwindcss.com */')));
  const complete = html.replace('<body', `<style>\n${css}\n</style>\n<body`);
  check(`${name}: standalone fixture has no scripts or external assets`, () => assert.doesNotMatch(complete, /<script\b|<link\b|\s(?:src|href)\s*=/i));
  writeFileSync(path.join(output, `${name}.compiled.html`), complete);
}
// The v3 comparison page uses the same reviewed token/base bytes and raw CLI output.
const v3FixtureCss = ['claude-tokens.css', 'claude-reset-and-base.css']
  .map(name => read(path.join(root, 'tests/reference', name))).join('\n')
  + '\n' + read(path.join(output, 'v3.compiled.css'));
writeFileSync(path.join(output, 'v3.compiled.html'),
  read(path.join(root, 'tests/v3.fixture.html')).replace('<body>',
    '<style>\n/*! Fixture generated with Tailwind CSS v3.4.19 (MIT). See THIRD-PARTY-LICENSES/tailwindcss-3.4.19-MIT.txt. */\n'
    + v3FixtureCss + '\n</style><body>'));
for (const [name, dir] of [['v4', v4], ['v3', v3]]) {
  for (const file of ['package.json', 'package-lock.json']) cpSync(path.join(dir, file), path.join(output, `${name}.${file}`));
}
const report = {
  generatedAt: new Date().toISOString(),
  status: 'passed',
  node: process.version,
  compilers: { tailwindcssV4: pkg(v4, 'tailwindcss').version, tailwindcssCli: pkg(v4, '@tailwindcss/cli').version, tailwindcssV3: pkg(v3, 'tailwindcss').version },
  registry: 'https://registry.npmjs.org/',
  installation: 'Exact versions; --ignore-scripts --no-audit --no-fund; separate tooling folders; no publication dependency changes.',
  sourceSnapshots: snapshots,
  assertions: tests.length,
  tests,
  browserStatus: 'Not run by this script. Browser verification is separate; see browser-results.json if present.',
  limits: ['No cross-version equivalence claim.', 'No all-browser compatibility claim.', 'No Preflight is not zero global CSS: Tailwind utility custom-property initializers may be global.', 'Optional @scope dark variant is not imported by the default bridge.']
};
writeFileSync(path.join(output, 'results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(`${tests.length} assertions passed. Compiled v4.3.3 base/dark + v3.4.19 original config regression. Report: ${output}`);
} finally {
  // Only this invocation's newly created directory is removed.
  rmSync(work, { recursive: true, force: true });
}
