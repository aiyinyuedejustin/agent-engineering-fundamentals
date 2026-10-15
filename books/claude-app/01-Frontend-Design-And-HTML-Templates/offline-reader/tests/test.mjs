import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { BASE, PREVIEW, build, escape } from '../build.mjs';

const scratch = path.join(BASE,'tests','.scratch');
fs.mkdirSync(scratch,{recursive:true});
const fixture = fs.mkdtempSync(path.join(scratch,'fixture-'));
const section='01-Frontend-Design-And-HTML-Templates';
const set=(rel,text)=>{const f=path.join(fixture,rel);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,text);};
const md=`# 安全测试 &lt;标题&gt;

## 同名
## 同名
## 同名-1
## main

> ## 嵌套标题
> ## 嵌套标题

[保留ID](#main)
[第三标题](#同名-1-1)
[嵌套锚点](#嵌套标题-1)

[下一页](${section}/README.md#中文标题)
[嵌套图片](${section}/README.md)
[![原图](assets/good.svg)](assets/good.svg)
[模板](${section}/demo.html)
[目录](${section}/files/)
[正常来源](https://example.com/reference?q=%22test%22)
[危险协议](javascript:alert%281%29)
[实体协议](j&#97;vascript:alert%281%29)
[大小写协议](JaVaScRiPt:alert%281%29)
[数据协议](data:text/html,%3Cscript%3Ealert%281%29%3C/script%3E)
[本机协议](file:///etc/passwd)
[网络路径](//example.com/leak)
[逃离根目录](../private-downloads/secret.md)
[编码逃离根目录](%2e%2e/private-downloads/secret.md)
[符号链接](assets/secret.md)
[不存在](missing.md)

![远程图片](https://example.com/tracker.jpg)
![坏图](assets/bad.svg)
![外链图](assets/external.svg)
![动画图](assets/animate.svg)

<script>alert('raw')</script>

<iframe src="https://example.com/escape"></iframe>

内联 <img src=x onerror="alert(1)"> 文字 <br> 下一行 <br onclick="alert(1)">

<svg onload="alert(1)"></svg>

~~~html onload="alert(1)"
<script>globalThis.executed=true</script>
</code></pre><img src=x onerror=alert(1)>
~~~

~~~mermaid
flowchart LR
  A --> B
~~~

| 对齐 | 转义 | 代码 |
|:---|---:|:---:|
| **加粗** | <img src=x onerror=alert(1)> | \`a \\| b\` |

- [x] 已完成
- [ ] 未完成
  - 嵌套列表

> 引用 **文本**
`;
set('README.md',md);
set(section+'/README.md','# 子页\n\n## 中文标题\n\n[返回](../README.md#同名-1)\n\n正文。\n');
set(section+'/demo.html','<!doctype html><script>globalThis.executed=true</script><img src="https://example.com/tracker">');
set(section+'/files/sample.js','fetch("https://example.com/not-run")');
set('assets/good.svg','<svg xmlns="http://www.w3.org/2000/svg" width="100" height="40"><title>safe</title><rect width="100" height="40" fill="#f8f7f3"/></svg>');
set('assets/bad.svg','<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>');
set('assets/external.svg','<svg xmlns="http://www.w3.org/2000/svg"><style>text{fill:url(https://example.com/leak)}</style></svg>');
set('assets/animate.svg','<svg xmlns="http://www.w3.org/2000/svg"><animate attributeName="href" values="javascript:alert(1)"/></svg>');
set('assets/long-invalid-css.svg','<svg xmlns="http://www.w3.org/2000/svg"><style>'+'a'.repeat(100000)+'</style></svg>');
set('assets/utf16-entity.svg',Buffer.from('<?xml version="1.0" encoding="UTF-16"?><!DOCTYPE svg [<!ENTITY name "ENTITY_EXPANSION">]><svg xmlns="http://www.w3.org/2000/svg"><text>&name;</text></svg>','utf16le'));
set('private-downloads/secret.md','# MUST_NOT_APPEAR_IN_OUTPUT');
set('.hidden/secret.md','# MUST_NOT_APPEAR_IN_OUTPUT');
set('assets/screenshots/07-color-catalog-dark-green-d63d0f4.jpg','POLICY_EXCLUDED_DO_NOT_READ');
fs.symlinkSync('../private-downloads/secret.md',path.join(fixture,'assets/secret.md'));
const outA=path.join(scratch,'a'),outB=path.join(scratch,'b');
const result=build({source:fixture,out:outA});
const html=fs.readFileSync(path.join(outA,'index.html'),'utf8');
function treeDigest(dir){
  const entries=[];
  function walk(rel=''){for(const n of fs.readdirSync(path.join(dir,rel)).sort()){const p=rel?rel+'/'+n:n;if(fs.statSync(path.join(dir,p)).isDirectory())walk(p);else entries.push([p,crypto.createHash('sha256').update(fs.readFileSync(path.join(dir,p))).digest('hex')]);}}walk();return entries;
}

