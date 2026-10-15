'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const {split}=require('./split-page.cjs');
// 可通过 ATELIER_TEMPLATE_SOURCE 指定未合并补丁时的只读原模板目录。
const source=path.resolve(process.env.ATELIER_TEMPLATE_SOURCE || path.join(__dirname,'..'));
function fixture(fn){const dir=fs.mkdtempSync(path.join(os.tmpdir(),'atelier-output-safety-'));try{fn(dir,path.join(dir,'output'));}finally{fs.rmSync(dir,{recursive:true,force:true});}}
function patch(method,wrapper,fn){const original=fs[method];fs[method]=wrapper(original);try{fn();}finally{fs[method]=original;}}
const sentinel='another writer owns this content\n';
test('already existing output is rejected without changing its contents',()=>fixture((dir,out)=>{
 fs.mkdirSync(out);fs.writeFileSync(path.join(out,'index.html'),sentinel);
 assert.throws(()=>split(source,out),{code:'EEXIST'});assert.equal(fs.readFileSync(path.join(out,'index.html'),'utf8'),sentinel);assert.deepEqual(fs.readdirSync(out),['index.html']);
}));
test('output directory injected immediately before exclusive mkdir is preserved',()=>fixture((dir,out)=>{
 patch('mkdirSync',original=>(target,...args)=>{if(target===out){original(out);fs.writeFileSync(path.join(out,'index.html'),sentinel);}return original(target,...args);},()=>assert.throws(()=>split(source,out),{code:'EEXIST'}));
 assert.equal(fs.readFileSync(path.join(out,'index.html'),'utf8'),sentinel);assert.deepEqual(fs.readdirSync(out),['index.html']);
}));
test('styles directory injected immediately before mkdir is preserved',()=>fixture((dir,out)=>{
 const styles=path.join(out,'styles');
 patch('mkdirSync',original=>(target,...args)=>{if(target===styles){original(styles);fs.writeFileSync(path.join(styles,'owned.css'),sentinel);}return original(target,...args);},()=>assert.throws(()=>split(source,out),{code:'EEXIST'}));
 assert.equal(fs.readFileSync(path.join(styles,'owned.css'),'utf8'),sentinel);assert.deepEqual(fs.readdirSync(out),['styles']);
}));
for(const kind of ['file','hardlink','symlink'])test(kind+' injected immediately before index.html write is not overwritten',()=>fixture((dir,out)=>{
 const victim=path.join(dir,'victim.txt');fs.writeFileSync(victim,sentinel);const target=path.join(out,'index.html');
 patch('writeFileSync',original=>(file,...args)=>{if(file===target){if(kind==='file')original(file,sentinel);else if(kind==='hardlink')fs.linkSync(victim,file);else fs.symlinkSync(victim,file);}return original(file,...args);},()=>assert.throws(()=>split(source,out),{code:'EEXIST'}));
 assert.equal(fs.readFileSync(victim,'utf8'),sentinel);assert.equal(fs.readFileSync(target,'utf8'),sentinel);
 if(kind==='hardlink')assert.equal(fs.statSync(victim).ino,fs.statSync(target).ino);
 if(kind==='symlink')assert.equal(fs.lstatSync(target).isSymbolicLink(),true);
 assert.equal(fs.existsSync(path.join(out,'page.css')),false);
}));
test('source.json metadata uses exclusive creation too and retains partial output',()=>fixture((dir,out)=>{
 const target=path.join(out,'source.json');
 patch('writeFileSync',original=>(file,...args)=>{if(file===target)original(file,sentinel);return original(file,...args);},()=>assert.throws(()=>split(source,out),{code:'EEXIST'}));
 assert.equal(fs.readFileSync(target,'utf8'),sentinel);assert.equal(fs.existsSync(path.join(out,'index.html')),true);
}));
test('missing parent fails without recursive directory creation',()=>fixture((dir,out)=>{
 assert.throws(()=>split(source,path.join(out,'child')),{code:'ENOENT'});assert.equal(fs.existsSync(out),false);
}));
