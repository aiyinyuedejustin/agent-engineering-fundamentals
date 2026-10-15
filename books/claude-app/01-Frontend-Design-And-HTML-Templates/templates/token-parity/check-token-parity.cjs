#!/usr/bin/env node
'use strict';
// Static source-contract check. No browser, network, script execution, or source writes.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const postcss = require('postcss');
const parse5 = require('parse5');

const PALETTES = ['paper', 'sage', 'ocean', 'plum', 'graphite'];
const THEMES = ['light', 'dark'];
const ROLES = ['canvas', 'sidebar', 'surface', 'ink', 'muted', 'line', 'line-strong', 'accent', 'accent-soft'];
const COMMON = ['action', 'on-action', 'danger', 'danger-soft', 'success', 'success-soft', 'scrim'];
const SCOPE = '[data-ui="atelier"]';
const scope = extra => `:where(${SCOPE}${extra || ''})`;
const hash = value => crypto.createHash('sha256').update(value).digest('hex');
const isToken = prop => {
  // Fail closed rather than partially decoding CSS escapes and missing equivalent names.
  if (prop.includes('\\')) throw new Error(`Unsupported escaped CSS declaration name: ${prop}`);
  return prop.startsWith('--ui-') || prop.toLowerCase() === 'color-scheme';
};
const clean = record => ({ context: record.context, selectors: record.selectors, declarations: record.declarations });

function tokenRules(css, file, lineOffset = 0) {
  const ast = postcss.parse(css, { from: file });
  const records = [];
  ast.walkAtRules(node => {
    if (node.name.includes('\\')) throw new Error(`${file}: escaped CSS at-rule name is outside this static contract`);
    const name = node.name.toLowerCase();
    if (name === 'import') throw new Error(`${file}: external stylesheet @import is outside this inline contract`);
    if (name === 'property' && (node.params.includes('\\') || node.params.trim().startsWith('--ui-'))) {
      throw new Error(`${file}: @property token registration is outside this static contract`);
    }
  });
  ast.walkDecls(decl => {
    if (isToken(decl.prop) && decl.parent.type !== 'rule') throw new Error(`${file}: token declaration outside a CSS rule`);
  });
  ast.walkRules(rule => {
    if (!rule.nodes.some(node => node.type === 'decl' && isToken(node.prop))) return;
    const context = [];
    for (let parent = rule.parent; parent && parent.type !== 'root'; parent = parent.parent) {
      context.unshift(parent.type === 'atrule' ? `@${parent.name} ${parent.params.trim()}` : `rule:${parent.selector}`);
    }
    records.push({
      location: `${file}:${rule.source.start.line + lineOffset}`,
      context,
      // Only trim selector-list separators; preserve meaningful internal whitespace.
      selectors: postcss.list.comma(rule.selector).map(value => value.trim()),
      declarations: rule.nodes.filter(node => node.type === 'decl').map(node => ({
        property: node.prop, value: node.value.trim(), important: Boolean(node.important),
      })),
    });
  });
  return records;
}

function readDocument(html, file) {
  const doc = parse5.parse(html, { sourceCodeLocationInfo: true });
  let root;
  const rules = [], styles = [], inlineTokens = [];
  function walk(node) {
    if (node.tagName === 'html') root = Object.fromEntries(node.attrs.map(a => [a.name, a.value]));
    if (node.tagName === 'link') {
      const attrs = Object.fromEntries(node.attrs.map(a => [a.name, a.value]));
      if ((attrs.rel || '').toLowerCase().split(/\s+/).includes('stylesheet')) throw new Error(`${file}: external stylesheet LINK is outside this inline contract`);
    }
    if (node.tagName === 'style') {
      const css = (node.childNodes || []).map(child => child.value || '').join('');
      const attrs = Object.fromEntries(node.attrs.map(a => [a.name, a.value]));
      const records = tokenRules(css, file, node.sourceCodeLocation.startTag.endLine - 1);
      // A disabled/non-CSS/conditional style block is not equivalent to an active inline stylesheet.
      if (records.length && (('media' in attrs) || ('disabled' in attrs) || (attrs.type && attrs.type.toLowerCase() !== 'text/css'))) {
        throw new Error(`${file}: token-containing STYLE has conditional or inactive attributes`);
      }
      rules.push(...records); styles.push(css);
    }
    const inline = (node.attrs || []).find(a => a.name === 'style');
    if (inline) {
      postcss.parse(`x{${inline.value}}`, { from: file }).walkDecls(decl => {
        if (isToken(decl.prop)) inlineTokens.push({ location: `${file}:${node.sourceCodeLocation.startLine}`, property: decl.prop, value: decl.value });
      });
    }
    for (const child of node.childNodes || []) walk(child);
    // Deliberately exclude inert TEMPLATE content, script strings, and iframe documents.
  }
  walk(doc);
  return { root, rules, styles, inlineTokens };
}

