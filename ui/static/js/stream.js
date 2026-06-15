// ==================== 发送消息 ====================
// 状态读取自 Alpine.store('app')
var $a = function() { return Alpine.store('app'); };

function app() { return $a(); }

function ensureSystemPrompt(conv) {
    if (!conv || !conv.promptId) return;
    if (conv.messages.length > 0 && conv.messages[0].role === 'system') return;
    var p = app().prompts.find(function(x) { return x.id === conv.promptId; });
    if (!p || !p.content) return;
    conv.messages.unshift({ role: 'system', content: p.content });
    conv.promptName = p.name;
}

function buildApiMessages(conv) {
    ensureSystemPrompt(conv);
    return conv.messages.filter(function(m) { return m.content !== '\u601D\u8003\u4E2D...'; });
}

async function send() {
    var a = app();
    if (a.loading) return;
    var input = document.getElementById('input');
    var text = (input.value || '').trim();
    if (!text) return;
    input.value = ''; autoResize();
    var conv = a.current;
    if (!conv) return;
    conv.messages.push({ role: 'user', content: text, timestamp: Date.now() });
    if (conv.messages.length === 1 || (conv.messages.length === 2 && conv.messages[0].role === 'system')) {
        conv.title = text.slice(0, 30) + (text.length > 30 ? '...' : '');
        if (!conv.folderId) conv.folderId = a.drawerOpen ? a.drawerFolderId : 'f_default';
    }
    conv.messages.push({ role: 'assistant', content: '\u601D\u8003\u4E2D...' });
    conv.updatedAt = Date.now();
    if (a.drawerOpen && conv.folderId !== a.drawerFolderId) conv.folderId = a.drawerFolderId;
    renderMessages(); a._save();
    a.loading = true;
    setLoading(true);
    var msgs = buildApiMessages(conv);
    if (typeof pywebview === 'undefined' || !pywebview.api) return;
    pywebview.api.sendMessage(JSON.stringify({
        messages: msgs,
        model: a.model,
        thinking: a.thinking,
        reasoning_effort: a.effort,
    }));
}

window._onStreamChunk = function(data) {
    var conv = app().current;
    if (!conv) return;
    var lastMsg = conv.messages[conv.messages.length - 1];
    if (!lastMsg || lastMsg.role !== 'assistant') return;
    if (lastMsg.content === '\u601D\u8003\u4E2D...') { lastMsg.content = ''; lastMsg.reasoning_content = ''; }
    if (data.content) lastMsg.content += data.content;
    if (data.reasoning_content) lastMsg.reasoning_content = (lastMsg.reasoning_content || '') + data.reasoning_content;
    updateLastMessage();
};

window._onStreamDone = function(data) {
    var a = app();
    a.loading = false;
    setLoading(false);
    var conv = a.current;
    if (!conv) return;
    if (!data.ok) {
        var lastMsg = conv.messages[conv.messages.length - 1];
        if (lastMsg && lastMsg.role === 'assistant') { lastMsg.content = '\u274C \u9519\u8BEF: ' + (data.error || '\u672A\u77E5\u9519\u8BEF'); lastMsg.reasoning_content = ''; }
    } else {
        var lastMsg2 = conv.messages[conv.messages.length - 1];
        if (lastMsg2 && lastMsg2.role === 'assistant') lastMsg2.timestamp = Date.now();
    }
    renderMessages(); a._save();
};

// ==================== 重新生成 ====================
function regenerate() {
    var a = app();
    if (a.loading) return;
    var conv = a.current;
    if (!conv || conv.messages.length < 2) return;
    var last = conv.messages[conv.messages.length - 1];
    if (last.role !== 'assistant') return;
    conv.messages.pop();
    conv.messages.push({ role: 'assistant', content: '\u601D\u8003\u4E2D...' });
    renderMessages(); a._save();
    a.loading = true;
    setLoading(true);
    var msgs = buildApiMessages(conv);
    if (typeof pywebview === 'undefined' || !pywebview.api) return;
    pywebview.api.sendMessage(JSON.stringify({
        messages: msgs,
        model: a.model,
        thinking: a.thinking,
        reasoning_effort: a.effort,
    }));
}

function updateLastMessage() {
    var container = document.getElementById('messages');
    var conv = app().current;
    if (!conv || !conv.messages || conv.messages.length === 0) return;
    var lastMsg = conv.messages[conv.messages.length - 1];
    var lastEl = container.querySelector('.msg:last-child .bubble');
    if (!lastEl) { renderMessages(); return; }
    if (lastMsg.role === 'user') return;
    var html = renderMarkdown(lastMsg.content);
    var r = '';
    if (lastMsg.reasoning_content) {
        var rid = 'reasoning_' + (conv.messages.length - 1);
        r = '<div class="reasoning-toggle" onclick="var c=document.getElementById(\'' + rid + '\');var t=this;c.classList.toggle(\'open\');t.textContent=c.classList.contains(\'open\')?\'\u{1F9E0} \u6536\u8D77\u601D\u8003\u8FC7\u7A0B\':\'\u{1F9E0} \u67E5\u770B\u601D\u8003\u8FC7\u7A0B\';">\u{1F9E0} \u67E5\u770B\u601D\u8003\u8FC7\u7A0B</div><div class="reasoning-content open" id="' + rid + '">' + escapeHtml(lastMsg.reasoning_content) + '</div>';
    }
    lastEl.innerHTML = r + html;
    var rc = lastEl.querySelector('.reasoning-content.open');
    if (rc) rc.scrollTop = rc.scrollHeight;
    if (container.scrollTop + container.clientHeight >= container.scrollHeight - 80) {
        container.scrollTop = container.scrollHeight;
    }
    addCodeCopyButtons();
    var msgEl = lastEl.closest('.msg');
    if (msgEl) {
        if (isNarrowContent(lastEl)) { msgEl.classList.add('narrow'); }
        else { msgEl.classList.remove('narrow'); }
    }
}
