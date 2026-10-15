'use strict';
// Local DOM contracts only. No browser/CSP-enforcement or rendered-visibility claim.
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const {JSDOM,VirtualConsole}=require('jsdom');
const ROOT=path.resolve(process.argv[2]||path.join(__dirname,'..'));
const OUTPUT=path.resolve(process.argv[3]||path.join(__dirname,'input-contract-results.json'));
const file='03-split-artifact-ide-template.html';
const source=fs.readFileSync(path.join(ROOT,file),'utf8');
const POLICY="default-src 'none'; script-src 'none'; connect-src 'none'; img-src 'none'; media-src 'none'; font-src 'none'; frame-src 'none'; object-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'";
const results=[];
function harness(){
 const errors=[],network=[],vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));
 // Resource loading is disabled; author scripts run only by explicit trusted-source evaluation.
 const dom=new JSDOM(source,{runScripts:'outside-only',pretendToBeVisual:true,url:'https://offline.invalid/',virtualConsole:vc});
 const w=dom.window,d=w.document,$=s=>d.querySelector(s);w.matchMedia=()=>({matches:false});d.execCommand=()=>false;
 for(const api of ['fetch','WebSocket','EventSource'])w[api]=(...args)=>{network.push({api,args});throw Error('network forbidden');};
 w.XMLHttpRequest=class{open(...args){network.push({api:'xhr',args});throw Error('network forbidden');}};
 w.navigator.sendBeacon=(...args)=>{network.push({api:'beacon',args});return false;};
 for(const script of d.querySelectorAll('script'))w.eval(script.textContent);
 function input(value){$('#code-editor').value=value;$('#code-editor').dispatchEvent(new w.Event('input',{bubbles:true}));}
 function preview(value){input(value);$('#run-code').click();}
 return{dom,w,d,$,errors,network,input,preview,close:()=>w.close()};
}
function secure(h){
 const f=h.$('#preview-frame');assert.equal(h.d.querySelectorAll('iframe').length,1);assert.equal(f.getAttribute('sandbox'),'');assert.equal(f.getAttribute('referrerpolicy'),'no-referrer');assert.equal(f.getAttribute('src'),null);assert.equal(f.getAttribute('onload'),null);
 const t=h.d.createElement('template');t.innerHTML=f.srcdoc;assert.equal(t.content.querySelector('meta[http-equiv="Content-Security-Policy"]').content,POLICY);return f;
}
function inertDocument(h){const t=h.d.createElement('template');t.innerHTML=h.$('#preview-frame').srcdoc;return t.content;}
function accept(h,value,check=()=>{}){const old=secure(h);h.preview(value);assert.equal(h.$('#preview-error').hidden,true,'valid retained static content must be accepted');const f=secure(h);assert.notEqual(f,old);assert.equal(old.isConnected,false);check(inertDocument(h),f.srcdoc);}
function reject(h,value){const old=secure(h),markup=old.srcdoc;h.preview(value);assert.equal(h.$('#preview-error').hidden,false);assert.equal(secure(h),old);assert.equal(old.srcdoc,markup);assert.notEqual(h.$('#artifact-status').textContent,'有未预览的更改');}
function test(id,title,fn){let h;const started=performance.now();try{h=harness();fn(h);assert.deepEqual(h.errors,[]);assert.deepEqual(h.network,[]);results.push({id,title,result:'pass',elapsedMs:Math.round(performance.now()-started)});}catch(e){results.push({id,title,result:'fail',error:e.message,elapsedMs:Math.round(performance.now()-started)});}finally{h?.close();}}
// New product regressions: retained structure is a content contract, not a visibility test.
test('INPUT-01','Text-free CSS shape is supported static layout content',h=>accept(h,'<div style="width:120px;height:120px;background:#c96442"></div>',d=>{const s=d.querySelector('div');assert.equal(s.style.width,'120px');assert.equal(s.textContent,'');}));
test('INPUT-02','HR is retained without requiring neighboring text',h=>accept(h,'<hr>',d=>assert.ok(d.querySelector('hr'))));
test('INPUT-03','CSS generated content may accompany text-free static structure',h=>accept(h,'<style>.shape::before{content:"Visible label"}</style><div class="shape"></div>',(d,s)=>{assert.equal(d.querySelector('.shape').textContent,'');assert.match(s,/content:"Visible label"/);}));
test('INPUT-04','Empty layout skeletons are accepted; no rendered visibility inference',h=>accept(h,'<main style="display:grid"><section></section><section></section></main>',d=>assert.equal(d.querySelectorAll('section').length,2)));
test('INPUT-05','CSS-hidden static structure remains valid under the structural contract',h=>accept(h,'<div style="display:none"></div>',d=>assert.equal(d.querySelector('div').style.display,'none')));
for(const [id,title,value] of [
 ['06','Empty input',''],['07','Whitespace-only input',' \t\n\r'],['08','Comment-only input','<!-- harmless note -->'],
 ['09','Stylesheet-only input','<style>body{background:#c96442}</style>'],
 ['10','Several stylesheets and whitespace','\n<style>body{margin:0}</style>\n<style>div{color:red}</style>\n'],
 ['11','Removed script-only input','<script>window.fixtureExecuted=true</script>'],
 ['12','Removed SVG-only input','<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"><rect width="20" height="20" fill="red"/></svg>'],
 ['13','Removed data-image-only input','<img src="data:image/png;base64,iVBORw0KGgo=" onerror="window.fixtureExecuted=true">'],
 ['14','Removed inert nested-template input','<template><h1>Template content is not the preview</h1></template>'],
 ['15','Removed form-only input','<form><input value="test"><button>Submit</button></form>'],
 ['16','Over-limit input','x'.repeat(100001)],
])test('INPUT-'+id,title+' preserves last-good frame and reports rejection',h=>reject(h,value));
test('INPUT-17','The 100,000-character input boundary is inclusive',h=>accept(h,'x'.repeat(100000),(d,s)=>assert.ok(s.includes('x'.repeat(100000)))));
test('INPUT-18','99,999 characters remain supported',h=>accept(h,'x'.repeat(99999)));
test('INPUT-19','Plain text and escaped tags stay literal',h=>accept(h,'Plain &amp; &lt;script&gt; &lt;img src=x&gt;',(d,s)=>{assert.match(s,/Plain &amp; &lt;script&gt; &lt;img src=x&gt;/);assert.equal(d.querySelector('script,img'),null);}));
test('INPUT-20','Broken HTML nesting is normalized to retained static elements',h=>accept(h,'<table><h1>Fostered heading<tr><td><b>Cell<p>Paragraph',(d)=>{assert.ok(d.querySelector('h1'));assert.ok(d.querySelector('table'));assert.equal(d.querySelector('script'),null);}));
test('INPUT-21','Raw style termination cannot preserve a subsequent script',h=>accept(h,'<style>/* </style><script>window.fixtureExecuted=true</script><h1>Kept</h1>',(d,s)=>{assert.equal(d.querySelector('script'),null);assert.equal(d.querySelector('h1').textContent,'Kept');assert.doesNotMatch(s,/fixtureExecuted/);}));
test('INPUT-22','Active elements, navigation, event handlers and URL attributes are removed',h=>accept(h,'<meta http-equiv="refresh" content="0;url=data:text/html,no"><base href="data:text/html,no"><link rel="stylesheet" href="data:text/css,no"><a href="#move">Navigation</a><iframe srcdoc="<p>Nested</p>"></iframe><object data="data:text/plain,no"></object><form><button>Go</button></form><h1 onmouseover="window.fixtureExecuted=true" href="#move" src="data:text/plain,no" class="keep" aria-label="Title">Kept</h1>',d=>{assert.equal(d.querySelector('script,base,link,a,iframe,object,form'),null);const h1=d.querySelector('h1');assert.equal(h1.attributes.length,2);assert.equal(h1.className,'keep');assert.equal(h1.getAttribute('aria-label'),'Title');}));
test('INPUT-23','SVG foreignObject and MathML trees are removed as complete subtrees',h=>accept(h,'<svg><foreignObject><div><style>.x{color:red}</style><h1>Foreign</h1></div></foreignObject></svg><math><mtext><h1>Math</h1></mtext></math><p>Kept</p>',(d,s)=>{assert.equal(d.querySelector('svg,math,foreignObject'),null);assert.doesNotMatch(s,/Foreign|Math/);assert.equal(d.querySelector('p').textContent,'Kept');}));
test('INPUT-24','Data-image and local-fragment image URLs are removed with IMG nodes',h=>accept(h,'<img src="data:image/svg+xml,%3Csvg/%3E"><img src="#local-image"><p>Kept</p>',(d,s)=>{assert.equal(d.querySelector('img'),null);assert.doesNotMatch(s,/data:image|local-image/);}));
test('INPUT-25','CSS URLs remain in CSS; image blocking belongs to iframe CSP',h=>accept(h,'<style>.paint{background-image:url("data:image/svg+xml,%3Csvg/%3E")}</style><p class="paint">Kept</p>',(d,s)=>{assert.match(s,/data:image\/svg\+xml/);assert.match(s,/img-src 'none'/);assert.ok(d.querySelector('style'));}));
test('INPUT-26','Escaped CSS url tokens are retained; no false DOM-sanitizer guarantee',h=>accept(h,'<p style="background-image:u\\72l(data:image/png;base64,AA==)">Kept</p>',(d,s)=>{assert.match(s,/u\\72l\(data:image/);assert.match(s,/img-src 'none'/);}));
test('INPUT-27','CSS imports and font URLs remain text; network enforcement is CSP responsibility',h=>accept(h,'<style>@import "data:text/css,body%7Bcolor:red%7D";@font-face{font-family:localtest;src:url(data:font/woff2;base64,AA==)}p{font-family:localtest}</style><p>Kept</p>',(d,s)=>{assert.match(s,/@import/);assert.match(s,/font-src 'none'/);assert.match(s,/default-src 'none'/);}));
test('INPUT-28','Malformed CSS is not a parser-level HTML failure',h=>accept(h,'<style>.x{color:red; /* unclosed CSS comment</style><p class="x">Kept</p>',d=>assert.equal(d.querySelector('p').textContent,'Kept')));
test('INPUT-29','500 nested retained nodes still preserve the innermost text',h=>accept(h,'<div>'.repeat(500)+'Deep'+'</div>'.repeat(500),d=>{assert.equal(d.querySelectorAll('div').length,500);assert.match(d.textContent,/Deep/);}));
test('INPUT-30','Repeated rejection then a valid graphic preserves and replaces the expected document',h=>{const old=secure(h),markup=old.srcdoc;for(const v of ['', '<style>body{color:red}</style>', '<svg/>', 'x'.repeat(100001)]){reject(h,v);assert.equal(h.$('#preview-frame'),old);assert.equal(old.srcdoc,markup);}accept(h,'<div style="height:20px;background:red"></div>');assert.equal(h.$('#preview-error').hidden,true);});
test('INPUT-31','No-text graphic replaces previous good content via keyboard shortcut',h=>{h.$('#code-tab').click();h.input('<hr>');h.$('#code-editor').dispatchEvent(new h.w.KeyboardEvent('keydown',{key:'Enter',ctrlKey:true,bubbles:true,cancelable:true}));assert.equal(h.$('#preview-error').hidden,true);assert.equal(h.$('#preview-panel').hidden,false);assert.ok(inertDocument(h).querySelector('hr'));});
test('INPUT-32','Error restore returns a valid no-text static layout',h=>{h.input('<div style="width:20px;height:20px;background:red"></div>');h.$('#insert-error').click();assert.equal(h.$('#preview-error').hidden,false);h.$('#insert-error').click();assert.equal(h.$('#preview-error').hidden,true);assert.ok(inertDocument(h).querySelector('div'));});
const report={generatedAt:new Date().toISOString(),file,sha256:crypto.createHash('sha256').update(source).digest('hex'),runner:{node:process.version,jsdom:require('jsdom/package.json').version},scope:'Local jsdom DOM/input contracts only; resource loading disabled. CSP strings inspected, never claimed as enforced. Retained static structure is not proof of rendered visibility.',summary:{total:results.length,passed:results.filter(x=>x.result==='pass').length,failed:results.filter(x=>x.result==='fail').length},results};
fs.writeFileSync(OUTPUT,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report.summary));for(const r of results.filter(x=>x.result==='fail'))console.log(r.id+' '+r.title+'\n'+r.error);process.exitCode=report.summary.failed?1:0;
