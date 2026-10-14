import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const css = readFileSync(new URL('./tokens.css', import.meta.url), 'utf8');
const rules = [...css.matchAll(/:root(?:\[data-theme="dark"\])?\s*\{([^}]+)\}/g)];
const values = body => Object.fromEntries([...body.matchAll(/--([\w-]+):\s*(#[a-f\d]{6})\s*;/gi)].map(m => [m[1], m[2]]));
const luminance = hex => {
  const rgb = hex.slice(1).match(/../g).map(v => parseInt(v, 16) / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4);
  return rgb[0] * .2126 + rgb[1] * .7152 + rgb[2] * .0722;
};
const contrast = (a, b) => { const x = luminance(a), y = luminance(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
test('both original themes preserve selected text and control contrast', () => {
  assert.equal(rules.length, 2);
  for (const rule of rules) {
    const v = values(rule[1]);
    for (const foreground of ['text', 'muted', 'brand']) for (const background of ['canvas', 'surface', 'raised', 'selection']) assert.ok(contrast(v[foreground], v[background]) >= 4.5, `${foreground}/${background}`);
    assert.ok(contrast(v['on-action'], v.action) >= 4.5);
    assert.ok(contrast(v.danger, v['danger-bg']) >= 4.5);
    for (const bg of ['canvas', 'surface', 'raised', 'selection']) {
      assert.ok(contrast(v.focus, v[bg]) >= 3);
      assert.ok(contrast(v['control-border'], v[bg]) >= 3);
    }
  }
});
test('the portable HTML uses local styles and text-only user insertion', () => {
  const html = readFileSync(new URL('./skeleton.html', import.meta.url), 'utf8');
  assert.ok(html.includes('href="tokens.css"'));
  assert.ok(html.includes('body.textContent = value'));
  assert.ok(!/\binnerHTML\b|https?:\/\//.test(html));
});
