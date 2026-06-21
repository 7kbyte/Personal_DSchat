// ==================== 消息渲染 (TypeScript) ====================
function renderMessages(): void {
  const container = document.getElementById('messages');
  if (!container) return;
  const app = Alpine.store('app');
  const conv = app.current;
  if (!conv || !conv.messages || conv.messages.length === 0) {
    container.innerHTML = '<div class="empty"><div class="logo">🐱</div><h2>你好！我是 DeepSeek</h2><p>有什么可以帮你的吗？</p></div>';
    return;
  }
  const visible = conv.messages.filter((m: MessageData) => m.role !== 'system');
  if (visible.length === 0) {
    container.innerHTML = '<div class="empty"><div class="logo">🐱</div><h2>你好！我是 DeepSeek</h2><p>有什么可以帮你的吗？</p></div>';
    return;
  }
  let html = '';
  for (let i = 0; i < visible.length; i++) {
    const m = visible[i];
    const isUser = m.role === 'user';
    const avatar = isUser ? '我' : 'DS';
    const contentHtml = renderMarkdown(m.content);
    let reasoningHtml = '';
    if (!isUser && m.reasoning_content) {
      const rid = 'reasoning_' + i;
      reasoningHtml = '<div class="reasoning-toggle" onclick="var c=document.getElementById(\'' + rid + '\');var t=this;c.classList.toggle(\'open\');t.textContent=c.classList.contains(\'open\')?\'🧠 收起思考过程\':\'🧠 查看思考过程\';">🧠 查看思考过程</div><div class="reasoning-content" id="' + rid + '">' + escapeHtml(m.reasoning_content) + '</div>';
    }
    let actionsHtml = '';
    if (!isUser && i === visible.length - 1 && !app.loading) {
      actionsHtml = '<div class="msg-actions"><button class="regenerate-btn" onclick="regenerate()" title="重新生成">🔄</button></div>';
    }
    // Find the original index in conv.messages (not visible)
    const origIdx = conv.messages!.indexOf(m);
    html += '<div class="msg ' + m.role + '" data-msg-idx="' + origIdx + '" oncontextmenu="Alpine.store(\'app\').onMsgCtx(event,' + i + ')">'
      + '<div class="msg-side"><div class="avatar">' + avatar + '</div><div class="msg-time">' + fmtTimeGlobal(m.timestamp as number) + '</div></div>'
      + '<div class="bubble">' + reasoningHtml + contentHtml + '</div>'
      + actionsHtml
      + '</div>';
  }
  container.innerHTML = html;
  container.scrollTop = container.scrollHeight;
  addCodeCopyButtons();
  container.querySelectorAll('.msg.assistant .bubble').forEach((b) => {
    const msg = b.closest('.msg');
    if (msg && isNarrowContent(b as HTMLElement)) { msg.classList.add('narrow'); }
    else if (msg) { msg.classList.remove('narrow'); }
  });
}

function addCodeCopyButtons(): void {
  document.querySelectorAll('.bubble pre').forEach((pre) => {
    if (pre.querySelector('.code-copy-btn')) return;
    (pre as HTMLElement).style.position = 'relative';
    const btn = document.createElement('button');
    btn.className = 'code-copy-btn';
    btn.textContent = '📋';
    btn.title = '复制代码';
    btn.onclick = () => {
      const clone = pre.cloneNode(true) as HTMLElement;
      const btnInClone = clone.querySelector('.code-copy-btn');
      if (btnInClone) btnInClone.remove();
      if (typeof pywebview !== 'undefined' && pywebview!.api)
        pywebview!.api.copyToClipboard(clone.textContent || '');
      btn.textContent = '✅';
      setTimeout(() => { btn.textContent = '📋'; }, 1500);
    };
    pre.appendChild(btn);
  });
}

function setLoading(on: boolean): void {
  Alpine.store('app').loading = on;
}

function fmtTimeGlobal(ts: number): string {
  if (!ts) return '';
  const d = new Date(ts);
  return d.getHours().toString().padStart(2, '0') + ':' + d.getMinutes().toString().padStart(2, '0');
}

async function stopGeneration(): Promise<void> {
  if (typeof pywebview !== 'undefined' && pywebview!.api)
    pywebview!.api.stopGeneration();
}

// 拦截所有消息区域内的链接点击，在系统默认浏览器中打开
function setupLinkInterceptor(): void {
  const container = document.getElementById('messages');
  if (!container) return;
  container.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;
    const anchor = target.closest('a');
    if (!anchor) return;
    const href = anchor.getAttribute('href');
    if (!href) return;
    // 只拦截外部链接 (http/https)，保留页面内锚点跳转
    if (href.startsWith('http://') || href.startsWith('https://')) {
      e.preventDefault();
      if (typeof pywebview !== 'undefined' && pywebview!.api)
        pywebview!.api.openExternalLink(href);
    }
  });
}
