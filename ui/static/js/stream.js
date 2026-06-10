// ==================== 发送消息 ====================
async function send() {
    if (state.loading) return;
    const input = document.getElementById('input');
    const text = input.value.trim();
    if (!text) return;
    input.value = ''; autoResize();
    const conv = getCurrent();
    if (!conv) return;
    conv.messages.push({ role: 'user', content: text, timestamp: Date.now() });
    if (conv.messages.length === 1) {
        conv.title = text.slice(0, 30) + (text.length > 30 ? '...' : '');
        if (!conv.folderId) conv.folderId = state.drawerOpen ? state.drawerFolderId : 'f_default';
    }
    conv.messages.push({ role: 'assistant', content: '思考中...' });
    conv.updatedAt = Date.now();
    if (state.drawerOpen && conv.folderId !== state.drawerFolderId) conv.folderId = state.drawerFolderId;
    renderAll(); save();
    state.loading = true;
    setLoading(true);
    updateStatus();
    const model = getModel();
    const thinking = document.getElementById('thinkToggle').checked;
    const effort = getEffort();
    pywebview.api.sendMessage(JSON.stringify({
        messages: conv.messages.filter(m => m.content !== '思考中...'),
        model: model, thinking: thinking, reasoning_effort: effort,
    }));
}

window._onStreamChunk = function(data) {
    const conv = getCurrent();
    if (!conv) return;
    const lastMsg = conv.messages[conv.messages.length - 1];
    if (!lastMsg || lastMsg.role !== 'assistant') return;
    if (lastMsg.content === '思考中...') { lastMsg.content = ''; lastMsg.reasoning_content = ''; }
    if (data.content) lastMsg.content += data.content;
    if (data.reasoning_content) lastMsg.reasoning_content = (lastMsg.reasoning_content || '') + data.reasoning_content;
    updateLastMessage();
};

window._onStreamDone = function(data) {
    state.loading = false;
    setLoading(false);
    updateStatus();
    const conv = getCurrent();
    if (!conv) return;
    if (!data.ok) {
        const lastMsg = conv.messages[conv.messages.length - 1];
        if (lastMsg && lastMsg.role === 'assistant') { lastMsg.content = '❌ 错误: ' + (data.error || '未知错误'); lastMsg.reasoning_content = ''; }
    } else {
        const lastMsg = conv.messages[conv.messages.length - 1];
        if (lastMsg && lastMsg.role === 'assistant') lastMsg.timestamp = Date.now();
    }
    renderAll(); save();
};

// ==================== 重新生成 ====================
function regenerate() {
    if (state.loading) return;
    const conv = getCurrent();
    if (!conv || conv.messages.length < 2) return;
    const last = conv.messages[conv.messages.length - 1];
    if (last.role !== 'assistant') return;
    conv.messages.pop();
    conv.messages.push({ role: 'assistant', content: '思考中...' });
    renderAll(); save();
    state.loading = true;
    setLoading(true);
    updateStatus();
    const model = getModel();
    const thinking = document.getElementById('thinkToggle').checked;
    const effort = getEffort();
    pywebview.api.sendMessage(JSON.stringify({
        messages: conv.messages.filter(m => m.content !== '思考中...'),
        model: model, thinking: thinking, reasoning_effort: effort,
    }));
}

function updateLastMessage() {
    const container = document.getElementById('messages');
    const conv = getCurrent();
    if (!conv || !conv.messages || conv.messages.length === 0) return;
    const lastMsg = conv.messages[conv.messages.length - 1];
    const lastEl = container.querySelector('.msg:last-child .bubble');
    if (!lastEl) { renderMessages(); return; }
    if (lastMsg.role === 'user') return;
    const html = renderMarkdown(lastMsg.content);
    let r = '';
    if (lastMsg.reasoning_content) {
        const rid = 'reasoning_' + (conv.messages.length - 1);
        r = '<div class="reasoning-toggle" onclick="var c=document.getElementById(\'' + rid + '\');var t=this;c.classList.toggle(\'open\');t.textContent=c.classList.contains(\'open\')?\'🧠 收起思考过程\':\'🧠 查看思考过程\';">🧠 查看思考过程</div><div class="reasoning-content open" id="' + rid + '">' + escapeHtml(lastMsg.reasoning_content) + '</div>';
    }
    lastEl.innerHTML = r + html;
    // 保持思考内容滚动在底部
    var rc = lastEl.querySelector('.reasoning-content.open');
    if (rc) rc.scrollTop = rc.scrollHeight;
    if (container.scrollTop + container.clientHeight >= container.scrollHeight - 80) {
        container.scrollTop = container.scrollHeight;
    }
    addCodeCopyButtons();
    // 流式更新时动态切换窄/宽气泡
    var msgEl = lastEl.closest('.msg');
    if (msgEl) {
        if (isNarrowContent(lastEl)) { msgEl.classList.add('narrow'); }
        else { msgEl.classList.remove('narrow'); }
    }
}
