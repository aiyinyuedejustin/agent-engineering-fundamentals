/* 原创教学组件；不是完整模板 02 的组件化版本。经典脚本，可离线加载。 */
(function (global) {
  'use strict';
  const mounted = new WeakMap();
  let serial = 0;
  function mount(root, {namespace, storage, delay = 900} = {}) {
    if (!root || root.childNodes.length || mounted.has(root)) throw Error('需要空且未挂载的容器');
    if (!namespace || typeof namespace !== 'string') throw Error('必须显式传入 storage namespace');
    const d = root.ownerDocument, w = d.defaultView;
    // 不把 localStorage 放到默认参数：仅访问它也可能抛 SecurityError。
    const store = () => storage === undefined ? w.localStorage : storage;
    const read = (key, fallback) => { try { return JSON.parse(store().getItem(namespace + ':' + key)) ?? fallback; } catch { return fallback; } };
    const write = (key, value) => { try { store().setItem(namespace + ':' + key, JSON.stringify(value)); return true; } catch { return false; } };
    const original = new Map(['data-ui','data-theme','data-palette','data-scoped-chat'].map(k => [k, root.getAttribute(k)]));
    let id;
    do { id = 'atelier-mini-' + (++serial); } while (d.getElementById(id + '-input') || d.getElementById(id + '-messages'));
    root.dataset.ui = 'atelier'; root.dataset.scopedChat = '';
    root.innerHTML = `<div class="mini-toolbar"><button type="button" data-action="theme">切换主题</button><label>配色 <select data-role="palette"><option value="paper">纸与陶</option><option value="sage">苔绿</option><option value="ocean">雾蓝</option><option value="plum">梅灰</option><option value="graphite">石墨</option></select></label><button type="button" data-action="new" aria-controls="${id}-messages">新对话</button></div><div id="${id}-messages" data-role="messages" aria-live="polite"></div><form><label for="${id}-input">本地草稿</label><textarea id="${id}-input" maxlength="4000"></textarea><button type="submit" data-action="send">发送</button></form><p data-role="status" role="status"></p>`;
    const $ = s => root.querySelector(s), input = $('textarea'), messages = $('[data-role="messages"]'), status = $('[data-role="status"]');
    const controller = new w.AbortController();
    const on = (target, event, fn) => target.addEventListener(event, fn, {signal: controller.signal});
    let disposed = false, composing = false, timer = null, busy = false, last = '', generation = 0;
    const media = w.matchMedia?.('(prefers-color-scheme: dark)');
    let theme = read('theme', null);
    if (!['light', 'dark'].includes(theme)) theme = null;
    let explicitTheme = theme !== null;
    function applyTheme(value) {
      if (disposed) return;
      root.dataset.theme = value;
      $('[data-action="theme"]').setAttribute('aria-pressed', String(value === 'dark'));
    }
    applyTheme(theme || (media?.matches ? 'dark' : 'light'));
    const onMedia = e => { if (!explicitTheme) applyTheme(e.matches ? 'dark' : 'light'); };
    // 本例增加“未手动选择时跟随系统”；原页面仅启动时读取主题。
    media?.addEventListener?.('change', onMedia);
    const palettes = ['paper','sage','ocean','plum','graphite'];
    const savedPalette = read('palette', 'paper');
    root.dataset.palette = palettes.includes(savedPalette) ? savedPalette : 'paper';
    $('[data-role="palette"]').value = root.dataset.palette;
    const draft = read('draft', ''); input.value = typeof draft === 'string' ? draft.slice(0,4000) : '';
    const persistDraft = () => { if (!write('draft',input.value)) status.textContent = '已在本页保留；无法持久保存。'; };
    function cancelPending() { generation++; w.clearTimeout(timer); timer = null; busy = false; $('[data-action="send"]').textContent = '发送'; }
    function reset() { cancelPending(); messages.replaceChildren(); input.value = ''; persistDraft(); status.textContent = '新对话'; input.focus(); }
    function append(text, role) { const p = d.createElement('p'); p.dataset.role = role; p.textContent = text; messages.append(p); }
    const ime = e => composing || e?.isComposing || e?.keyCode === 229;
    function send() {
      if (disposed || ime()) return;
      if (busy) { cancelPending(); if (!input.value.trim()) input.value = last; status.textContent = '已停止，草稿保留'; persistDraft(); return; }
      const text = input.value.trim(); if (!text) return;
      last = text; append(text,'user'); input.value = ''; persistDraft(); busy = true;
      $('[data-action="send"]').textContent = '停止'; status.textContent = '本地示例生成中';
      const ticket = ++generation;
      timer = w.setTimeout(() => {
        if (disposed || ticket !== generation) return; // clearTimeout 之外也保护已排队回调。
        cancelPending(); append('先明确目标，再验证边界。这是本地预设回复。','assistant'); status.textContent = '已完成';
      }, delay);
    }
    on($('[data-action="theme"]'),'click', () => { explicitTheme = true; applyTheme(root.dataset.theme === 'dark' ? 'light' : 'dark'); if (!write('theme',root.dataset.theme)) status.textContent = '主题已应用；无法持久保存。'; });
    on($('[data-role="palette"]'),'change', e => { if (!palettes.includes(e.target.value)) return; root.dataset.palette = e.target.value; if (!write('palette',e.target.value)) status.textContent = '配色已应用；无法持久保存。'; });
    on(input,'input',persistDraft);
    on(input,'compositionstart', () => { composing = true; });
    on(input,'compositionend', () => { composing = false; });
    on($('form'),'submit', e => { e.preventDefault(); send(); });
    on(input,'keydown', e => { if (!ime(e) && e.key === 'Enter' && !e.shiftKey && !e.ctrlKey && !e.metaKey && !e.altKey) { e.preventDefault(); send(); } });
    on($('[data-action="new"]'),'click',reset);
    // 只监听容器冒泡，且要求真实焦点在此容器。宿主或另一个实例不会被抢键。
    on(root,'keydown', e => {
      if (e.defaultPrevented || !root.contains(d.activeElement) || ime(e) || e.altKey || e.shiftKey) return;
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); reset(); }
    });
    function unmount() {
      if (disposed) return;
      disposed = true; cancelPending(); controller.abort(); media?.removeEventListener?.('change',onMedia);
      root.replaceChildren();
      for (const [key,value] of original) value === null ? root.removeAttribute(key) : root.setAttribute(key,value);
      mounted.delete(root);
    }
    const api = Object.freeze({unmount}); mounted.set(root,api); return api;
  }
  global.AtelierScopedChat = Object.freeze({mount});
})(window);
