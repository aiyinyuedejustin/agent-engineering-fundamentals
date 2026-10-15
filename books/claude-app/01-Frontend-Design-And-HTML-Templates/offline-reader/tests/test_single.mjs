import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { BASE, PREVIEW, build } from '../build.mjs';
import { buildSingle } from '../build-preview-single.mjs';

const scratch=fs.mkdtempSync(path.join(BASE,'tests/.single-scratch-'));
const source=path.join(scratch,'source');fs.mkdirSync(source);
const put=(rel,data)=>{const file=path.join(source,rel);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,data);};
put(PREVIEW.entry,`# 单文件测试

## reader-single-source
## reader-single-contents
## main

[正文](#main)
[![预算图](../../assets/figures/context-budget-ledger.svg)](../../assets/figures/context-budget-ledger.svg)
[未收录](README.md)
[来源](https://example.com/reference)
[危险](javascript:alert%281%29)

<script>globalThis.executed=true</script>

<img src="https://example.com/tracker" onerror="alert(1)">

~~~html
</style><script>alert('code')</script>
~~~
`);
put(PREVIEW.images[0],'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="40"><style>text{fill:#26251f}</style><rect width="100" height="40" fill="#f8f7f3"/><text x="4" y="24">预算图</text></svg>');
put('01-Frontend-Design-And-HTML-Templates/README.md','MUST_NOT_READ_OUTSIDE_PREVIEW'+'.'.repeat(6*1024*1024));
const one=path.join(scratch,'one.html'),two=path.join(scratch,'two.html');
const first=buildSingle({source,out:one});
const html=fs.readFileSync(one,'utf8');
const audit=file=>spawnSync('python3',[path.join(BASE,'tests/audit_single.py'),file],{encoding:'utf8'});

test('single-file preview has exact CSS hash, one validated data SVG and valid same-page navigation',()=>{
  const result=audit(one);assert.equal(result.status,0,result.stdout+result.stderr);
  assert.match(html,/style-src &#x27;sha256-/);
  assert.match(html,/img-src data:/);
  assert.ok(!html.includes('unsafe-inline')&&!html.includes('https:*'));
  assert.ok(!/<link\b|<script\b|<iframe\b|<base\b|<svg\b/i.test(html));
  assert.ok(!/src="https?:/.test(html));
  assert.match(html,/id="reader-single-source-1"/);
  assert.match(html,/id="reader-single-contents-1"/);
  assert.match(html,/&lt;script&gt;globalThis.executed=true&lt;\/script&gt;/);
  assert.ok(!html.includes('MUST_NOT_READ_OUTSIDE_PREVIEW'));
});
test('single-file build is byte-deterministic and leaves no temporary parts',()=>{
  const second=buildSingle({source,out:two});assert.equal(first.sha256,second.sha256);
  assert.equal(fs.readFileSync(one,'utf8'),fs.readFileSync(two,'utf8'));
  assert.ok(!fs.readdirSync(scratch).some(name=>name.startsWith('.single-preview-work-')));
});
test('CRLF stylesheet checkouts normalize before calculating the inline CSP hash',()=>{
  const site=path.join(scratch,'crlf-parts');build({source,out:site,preview:true});
  const css=path.join(site,'reader.css');fs.writeFileSync(css,fs.readFileSync(css,'utf8').replace(/\n/g,'\r\n'));
  const result=spawnSync('python3',[path.join(BASE,'single_page.py'),site],{encoding:'utf8',input:JSON.stringify({entry:PREVIEW.entry,image:PREVIEW.images[0],compilerInputs:[]})});
  assert.equal(result.status,0,result.stderr);
  const output=path.join(scratch,'crlf.html');fs.writeFileSync(output,result.stdout);
  const checked=audit(output);assert.equal(checked.status,0,checked.stdout+checked.stderr);
});
test('independent audit detects CSS tampering, broader CSP, and active SVG data',()=>{
  const altered=path.join(scratch,'tampered.html');
  for(const bad of [
    html.replace('<style>','<style>/* changed */'),
    html.replace('img-src data:','img-src data: https:'),
    html.replace(/data:image\/svg\+xml;base64,[A-Za-z0-9+/=]+/,'data:image/svg+xml;base64,'+Buffer.from('<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>').toString('base64')),
  ]){fs.writeFileSync(altered,bad);assert.notEqual(audit(altered).status,0);}
});
test('single output never overwrites, traverses symlinks, or writes within the book',()=>{
  assert.throws(()=>buildSingle({source,out:one}),/already exists/);
  assert.equal(fs.readFileSync(one,'utf8'),html);
  assert.throws(()=>buildSingle({source,out:path.join(source,'new.html')}),/outside source/);
  const alias=path.join(scratch,'alias');fs.symlinkSync('/tmp',alias);
  assert.throws(()=>buildSingle({source,out:path.join(alias,'new-single.html')}),/symlink/);
});
test.after(()=>fs.rmSync(scratch,{recursive:true,force:true}));
