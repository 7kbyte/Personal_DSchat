// ==================== 消息渲染 ====================
// 状态读取自 Alpine.store('app')
var $a = function() { return Alpine.store('app'); };

function renderMessages() {
    const container = document.getElementById('messages');
    if (!container) return;
    const app = $a();
    const conv = app.current;
    if (!conv || !conv.messages || conv.messages.length === 0) {
        container.innerHTML = '<div class="empty"><div class="logo">\u{1F431}</div><h2>\u4F60\u597D\uFF01\u6211\u662F DeepSeek</h2><p>\u6709\u4EC0\u4E48\u53EF\u4EE5\u5E2E\u4F60\u7684\u5417\uFF1F</p></div>';
        return;
    }
    var visible = conv.messages.filter(function(m) { return m.role !== 'system'; });
    if (visible.length === 0) {
        container.innerHTML = '<div class="empty"><div class="logo">\u{1F431}</div><h2>\u4F60\u597D\uFF01\u6211\u662F DeepSeek</h2><p>\u6709\u4EC0\u4E48\u53EF\u4EE5\u5E2E\u4F60\u7684\u5417\uFF1F</p></div>';
        return;
    }
    var html = '';
    for (var i = 0; i < visible.length; i++) {
        var m = visible[i];
        var isUser = m.role === 'user';
        var avatar = isUser ? '\u6211' : 'DS';
        var contentHtml = renderMarkdown(m.content);
        var reasoningHtml = '';
        if (!isUser && m.reasoning_content) {
            var rid = 'reasoning_' + i;
            reasoningHtml = '<div class="reasoning-toggle" onclick="var c=document.getElementById(\'' + rid + '\');var t=this;c.classList.toggle(\'open\');t.textContent=c.classList.contains(\'open\')?\'\u{1F9E0} \u6536\u8D77\u601D\u8003\u8FC7\u7A0B\':\'\u{1F9E0} \u67E5\u770B\u601D\u8003\u8FC7\u7A0B\';">\u{1F9E0} \u67E5\u770B\u601D\u8003\u8FC7\u7A0B</div><div class="reasoning-content" id="' + rid + '">' + escapeHtml(m.reasoning_content) + '</div>';
        }
        var actionsHtml = '';
        if (!isUser && i === visible.length - 1 && !app.loading) {
            actionsHtml = '<div class="msg-actions"><button class="regenerate-btn" onclick="regenerate()" title="\u91CD\u65B0\u751F\u6210">\u{1F504}</button></div>';
        }
        html += '<div class="msg ' + m.role + '" oncontextmenu="Alpine.store(\'app\').onMsgCtx(event,' + i + ')">'
            + '<div class="msg-side"><div class="avatar">' + avatar + '</div><div class="msg-time">' + fmtTime(m.timestamp) + '</div></div>'
            + '<div class="bubble">' + reasoningHtml + contentHtml + '</div>'
            + actionsHtml
            + '</div>';
    }
    container.innerHTML = html;
    container.scrollTop = container.scrollHeight;
    addCodeCopyButtons();
    container.querySelectorAll('.msg.assistant .bubble').forEach(function(b) {
        var msg = b.closest('.msg');
        if (isNarrowContent(b)) { msg.classList.add('narrow'); }
        else { msg.classList.remove('narrow'); }
    });
}

function addCodeCopyButtons() {
    document.querySelectorAll('.bubble pre').forEach(pre => {
        if (pre.querySelector('.code-copy-btn')) return;
        pre.style.position = 'relative';
        var btn = document.createElement('button');
        btn.className = 'code-copy-btn';
        btn.textContent = '\u{1F4CB}';
        btn.title = '\u590D\u5236\u4EE3\u7801';
        btn.onclick = function() {
            var clone = pre.cloneNode(true);
            var btnInClone = clone.querySelector('.code-copy-btn');
            if (btnInClone) btnInClone.remove();
            if (typeof pywebview !== 'undefined' && pywebview.api)
                pywebview.api.copyToClipboard(clone.textContent || '');
            btn.textContent = '\u2705';
            setTimeout(function() { btn.textContent = '\u{1F4CB}'; }, 1500);
        };
        pre.appendChild(btn);
    });
}

function setLoading(on) {
    $a().loading = on;
}

async function stopGeneration() {
    if (typeof pywebview !== 'undefined' && pywebview.api)
        pywebview.api.stopGeneration();
}
