'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict');
const {JSDOM,VirtualConsole}=require('jsdom');
const input=process.argv[2]||require('node:path').join(__dirname,'../04-editorial-blog-and-doc-template.html');let count=0;
function run(title,fn){try{fn();console.log('PASS '+title);count++;}catch(e){console.error('FAIL '+title+': '+e.message);process.exitCode=1;}}
function fixture(base=false,local=false){
 let html=fs.readFileSync(input,'utf8');if(base)html=html.replace('<head>','<head><base href="https://source.invalid/files/">');
 const errors=[];const vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));
 const dom=new JSDOM(html,{url:local?'file:///tmp/editorial.html':'https://preview.invalid/?document=book',runScripts:'outside-only',pretendToBeVisual:true,virtualConsole:vc});
 const w=dom.window,d=w.document;w.matchMedia=()=>({matches:false});w.HTMLElement.prototype.scrollIntoView=function(){};w.scrollTo=()=>{};
 for(const script of d.querySelectorAll('script'))w.eval(script.textContent);
 return {w,d,errors,close:()=>w.close()};
}
for(const [base,local] of [[false,false],[true,false],[false,true]]){
 run(`dynamic directory remains in document base=${base} file=${local}`,()=>{const h=fixture(base,local);try{h.d.querySelector('#docs-tab').click();for(const a of h.d.querySelectorAll('.toc a')){const expected=new URL(h.w.location.href);expected.hash=a.dataset.section;assert.equal(a.href,expected.href);}assert.deepEqual(h.errors,[]);}finally{h.close();}});
 run(`search locates and focuses result base=${base} file=${local}`,()=>{const h=fixture(base,local);try{const s=h.d.querySelector('#doc-search');s.value='主题';s.dispatchEvent(new h.w.Event('input',{bubbles:true}));h.d.querySelector('.search-result').click();if(!local)assert.equal(h.w.location.hash,'#docs-theme');assert.equal(h.d.activeElement.id,'docs-theme');assert.equal(h.d.querySelector('#search-results').hidden,true);assert.deepEqual(h.errors,[]);}finally{h.close();}});
}
run('history rejection does not block focus or mode switch',()=>{const h=fixture();try{h.w.history.replaceState=()=>{throw new h.w.DOMException('blocked','SecurityError');};const s=h.d.querySelector('#doc-search');s.value='主题';s.dispatchEvent(new h.w.Event('input',{bubbles:true}));h.d.querySelector('.search-result').click();assert.equal(h.d.activeElement.id,'docs-theme');assert.equal(h.d.querySelector('#search-results').hidden,true);assert.deepEqual(h.errors,[]);}finally{h.close();}});
run('reuse instructions name shipped styles folder',()=>{const s=fs.readFileSync(input,'utf8');assert.ok(s.includes('与 templates 同级的 styles 目录'));assert.ok(!s.includes('shared 目录'));});
console.log(`${count}/8 checks passed`);
