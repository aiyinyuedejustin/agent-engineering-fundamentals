#!/usr/bin/env node
/** Offline book compiler. Source bytes are data, never scripts or HTML. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { marked } from './vendor/marked.mjs';

export const BASE = path.dirname(fileURLToPath(import.meta.url));
export const VERSION = '0.1.0';
export const defaultOutputPath = () => path.join(fs.realpathSync(os.tmpdir()),'claude-offline-reader-'+crypto.randomUUID());
export const PREVIEW = Object.freeze({
  entry:'02-Illustrated-Deep-Dive-Book/05-Context-And-File-Pipeline/worked-case.md',
  images:Object.freeze(['assets/figures/context-budget-ledger.svg']),
});
export const SECTIONS = [
  ['01-Frontend-Design-And-HTML-Templates', '前端审美与设计系统'],
  ['02-Illustrated-Deep-Dive-Book', '技术全书'],
  ['03-Ready-To-Use-Agent-Skills', 'Agent Skills'],
  ['04-Extracted-Core-Code-And-Scripts', '代码与证据'],
  ['05-Automated-Reverse-Toolkit', '逆向工具箱'],
];
const ALLOWED_ROOTS = new Set([...SECTIONS.map(([name]) => name), 'assets']);
const TEXT_EXTS = new Set(['.md', '.txt', '.json', '.jsonl', '.js', '.mjs', '.cjs', '.py', '.css', '.html', '.mmd', '.dot', '.sample']);
const IMAGE_EXTS = new Set(['.svg', '.png', '.jpg', '.jpeg', '.webp', '.gif']);
const SKIP_DIRS = new Set(['node_modules', '__pycache__', 'offline-reader', 'offline-book-reader']);
// A prior publication action explicitly rejected this asset. Never read or repackage it.
const EXCLUDED_FILES = new Set(['assets/screenshots/07-color-catalog-dark-green-d63d0f4.jpg']);
export const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
const uri = value => value.split('/').map(encodeURIComponent).join('/');
export function decodeEntities(value) {
  return value.replace(/&(#x[0-9a-f]+|#\d+|amp|lt|gt|quot|apos|nbsp);/gi, (all, name) => {
    if (!name.startsWith('#')) return ({amp:'&',lt:'<',gt:'>',quot:'"',apos:"'",nbsp:'\u00a0'})[name.toLowerCase()];
    const n = name[1].toLowerCase() === 'x' ? parseInt(name.slice(2), 16) : Number(name.slice(1));
    return n > 0 && n <= 0x10ffff && !(n >= 0xd800 && n <= 0xdfff) ? String.fromCodePoint(n) : '\ufffd';
  });
}
export function plain(tokens) {
  return tokens.map(t => t.tokens ? plain(t.tokens) : decodeEntities(t.text ?? t.raw ?? '')).join('');
}
export function slug(text) {
  return text.toLowerCase().replace(/[^\p{L}\p{M}\p{N}_\-\s]/gu, '').replace(/\s/g, '-');
}
function headings(tokens) {
  const sourceIds = new Set(), outputIds = new Set(['main']), result = [];
  const allocate = (base, used) => {
    let candidate = base, number = 0;
    while (used.has(candidate)) candidate = base + '-' + (++number);
    used.add(candidate); return candidate;
  };
  function walk(items) {
    for (const t of items) {
      if (t.type === 'heading') {
        const text = plain(t.tokens), key = slug(text) || 'section';
        const sourceId = allocate(key, sourceIds);
        t.id = allocate(sourceId, outputIds);
        result.push({depth:t.depth, text, id:t.id, sourceId});
      }
      if (t.tokens) walk(t.tokens);
      if (t.items) for (const item of t.items) walk(item.tokens);
    }
  }
  walk(tokens);
  return result;
}
function within(root, candidate) { const rel = path.relative(root, candidate); return !rel.startsWith('..' + path.sep) && rel !== '..' && !path.isAbsolute(rel); }
function snapshot(source, selectedPaths = null) {
  if (fs.lstatSync(source).isSymbolicLink()) throw new Error('Source root cannot be a symlink');
  const files = new Map(), directories = new Set(['']), excluded = [];
  function walk(relative) {
    const folder = path.join(source, relative);
    for (const entry of fs.readdirSync(folder, {withFileTypes:true}).sort((a,b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0)) {
      if (entry.name.startsWith('.') || SKIP_DIRS.has(entry.name) || entry.isSymbolicLink()) continue;
      const rel = relative ? relative + '/' + entry.name : entry.name;
      if (EXCLUDED_FILES.has(rel)) { excluded.push({path:rel,reason:'Excluded by publication policy; not read or copied'}); continue; }
      if (!relative && rel !== 'README.md' && !ALLOWED_ROOTS.has(entry.name)) continue;
      if (selectedPaths && !selectedPaths.has(rel) && ![...selectedPaths].some(selected=>selected.startsWith(rel+'/'))) continue;
      if (entry.isDirectory()) { directories.add(rel); walk(rel); }
      else if (entry.isFile()) {
        const ext = path.posix.extname(rel).toLowerCase();
        if (TEXT_EXTS.has(ext) || IMAGE_EXTS.has(ext)) {
          const filename = path.join(source, rel);
          if (fs.statSync(filename).size > 5 * 1024 * 1024) throw new Error(`Input too large: ${rel}`);
          files.set(rel, {bytes:fs.readFileSync(filename), ext, filename});
        }
      }
    }
  }
  walk('');
  if (!files.has(selectedPaths ? PREVIEW.entry : 'README.md')) throw new Error('Book entry Markdown missing');
  return {files, directories, excluded};
}
const pagePath = (rel, entry = 'README.md') => rel === entry ? 'index.html' : 'pages/' + rel + '.html';
const sourcePath = rel => 'source/' + rel + '.html';
const dirPath = rel => 'directories/' + (rel ? rel + '/' : '') + 'index.html';
const mediaPath = rel => 'media/' + rel;
function href(from, to, fragment = '') { return uri(path.posix.relative(path.posix.dirname(from), to)) + (fragment ? '#' + encodeURIComponent(fragment) : ''); }

export class Renderer {
  constructor(book, source, output) { this.book = book; this.source = source; this.output = output; }
  warn(type, target) { this.book.warnings.push({source:this.source, type, target}); }
  resolve(raw, image = false) {
    let dest = decodeEntities(raw).trim();
    if (!dest || /[\x00-\x20\x7f\\]/.test(dest)) { this.warn('blocked-url', raw); return null; }
    if (/^https?:\/\//i.test(dest) || /^mailto:/i.test(dest)) {
      try { const url = new URL(dest); if (url.username || url.password) throw new Error(); }
      catch { this.warn('blocked-url', raw); return null; }
      if (image) { this.warn('remote-image-not-loaded', raw); return {remote:true, href:dest}; }
      return {external:true, href:dest};
    }
    if (/^[a-z][a-z0-9+.-]*:/i.test(dest) || dest.startsWith('//') || dest.startsWith('/')) { this.warn('blocked-url', raw); return null; }
    const hashPos = dest.indexOf('#');
    let fragment = hashPos < 0 ? '' : dest.slice(hashPos + 1);
    let file = (hashPos < 0 ? dest : dest.slice(0, hashPos)).split('?')[0];
    try { file = decodeURIComponent(file); fragment = decodeURIComponent(fragment); }
    catch { this.warn('blocked-url', raw); return null; }
    if (/[\x00-\x1f\x7f\\]/.test(file + fragment) || file.startsWith('/') || /^[a-z][a-z0-9+.-]*:/i.test(file)) { this.warn('blocked-url', raw); return null; }
    let rel = file ? path.posix.normalize(path.posix.join(path.posix.dirname(this.source), file)) : this.source;
    rel = rel.replace(/\/+$/, ''); if (rel === '.') rel = '';
    if (rel === '..' || rel.startsWith('../') || path.posix.isAbsolute(rel)) { this.warn('outside-source-root', raw); return null; }
    let target = rel;
    if (this.book.directories.has(target)) {
      target = target ? target + '/README.md' : 'README.md';
      if (!this.book.files.has(target)) return image ? null : {href:href(this.output, dirPath(rel)), local:true};
    }
    const info = this.book.files.get(target);
    if (!info) { this.warn('missing-local-target', raw); return null; }
    if (image) {
      if (!IMAGE_EXTS.has(info.ext) || !this.book.safeImages.has(target)) { this.warn('unsupported-image', raw); return null; }
      return {href:href(this.output, mediaPath(target)), local:true};
    }
    if (info.ext === '.md') {
      if (fragment) {
        const heading = this.book.docs.get(target).headings.find(h => h.sourceId === fragment);
        if (heading) fragment = heading.id;
        else this.warn('missing-heading-fragment', raw);
      }
      return {href:href(this.output, pagePath(target,this.book.entry), fragment), local:true};
    }
    // Never link directly to executable examples, HTML templates, or active SVG documents.
    return {href:href(this.output, sourcePath(target)), local:true, sourceView:true};
  }
  inline(tokens) { return tokens.map(t => this.token(t)).join(''); }
  token(t) {
    switch (t.type) {
      case 'space': case 'def': return '';
      case 'text': return t.tokens ? this.inline(t.tokens) : escape(decodeEntities(t.text));
      case 'escape': return escape(t.text);
      case 'strong': return `<strong>${this.inline(t.tokens)}</strong>`;
      case 'em': return `<em>${this.inline(t.tokens)}</em>`;
      case 'del': return `<del>${this.inline(t.tokens)}</del>`;
      case 'codespan': return `<code>${escape(t.text)}</code>`;
      case 'br': return '<br>';
      case 'hr': return '<hr>';
      case 'paragraph': return `<p>${this.inline(t.tokens)}</p>\n`;
      case 'heading': return `<h${t.depth} id="${escape(t.id ?? slug(plain(t.tokens)))}" tabindex="-1">${this.inline(t.tokens)}</h${t.depth}>\n`;
      case 'blockquote': return `<blockquote>${this.inline(t.tokens)}</blockquote>\n`;
      case 'html':
        // Recognize just the literal Markdown table line-break convention, never pass HTML through.
        if (/^<br\s*\/?>$/i.test(t.text)) return '<br>';
        this.warn('raw-html-shown-as-text', t.text.slice(0,160));
        return t.block ? `<pre class="raw-html">${escape(t.text)}</pre>\n` : escape(t.text);
      case 'code': {
        const lang = (t.lang || 'text').split(/\s/)[0];
        const label = lang.toLowerCase() === 'mermaid' ? 'Mermaid 源码 · 本阅读页不运行图表引擎' : `${lang} · 只读代码`;
        return `<div class="code-block"><div class="code-label">${escape(label)}</div><pre tabindex="0" aria-label="${escape(label)}"><code>${escape(t.text)}</code></pre></div>\n`;
      }
      case 'list': {
        const tag = t.ordered ? 'ol' : 'ul';
        const start = t.ordered && Number.isSafeInteger(t.start) && t.start !== 1 ? ` start="${t.start}"` : '';
        return `<${tag}${start}>${t.items.map(i => `<li>${i.task ? `<span class="task-state" role="img" aria-label="${i.checked ? '已完成' : '未完成'}">${i.checked ? '☑' : '☐'}</span>` : ''}${this.inline(i.tokens)}</li>`).join('')}</${tag}>\n`;
      }
      case 'table': {
        const row = (cells, tag) => '<tr>' + cells.map((c,i) => `<${tag}${tag==='th'?' scope="col"':''}${t.align[i] ? ` class="align-${t.align[i]}"` : ''}>${this.inline(c.tokens)}</${tag}>`).join('') + '</tr>';
        return `<div class="table-scroll" tabindex="0" role="region" aria-label="表格，可横向滚动"><table><thead>${row(t.header,'th')}</thead><tbody>${t.rows.map(r => row(r,'td')).join('')}</tbody></table></div>\n`;
      }
      case 'link': {
        const dest = this.resolve(t.href), label = this.inline(t.tokens);
        if (!dest) return `<span class="blocked-link" title="链接未收录或不允许打开">${label}</span>`;
        return `<a href="${escape(dest.href)}"${dest.external ? ' rel="noreferrer noopener"' : ''}${t.title ? ` title="${escape(decodeEntities(t.title))}"` : ''}>${label}</a>`;
      }
      case 'image': {
        const dest = this.resolve(t.href, true), alt = plain(t.tokens || [{text:t.text}]);
        if (!dest || dest.remote) return `<span class="image-fallback">${escape(alt)}（${dest?.remote ? '远程图片未自动加载' : '图片未收录'}）${dest?.remote ? `<a href="${escape(dest.href)}" rel="noreferrer noopener">原始图片来源</a>` : ''}</span>`;
        return `<img src="${escape(dest.href)}" alt="${escape(alt)}" loading="lazy" decoding="async"${t.title ? ` title="${escape(decodeEntities(t.title))}"` : ''}>`;
      }
      default:
        this.warn('unsupported-token-shown-as-text', t.type);
        return `<span class="unsupported">${escape(t.raw ?? '')}</span>`;
    }
  }
}

function documentShell(book, {output, title, body, rel, toc = [], sourceView = false, previous, next}) {
  const page = rel => pagePath(rel,book.entry);
  const link = (dest, text, attrs='') => `<a href="${escape(href(output,dest))}"${attrs}>${escape(text)}</a>`;
  const sections = `<nav aria-label="全书分区">${link('index.html',book.preview?'样章首页':'书的首页',rel===book.entry?' aria-current="page"':'')}${SECTIONS.filter(([dir]) => book.docs.has(dir+'/README.md')).map(([dir,label]) => link(page(dir+'/README.md'),label,rel===dir+'/README.md'?' aria-current="page"':'')).join('')}</nav>`;
  const tocMarkup = `<nav class="toc" aria-label="本页目录">${toc.filter(h=>h.depth===2||h.depth===3).map(h=>`<a class="level-${h.depth}" href="#${escape(encodeURIComponent(h.id))}">${escape(h.text)}</a>`).join('')}</nav>`;
  const chapters = book.sequence.filter(p => p.startsWith('02-Illustrated-Deep-Dive-Book/'));
  const chapterNav = `<nav aria-label="技术卷目录">${chapters.map(p=>link(page(p),book.docs.get(p).title,rel===p?' aria-current="page"':'')).join('')}</nav>`;
  const csp = "default-src 'none'; script-src 'none'; style-src 'self'; img-src 'self'; font-src 'none'; connect-src 'none'; object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'";
  const meta = rel ? `<div class="source-meta"><span>${escape(rel)}</span>${link(sourceView ? page(rel) : sourcePath(rel),sourceView ? '返回阅读页' : '查看原始 Markdown')} · 由原文生成</div>` : '';
  const stepNav = previous || next ? `<nav class="endnav" aria-label="连续阅读">${previous ? `<a rel="prev" href="${escape(href(output,page(previous)))}"><small>← 上一篇</small>${escape(book.docs.get(previous).title)}</a>` : '<span></span>'}${next ? `<a rel="next" href="${escape(href(output,page(next)))}"><small>下一篇 →</small>${escape(book.docs.get(next).title)}</a>` : ''}</nav>` : '';
  const previewNotice = book.preview ? '<p class="notice"><strong>排版样章，完整书请运行构建器。</strong><br>只收录附件预算案例与原图；其他本地引用保留为文字。正文直接来自书中的 Markdown。</p>' : '';
  return `<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="${escape(csp)}"><meta name="referrer" content="no-referrer"><meta name="color-scheme" content="light dark"><title>${escape(title)} · 拆开 Claude App</title><link rel="stylesheet" href="${escape(href(output,'reader.css'))}"></head>
<body${sourceView?' class="source-page"':''}><a class="skip" href="#main">跳到正文</a><header class="topbar"><a class="brand" href="${escape(href(output,'index.html'))}"><span class="brand-mark" aria-hidden="true">册</span>拆开 Claude App</a><nav class="top-links" aria-label="阅读工具">${link('contents.html',book.preview?'样章目录':'完整目录')}${link('about.html','阅读说明')}<a href="#main">正文 ↓</a></nav></header>
<details class="mobile-nav"><summary>目录与章节</summary>${sections}${tocMarkup}<details><summary>技术全书卷目</summary>${chapterNav}</details></details>
<div class="layout"><aside class="side"><p class="eyebrow">A FIELD GUIDE / 离线阅读</p><p class="book-title">从界面，<br>读到系统。</p>${sections}${toc.length?`<details open><summary>本页目录</summary>${tocMarkup}</details>`:''}<details><summary>技术全书卷目</summary>${chapterNav}</details><p class="side-note">暖纸面，慢一点读。<br>系统字体 · 本地图片 · 只读代码<br>页面查找可用浏览器的 Ctrl / ⌘ F。</p></aside>
<main id="main" tabindex="-1" class="article"><p class="eyebrow">CLAUDE APP / RESEARCH LIBRARY</p>${previewNotice}${meta}${body}${stepNav}</main></div>
<footer class="footer"><span>拆开 Claude App · 静态阅读版</span><span>从 Markdown 生成 · 内容以原文为准 · <a href="#main">回到正文 ↑</a></span></footer></body></html>\n`;
}

export function build({source, out, preview = false}) {
  if (!source) throw new Error('Explicit source book root required');
  if (!out) out = defaultOutputPath();
  source = path.resolve(source); out = path.resolve(out);
  // Never delete or overwrite output, even if it carries a marker from an earlier build.
  // Each build gets a fresh directory; existing ancestors must not redirect through symlinks.
  try { fs.lstatSync(out); throw new Error('Output already exists; choose a new output directory'); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
  let ancestor = path.dirname(out);
  if (!fs.existsSync(ancestor)) throw new Error('Output parent must already exist');
  while (ancestor !== path.dirname(ancestor)) {
    if (fs.lstatSync(ancestor).isSymbolicLink()) throw new Error('Output cannot traverse a symlink');
    ancestor = path.dirname(ancestor);
  }
  if (fs.lstatSync(source).isSymbolicLink()) throw new Error('Source root cannot be a symlink');
  source = fs.realpathSync(source);
  if (within(out,source) || within(source,out) || out===BASE) throw new Error('Output must be separate from source and compiler');
  const selectedPaths = preview ? new Set([PREVIEW.entry,...PREVIEW.images]) : null;
  const {files,directories,excluded} = snapshot(source,selectedPaths);
  const book = {files,directories,preview,entry:preview?PREVIEW.entry:'README.md',docs:new Map(),safeImages:new Set(),warnings:[],sequence:[]};
  const page = rel => pagePath(rel,book.entry);
  const svgPaths = [...files].filter(([,f])=>f.ext==='.svg').map(([rel,f])=>({path:rel,data:f.bytes.toString('base64')}));
  const checked = spawnSync('python3',[path.join(BASE,'svg_check.py')],{input:JSON.stringify(svgPaths),encoding:'utf8',maxBuffer:4*1024*1024,timeout:15000,killSignal:'SIGKILL'});
  if (checked.status!==0) throw new Error('SVG validation failed: '+(checked.error?.message||checked.stderr));
  const svgResult = JSON.parse(checked.stdout);
  for (const [rel, info] of files) {
    if (IMAGE_EXTS.has(info.ext)) {
      if (info.ext!=='.svg' || svgResult[rel]?.svg) book.safeImages.add(rel);
      else book.warnings.push({source:rel,type:'rejected-svg',target:svgResult[rel]?.error});
    }
    if (info.ext === '.md') {
      const tokens = marked.lexer(info.bytes.toString('utf8'), {gfm:true,breaks:false});
      const hs = headings(tokens); book.docs.set(rel,{tokens,headings:hs,title:hs.find(h=>h.depth===1)?.text || rel});
    }
  }
  book.sequence = preview ? [book.entry] : ['README.md',...SECTIONS.flatMap(([dir]) => {
    const root = dir+'/README.md';
    return [root,...[...book.docs.keys()].filter(p=>p.startsWith(dir+'/') && p!==root && (dir!=='02-Illustrated-Deep-Dive-Book' || /^02-Illustrated-Deep-Dive-Book\/\d{2}-[^/]+\/README\.md$/.test(p)))];
  })].filter(rel=>book.docs.has(rel));
  fs.mkdirSync(out); // Exclusive reservation; no recursive creation, deletion, or overwrite.
  const write = (rel,data) => { const filename=path.join(out,rel); fs.mkdirSync(path.dirname(filename),{recursive:true}); fs.writeFileSync(filename,data); };
  write('.offline-reader-generated','Generated by offline-book-reader. Do not edit.\n');
  write('reader.css',fs.readFileSync(path.join(BASE,'reader.css')));
  for (const [rel,doc] of book.docs) {
    const output=page(rel), renderer=new Renderer(book,rel,output), index=book.sequence.indexOf(rel);
    write(output,documentShell(book,{output,title:doc.title,body:renderer.inline(doc.tokens),rel,toc:doc.headings,previous:index>0?book.sequence[index-1]:null,next:index>=0?book.sequence[index+1]:null}));
  }
  for (const [rel,info] of files) {
    const output=sourcePath(rel), doc=book.docs.get(rel);
    let body=`<h1>${escape(doc?.title || path.posix.basename(rel))}</h1>`;
    if (IMAGE_EXTS.has(info.ext)) {
      if (book.safeImages.has(rel)) {write(mediaPath(rel),info.ext==='.svg'?svgResult[rel].svg:info.bytes); body+=`<img src="${escape(href(output,mediaPath(rel)))}" alt="${escape(path.posix.basename(rel))}">`;}
      else body+='<p class="notice">此 SVG 未通过静态图像白名单。保留源码供审阅。</p>';
    }
    if (TEXT_EXTS.has(info.ext) || info.ext==='.svg') body+=`<p class="notice">原文件只读视图。HTML、脚本、命令和图表源码均不会在此页执行。</p><div class="code-block"><div class="code-label">${escape(rel)} · SHA-256 ${hash(info.bytes).slice(0,12)}</div><pre tabindex="0" aria-label="原始文件源码"><code>${escape(info.bytes.toString('utf8'))}</code></pre></div>`;
    write(output,documentShell(book,{output,title:doc?.title||rel,body,rel:doc?rel:null,sourceView:true}));
  }
  for (const dir of directories) {
    const output=dirPath(dir), entries=[];
    for (const child of directories) if(child && path.posix.dirname(child)===(dir||'.')) entries.push([dirPath(child),path.posix.basename(child)+'/']);
    for (const [rel,info] of files) if(path.posix.dirname(rel)===(dir||'.')) entries.push([info.ext==='.md'?page(rel):sourcePath(rel),path.posix.basename(rel)]);
    const body=`<h1>${escape(dir||'书的文件目录')}</h1><ul class="directory-list">${entries.map(([to,label])=>`<li><a href="${escape(href(output,to))}">${escape(label)}</a></li>`).join('')}</ul>`;
    write(output,documentShell(book,{output,title:dir||'文件目录',body}));
  }
  const contents=`<h1>${preview?'样章目录':'完整目录'}</h1><p>每一页都从书的 Markdown 生成。用浏览器的页面查找，快速定位主题。</p>${SECTIONS.filter(([dir])=>[...book.docs.keys()].some(rel=>rel.startsWith(dir+'/'))).map(([dir,label])=>`<h2>${escape(label)}</h2><ul class="directory-list">${[...book.docs].filter(([rel])=>rel.startsWith(dir+'/')).map(([rel,doc])=>`<li><a href="${escape(href('contents.html',page(rel)))}">${escape(doc.title)}</a></li>`).join('')}</ul>`).join('')}`;
  write('contents.html',documentShell(book,{output:'contents.html',title:'完整目录',body:contents}));
  const about=`<h1>把书打开，慢一点读。</h1><p>这是现有研究书的静态阅读入口。正文、图、表和来源都来自同一份 Markdown；更新内容后重新构建即可。</p><h2>离线阅读</h2><p>解压完整生成目录后，用浏览器打开 index.html。不要只取一个 HTML 文件，图片和样式需要保持相对位置。手机文件管理器若限制本地 HTML，可用支持本地目录的浏览器或在同一网络内静态提供整个目录。</p><h2>阅读与键盘</h2><ul><li>Tab 可遍历链接和目录；首个链接可跳过导航直达正文。</li><li>窄屏顶部的目录可用 Enter 或空格展开。</li><li>代码和宽表格可获得键盘焦点，使用方向键横向滚动。</li><li>浏览器自带的 Ctrl / ⌘ F 查找当前页，缩放和打印仍可使用。</li><li>浅深主题跟随系统。没有账号、进度同步或远程字体。</li></ul><h2>渲染范围</h2><p>支持标题与目录、段落、强调、行内代码、围栏代码、引用、有序/无序/嵌套/任务列表、链接、图片，以及普通管道表格。并非完整 GFM 实现：没有脚注扩展、数学排版、自动生成参考文献或 Mermaid 图表引擎。不能渲染的原始 HTML 保留为文字；Mermaid 保留源码，已有 SVG 与截图继续展示。</p><h2>来源与安全边界</h2><p>相对 Markdown 链接转到阅读页；示例 HTML、脚本、JSON 和 SVG 链接转到只读源码/图像页。阅读器不会执行示例、联网请求模型、载入外部脚本或字体。网络图片不会自动载入；原始网站来源链接仅在你主动打开时离开离线阅读。</p><p>每页可查看原文。build-manifest.json 记录输入指纹、渲染器版本及未收录链接，便于核验生成结果。生成物不应手工编辑。</p>`;
  write('about.html',documentShell(book,{output:'about.html',title:'阅读说明',body:about}));
  const inputHashes=[...files].map(([name,info])=>({path:name,sha256:hash(info.bytes)}));
  const compilerInputs=['build.mjs','svg_check.py','reader.css','vendor/marked.mjs'].map(name=>({path:name,sha256:hash(fs.readFileSync(path.join(BASE,name)))}));
  const manifest={format:1,mode:preview?'typesetting-preview':'full-book',entry:book.entry,renderer:VERSION,parser:'marked 16.4.2 (lexer only; vendored)',compilerInputs,sourceFingerprint:hash(JSON.stringify(inputHashes)),documents:book.docs.size,images:book.safeImages.size,excluded,inputs:inputHashes,warnings:book.warnings.sort((a,b)=>JSON.stringify(a)<JSON.stringify(b)?-1:1)};
  write('build-manifest.json',JSON.stringify(manifest,null,2)+'\n');
  return manifest;
}

if (process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const args=process.argv.slice(2); const options={out:defaultOutputPath()};
  while(args.length){const key=args.shift();if(key==='--preview'){options.preview=true;continue;}if(!['--source','--out'].includes(key)||!args.length)throw new Error('Usage: node build.mjs --source BOOK_ROOT [--out NEW_DIRECTORY] [--preview]');options[key.slice(2)]=args.shift();}
  const result=build(options); console.log(JSON.stringify({documents:result.documents,images:result.images,warnings:result.warnings.length,sourceFingerprint:result.sourceFingerprint,out:options.out},null,2));
}
