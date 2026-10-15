#!/usr/bin/env node
/** Compose the fixed, audited two-input preview into one self-contained HTML file. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { BASE, PREVIEW, build } from './build.mjs';

const inside=(root,target)=>{const rel=path.relative(root,target);return rel===''||(!rel.startsWith('..'+path.sep)&&rel!=='..'&&!path.isAbsolute(rel));};
export function buildSingle({source,out}) {
  if(!source) throw new Error('Explicit source book root required');
  out=path.resolve(out||path.join(fs.realpathSync(os.tmpdir()),'claude-preview-'+crypto.randomUUID()+'.html'));
  if(path.extname(out)!=='.html') throw new Error('Single preview output must have .html extension');
  try{fs.lstatSync(out);throw new Error('Output already exists; choose a new file');}catch(error){if(error.code!=='ENOENT')throw error;}
  const parent=path.dirname(out);
  if(!fs.existsSync(parent))throw new Error('Output parent must already exist');
  for(let p=parent;p!==path.dirname(p);p=path.dirname(p))if(fs.lstatSync(p).isSymbolicLink())throw new Error('Output cannot traverse a symlink');
  if(inside(fs.realpathSync(source),out))throw new Error('Output must be outside source tree');
  // Only this just-created private work directory is ever removed; no existing output is touched.
  const work=fs.mkdtempSync(path.join(parent,'.single-preview-work-'));
  try {
    const site=path.join(work,'site');
    const manifest=build({source,out:site,preview:true});
    const expected=[PREVIEW.entry,...PREVIEW.images].sort();
    if(JSON.stringify(manifest.inputs.map(x=>x.path).sort())!==JSON.stringify(expected)||manifest.images!==1)
      throw new Error('Single preview requires exactly its fixed Markdown and one valid SVG');
    const compilerInputs=['build-preview-single.mjs','single_page.py'].map(name=>({path:name,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(BASE,name))).digest('hex')}));
    const rendered=spawnSync('python3',[path.join(BASE,'single_page.py'),site],{
      input:JSON.stringify({entry:PREVIEW.entry,image:PREVIEW.images[0],compilerInputs}),encoding:'utf8',timeout:15000,killSignal:'SIGKILL',maxBuffer:8*1024*1024,
    });
    if(rendered.status!==0)throw new Error('Single preview composition failed: '+(rendered.error?.message||rendered.stderr));
    // Exclusive creation also protects against output appearing after the first check.
    fs.writeFileSync(out,rendered.stdout,{encoding:'utf8',flag:'wx'});
    return {out,bytes:Buffer.byteLength(rendered.stdout),sha256:crypto.createHash('sha256').update(rendered.stdout).digest('hex'),sourceFingerprint:manifest.sourceFingerprint};
  } finally { fs.rmSync(work,{recursive:true,force:true}); }
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const options={},args=process.argv.slice(2);
  while(args.length){const key=args.shift();if(!['--source','--out'].includes(key)||!args.length)throw new Error('Usage: node build-preview-single.mjs --source BOOK_ROOT [--out NEW_FILE.html]');options[key.slice(2)]=args.shift();}
  console.log(JSON.stringify(buildSingle(options),null,2));
}
