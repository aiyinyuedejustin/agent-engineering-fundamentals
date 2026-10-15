'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { test, after } = require('node:test');
const { audit, readDocument } = require('./check-token-parity.cjs');

const source = process.env.TOKEN_PARITY_ROOT;
assert.ok(source, 'Set TOKEN_PARITY_ROOT to the chapter directory');
const fixture = fs.mkdtempSync(path.join(__dirname, '.mutation-'));
const originals = new Map();
for (const directory of ['styles', 'templates']) fs.mkdirSync(path.join(fixture, directory));
for (const file of ['styles/claude-tokens.css', 'styles/design-tokens.json', ...fs.readdirSync(path.join(source, 'templates')).filter(name => /^0[1-6]-.*\.html$/.test(name)).map(name => `templates/${name}`)]) {
  const text = fs.readFileSync(path.join(source, file), 'utf8');
  originals.set(file, text); fs.writeFileSync(path.join(fixture, file), text);
}
after(() => fs.rmSync(fixture, { recursive: true, force: true }));
const first = 'templates/01-component-gallery.html';
function mutate(file, transform, fn) {
  const before = originals.get(file), after = transform(before);
  assert.notEqual(after, before, 'mutation must change the fixture');
  fs.writeFileSync(path.join(fixture, file), after);
  try { fn(); } finally { fs.writeFileSync(path.join(fixture, file), before); }
}
function rejects(name, transform, subject, file = first) {
  test(name, () => mutate(file, transform, () => {
    const report = audit(fixture);
    assert.equal(report.passed, false);
    assert.ok(report.differences.some(d => d.subject.includes(subject)), `Expected diagnostic containing ${subject}`);
  }));
}
test('unchanged eight-file fixture passes all six pages and sixty palette/theme cells', () => {
  const report = audit(fixture);
  assert.equal(report.passed, true);
  assert.equal(report.templates.length, 6);
  assert.equal(report.templates.flatMap(t => t.paletteThemes).filter(t => t.passed).length, 60);
  assert.equal(report.baseline.customPropertyDeclarations, 188);
});
const data = JSON.parse(originals.get('styles/design-tokens.json'));
for (const file of originals.keys()) if (file.startsWith('templates/')) {
  for (const [palette, values] of Object.entries(data.palettes)) for (const theme of ['light', 'dark']) {
    rejects(`${file}: detects ${palette}/${theme} value drift`, text => text.replace(`--ui-canvas: ${values[theme].canvas};`, '--ui-canvas: #010203;'), '--ui-canvas', file);
  }
}
rejects('detects missing palette declaration', text => text.replace('  --ui-canvas: #f8f7f3;\n', ''), 'declaration order/set');
rejects('detects duplicate property even with identical value', text => text.replace('--ui-canvas: #f8f7f3;', '--ui-canvas: #f8f7f3; --ui-canvas: #f8f7f3;'), 'declaration order/set');
rejects('detects important priority drift', text => text.replace('--ui-canvas: #f8f7f3;', '--ui-canvas: #f8f7f3 !important;'), '--ui-canvas');
rejects('detects independently controlled action drift', text => text.replace('--ui-action: #272722;', '--ui-action: #111111;'), '--ui-action');
rejects('detects font stack drift', text => text.replace('BlinkMacSystemFont,', 'Arial,'), '--ui-font');
rejects('detects density value drift', text => text.replace('--ui-control: 36px;', '--ui-control: 35px;'), '--ui-control');
rejects('detects reading value drift', text => text.replace('--ui-reading-size: 21px;', '--ui-reading-size: 22px;'), '--ui-reading-size');
rejects('detects color-scheme drift despite unchanged dataset code', text => text.replace('color-scheme: light;', 'color-scheme: dark;'), 'color-scheme');
rejects('detects selector specificity drift', text => text.replace(':where([data-ui="atelier"][data-palette="sage"][data-theme="dark"])', '[data-ui="atelier"][data-palette="sage"][data-theme="dark"]'), 'selector/context');
rejects('detects same-element versus descendant scope drift', text => text.replace('[data-ui="atelier"][data-palette="sage"]', '[data-ui="atelier"] [data-palette="sage"]'), 'selector/context');
rejects('detects removed default paper/light selector', text => text.replace(':where([data-ui="atelier"]),\n', ''), 'selector/context');
rejects('detects media condition drift', text => text.replace('@media (prefers-reduced-motion: reduce)', '@media (prefers-reduced-motion: no-preference)'), 'selector/context');
rejects('detects appended rule override in a second style element', text => text.replace('</head>', '<style>[data-ui="atelier"]{--ui-canvas:#000}</style></head>'), 'token rule count');
rejects('detects inline style token override', text => text.replace('<body>', '<body style="--ui-canvas:#000">'), 'inline token overrides');
rejects('detects missing root scope attribute', text => text.replace('data-ui="atelier"', 'data-ui="other"'), 'root data-ui');
rejects('detects JSON-only color drift', text => text.replace('#f8f7f3', '#f8f7f2'), 'JSON/CSS paper/light/canvas', 'styles/design-tokens.json');
rejects('detects JSON-only density drift', text => text.replace('"36px"', '"35px"'), 'JSON/CSS compact control', 'styles/design-tokens.json');
rejects('detects JSON font category drift', text => text.replace('system serif', 'system sans-serif'), 'JSON font category reading', 'styles/design-tokens.json');
test('rejects conditional style container rather than claiming active parity', () => mutate(first, text => text.replace('<style>', '<style media="print">'), () => assert.throws(() => audit(fixture), /conditional or inactive/)));
test('rejects unsupported token registration', () => mutate(first, text => text.replace('</style>', '@property --ui-canvas { syntax: "<color>"; inherits: false; initial-value: red; }</style>'), () => assert.throws(() => audit(fixture), /registration is outside/)));
test('rejects escaped property names in added CSS rules', () => mutate(first, text => text.replace('</head>', '<style>[data-ui="atelier"]{--\\75i-canvas:#010203!important}</style></head>'), () => assert.throws(() => audit(fixture), /escaped CSS declaration/)));
test('rejects escaped property names in inline style attributes', () => mutate(first, text => text.replace('<body>', '<body style="--\\000075i-canvas:#010203">'), () => assert.throws(() => audit(fixture), /escaped CSS declaration/)));
test('rejects escaped registration names', () => mutate(first, text => text.replace('</style>', '@property --\\75i-canvas { syntax: "<color>"; inherits: false; initial-value: red; }</style>'), () => assert.throws(() => audit(fixture), /registration is outside/)));
test('rejects uppercase PROPERTY registration', () => mutate(first, text => text.replace('</style>', '@PROPERTY --ui-canvas { syntax: "<color>"; inherits: false; initial-value: red; }</style>'), () => assert.throws(() => audit(fixture), /registration is outside/)));
test('rejects external CSS import without loading it', () => mutate(first, text => text.replace('<style>', '<style>@import "override.css";'), () => assert.throws(() => audit(fixture), /external stylesheet @import/)));
test('rejects external stylesheet LINK without loading it', () => mutate(first, text => text.replace('</head>', '<link rel="stylesheet" href="override.css"></head>'), () => assert.throws(() => audit(fixture), /external stylesheet LINK/)));
test('rejects invalid CSS syntax rather than silently skipping it', () => mutate(first, text => text.replace('--ui-canvas: #f8f7f3;', '--ui-canvas #f8f7f3;'), () => assert.throws(() => audit(fixture), /Unknown word/)));
test('ignores inert script strings instead of treating their STYLE text as active CSS', () => mutate(first, text => text.replace('</body>', '<script>const demo = "<style>:root{--ui-canvas:red}</style>";</script></body>'), () => assert.equal(audit(fixture).passed, true)));
test('excludes inert TEMPLATE content from the initial-document contract', () => mutate(first, text => text.replace('</body>', '<template><style>:root{--ui-canvas:red}</style></template></body>'), () => assert.equal(audit(fixture).passed, true)));
test('allows comments and selector-list separator formatting without changing declarations', () => mutate(first, text => text.replace(':where([data-ui="atelier"]),\n', '/* changed comment */ :where([data-ui="atelier"]),   \n'), () => {
  const report = audit(fixture); assert.equal(report.passed, true); assert.equal(report.templates[0].exactCanonicalPrefix, false);
}));
test('template 03 contains one active style element; its JavaScript preview string is separate', () => {
  const file = [...originals.keys()].find(name => name.startsWith('templates/03-'));
  assert.equal(readDocument(originals.get(file), file).styles.length, 1);
});
test('CLI returns status 0 and machine-readable JSON for passing sources', () => {
  const result = spawnSync(process.execPath, [path.join(__dirname, 'check-token-parity.cjs'), fixture], { encoding: 'utf8' });
  assert.equal(result.status, 0); assert.equal(JSON.parse(result.stdout).passed, true);
});
test('CLI returns status 1 and exact diagnostic for drift', () => mutate(first, text => text.replace('--ui-canvas: #f8f7f3;', '--ui-canvas: #010203;'), () => {
  const result = spawnSync(process.execPath, [path.join(__dirname, 'check-token-parity.cjs'), fixture], { encoding: 'utf8' });
  assert.equal(result.status, 1); assert.equal(JSON.parse(result.stdout).passed, false);
  assert.match(result.stdout, /--ui-canvas/);
}));
test('CLI returns status 2 for missing required input', () => {
  const result = spawnSync(process.execPath, [path.join(__dirname, 'check-token-parity.cjs')], { encoding: 'utf8' });
  assert.equal(result.status, 2); assert.match(result.stderr, /Usage:/);
});
