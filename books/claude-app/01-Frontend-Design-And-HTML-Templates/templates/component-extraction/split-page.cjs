// 只识别本套原创模板的明确标记，绝不是通用 HTML/CSS 解析器。
'use strict';
const fs = require('node:fs'), path = require('node:path'), assert = require('node:assert/strict');
const crypto = require('node:crypto');
function split(sourceDir, destination) {
  sourceDir = path.resolve(sourceDir); destination = path.resolve(destination);
  const filename = '02-chat-workspace-template.html';
  const original = fs.readFileSync(path.join(sourceDir,filename),'utf8');
  const styles = [...original.matchAll(/<style>([\s\S]*?)<\/style>/g)];
  const scripts = [...original.matchAll(/<script>([\s\S]*?)<\/script>/g)];
  assert.equal(styles.length,1); assert.equal(scripts.length,1);
  const css = styles[0][1];
  const reset = css.indexOf('/* 有边界的 reset 与基础样式。');
  const component = css.indexOf('/* 原创组件层：');
  assert.ok(reset > 0 && component > reset, '模板标记改变，请重新审阅边界');
  const tokens = fs.readFileSync(path.join(sourceDir,'../styles/claude-tokens.css'),'utf8');
  const base = fs.readFileSync(path.join(sourceDir,'../styles/claude-reset-and-base.css'),'utf8');
  assert.equal(css.slice(0,reset).trim(), tokens.trim(), '内联 tokens 与共享文件不同');
  assert.equal(css.slice(reset,component).trim(), base.trim(), '内联 reset 与共享文件不同');
  const html = original.replace(styles[0][0],'<link rel="stylesheet" href="styles/claude-tokens.css">\n<link rel="stylesheet" href="styles/claude-reset-and-base.css">\n<link rel="stylesheet" href="page.css">').replace(scripts[0][0],'<script defer src="page.js"></script>');
  // mkdir 是独占创建，不用 existsSync + recursive mkdir 的先检查后使用流程。
  // 父目录必须已存在；失败不清理输出，以免删掉并发写入的他人内容。
  fs.mkdirSync(destination);
  fs.mkdirSync(path.join(destination,'styles'));
  for (const [file,data] of Object.entries({'index.html':html,'page.css':css.slice(component),'page.js':scripts[0][1],'styles/claude-tokens.css':tokens,'styles/claude-reset-and-base.css':base})) fs.writeFileSync(path.join(destination,file),data,{flag:'wx'});
  fs.writeFileSync(path.join(destination,'source.json'),JSON.stringify({filename,sha256:crypto.createHash('sha256').update(original).digest('hex'),method:'Only externalization; page-wide IDs and behavior retained.'},null,2)+'\n',{flag:'wx'});
}
module.exports = {split};
if (require.main === module) {
  if (process.argv.length !== 4) throw Error('node split-page.cjs <原 templates 目录> <不存在的输出目录>');
  split(process.argv[2],process.argv[3]);
}
