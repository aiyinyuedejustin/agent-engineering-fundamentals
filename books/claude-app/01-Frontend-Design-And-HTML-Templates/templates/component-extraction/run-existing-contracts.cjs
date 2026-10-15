// 把副本重新内联后复用既有合同；外链解析另由 test-split.cjs 核验。
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),{spawnSync}=require('node:child_process');
const {split}=require('./split-page.cjs');
const source=path.resolve(process.argv[2]||path.join(__dirname,'..'));
const work=fs.mkdtempSync(path.join(os.tmpdir(),'atelier-contracts-'));
try {
 const templates=path.join(work,'templates');fs.cpSync(source,templates,{recursive:true});
 const output=path.join(work,'split');split(source,output);
 let html=fs.readFileSync(path.join(output,'index.html'),'utf8');
 html=html.replace(/<link rel="stylesheet" href="([^"]+)">/g,(_,file)=>'<style>'+fs.readFileSync(path.join(output,file),'utf8')+'</style>');
 html=html.replace('<script defer src="page.js"></script>',()=>'<script>'+fs.readFileSync(path.join(output,'page.js'),'utf8')+'</script>');
 fs.writeFileSync(path.join(templates,'02-chat-workspace-template.html'),html);
 for(const file of ['run.cjs','edge.cjs','preview-lifecycle.cjs','editorial-navigation.cjs','active-section.cjs']) {
   const r=spawnSync(process.execPath,[path.join(templates,'tests',file)],{encoding:'utf8',env:process.env});process.stdout.write(r.stdout);process.stderr.write(r.stderr);if(r.status!==0)throw Error(file+' failed');
 }
 console.log('Existing contracts passed on a temporary snapshot with the split page re-inlined. No browser was run.');
} finally {fs.rmSync(work,{recursive:true,force:true});}