test('all output bytes and manifests are deterministic across clean output paths',()=>{
  build({source:fixture,out:outB});assert.deepEqual(treeDigest(outA),treeDigest(outB));
  assert.throws(()=>build({source:fixture,out:outA}),/already exists/);
});
test('source Markdown changes drive output and fingerprint changes',()=>{
  set(section+'/README.md','# 子页\n\n## 中文标题\n\n更新后的正文。\n');
  const changed=build({source:fixture,out:path.join(scratch,'changed')});
  assert.notEqual(changed.sourceFingerprint,result.sourceFingerprint);
  assert.match(fs.readFileSync(path.join(scratch,'changed/pages',section,'README.md.html'),'utf8'),/更新后的正文/);
});
test('raw HTML and fenced examples are escaped, never live elements',()=>{
  assert.ok(!/<script\b|<iframe\b|<svg\b/i.test(html));
  assert.match(html,/&lt;script&gt;alert\(&#39;raw&#39;\)&lt;\/script&gt;/);
  assert.match(html,/&lt;\/code&gt;&lt;\/pre&gt;&lt;img/);
  assert.ok(!/<br\b[^>]*onclick/.test(html));
  assert.match(html,/script-src &#39;none&#39;/);
  assert.equal(escape('<>&"\''),'&lt;&gt;&amp;&quot;&#39;');
});
test('protocol, entity, path traversal and symlink attacks become inactive labels',()=>{
  assert.ok(result.warnings.some(w=>w.type==='outside-source-root'));
  assert.ok(result.warnings.some(w=>w.target==='assets/secret.md'&&w.type==='missing-local-target'));
  assert.ok(!/href="(?:javascript:|JaVaScRiPt:|data:|file:|\/\/)/i.test(html));
  assert.ok(!html.includes('MUST_NOT_APPEAR_IN_OUTPUT'));
  assert.ok(!result.inputs.some(f=>f.path.includes('private-downloads')||f.path.includes('secret')));
  assert.equal(result.excluded.length,1);
  assert.ok(!result.inputs.some(f=>f.path.includes('dark-green')));
});
test('images are local, strict SVG whitelist rejects active elements and CSS',()=>{
  assert.equal(result.images,1);
  assert.equal(result.warnings.filter(w=>w.type==='rejected-svg').length,5);
  assert.ok(!/<img[^>]+src="https?:/.test(html));
  assert.ok(!fs.existsSync(path.join(outA,'media/assets/bad.svg')));
  assert.match(html,/远程图片未自动加载/);
});
test('Markdown relative links, duplicate heading anchors, source views and directory links survive',()=>{
  assert.match(html,/id="同名-1"/);
  assert.match(html,/id="同名-1-1"/);
  assert.match(html,/id="main-1"/);
  assert.match(html,/href="index.html#main-1"/);
  assert.match(html,/id="嵌套标题-1"/);
  assert.match(html,/pages\/01-Frontend-Design-And-HTML-Templates\/README.md.html#%E4%B8%AD%E6%96%87%E6%A0%87%E9%A2%98/);
  assert.match(html,/source\/01-Frontend-Design-And-HTML-Templates\/demo.html.html/);
  assert.match(html,/directories\/01-Frontend-Design-And-HTML-Templates\/files\/index.html/);
  const source=fs.readFileSync(path.join(outA,'source',section,'demo.html.html'),'utf8');
  assert.ok(!source.includes('<script>'));assert.match(source,/&lt;script&gt;/);
});
test('tables, lists, code, Mermaid and keyboard affordances use inert semantics',()=>{
  for(const marker of ['<table>','scope="col"','class="align-right"','<blockquote>','aria-label="已完成"','Mermaid 源码','tabindex="0"','class="skip"','<details']) assert.ok(html.includes(marker),marker);
  assert.match(html,/<code>a \| b<\/code>/);
});
test('independent HTML parser rejects executable markup and checks local links throughout fixture',()=>{
  const r=spawnSync('python3',[path.join(BASE,'tests/audit_html.py'),outA],{encoding:'utf8'});
  assert.equal(r.status,0,r.stdout+r.stderr);
});
test('requires explicit source, preserves existing output, rejects nested output and symlink escape',()=>{
  assert.throws(()=>build({out:path.join(scratch,'no-source')}),/Explicit source/);
  assert.throws(()=>build({source:fixture,out:fixture}),/already exists/);
  assert.throws(()=>build({source:fixture,out:path.join(fixture,'new-output')}),/separate/);
  const unmarked=path.join(scratch,'unmarked');fs.mkdirSync(unmarked,{recursive:true});
  fs.writeFileSync(path.join(unmarked,'.offline-reader-generated'),'not deletion authority');
  fs.writeFileSync(path.join(unmarked,'keep.txt'),'user content');
  assert.throws(()=>build({source:fixture,out:unmarked}),/already exists/);
  assert.equal(fs.readFileSync(path.join(unmarked,'keep.txt'),'utf8'),'user content');
  const link=path.join(scratch,'escape-link');if(!fs.existsSync(link))fs.symlinkSync('/tmp',link);
  assert.throws(()=>build({source:fixture,out:path.join(link,'reader-test')}),/symlink/);
  const dangling=path.join(scratch,'dangling');fs.symlinkSync('/tmp/absent-reader-output',dangling);
  assert.throws(()=>build({source:fixture,out:dangling}),/already exists/);
});

test('preview reads only its fixed chapter and image, has no dead links and stays deterministic',()=>{
  const source=fs.mkdtempSync(path.join(scratch,'preview-fixture-'));
  const put=(rel,data)=>{const file=path.join(source,rel);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,data);};
  put(PREVIEW.entry,'# 排版样章\n\n中文正文。\n\n![预算图](../../assets/figures/context-budget-ledger.svg)\n\n[未收录](README.md)\n\n| 表头 | 数值 |\n|---|---:|\n| 样章 | 12 |\n\n```js\nthrow new Error("do not run");\n```\n');
  put(PREVIEW.images[0],fs.readFileSync(path.join(fixture,'assets/good.svg')));
  put(section+'/README.md','MUST_NOT_READ_OTHER_CHAPTER'+'.'.repeat(6*1024*1024));
  put('README.md','MUST_NOT_COPY_BOOK_HOME');
  put('assets/figures/unselected.svg','MUST_NOT_COPY_OTHER_IMAGE');
  const out=path.join(scratch,'preview-a'),other=path.join(scratch,'preview-b');
  const report=build({source,out,preview:true});
  build({source,out:other,preview:true});
  assert.deepEqual(report.inputs.map(x=>x.path).sort(),[PREVIEW.entry,...PREVIEW.images].sort());
  assert.equal(report.documents,1); assert.equal(report.images,1); assert.equal(report.mode,'typesetting-preview');
  assert.deepEqual(treeDigest(out),treeDigest(other));
  const index=fs.readFileSync(path.join(out,'index.html'),'utf8');
  assert.match(index,/排版样章，完整书请运行构建器/);
  assert.ok(!index.includes('MUST_NOT_COPY')&&!index.includes('MUST_NOT_READ'));
  assert.ok(treeDigest(out).length<=20);
  const audit=spawnSync('python3',[path.join(BASE,'tests/audit_html.py'),out],{encoding:'utf8'});
  assert.equal(audit.status,0,audit.stdout+audit.stderr);
});

test.after(()=>{fs.rmSync(scratch,{recursive:true,force:true});});
