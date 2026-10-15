'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const {JSDOM}=require('jsdom');const {render,build}=require('./build-preview.cjs');
const source=path.resolve(process.env.ATELIER_COMPONENT_SOURCE||__dirname);
function fixture(fn){const dir=fs.mkdtempSync(path.join(os.tmpdir(),'atelier-preview-'));const src=path.join(dir,'templates/component-extraction');fs.mkdirSync(src,{recursive:true});fs.mkdirSync(path.join(dir,'styles'));for(const file of ['demo.html','scoped-chat.js','scoped-chat.css','../../styles/claude-tokens.css','../../styles/claude-reset-and-base.css'])fs.copyFileSync(path.join(source,file),path.join(src,file));try{fn(dir,src,path.join(dir,'preview.html'));}finally{fs.rmSync(dir,{recursive:true,force:true});}}
test('three CSS and component JS are byte-equivalent text with the initializer unchanged',()=>{
 const original=new JSDOM(fs.readFileSync(path.join(source,'demo.html'),'utf8')),preview=new JSDOM(render(source));
 try{const d=preview.window.document;assert.equal(d.querySelectorAll('link[rel=stylesheet],script[src]').length,0);
 const styles=[...d.querySelectorAll('style')];assert.equal(styles.length,3);
 for(const el of styles)assert.equal(el.textContent,fs.readFileSync(path.join(source,el.dataset.previewSource),'utf8'));
 const scripts=[...d.querySelectorAll('script')];assert.equal(scripts.length,2);assert.equal(scripts[0].textContent,fs.readFileSync(path.join(source,'scoped-chat.js'),'utf8'));assert.equal(scripts[1].textContent,original.window.document.querySelectorAll('script')[1].textContent);
 assert.equal(d.body.querySelectorAll('section').length,2);
 }finally{original.window.close();preview.window.close();}
});
test('generated preview executes component before initializer and mounts two isolated instances',()=>{
 const dom=new JSDOM(render(source),{runScripts:'outside-only',url:'https://example.invalid'});try{const w=dom.window,d=w.document;for(const el of d.querySelectorAll('script'))w.eval(el.textContent);assert.equal(d.querySelectorAll('[data-scoped-chat]').length,2);
 const roots=[...d.querySelectorAll('section')];roots[0].querySelector('[data-action="theme"]').click();assert.notEqual(roots[0].dataset.theme,roots[1].dataset.theme);d.getElementById('remount').click();assert.equal(d.querySelectorAll('[data-scoped-chat]').length,2);
 }finally{dom.window.close();}
});
for(const [file,payload] of [['scoped-chat.js','/* </ScRiPt ><script>bad()</script> */'],['scoped-chat.css','/* </StYlE ><script>bad()</script> */']])test(file+' closing-tag injection is rejected before output creation',()=>fixture((dir,src,out)=>{
 fs.appendFileSync(path.join(src,file),payload);assert.throws(()=>build(src,out),/结束标记/);assert.equal(fs.existsSync(out),false);
}));
for(const mutation of ['duplicate','unexpected','order'])test('rejects demo resource '+mutation,()=>fixture((dir,src,out)=>{
 const f=path.join(src,'demo.html');let text=fs.readFileSync(f,'utf8');if(mutation==='duplicate')text+='<script src="scoped-chat.js"></script>';if(mutation==='unexpected')text=text.replace('href="scoped-chat.css"','href="https://other.invalid/style.css"');if(mutation==='order')text=text.replace('<script src="scoped-chat.js"></script>','')+'<script src="scoped-chat.js"></script>';fs.writeFileSync(f,text);assert.throws(()=>build(src,out));assert.equal(fs.existsSync(out),false);
}));
for(const kind of ['file','hardlink','symlink'])test('existing '+kind+' output is preserved',()=>fixture((dir,src,out)=>{
 const victim=path.join(dir,'victim');fs.writeFileSync(victim,'KEEP');if(kind==='file')fs.writeFileSync(out,'KEEP');else if(kind==='hardlink')fs.linkSync(victim,out);else fs.symlinkSync(victim,out);
 assert.throws(()=>build(src,out),{code:'EEXIST'});assert.equal(fs.readFileSync(out,'utf8'),'KEEP');assert.equal(fs.readFileSync(victim,'utf8'),'KEEP');
}));
test('concurrent output creation at write boundary is preserved',()=>fixture((dir,src,out)=>{
 const write=fs.writeFileSync;fs.writeFileSync=(file,...args)=>{if(file===out)write(file,'OTHER WRITER');return write(file,...args);};try{assert.throws(()=>build(src,out),{code:'EEXIST'});}finally{fs.writeFileSync=write;}assert.equal(fs.readFileSync(out,'utf8'),'OTHER WRITER');
}));
test('fresh output equals render without a second business implementation',()=>fixture((dir,src,out)=>{
 build(src,out);assert.equal(fs.readFileSync(out,'utf8'),render(src));
}));
