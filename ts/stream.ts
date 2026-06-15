// ==================== 流式传输 / 发送 (TypeScript) ====================

function ensureSystemPrompt(conv: ConvData): void {
  if (!conv || !conv.promptId) return;
  if (conv.messages.length > 0 && conv.messages[0].role === 'system') return;
  const p = Alpine.store('app').prompts.find((x: PromptData) => x.id === conv.promptId);
  if (!p || !p.content) return;
  conv.messages.unshift({ role: 'system', content: p.content });
  conv.promptName = p.name;
}

function buildApiMessages(conv: ConvData): MessageData[] {
  ensureSystemPrompt(conv);
  return conv.messages.filter((m: MessageData) => m.content !== '思考中...');
}

async function send(): Promise<void> {
  const app = Alpine.store('app');
  if (app.loading) return;
  const input = document.getElementById('input') as HTMLTextAreaElement | null;
  if (!input) return;
  const text = (input.value || '').trim();
  if (!text) return;
  input.value = '';
  autoResize();
  const conv = app.current;
  if (!conv) return;
  conv.messages.push({ role: 'user', content: text, timestamp: Date.now() });
  if (conv.messages.length === 1 || (conv.messages.length === 2 && conv.messages[0].role === 'system')) {
    conv.title = text.slice(0, 30) + (text.length > 30 ? '...' : '');
    if (!conv.folderId) conv.folderId = app.drawerOpen ? app.drawerFolderId! : 'f_default';
  }
  conv.messages.push({ role: 'assistant', content: '思考中...' });
  conv.updatedAt = Date.now();
  if (app.drawerOpen && conv.folderId !== app.drawerFolderId) conv.folderId = app.drawerFolderId!;
  renderMessages();
  app._save();
  app.loading = true;
  setLoading(true);
  const msgs = buildApiMessages(conv);
  if (typeof pywebview === 'undefined' || !pywebview!.api) return;
  pywebview!.api.sendMessage(JSON.stringify({
    messages: msgs,
    model: app.model,
    thinking: app.thinking,
    reasoning_effort: app.effort,
  }));
}

(window as any)._onStreamChunk = function (data: { content?: string; reasoning_content?: string }): void {
  const app = Alpine.store('app');
  const conv = app.current;
  if (!conv) return;
  const lastMsg = conv.messages[conv.messages.length - 1];
  if (!lastMsg || lastMsg.role !== 'assistant') return;
  if (lastMsg.content === '思考中...') { lastMsg.content = ''; lastMsg.reasoning_content = ''; }
  if (data.content) lastMsg.content += data.content;
  if (data.reasoning_content) lastMsg.reasoning_content = (lastMsg.reasoning_content || '') + data.reasoning_content;
  updateLastMessage();
};

(window as any)._onStreamDone = function (data: { ok: boolean; error?: string }): void {
  const app = Alpine.store('app');
  app.loading = false;
  setLoading(false);
  const conv = app.current;
  if (!conv) return;
  if (!data.ok) {
    const lastMsg = conv.messages[conv.messages.length - 1];
    if (lastMsg && lastMsg.role === 'assistant') { lastMsg.content = '❌ 错误: ' + (data.error || '未知错误'); lastMsg.reasoning_content = ''; }
  } else {
    const lastMsg2 = conv.messages[conv.messages.length - 1];
    if (lastMsg2 && lastMsg2.role === 'assistant') lastMsg2.timestamp = Date.now();
  }
  renderMessages();
  app._save();
};

function regenerate(): void {
  const app = Alpine.store('app');
  if (app.loading) return;
  const conv = app.current;
  if (!conv || conv.messages.length < 2) return;
  const last = conv.messages[conv.messages.length - 1];
  if (last.role !== 'assistant') return;
  conv.messages.pop();
  conv.messages.push({ role: 'assistant', content: '思考中...' });
  renderMessages();
  app._save();
  app.loading = true;
  setLoading(true);
  const msgs = buildApiMessages(conv);
  if (typeof pywebview === 'undefined' || !pywebview!.api) return;
  pywebview!.api.sendMessage(JSON.stringify({
    messages: msgs,
    model: app.model,
    thinking: app.thinking,
    reasoning_effort: app.effort,
  }));
}

function updateLastMessage(): void {
  const container = document.getElementById('messages');
  const conv = Alpine.store('app').current;
  if (!conv || !conv.messages || conv.messages.length === 0) return;
  const lastMsg = conv.messages[conv.messages.length - 1];
  const lastEl = container?.querySelector('.msg:last-child .bubble') as HTMLElement | null;
  if (!lastEl) { renderMessages(); return; }
  if (lastMsg.role === 'user') return;
  const html = renderMarkdown(lastMsg.content);
  let r = '';
  if (lastMsg.reasoning_content) {
    const rid = 'reasoning_' + (conv.messages.length - 1);
    r = '<div class="reasoning-toggle" onclick="var c=document.getElementById(\'' + rid + '\');var t=this;c.classList.toggle(\'open\');t.textContent=c.classList.contains(\'open\')?\'🧠 收起思考过程\':\'🧠 查看思考过程\';">🧠 查看思考过程</div><div class="reasoning-content open" id="' + rid + '">' + escapeHtml(lastMsg.reasoning_content) + '</div>';
  }
  lastEl.innerHTML = r + html;
  const rc = lastEl.querySelector('.reasoning-content.open') as HTMLElement | null;
  if (rc) rc.scrollTop = rc.scrollHeight;
  if (container && container.scrollTop + container.clientHeight >= container.scrollHeight - 80) {
    container.scrollTop = container.scrollHeight;
  }
  addCodeCopyButtons();
  const msgEl = lastEl.closest('.msg');
  if (msgEl) {
    if (isNarrowContent(lastEl)) { msgEl.classList.add('narrow'); }
    else { msgEl.classList.remove('narrow'); }
  }
}
