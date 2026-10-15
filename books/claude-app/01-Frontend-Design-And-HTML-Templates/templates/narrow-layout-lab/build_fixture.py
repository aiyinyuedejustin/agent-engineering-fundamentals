#!/usr/bin/env python3
"""Build one new offline HTML file from six pinned, read-only template sources."""
from __future__ import annotations

import argparse
import base64
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_REL = 'templates'
FILES = (
    ('01-component-gallery.html', '01 组件图谱'),
    ('02-chat-workspace-template.html', '02 对话工作区'),
    ('03-split-artifact-ide-template.html', '03 作品与代码工作区'),
    ('04-editorial-blog-and-doc-template.html', '04 编辑式博客与文档'),
    ('05-settings-and-dashboard-template.html', '05 设置与概览'),
    ('06-floating-launcher-template.html', '06 浮动轻入口'),
)
BUNDLE_ALGORITHM = 'SHA-256 of UTF-8 compact sorted-key JSON of templates array; ensure_ascii=false'


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def read_regular(path):
    """Reject symlink components; sources and locks are local regular files only."""
    path = Path(path)
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise ValueError(f'Expected a regular, non-symlink file: {path}')
    return path.read_bytes()


class ScriptCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.scripts = []
        self.attributes = []
        self.active = False

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.active = True
            self.scripts.append('')
            self.attributes.append(attrs)

    def handle_endtag(self, tag):
        if tag == 'script':
            self.active = False

    def handle_data(self, data):
        if self.active:
            self.scripts[-1] += data