function audit(root) {
  root = path.resolve(root);
  const differences = [], files = {};
  const compare = (subject, actual, expected) => {
    if (JSON.stringify(actual) !== JSON.stringify(expected)) differences.push({ subject, expected, actual });
  };
  const read = relative => {
    const contents = fs.readFileSync(path.join(root, relative), 'utf8');
    files[relative] = hash(contents); return contents;
  };
  const css = read('styles/claude-tokens.css');
  const data = JSON.parse(read('styles/design-tokens.json'));
  const baseline = tokenRules(css, 'styles/claude-tokens.css');
  const values = record => Object.fromEntries((record?.declarations || []).map(d => [d.property, d.value]));
  const expectValue = (record, property, expected, subject) => compare(subject, values(record)[property], String(expected));
  compare('JSON schemaVersion', data.schemaVersion, 1);
  compare('JSON scope', data.scope, SCOPE);
  compare('JSON palette set', Object.keys(data.palettes || {}).sort(), [...PALETTES].sort());
  compare('canonical token rule count', baseline.length, 16);

  const shape = PALETTES.flatMap(palette => THEMES.map(theme => ({
    context: [], selectors: [...(palette === 'paper' && theme === 'light' ? [scope()] : []), scope(`[data-palette="${palette}"][data-theme="${theme}"]`)],
  })));
  shape.push(
    { context: [], selectors: [scope()] },
    { context: [], selectors: [scope('[data-theme="dark"]')] },
    { context: [], selectors: [scope('[data-density="compact"]')] },
    { context: [], selectors: [scope('[data-density="comfortable"]')] },
    { context: [], selectors: [scope('[data-reading="large"]')] },
    { context: ['@media (prefers-reduced-motion: reduce)'], selectors: [scope()] },
  );
  shape.forEach((expected, index) => {
    const rule = baseline[index];
    compare(`canonical rule ${index + 1} selector/context contract`, rule && { context: rule.context, selectors: rule.selectors }, expected);
  });
  baseline.forEach((rule, index) => {
    compare(`canonical rule ${index + 1} duplicate declarations`, new Set(rule.declarations.map(d => d.property)).size, rule.declarations.length);
    compare(`canonical rule ${index + 1} importance`, rule.declarations.some(d => d.important), false);
  });
  const matrix = [];
  PALETTES.forEach((palette, p) => THEMES.forEach((theme, t) => {
    const rule = baseline[p * 2 + t], json = data.palettes?.[palette]?.[theme] || {};
    compare(`JSON ${palette}/${theme} role set`, Object.keys(json).sort(), [...ROLES].sort());
    compare(`CSS ${palette}/${theme} declaration set`, Object.keys(values(rule)).sort(), ['color-scheme', ...ROLES.concat(COMMON).map(role => `--ui-${role}`)].sort());
    expectValue(rule, 'color-scheme', theme, `CSS ${palette}/${theme} color-scheme`);
    ROLES.forEach(role => expectValue(rule, `--ui-${role}`, json[role], `JSON/CSS ${palette}/${theme}/${role}`));
    COMMON.forEach(role => expectValue(rule, `--ui-${role}`, values(baseline[t])[`--ui-${role}`], `CSS common ${palette}/${theme}/${role}`));
    matrix.push({ palette, theme, jsonRoles: ROLES.length, cssCustomProperties: rule?.declarations.filter(d => d.property.startsWith('--ui-')).length, location: rule?.location });
  }));
  const foundation = baseline[10];
  (data.spacing || []).forEach((value, i) => expectValue(foundation, `--ui-space-${i + 1}`, `${value}px`, `JSON/CSS spacing ${i + 1}`));
  compare('JSON spacing count', data.spacing?.length, 8);
  for (const [name, prop] of Object.entries({ control: 'radius', card: 'card-radius', composer: 'composer-radius' })) {
    expectValue(foundation, `--ui-${prop}`, `${data.radius?.[name]}px`, `JSON/CSS radius ${name}`);
  }
  for (const [i, density] of ['compact', 'comfortable'].entries()) {
    expectValue(baseline[12 + i], '--ui-control', data.profiles?.[density]?.controlMinHeight, `JSON/CSS ${density} control`);
    expectValue(baseline[12 + i], '--ui-text', data.profiles?.[density]?.uiFontSize, `JSON/CSS ${density} text`);
  }
  expectValue(foundation, '--ui-reading-size', data.profiles?.reading?.default, 'JSON/CSS default reading');
  expectValue(foundation, '--ui-leading', data.profiles?.reading?.lineHeight, 'JSON/CSS reading line height');
  expectValue(baseline[14], '--ui-reading-size', data.profiles?.reading?.large, 'JSON/CSS large reading');
  // JSON fonts are generic categories, not literal font stacks. Compare their generic fallback only.
  for (const [name, prop, generic] of [['ui', 'font', 'sans-serif'], ['reading', 'reading', 'serif'], ['code', 'mono', 'monospace']]) {
    compare(`JSON font category ${name}`, data.fonts?.[name], `system ${generic}`);
    compare(`CSS generic font fallback ${name}`, values(foundation)[`--ui-${prop}`]?.split(',').at(-1).trim(), generic);
  }

  const names = fs.readdirSync(path.join(root, 'templates')).filter(name => /^0[1-6]-.*\.html$/.test(name)).sort();
  compare('six template numbers', names.map(name => name.slice(0, 2)), ['01', '02', '03', '04', '05', '06']);
  const templates = names.map(name => {
    const relative = `templates/${name}`, html = read(relative), start = differences.length;
    const document = readDocument(html, relative);
    compare(`${relative} root data-ui`, document.root?.['data-ui'], 'atelier');
    compare(`${relative} root data-palette valid`, PALETTES.includes(document.root?.['data-palette']), true);
    compare(`${relative} root data-theme valid`, THEMES.includes(document.root?.['data-theme']), true);
    compare(`${relative} inline token overrides`, document.inlineTokens, []);
    compare(`${relative} token rule count`, document.rules.length, baseline.length);
    const length = Math.max(document.rules.length, baseline.length);
    for (let i = 0; i < length; i++) {
      const actual = document.rules[i], expected = baseline[i], prefix = `${relative} rule ${i + 1}${actual ? ` (${actual.location})` : ''}`;
      compare(`${prefix} selector/context`, actual && { context: actual.context, selectors: actual.selectors }, expected && { context: expected.context, selectors: expected.selectors });
      compare(`${prefix} declaration order/set`, actual?.declarations.map(d => d.property), expected?.declarations.map(d => d.property));
      for (const declaration of expected?.declarations || []) {
        compare(`${prefix} ${declaration.property}`, actual?.declarations.filter(d => d.property === declaration.property), [declaration]);
      }
    }
    return { file: relative, passed: differences.length === start, styleElements: document.styles.length,
      exactCanonicalPrefix: document.styles[0]?.trimStart().startsWith(css) || false,
      tokenRules: document.rules.length, customPropertyDeclarations: document.rules.flatMap(r => r.declarations).filter(d => d.property.startsWith('--ui-')).length,
      paletteThemes: matrix.map(({ palette, theme }) => ({ palette, theme, passed: JSON.stringify(clean(document.rules[PALETTES.indexOf(palette) * 2 + THEMES.indexOf(theme)] || { context: [], selectors: [], declarations: [] })) === JSON.stringify(clean(baseline[PALETTES.indexOf(palette) * 2 + THEMES.indexOf(theme)] || { context: [], selectors: [], declarations: [] })) })),
    };
  });
  return { schemaVersion: 1, generatedAt: new Date().toISOString(), runner: { node: process.version, cssParser: `postcss ${postcss().version}`, htmlParser: 'parse5' }, method: 'Static HTML + CSS AST declaration/selector contract; no browser cascade or paint verification',
    passed: differences.length === 0, baseline: { files: ['styles/claude-tokens.css', 'styles/design-tokens.json'], bytes: Buffer.byteLength(css), tokenRules: baseline.length,
      customPropertyDeclarations: baseline.flatMap(r => r.declarations).filter(d => d.property.startsWith('--ui-')).length,
      uniqueCustomProperties: new Set(baseline.flatMap(r => r.declarations).filter(d => d.property.startsWith('--ui-')).map(d => d.property)).size,
      jsonColorValues: 90, jsonNumericValues: 18, paletteThemes: matrix }, templates, differences, sha256: files };
}

if (require.main === module) {
  if (!process.argv[2] || process.argv.length > 3) { console.error('Usage: node check-token-parity.cjs <chapter-root>'); process.exitCode = 2; }
  else {
    try { const report = audit(process.argv[2]); process.stdout.write(JSON.stringify(report, null, 2) + '\n'); process.exitCode = report.passed ? 0 : 1; }
    catch (error) { console.error(error.stack); process.exitCode = 2; }
  }
}
module.exports = { audit, tokenRules, readDocument };
