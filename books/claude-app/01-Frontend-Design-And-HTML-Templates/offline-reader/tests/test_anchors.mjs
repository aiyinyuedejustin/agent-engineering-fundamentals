import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {build} from '../build.mjs';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()),'reader-anchor-tests-'));
const source=path.join(root,'source'); fs.mkdirSync(source);
const compiler='01-Frontend-Design-And-HTML-Templates/offline-reader';
fs.mkdirSync(path.join(source,compiler),{recursive:true});
fs.writeFileSync(path.join(source,compiler,'README.md'),'DO_NOT_PACKAGE_COMPILER');
const valid='<a id="03-网络与进程恢复"></a>';
const attacks=['<a id="evil" onclick="alert(1)"></a>', '<a id="evil" href="https://evil.test"></a>', '<a id="evil">text</a>', '<a id="bad&#34;id"></a>', '<a id="a b"></a>', '<a id="x:y"></a>', '<a id="x"><script>1</script></a>', '<a id="x"/>', '<a id="safe-pair"></a><svg onload="1"></svg>', '<a id="'+'x'.repeat(201)+'"></a>'];
fs.writeFileSync(path.join(source,'README.md'),`# Book\n\n${valid}\n\n[legacy](#03-网络与进程恢复)\n\n## main\n\n<a id="main"></a>\n\n<a id="main"></a>\n\n## other\n\n<a id="other"></a>\n\n[heading](#main)\n\n[build](${compiler}/README.md)\n\n[preview](${compiler}/preview/index.html)\n\n[unknown](${compiler}/evil.html)\n\n![not-image](${compiler}/README.md)\n\n${attacks.join('\n\n')}\n\n\`<a id="code"></a>\`\n\n~~~html\n<a id="fenced"></a>\n~~~\n`);
fs.writeFileSync(path.join(source,'01-Frontend-Design-And-HTML-Templates/README.md'), '# Nested anchors\n\n> <a id="nested"></a>\n\n| Anchor |\n| --- |\n| <a id="table"></a> |\n\n<a id="duplicate"></a>\n\n<a id="duplicate"></a>\n\n[dup](#duplicate)\n\n[cross](../README.md#03-网络与进程恢复)\n');
const out=path.join(root,'out'); const result=build({source,out});
const html=fs.readFileSync(path.join(out,'index.html'),'utf8');
test('legacy empty anchor is structural, linked, with unchanged source',()=>{
 assert.match(html,/<span id="03-网络与进程恢复"><\/span>/);
 assert.match(html,/href="index.html#03-%E7%BD%91/);
 assert.ok(!result.warnings.some(w=>w.type==='missing-heading-fragment'));
 assert.ok(fs.readFileSync(path.join(out,'source/README.md.html'),'utf8').includes('&lt;a id=&quot;03-网络与进程恢复&quot;&gt;&lt;/a&gt;'));
});
test('heading, template, duplicate anchors stay unique and heading semantics unchanged',()=>{
 const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]); assert.equal(ids.length,new Set(ids).size);
 assert.match(html,/<h2 id="main-1"/); assert.match(html,/href="index.html#main-1"/);
 assert.match(html,/<span id="main-2"><\/span>/); assert.match(html,/<span id="main-3"><\/span>/);
 assert.match(html,/<span id="other-1"><\/span>/);
});
test('only exact empty pairs become anchors; hostile HTML and code remain escaped',()=>{
 assert.ok(!/<a\s+id=/.test(html)); assert.ok(!/<script|<svg|<[^>]*\sonclick=/.test(html.replace(/&quot;/g,'')));
 for(const id of ['evil','bad','a b','x:y','x','code','fenced']) assert.ok(!html.includes(`<span id="${id}">`),id);
 assert.ok(result.warnings.some(w=>w.type==='raw-html-shown-as-text'));
});
test('compiler links map only to fixed built-in guidance without packaging compiler inputs',()=>{
 assert.match(html,/<a href="about.html#build-reader">build<\/a>/);
 assert.match(html,/<a href="about.html#build-reader">preview<\/a>/);
 assert.ok(result.warnings.some(w=>w.target===compiler+'/evil.html'));
 assert.ok(result.warnings.some(w=>w.target===compiler+'/README.md')); // image cannot use alias
 assert.ok(!result.inputs.some(i=>i.path.startsWith(compiler+'/')));
 assert.match(fs.readFileSync(path.join(out,'about.html'),'utf8'),/id="build-reader"/);
});
test('nested/table/cross-document anchors resolve and independently audit cleanly',()=>{
 const nested=fs.readFileSync(path.join(out,'pages/01-Frontend-Design-And-HTML-Templates/README.md.html'),'utf8');
 for(const id of ['nested','table','duplicate','duplicate-1']) assert.ok(nested.includes(`<span id="${id}"></span>`));
 assert.match(nested,/href="README.md.html#duplicate"/);
 assert.match(nested,/href="..\/..\/index.html#03-%E7%BD%91/);
 const audit=spawnSync('python3',[fileURLToPath(new URL('./audit_html.py',import.meta.url)),out],{encoding:'utf8'});
 assert.equal(audit.status,0,audit.stdout+audit.stderr);
});
test.after(()=>fs.rmSync(root,{recursive:true,force:true}));