def load_sources(source_dir=None, lock_path=None):
    # Parameters support temporary unit-test inputs; the CLI never accepts source paths.
    source_dir = Path(source_dir) if source_dir is not None else ROOT / SOURCE_REL
    lock_path = Path(lock_path) if lock_path is not None else HERE / 'source-lock.json'
    lock = json.loads(read_regular(lock_path))
    if lock.get('schema') != 1 or lock.get('sourceRoot') != SOURCE_REL:
        raise ValueError('Unrecognized source lock schema or source root')
    if lock.get('bundleAlgorithm') != BUNDLE_ALGORITHM:
        raise ValueError('Unrecognized bundle digest algorithm')
    records = lock.get('templates', [])
    if [(r.get('filename'), r.get('title')) for r in records] != list(FILES):
        raise ValueError('The source lock must contain exactly the six fixed templates, in order')
    digest = hashlib.sha256(canonical(records)).hexdigest()
    if lock.get('bundleSha256') != digest:
        raise ValueError('Source lock bundle digest mismatch')
    payloads = []
    script_hashes = set()
    for record in records:
        data = read_regular(source_dir / record['filename'])
        if len(data) > 128_000 or len(data) != record['bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
            raise ValueError(f"Source drift: {record['filename']}; review changes before deliberately replacing the lock")
        source = data.decode('utf-8', errors='strict')
        if '\r' in source:
            raise ValueError('Review CSP hashing before accepting CR/CRLF source bytes')
        parser = ScriptCollector()
        parser.feed(source)
        scripts = parser.scripts
        if len(scripts) != 1 or parser.attributes != [[]]:
            # A new executable script or external dependency needs a deliberate review.
            raise ValueError(f"Unexpected script structure: {record['filename']}")
        for script in scripts:
            script_hashes.add(base64.b64encode(hashlib.sha256(script.encode('utf-8')).digest()).decode('ascii'))
        payloads.append({**record, 'base64': base64.b64encode(data).decode('ascii')})
    return lock, payloads, script_hashes


RUNTIME = r'''"use strict";
(() => {
  const payload = JSON.parse(document.getElementById("fixture-data").textContent);
  const select = document.getElementById("template-select");
  let frame = document.getElementById("template-frame");
  const geometry = document.getElementById("geometry");
  const sourceName = document.getElementById("source-name");
  const sourceSha = document.getElementById("source-sha");
  const status = document.getElementById("load-status");
  const widthButtons = [...document.querySelectorAll("[data-width]")];
  const allowedWidths = [375, 768, 1024];
  let selectedWidth = 375;
  let generation = 0;
  let displayedItem = null;
  let observer = null;
  for (let index = 0; index < payload.templates.length; index++) {
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = payload.templates[index].title;
    select.append(option);
  }
  function measure() {
    // This is the measured iframe content box in CSS px, not a device viewport report.
    const bounds = frame.getBoundingClientRect();
    const actual = Math.round(bounds.width * 100) / 100;
    geometry.textContent = `选中 ${selectedWidth} CSS px · iframe 内容框实测 ${actual} × ${frame.clientHeight} CSS px`;
    geometry.dataset.matches = String(Math.abs(actual - selectedWidth) < 0.1);
  }
  function setWidth(width) {
    if (!allowedWidths.includes(width)) return;
    selectedWidth = width;
    frame.style.width = `${width}px`;
    for (const button of widthButtons) button.setAttribute("aria-pressed", String(Number(button.dataset.width) === width));
    requestAnimationFrame(measure);
  }
  async function loadSelected() {
    const ticket = ++generation;
    const index = Number(select.value);
    if (!Number.isInteger(index) || index < 0 || index >= payload.templates.length) {
      status.textContent = "拒绝非固定模板选项。";
      return;
    }
    const item = payload.templates[index];
    status.textContent = displayedItem
      ? "正在核对所选模板；画布与来源标签仍保留上一份已核对模板…"
      : "正在核对固定源字节…";
    try {
      const bytes = Uint8Array.from(atob(item.base64), char => char.charCodeAt(0));
      if (bytes.byteLength !== item.bytes) throw new Error("字节长度不符");
      let verified = false;
      if (globalThis.crypto?.subtle) {
        const digest = await crypto.subtle.digest("SHA-256", bytes);
        const actual = [...new Uint8Array(digest)].map(byte => byte.toString(16).padStart(2, "0")).join("");
        if (actual !== item.sha256) throw new Error("源 SHA-256 不符");
        verified = true;
      }
      if (ticket !== generation) return;
      const source = new TextDecoder("utf-8", {fatal: true, ignoreBOM: true}).decode(bytes);
      // Prepare the complete new document while detached. Reusing a live iframe
      // could retain the old painted document beneath the new source label.
      const next = frame.cloneNode(false);
      next.title = `${item.title}，固定源码，${selectedWidth} CSS px 布局容器`;
      next.dataset.digest = verified ? "verified" : "build-only";
      next.addEventListener("load", () => {
        // Both a pending newer selection and a detached old element invalidate load.
        if (ticket !== generation || frame !== next || next.srcdoc !== source) return;
        const checked = verified ? "源字节 SHA-256 已复核" : "仅构建时校验；当前上下文无 WebCrypto";
        status.textContent = `${checked}；iframe 已触发 load。尚需人工检查，load 不等于页面或 CSP 验收通过。`;
        measure();
      });
      next.srcdoc = source;
      // One synchronous commit: no old active document remains under a new label.
      if (observer) observer.unobserve(frame);
      frame.replaceWith(next);
      frame = next;
      displayedItem = item;
      sourceName.textContent = item.filename;
      sourceSha.textContent = item.sha256;
      status.textContent = verified
        ? "源字节 SHA-256 已复核；正在装载。此状态不代表视觉或交互通过。"
        : "仅构建时校验：当前上下文无 WebCrypto；正在装载。未声称运行时摘要通过。";
      if (observer) observer.observe(frame);
      requestAnimationFrame(measure);
    } catch (error) {
      if (ticket !== generation) return;
      status.textContent = `未装载：${error.message}` + (displayedItem ? "；画布与来源标签仍保留上一份已核对模板。" : "");
    }
  }
  for (const button of widthButtons) button.addEventListener("click", () => {
    setWidth(Number(button.dataset.width));
    frame.title = `${displayedItem?.title || "尚未装载模板"}，${selectedWidth} CSS px 布局容器`;
  });
  select.addEventListener("change", loadSelected);
  document.getElementById("reload-template").addEventListener("click", loadSelected);
  window.addEventListener("resize", measure);
  if (typeof ResizeObserver !== "undefined") {
    observer = new ResizeObserver(measure);
    observer.observe(frame);
  }
  select.value = "0";
  setWidth(375);
  loadSelected();
})();'''

SHELL = '''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="__CSP__">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="referrer" content="no-referrer">
<title>六个固定模板 · 窄容器布局检查</title>
<style>
:root { color-scheme: light; font-family: system-ui, sans-serif; color: #292b28; background: #eceee9; }
* { box-sizing: border-box; }
body { margin: 0; }
header { padding: 16px 20px 12px; border-bottom: 1px solid #b9c1b6; background: #f7f8f4; }
h1 { font-size: 20px; line-height: 1.4; margin: 0 0 8px; }
p { margin: 6px 0; font-size: 13px; line-height: 1.5; }
.controls { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin: 12px 0; }
select, button { min-height: 40px; padding: 7px 10px; font: inherit; font-size: 14px; border: 1px solid #8a9588; border-radius: 6px; background: white; color: inherit; }
select { max-width: 100%; }
button { cursor: pointer; }
button[aria-pressed="true"] { background: #304c3f; color: white; }
button:focus-visible, select:focus-visible, summary:focus-visible, .canvas:focus-visible { outline: 3px solid #ad511f; outline-offset: 3px; }
.widths { display: flex; flex-wrap: wrap; gap: 5px; }
.measure { font-weight: 650; }
.measure[data-matches="false"] { color: #9b2718; }
.hash { overflow-wrap: anywhere; font-family: ui-monospace, monospace; font-size: 12px; }
details { margin-top: 8px; font-size: 13px; }
summary { cursor: pointer; }
.canvas { padding: 16px; overflow-x: auto; }
.frame-border { width: max-content; padding: 1px; background: #6f786b; }
iframe { display: block; box-sizing: content-box; width: 375px; height: 900px; border: 0; padding: 0; margin: 0; max-width: none; flex: none; background: white; }
footer { padding: 0 20px 20px; font-size: 12px; color: #4c5549; overflow-wrap: anywhere; }
</style>
</head>
<body>
<header>
<h1>六个固定模板 · 窄容器布局检查</h1>
<p>只改变普通 iframe 的 CSS 内容框宽度；无设备仿真、无页面缩放、无浏览器设置修改。固定高度 900 CSS px。</p>
<div class="controls">
<label for="template-select">模板</label><select id="template-select" aria-describedby="contract"></select>
<div class="widths" role="group" aria-label="iframe 内容框宽度">
<button type="button" data-width="375" aria-pressed="true">375 CSS px</button>
<button type="button" data-width="768" aria-pressed="false">768 CSS px</button>
<button type="button" data-width="1024" aria-pressed="false">1024 CSS px</button>
</div>
<button id="reload-template" type="button">重新装载初始模板</button>
</div>
<p id="geometry" class="measure" role="status">等待测量 iframe 内容框…</p>
<p class="hash">固定源：<span id="source-name"></span> · SHA-256：<span id="source-sha"></span></p>
<p id="load-status" role="status">等待装载；如果保持此状态，请确认当前浏览器允许此文件中的固定脚本。</p>
<details id="contract"><summary>测试合同与安全边界</summary>
<p>范围：iframe 下 CSS 视口断点、排版、可见溢出与能在此沙盒内完成的本地交互。宽度按钮只调整尺寸、不重载；切换模板或重新装载会丢失当前临时输入。容器超出窗口时横向滚动，绝不缩放页面来塞进屏幕。</p>
<p>不代表 Android、iOS、触摸、真实设备、200% 缩放、浏览器地址栏变化、输入法或辅助技术验收。实测值是父页面看到的 iframe 内容框；不是独立读取子页面 innerWidth。页面滚动条可能影响可用排版宽度。</p>
<p>外层 sandbox 只允许脚本，不允许 same-origin；因此 localStorage 会被拒绝，模板走其原有异常回退，持久化、剪贴板与完整独立页面行为不在本页验收范围。外层未允许表单提交，因此表单提交类交互不能作为通过依据。不要输入敏感内容。此处只载入构建时锁定的六份公开原创代码，没有 URL、上传或任意源码入口。</p>
<p>模板 03 自带静态编辑器保持原样；其内层 sandbox 为空、净化器与禁止脚本/网络的 CSP 均未改动。外层 CSP 仅放行七段固定脚本摘要、内联样式及 about: 子框架，禁用网络资源与表单提交。应以实际浏览器验证 CSP 执行，不把静态检查算作执行证据。</p>
</details>
<noscript><p>此测试页需要运行内嵌固定脚本；当前没有装载模板。</p></noscript>
</header>
<main class="canvas" tabindex="0" aria-label="固定宽度模板画布，可横向滚动">
<div class="frame-border"><iframe id="template-frame" title="尚未装载模板" sandbox="allow-scripts" referrerpolicy="no-referrer"></iframe></div>
</main>
<footer>源集合版本（内容摘要）：__BUNDLE__ · 来源：__SOURCE_ROOT__ · 单文件衍生产物；源码唯一维护于来源目录。</footer>
<script id="fixture-data" type="application/json">__PAYLOAD__</script>
<script>__RUNTIME__</script>
</body>
</html>
'''


def render_fixture(lock, payloads, script_hashes):
    hashes = set(script_hashes)
    hashes.add(base64.b64encode(hashlib.sha256(RUNTIME.encode('utf-8')).digest()).decode('ascii'))
    policy = "default-src 'none'; script-src " + ' '.join("'sha256-" + h + "'" for h in sorted(hashes))
    policy += "; style-src 'unsafe-inline'; frame-src about:; connect-src 'none'; img-src 'none'; media-src 'none'; font-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"
    payload = json.dumps({'bundleSha256': lock['bundleSha256'], 'templates': payloads}, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    # RUNTIME and payload are inserted last so marker-like source text cannot be expanded.
    result = SHELL.replace('__CSP__', policy).replace('__BUNDLE__', lock['bundleSha256']).replace('__SOURCE_ROOT__', SOURCE_REL)
    return result.replace('__RUNTIME__', RUNTIME).replace('__PAYLOAD__', payload).encode('utf-8')


def valid_output(name):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*\.html', name):
        raise ValueError('Output must be a simple .html filename in this fixture directory; no paths')
    return name


def create_new(name, data, directory=HERE):
    name = valid_output(name)
    # O_EXCL never replaces a file or follows an existing output symlink.
    directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    created = False
    try:
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=directory_fd)
        created = True
        with os.fdopen(fd, 'wb') as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        if created:
            os.unlink(name, dir_fd=directory_fd)
        raise
    finally:
        os.close(directory_fd)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('--output', default='fixture.html', help='New .html filename in this directory; existing paths are refused')
    actions.add_argument('--check', metavar='FILENAME', help='Read-only: check source lock and exact reproducibility of an existing generated HTML')
    args = parser.parse_args(argv)
    try:
        name = valid_output(args.check or args.output)
        lock, payloads, hashes = load_sources()
        output = render_fixture(lock, payloads, hashes)
        if args.check:
            if read_regular(HERE / name) != output:
                raise ValueError('Generated output differs from the current pinned, reproducible build')
            print(f'PASS: six sources and {name} match bundle {lock["bundleSha256"]}')
        else:
            create_new(name, output)
            print(f'Created new file: {HERE / name} ({len(output)} bytes); bundle {lock["bundleSha256"]}')
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
