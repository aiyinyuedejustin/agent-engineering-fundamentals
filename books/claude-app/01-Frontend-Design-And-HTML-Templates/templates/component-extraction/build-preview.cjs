'use strict';
// 仅把固定 demo 的本地资源原样内联供 HTML 预览器使用，不转换或复制业务实现。
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const cssFiles=['../../styles/claude-tokens.css','../../styles/claude-reset-and-base.css','scoped-chat.css'];
const scriptFile='scoped-chat.js';
function once(text,marker){assert.equal(text.split(marker).length-1,1,'必须恰有一个固定标记: '+marker);}
function render(sourceDir){
 sourceDir=path.resolve(sourceDir);
 let html=fs.readFileSync(path.join(sourceDir,'demo.html'),'utf8');
 // 该构建器只接受已审核的 demo 资源形状，不做任意 URL 抓取或通用 HTML 转换。
 assert.equal((html.match(/<link\b/gi)||[]).length,3,'只允许三份固定样式');
 assert.equal((html.match(/<style\b/gi)||[]).length,0,'demo 不应含内联样式');
 assert.equal((html.match(/<script\b/gi)||[]).length,2,'只允许一个外链脚本及一个初始化脚本');
 assert.equal((html.match(/<\/script\s*>/gi)||[]).length,2,'script 边界必须完整');
 const marker='<script src="scoped-chat.js"></script>';
 once(html,marker);once(html,'<script>');
 assert.ok(html.indexOf(marker)<html.indexOf('<script>'),'组件脚本必须先于初始化脚本');
 const inline=[];
 for(const file of cssFiles){
  const tag='<link rel="stylesheet" href="'+file+'">';once(html,tag);
  const css=fs.readFileSync(path.join(sourceDir,file),'utf8');
  assert.ok(!/<\/style/i.test(css),'CSS 含 HTML style 结束标记，拒绝内联: '+file);
  inline.push([tag,'<style data-preview-source="'+file+'">'+css+'</style>']);
 }
 const js=fs.readFileSync(path.join(sourceDir,scriptFile),'utf8');
 assert.ok(!/<\/script/i.test(js),'JS 含 HTML script 结束标记，拒绝内联');
 for(const [tag,replacement] of inline)html=html.replace(tag,()=>replacement);
 html=html.replace(marker,()=>'<script data-preview-source="scoped-chat.js">'+js+'</script>');
 return html;
}
function build(sourceDir,output){
 const html=render(sourceDir); // 完成所有检查后才创建文件；父目录必须已存在。
 fs.writeFileSync(path.resolve(output),html,{flag:'wx'}); // 同名普通文件/链接都拒绝；不清理他人内容。
}
module.exports={render,build};
if(require.main===module){
 if(process.argv.length!==2&&process.argv.length!==4)throw Error('node build-preview.cjs [<component-extraction目录> <不存在的输出HTML>]');
 build(process.argv[2]||__dirname,process.argv[3]||path.join(__dirname,'preview-single.html'));
}
