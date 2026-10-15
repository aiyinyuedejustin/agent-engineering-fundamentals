'use strict';
// DOM lifecycle regression only: real rendering is verified separately in the browser.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { JSDOM, VirtualConsole } = require('jsdom');
const ROOT = path.resolve(process.argv[2] || path.join(__dirname, '..'));
const OUTPUT = path.resolve(process.argv[3] || path.join(__dirname, 'preview-lifecycle-results.json'));
const source = fs.readFileSync(path.join(ROOT, '03-split-artifact-ide-template.html'), 'utf8');
const results = [];
function harness(){
  const errors=[], vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));
  const dom=new JSDOM(source,{url:'https://offline.invalid/ide.html',runScripts:'outside-only',pretendToBeVisual:true,virtualConsole:vc});
  const w=dom.window,d=w.document,$=s=>d.querySelector(s);
  w.matchMedia=()=>({matches:false});d.execCommand=()=>false;
  for(const script of d.querySelectorAll('script'))w.eval(script.textContent);
  return {dom,w,d,$,errors,click:s=>$(s).click(),input(s,v){$(s).value=v;$(s).dispatchEvent(new w.Event('input',{bubbles:true}));},submit(){ $('#ide-form').dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true})); }};
}
function test(id,title,fn){let h;try{h=harness();fn(h);assert.deepEqual(h.errors,[]);results.push({id,title,result:'pass'});}catch(e){results.push({id,title,result:'fail',error:e.message});}finally{h?.dom.window.close();}}
function secure(h){const f=h.$('#preview-frame');assert.equal(h.d.querySelectorAll('iframe').length,1);assert.equal(f.id,'preview-frame');assert.equal(f.title,'作品静态隔离预览');assert.equal(f.getAttribute('sandbox'),'');assert.equal(f.getAttribute('referrerpolicy'),'no-referrer');assert.equal(f.getAttribute('src'),null);assert.equal(f.getAttribute('onload'),null);const doc=new JSDOM(f.srcdoc);assert.equal(doc.window.document.querySelector('meta[http-equiv="Content-Security-Policy"]').content,"default-src 'none'; script-src 'none'; connect-src 'none'; img-src 'none'; media-src 'none'; font-src 'none'; frame-src 'none'; object-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'");doc.window.close();return f;}
test('LIFECYCLE-01','A successful visible refresh replaces exactly one iframe and preserves all isolation attributes',h=>{const old=secure(h),content=old.srcdoc;h.click('#run-code');const next=secure(h);assert.notEqual(next,old);assert.equal(old.isConnected,false);assert.equal(next.srcdoc,content);});
test('LIFECYCLE-02','Code to Preview with unchanged source gets a new browsing context',h=>{const old=secure(h);h.click('#code-tab');assert.equal(h.$('#preview-panel').hidden,true);h.click('#preview-tab');assert.equal(h.$('#preview-panel').hidden,false);assert.notEqual(secure(h),old);});
test('LIFECYCLE-03','Hidden title instruction then Preview remounts without losing heading attributes',h=>{h.click('#code-tab');h.input('#code-editor','<!-- <h1>comment unchanged</h1> --><style>/* <h1>style unchanged</h1> */ .hero { color: #8b4d35; }</style><h1 class="hero" id="heading">Old title</h1><p>Structure regression sample.</p>');const before=secure(h);h.input('#ide-input','标题改为 真正的标题');h.submit();const hidden=secure(h);assert.notEqual(hidden,before);assert.equal(h.$('#preview-panel').hidden,true);assert.match(h.$('#code-editor').value,/comment unchanged/);h.click('#preview-tab');assert.notEqual(secure(h),hidden);assert.match(h.$('#preview-frame').srcdoc,/<h1 class="hero" id="heading">真正的标题<\/h1>/);});
for (const [kind,value] of [['empty',''],['oversize','x'.repeat(100001)],['unsupported','<script>bad()</script>']]) test('LIFECYCLE-04-'+kind,'Invalid '+kind+' source keeps last-good iframe identity and document',h=>{const old=secure(h),content=old.srcdoc;h.input('#code-editor',value);h.click('#run-code');assert.equal(secure(h),old);assert.equal(old.srcdoc,content);assert.equal(h.$('#preview-error').hidden,false);});
test('LIFECYCLE-05','Reset and error restoration remount good documents without retaining unsafe content',h=>{h.click('#code-tab');h.input('#code-editor','<h1>Safe</h1><img src="https://example.com/a"><script>bad()</script>');h.click('#run-code');const old=secure(h);assert.match(old.srcdoc,/<h1>Safe<\/h1>/);assert.doesNotMatch(old.srcdoc,/example.com|<script|<img/);h.click('#code-tab');h.click('#insert-error');assert.equal(secure(h),old);h.click('#insert-error');assert.notEqual(secure(h),old);const restored=secure(h);h.click('#reset-code');assert.notEqual(secure(h),restored);assert.match(h.$('#preview-frame').srcdoc,/Room for/);});
test('LIFECYCLE-06','Repeated tab and preview actions retain one frame and one instruction event path',h=>{for(let i=0;i<8;i++){h.click('#code-tab');h.click('#preview-tab');h.click('#run-code');secure(h);}const before=h.$('#ide-messages').children.length;h.input('#ide-input','标题改为 Once');h.submit();assert.equal(h.$('#ide-messages').children.length,before+2);assert.match(secure(h).srcdoc,/<h1>Once<\/h1>/);});
const report={scope:'jsdom DOM lifecycle; does not verify rendered pixels, CSP enforcement, or browser engine behavior',passed:results.filter(r=>r.result==='pass').length,failed:results.filter(r=>r.result==='fail').length,results};fs.writeFileSync(OUTPUT,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));process.exitCode=report.failed?1:0;
