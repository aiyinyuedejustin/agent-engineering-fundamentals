/* Original local-only behavior. No network, imports, backend, or model calls. */
(() => {
  'use strict';
  const $ = (selector, context = document) => context.querySelector(selector);
  const $$ = (selector, context = document) => [...context.querySelectorAll(selector)];
  const shell = $('#app-shell');
  const input = $('#message-input');
  const transcript = $('#transcript');
  const sendButton = $('#send-button');
  const quickInput = $('#quick-entry-input');
  let quickComposing = false;
  const mobileQuery = matchMedia('(max-width: 760px)');
  const compactQuery = matchMedia('(max-width: 1000px)');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let state = 'idle';
  let generation = 0;
  let timer = null;
  let activeReply = null;
  let failedPrompt = '';
  let composing = false;
  let toastTimer;
  let desktopSidebarOpen = true;
  let desktopInspectorOpen = true;
  const dialogOpeners = new WeakMap();
  const stateNames = { idle: '就绪', generating: '生成中', complete: '已完成', stopped: '已停止', error: '错误 · 可重试' };

  function icon(name) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'study-icon');
    svg.setAttribute('aria-hidden', 'true');
    const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
    use.setAttribute('href', `#i-${name}`);
    svg.append(use);
    return svg;
  }
  function announce(text) { $('#live-announcement').textContent = text; }
  function toast(text) {
    clearTimeout(toastTimer);
    $('#toast').textContent = text;
    $('#toast').hidden = false;
    toastTimer = setTimeout(() => { $('#toast').hidden = true; }, 3200);
  }
  function scrollToBottom() {
    const scroller = $('#conversation-scroll');
    scroller.scrollTop = scroller.scrollHeight;
  }
  function resizeInput() {
    input.style.height = 'auto';
    input.style.height = `${Math.min(Math.max(input.scrollHeight, 52), 144)}px`;
  }
  function updateSendButton() {
    const busy = state === 'generating';
    sendButton.disabled = !busy && !input.value.trim();
    sendButton.setAttribute('aria-label', busy ? '停止模拟生成' : '发送模拟消息');
    sendButton.title = busy ? '停止生成' : '发送模拟消息';
    sendButton.replaceChildren(icon(busy ? 'stop' : 'arrow'));
  }
  function setState(next) {
    state = next;
    $('#state-label').textContent = stateNames[state];
    $('#composer').dataset.state = state;
    $('#state-dot').style.background = state === 'error' ? 'var(--study-error)' : state === 'generating' ? 'var(--study-clay)' : 'var(--study-success)';
    $('[data-simulate="stop"]').disabled = state !== 'generating';
    $('[data-simulate="send"]').disabled = state === 'generating';
    $('[data-simulate="error"]').disabled = state === 'generating';
    $('#composer-status').textContent = state === 'idle' ? '不连接任何 AI 服务' : `${stateNames[state]} · 本地模拟`;
    updateSendButton();
  }
  function cancelTimer() {
    generation += 1;
    clearTimeout(timer);
    timer = null;
  }
  function createUserMessage(text) {
    const article = document.createElement('article');
    article.className = 'message message--user';
    article.dataset.part = 'UserMessage';
    article.setAttribute('aria-label', '你的示例消息');
    article.textContent = text;
    transcript.append(article);
  }
  function createAssistantMessage() {
    const article = document.createElement('article');
    article.className = 'message message--assistant';
    article.dataset.part = 'AssistantMessage';
    article.setAttribute('aria-label', '本地模拟回复');
    article.innerHTML = '<div class="message-meta"><span class="author-mark" aria-hidden="true">L</span><span>留白 · 模拟回复</span></div><div class="message-content"><p class="streaming-text"></p></div><div class="message-actions"><span class="response-status"></span></div>';
    transcript.append(article);
    return { article, text: $('.streaming-text', article), status: $('.response-status', article), actions: $('.message-actions', article), hasContent: false };
  }
  async function copyReply(reply) {
    const text = $('.message-content', reply).innerText;
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(text);
      toast('已复制这段示例文字');
    } catch (_) {
      const range = document.createRange();
      range.selectNodeContents($('.message-content', reply));
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      toast('无法自动复制，已选中文字。请使用系统复制命令。');
    }
  }
  function addCopyAction(reply) {
    if ($('.copy-reply', reply.article)) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'study-button study-button--quiet copy-reply';
    button.append(icon('copy'), document.createTextNode('复制文字'));
    button.addEventListener('click', () => copyReply(reply.article));
    reply.actions.prepend(button);
  }
  function replyFor(prompt) {
    if (/字体|文字|阅读/.test(prompt)) return '阅读与操作，承担不同的任务。\n\n操作标签需要迅速识别，系统无衬线字体适合稳定地扫描。较长的说明则可以借助衬线字体、适当行长与更宽松的行距，形成连续阅读的节奏。\n\n这是一种设计选择，不是由静态字体声明就能证明的产品规则。本示例只使用设备已有字体，因此不同系统的字形和换行会有所不同。';
    if (/深色|颜色|表面/.test(prompt)) return '深色模式需要重新安排层级。\n\n在这份示例中，画布保持最深，内容表面稍亮，输入框再向前一步。边框承担必要的区分，文字保留主要与次要两个清晰层次。\n\n色彩数值的出处与组件中的具体映射是两回事。部分数值可在所检包中找到；可访问性调整、控件边界和布局关系则是本研究的原创选择。';
    if (/错误|失败|状态|恢复/.test(prompt)) return '让错误成为可恢复的状态。\n\n用户首先需要知道发生了什么，其次是哪些内容还在，最后是下一步可以做什么。仅仅把边框变红，并不能回答这些问题。\n\n可以在右侧“状态”中启用“下一次发送模拟失败”，然后发送一条消息。输入不会丢失，错误说明会出现在输入区附近，并提供重试。生成途中也可以随时停止。';
    return '可以从三个层次建立一个可复用的系统。\n\n第一层是语义变量：画布、表面、文字与边界都按用途命名。第二层是基础组件：按钮、输入、反馈各自有稳定的状态。第三层才是页面组合：让内容与操作形成清晰的先后关系。\n\n这段文字是本地预置回复，并非模型生成。你可以切换主题、查看组件边界，或在“组件图谱”里比较同一套变量如何作用于不同组件。';
  }
  function finishReply(next) {
    cancelTimer();
    if (activeReply) {
      activeReply.text.classList.remove('is-streaming');
      activeReply.article.removeAttribute('aria-busy');
      activeReply.status.textContent = next === 'stopped' ? '已停止，可继续提问' : '本地示例 · 非模型输出';
      if (next === 'stopped' && !activeReply.hasContent) {
        activeReply.text.textContent = '已停止，尚未生成内容。';
      } else {
        if (!activeReply.text.textContent) activeReply.text.textContent = '示例已完成。';
        addCopyAction(activeReply);
      }
    }
    setState(next);
    announce(next === 'stopped' ? '已停止模拟生成。' : '模拟回复已完成。');
  }
  function stopReply() {
    if (state !== 'generating') return;
    finishReply('stopped');
    // A user action disabled the Stop control. Restore a usable text target;
    // passive completion deliberately does not call this focus path.
    focusComposer();
  }
  function focusComposer() {
    if ($('#inspector').classList.contains('is-overlay')) closeInspector(false);
    showView('conversation', false);
    input.focus({ preventScroll: true });
  }
  function failReply(prompt) {
    cancelTimer();
    if (activeReply) {
      activeReply.text.classList.remove('is-streaming');
      activeReply.article.removeAttribute('aria-busy');
      activeReply.text.textContent = '这次模拟没有完成。请在输入区查看错误说明。';
      activeReply.status.textContent = '模拟错误';
    }
    failedPrompt = prompt;
    if (!input.value) input.value = prompt;
    resizeInput();
    $('#error-banner').hidden = false;
    setState('error');
    scrollToBottom();
    announce('模拟响应中断。输入已保留，可重试。');
  }
  function startReply(prompt, options = {}) {
    if (state === 'generating') return;
    cancelTimer();
    const ticket = generation;
    $('#error-banner').hidden = true;
    showView('conversation', false);
    if (!options.retry) createUserMessage(prompt);
    if (!options.retry || input.value === failedPrompt) input.value = '';
    resizeInput();
    activeReply = createAssistantMessage();
    activeReply.text.textContent = '正在整理这条观察…';
    activeReply.text.classList.add('is-streaming');
    activeReply.article.setAttribute('aria-busy', 'true');
    activeReply.status.textContent = '生成中 · 可随时停止';
    setState('generating');
    announce('正在生成本地模拟回复。');
    scrollToBottom();
    const shouldFail = options.forceError || $('#fail-next').checked;
    $('#fail-next').checked = false;
    timer = setTimeout(() => {
      if (ticket !== generation) return;
      if (shouldFail) { failReply(prompt); return; }
      const fullText = replyFor(prompt);
      if (reducedMotion.matches) {
        activeReply.hasContent = true;
        activeReply.text.textContent = fullText;
        finishReply('complete');
        scrollToBottom();
        return;
      }
      let position = 0;
      activeReply.text.textContent = '';
      const stream = () => {
        if (ticket !== generation) return;
        position = Math.min(position + 4, fullText.length);
        activeReply.hasContent = true;
        activeReply.text.textContent = fullText.slice(0, position);
        const scroller = $('#conversation-scroll');
        const nearBottom = scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight < 120;
        if (nearBottom) scrollToBottom();
        if (position >= fullText.length) finishReply('complete');
        else timer = setTimeout(stream, 28);
      };
      stream();
    }, 800);
  }
  function initialTranscript() {
    createUserMessage('把这份设计观察，整理成可以复用的系统。');
    const reply = createAssistantMessage();
    $('.message-content', reply.article).innerHTML = '<p>先建立秩序，再增加细节。</p><p>一个安静的工作区，来自一组相互配合的选择：</p><ul><li><strong>温和的层次。</strong> 用画布、表面和边界区分区域，减少大块高饱和色。</li><li><strong>清楚的分工。</strong> 操作便于扫描，内容适合阅读；让文字承担更多表达。</li><li><strong>完整的状态。</strong> 不只设计完成时的样子，也照顾等待、中断与重试。</li></ul>';
    const artifact = document.createElement('button');
    artifact.type = 'button';
    artifact.className = 'artifact-card';
    artifact.dataset.part = 'ContentPreview';
    artifact.innerHTML = '<span class="artifact-card-icon"><svg class="study-icon" aria-hidden="true"><use href="#i-file"/></svg></span><span class="artifact-card-text"><strong>从视觉语言到组件系统</strong><small>研究笔记 · 原创内容 · 3 个设计原则</small></span><svg class="study-icon" aria-hidden="true"><use href="#i-chevron"/></svg>';
    artifact.addEventListener('click', () => openDialog($('#artifact-dialog'), artifact));
    $('.message-content', reply.article).append(artifact);
    reply.status.textContent = '示例内容';
    addCopyAction(reply);
  }
  function resetConversation(focus = false) {
    cancelTimer();
    activeReply = null;
    failedPrompt = '';
    transcript.replaceChildren();
    input.value = '';
    $('#fail-next').checked = false;
    $('#error-banner').hidden = true;
    resetQuickEntry();
    resizeInput();
    initialTranscript();
    setState('idle');
    $('#conversation-scroll').scrollTop = 0;
    if (focus) { if ($('#inspector').classList.contains('is-overlay')) closeInspector(false); showView('conversation', false); input.focus(); announce('示例对话已重置。'); }
  }
  function showView(view, focus = true) {
    if (!$(`#view-${view}`)) return;
    $$('.view').forEach(section => { section.hidden = section.id !== `view-${view}`; });
    $$('[data-view]').forEach(button => {
      if (button.dataset.view === view) button.setAttribute('aria-current', 'page');
      else button.removeAttribute('aria-current');
    });
    const names = { conversation: '对话与阅读', gallery: '组件图谱', tokens: '语义变量' };
    $('#view-label').textContent = names[view];
    if (mobileQuery.matches) closeSidebar(false);
    if (focus) $('#main-content').focus({ preventScroll: true });
  }
  function updateDrawerLock() { document.body.classList.toggle('drawer-open', shell.classList.contains('sidebar-open') || $('#inspector').classList.contains('is-overlay')); }
  function syncSidebar() {
    const activeBeforeResize = document.activeElement;
    const focusInside = $('#sidebar').contains(activeBeforeResize);
    $('.main-shell').inert = false;
    $('#sidebar').removeAttribute('role');
    $('#sidebar').removeAttribute('aria-modal');
    if (mobileQuery.matches) {
      shell.classList.remove('sidebar-collapsed');
      shell.classList.remove('sidebar-open');
      $('#sidebar-scrim').hidden = true;
      $('#sidebar-toggle').setAttribute('aria-expanded', 'false');
      $('#sidebar-toggle').setAttribute('aria-label', '展开导航');
    } else {
      shell.classList.remove('sidebar-open');
      shell.classList.toggle('sidebar-collapsed', !desktopSidebarOpen);
      $('#sidebar-scrim').hidden = true;
      $('#sidebar-toggle').setAttribute('aria-expanded', String(desktopSidebarOpen));
      $('#sidebar-toggle').setAttribute('aria-label', desktopSidebarOpen ? '收起导航' : '展开导航');
    }
    updateDrawerLock();
    if (focusInside && (mobileQuery.matches || !desktopSidebarOpen || activeBeforeResize === $('[data-close-sidebar]'))) $('#sidebar-toggle').focus({ preventScroll: true });
  }
  function closeSidebar(restoreFocus = true) {
    $('.main-shell').inert = false;
    $('#sidebar').removeAttribute('role');
    $('#sidebar').removeAttribute('aria-modal');
    shell.classList.remove('sidebar-open');
    $('#sidebar-scrim').hidden = true;
    $('#sidebar-toggle').setAttribute('aria-expanded', 'false');
    $('#sidebar-toggle').setAttribute('aria-label', '展开导航');
    updateDrawerLock();
    if (restoreFocus) $('#sidebar-toggle').focus();
  }
  function toggleSidebar() {
    if (mobileQuery.matches) {
      const open = !shell.classList.contains('sidebar-open');
      shell.classList.toggle('sidebar-open', open);
      $('.main-shell').inert = open;
      if (open) { $('#sidebar').setAttribute('role', 'dialog'); $('#sidebar').setAttribute('aria-modal', 'true'); }
      else { $('#sidebar').removeAttribute('role'); $('#sidebar').removeAttribute('aria-modal'); }
      $('#sidebar-scrim').hidden = !open;
      $('#sidebar-toggle').setAttribute('aria-expanded', String(open));
      $('#sidebar-toggle').setAttribute('aria-label', open ? '收起导航' : '展开导航');
      updateDrawerLock();
      if (open) $('[data-close-sidebar]').focus();
    } else {
      desktopSidebarOpen = !desktopSidebarOpen;
      syncSidebar();
    }
  }
  function closeInspector(restoreFocus = true) {
    $('#inspector').classList.remove('is-overlay');
    $('#inspector').removeAttribute('role');
    $('#inspector').removeAttribute('aria-modal');
    $('#inspector-scrim').hidden = true;
    $('#main-content').inert = false;
    $('.topbar').inert = false;
    $('#sidebar').inert = false;
    $('#inspector-toggle').setAttribute('aria-expanded', 'false');
    $('#inspector-toggle').setAttribute('aria-label', '显示设计注释');
    updateDrawerLock();
    if (restoreFocus) $('#inspector-toggle').focus();
  }
  function syncInspector() {
    const activeBeforeResize = document.activeElement;
    const focusInside = $('#inspector').contains(activeBeforeResize);
    closeInspector(false);
    $('#inspector').hidden = compactQuery.matches ? false : !desktopInspectorOpen;
    const open = !compactQuery.matches && desktopInspectorOpen;
    $('#inspector-toggle').setAttribute('aria-expanded', String(open));
    $('#inspector-toggle').setAttribute('aria-label', open ? '隐藏设计注释' : '显示设计注释');
    if (focusInside && (compactQuery.matches || !desktopInspectorOpen || activeBeforeResize === $('#inspector-close'))) $('#inspector-toggle').focus({ preventScroll: true });
  }
  function toggleInspector() {
    const panel = $('#inspector');
    let open;
    if (compactQuery.matches) {
      if (panel.classList.contains('is-overlay')) { closeInspector(); return; }
      panel.classList.add('is-overlay');
      panel.setAttribute('role', 'dialog');
      panel.setAttribute('aria-modal', 'true');
      $('#inspector-scrim').hidden = false;
      $('#main-content').inert = true;
      $('.topbar').inert = true;
      $('#sidebar').inert = true;
      open = true;
      updateDrawerLock();
      $('#inspector-close').focus({ preventScroll: true });
    } else { desktopInspectorOpen = !desktopInspectorOpen; panel.hidden = !desktopInspectorOpen; open = desktopInspectorOpen; }
    $('#inspector-toggle').setAttribute('aria-expanded', String(open));
    $('#inspector-toggle').setAttribute('aria-label', open ? '隐藏设计注释' : '显示设计注释');
  }
  function activateTab(name, focus = false) {
    $$('[data-tab]').forEach(tab => {
      const active = tab.dataset.tab === name;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      $(`#panel-${tab.dataset.tab}`).hidden = !active;
      if (active && focus) tab.focus();
    });
  }
  function openDialog(dialog, opener) {
    if (dialog.open) return;
    dialogOpeners.set(dialog, opener || document.activeElement);
    dialog.showModal();
    const firstButton = $('button', dialog);
    if (firstButton) firstButton.focus({ preventScroll: true });
  }
  $$('.study-dialog').forEach(dialog => {
    $$('[data-close-dialog]', dialog).forEach(button => button.addEventListener('click', () => dialog.close()));
    dialog.addEventListener('close', () => {
      const opener = dialogOpeners.get(dialog);
      if (opener?.isConnected && opener.getClientRects().length) opener.focus({ preventScroll: true });
      else $('#main-content').focus({ preventScroll: true });
    });
    dialog.addEventListener('click', event => {
      if (event.target !== dialog) return;
      const box = dialog.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
    });
  });

  const tokens = [
    ['画布', '--study-canvas', true], ['内容表面', '--study-surface', true], ['抬升表面', '--study-raised', true],
    ['主要文字', '--study-ink', true], ['次要文字', '--study-ink-secondary', true], ['辅助文字', '--study-ink-muted', false],
    ['Clay 强调', '--study-clay', true], ['焦点蓝', '--study-focus', true], ['输入边界', '--study-field-border', false],
    ['主操作', '--study-action', false], ['错误提示', '--study-error', false], ['成功提示', '--study-success', false]
  ];
  function renderTokens() {
    const computed = getComputedStyle(document.documentElement);
    $('#token-grid').replaceChildren();
    tokens.forEach(([name, token, observed]) => {
      const value = computed.getPropertyValue(token).trim();
      const card = document.createElement('article');
      card.className = 'token-card';
      const swatch = document.createElement('div');
      swatch.className = 'token-color';
      swatch.style.setProperty('--swatch', value);
      swatch.setAttribute('aria-hidden', 'true');
      const body = document.createElement('div');
      body.className = 'token-card-body';
      const heading = document.createElement('h2'); heading.textContent = name;
      const code = document.createElement('code'); code.textContent = token;
      const literal = document.createElement('p'); literal.className = 'token-value'; literal.textContent = value;
      const chip = document.createElement('span'); chip.className = `study-chip study-chip--${observed ? 'observed' : 'proposal'}`; chip.textContent = observed ? '观察值 · 原创映射' : '研究新增值';
      body.append(heading, code, literal, chip);
      card.append(swatch, body);
      $('#token-grid').append(card);
    });
    $$('[data-token-value]').forEach(element => { element.textContent = computed.getPropertyValue(element.dataset.tokenValue).trim(); });
  }
  function setTheme(theme, remember = true) {
    document.documentElement.dataset.theme = theme;
    $$('[data-theme-choice]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.themeChoice === theme)));
    if (remember) {
      try { localStorage.setItem('liubai-study-theme', theme); } catch (_) { /* file:// or privacy mode may deny persistence. */ }
    }
    renderTokens();
  }
  function renderEvidence() {
    const ev = window.STUDY_EVIDENCE;
    if (!ev) { $('#evidence-content').textContent = '证据摘要未载入。请参阅仓库研究文档。'; return; }
    const intro = document.createElement('p'); intro.textContent = ev.scope;
    const dl = document.createElement('dl'); dl.className = 'evidence-facts';
    const facts = [ ['所检版本', ev.inspectedPackage], ['源文件', ev.source], ['SHA-256', ev.sha256], ['浅色示例 · surface-0', `${ev.light.selector} / ${ev.light.block}\n${ev.light.surface0}`], ['深色示例 · surface-0', `${ev.dark.selector}\n${ev.dark.context} / ${ev.dark.block}\n${ev.dark.surface0}`], ['偏移约定', ev.offsetConvention] ];
    facts.forEach(([label, value]) => { const dt = document.createElement('dt'); dt.textContent = label; const dd = document.createElement('dd'); dd.textContent = value; dl.append(dt, dd); });
    const limit = document.createElement('p'); limit.textContent = ev.limitation;
    const implementation = document.createElement('p'); implementation.textContent = ev.implementation;
    $('#evidence-content').append(intro, dl, limit, implementation);
  }

  // These two axes demonstrate independent original choices. Density is local
  // to the specimen; the message preference is inherited only by reading rules.
  const densityChoices = {
    compact: '原创紧凑：控件最小高度 40 px · 图标 16 px · 内边距 12 px · 间距 8 px · 圆角 8 px',
    comfortable: '原创舒适：控件最小高度 48 px · 图标 20 px · 内边距 20 px · 间距 12 px · 圆角 12 px'
  };
  const readingChoices = { sm: 14, md: 16, lg: 18 };
  function setDensity(choice) {
    if (!Object.hasOwn(densityChoices, choice)) return;
    $('#density-example').dataset.density = choice;
    $$('[data-density-choice]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.densityChoice === choice)));
    $('#density-metrics').textContent = densityChoices[choice];
    $('#display-preference-status').textContent = `${densityChoices[choice]}。消息阅读大小保持不变。`;
  }
  function setReadingSize(choice) {
    if (!Object.hasOwn(readingChoices, choice)) return;
    document.documentElement.dataset.messageSize = choice;
    $$('[data-reading-choice]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.readingChoice === choice)));
    $('#reading-metrics').textContent = `消息正文 ${readingChoices[choice]} px · 行高 1.9`;
    $('#display-preference-status').textContent = `消息正文已改为 ${readingChoices[choice]} px。控件密度保持不变。`;
  }
  $$('[data-density-choice]').forEach(button => button.addEventListener('click', () => setDensity(button.dataset.densityChoice)));
  $$('[data-reading-choice]').forEach(button => button.addEventListener('click', () => setReadingSize(button.dataset.readingChoice)));

  // An in-page capture specimen, not a native window or conversation composer.
  // Drafts and the latest capture live only in DOM memory, never in storage.
  function resizeQuickInput() {
    quickInput.style.height = 'auto';
    quickInput.style.height = `${Math.min(Math.max(quickInput.scrollHeight, 26), 120)}px`;
  }
  function updateQuickInput() {
    const tooLong = quickInput.value.length > 300;
    quickInput.setAttribute('aria-invalid', String(tooLong));
    $('#quick-entry-submit').disabled = quickComposing || !quickInput.value.trim() || tooLong;
    if (tooLong) $('#quick-entry-status').textContent = '速记最多 300 个字符；请缩短内容后重试。';
  }
  function setQuickEntryOpen(open, restoreFocus = true) {
    $('#quick-entry-panel').hidden = !open;
    $('#quick-entry-open').setAttribute('aria-expanded', String(open));
    if (open) {
      resizeQuickInput();
      quickInput.focus({ preventScroll: true });
    } else if (restoreFocus) $('#quick-entry-open').focus({ preventScroll: true });
  }
  function resetQuickEntry() {
    quickComposing = false;
    quickInput.value = '';
    $('#quick-entry-context').value = 'inbox';
    $('#quick-entry-result').hidden = true;
    $('#quick-entry-result-text').textContent = '';
    $('#quick-entry-result-context').textContent = '';
    $('#quick-entry-status').textContent = '没有记录；刷新或“新的观察”会清空。';
    updateQuickInput();
    setQuickEntryOpen(false, false);
  }
  function captureQuickEntry() {
    if (quickComposing || $('#quick-entry-panel').hidden) return;
    const text = quickInput.value.trim();
    if (!text) return;
    if (quickInput.value.length > 300) { updateQuickInput(); return; }
    const contexts = { inbox: '收件盒', ideas: '灵感' };
    const context = contexts[$('#quick-entry-context').value] || contexts.inbox;
    // User input is always literal text, including markup-looking content.
    $('#quick-entry-result-text').textContent = text;
    $('#quick-entry-result-context').textContent = `${context} · 最近一条本地速记`;
    $('#quick-entry-result').hidden = false;
    quickInput.value = '';
    resizeQuickInput();
    updateQuickInput();
    $('#quick-entry-status').textContent = `已暂存到本页的${context}。没有发送到网络；刷新会清空。`;
    quickInput.focus({ preventScroll: true });
  }
  $('#quick-entry-open').addEventListener('click', () => setQuickEntryOpen(true));
  $('#quick-entry-dismiss').addEventListener('click', () => setQuickEntryOpen(false));
  $('#quick-entry-form').addEventListener('submit', event => { event.preventDefault(); captureQuickEntry(); });
  quickInput.addEventListener('input', () => {
    const wasInvalid = quickInput.getAttribute('aria-invalid') === 'true';
    resizeQuickInput();
    updateQuickInput();
    if (wasInvalid && quickInput.getAttribute('aria-invalid') === 'false') $('#quick-entry-status').textContent = '内容长度已符合要求，可以暂存。';
  });
  quickInput.addEventListener('compositionstart', () => { quickComposing = true; updateQuickInput(); });
  quickInput.addEventListener('compositionend', () => { quickComposing = false; updateQuickInput(); resizeQuickInput(); });
  quickInput.addEventListener('keydown', event => {
    if (event.isComposing || quickComposing || event.keyCode === 229) return;
    if (event.key === 'Enter' && !event.shiftKey && !event.altKey && !event.ctrlKey && !event.metaKey) {
      event.preventDefault();
      captureQuickEntry();
    }
  });
  $('#quick-entry-panel').addEventListener('keydown', event => {
    if (event.key !== 'Escape' || event.isComposing || quickComposing || event.keyCode === 229) return;
    event.preventDefault();
    event.stopPropagation();
    setQuickEntryOpen(false);
    $('#quick-entry-status').textContent = quickInput.value ? '速记已收起，草稿仍在本页。' : '速记已收起。';
  });
  $('#quick-entry-clear').addEventListener('click', () => {
    $('#quick-entry-result').hidden = true;
    $('#quick-entry-result-text').textContent = '';
    $('#quick-entry-result-context').textContent = '';
    $('#quick-entry-status').textContent = '这条记录已清除。速记草稿保持不变。';
    const focusTarget = $('#quick-entry-panel').hidden ? $('#quick-entry-open') : quickInput;
    focusTarget.focus({ preventScroll: true });
  });

  $('#composer').addEventListener('submit', event => {
    event.preventDefault();
    if (composing) return;
    if (state === 'generating') { stopReply(); return; }
    const text = input.value.trim();
    if (text) startReply(text);
  });
  input.addEventListener('input', () => { resizeInput(); updateSendButton(); });
  input.addEventListener('compositionstart', () => { composing = true; });
  input.addEventListener('compositionend', () => { composing = false; updateSendButton(); });
  input.addEventListener('keydown', event => {
    if (event.key === 'Enter' && !event.shiftKey && !event.isComposing && !composing && event.keyCode !== 229) {
      event.preventDefault();
      if (state !== 'generating' && input.value.trim()) startReply(input.value.trim());
    }
  });
  $('#retry-button').addEventListener('click', () => { if (state === 'error' && failedPrompt) { startReply(failedPrompt, { retry: true }); focusComposer(); } });
  $$('[data-simulate]').forEach(button => button.addEventListener('click', () => {
    const action = button.dataset.simulate;
    if (action === 'stop' && state === 'generating') stopReply();
    if (action === 'reset') resetConversation(true);
    if (action === 'send' && state !== 'generating') { startReply(input.value.trim() || '如何把这些设计原则应用到一个新的 AI 工作区？'); focusComposer(); }
    if (action === 'error' && state !== 'generating') { startReply(input.value.trim() || '演示一个可以恢复的错误状态。', { forceError: true }); focusComposer(); }
  }));
  $('#new-session').addEventListener('click', () => resetConversation(true));
  $$('[data-view]').forEach(button => button.addEventListener('click', () => showView(button.dataset.view)));
  $$('[data-prompt]').forEach(button => button.addEventListener('click', () => { showView('conversation', false); input.value = button.dataset.prompt; resizeInput(); updateSendButton(); input.focus(); }));
  $('#sidebar-toggle').addEventListener('click', toggleSidebar);
  $('#sidebar-scrim').addEventListener('click', () => closeSidebar());
  $('[data-close-sidebar]').addEventListener('click', () => closeSidebar());
  $('#inspector-toggle').addEventListener('click', toggleInspector);
  $('#inspector-close').addEventListener('click', () => closeInspector());
  $('#inspector-scrim').addEventListener('click', () => closeInspector());
  $('#show-outlines').addEventListener('change', event => shell.classList.toggle('show-outlines', event.target.checked));
  $$('[data-theme-choice]').forEach(button => button.addEventListener('click', () => setTheme(button.dataset.themeChoice)));
  $$('[data-tab]').forEach(button => {
    button.addEventListener('click', () => activateTab(button.dataset.tab));
    button.addEventListener('keydown', event => {
      const tabs = $$('[data-tab]');
      let next = tabs.indexOf(button);
      if (event.key === 'ArrowRight') next = (next + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') next = (next + tabs.length - 1) % tabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = tabs.length - 1;
      else return;
      event.preventDefault(); activateTab(tabs[next].dataset.tab, true);
    });
  });
  $$('[data-open-about]').forEach(button => button.addEventListener('click', () => openDialog($('#about-dialog'), button)));
  $$('[data-open-evidence]').forEach(button => button.addEventListener('click', () => openDialog($('#evidence-dialog'), button)));
  $$('[data-gallery-notice]').forEach(button => button.addEventListener('click', () => { $('#gallery-live').textContent = button.dataset.galleryNotice; }));
  $('#validate-input').addEventListener('click', () => {
    const field = $('#gallery-input');
    const valid = field.value.trim().length >= 2;
    field.setAttribute('aria-invalid', String(!valid));
    $('#gallery-helper').classList.toggle('study-helper--error', !valid);
    $('#gallery-helper').textContent = valid ? '检查通过。这是本地示例，不会保存数据。' : '名称至少需要 2 个字符。请补充内容后重试。';
    $('#gallery-live').textContent = valid ? '输入检查通过。' : '输入有误，名称至少需要 2 个字符。';
    if (!valid) field.focus();
  });
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || $('dialog[open]')) return;
    if (shell.classList.contains('sidebar-open')) closeSidebar();
    else if ($('#inspector').classList.contains('is-overlay')) { toggleInspector(); $('#inspector-toggle').focus(); }
  });
  // The small-screen navigation drawer is modal while its scrim is visible.
  // The background is inert, focus cycles inside, and Escape restores the opener.
  $('#sidebar').addEventListener('keydown', event => {
    if (event.key !== 'Tab' || !mobileQuery.matches || !shell.classList.contains('sidebar-open')) return;
    const focusable = $$('button:not(:disabled), a[href]', $('#sidebar')).filter(el => el.getClientRects().length);
    const first = focusable[0], last = focusable.at(-1);
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
  $('#inspector').addEventListener('keydown', event => {
    if (event.key !== 'Tab' || !$('#inspector').classList.contains('is-overlay')) return;
    const focusable = $$('button:not(:disabled), input:not(:disabled), [tabindex]', $('#inspector')).filter(el => el.getClientRects().length && el.tabIndex >= 0);
    const first = focusable[0], last = focusable.at(-1);
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
  mobileQuery.addEventListener('change', syncSidebar);
  compactQuery.addEventListener('change', syncInspector);
  let initialTheme = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  try { const stored = localStorage.getItem('liubai-study-theme'); if (stored === 'dark' || stored === 'light') initialTheme = stored; } catch (_) { /* No persistence is required. */ }
  resetConversation();
  renderEvidence();
  setTheme(initialTheme, false);
  syncSidebar();
  syncInspector();
})();
