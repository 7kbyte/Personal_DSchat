// ==================== 渲染 ====================
function renderAll() { renderPinned(); renderFolderList(); renderMessages(); if (state.drawerOpen) renderDrawer(); }

function renderPinned() {
    const pinned = state.conversations.filter(c => c.pinned && c.messages && c.messages.length > 0);
    const section = document.getElementById('pinnedSection');
    const list = document.getElementById('pinnedList');
    if (pinned.length === 0) { section.style.display = 'none'; return; }
    section.style.display = 'block';
    list.innerHTML = pinned.map(c => {
        const folder = state.folders.find(f => f.id === c.folderId);
        const folderTag = folder ? '<span class="pinned-folder-tag">' + escapeHtml(folder.icon + ' ' + folder.name) + '</span>' : '';
        return '<div class="pinned-item' + (c.id === state.currentId ? ' active' : '') + '" draggable="true" data-conv-id="' + c.id + '"'
            + ' onclick="switchConv(\'' + c.id + '\')"'
            + ' oncontextmenu="onPinnedCtx(event,\'' + c.id + '\')"'
            + ' ondragstart="onPinnedDragStart(event,\'' + c.id + '\')"'
            + ' ondragend="onPinnedDragEnd(event)"'
            + ' ondragover="onPinnedDragOver(event)"'
            + ' ondragleave="onPinnedDragLeave(event)"'
            + ' ondrop="onPinnedDrop(event,\'' + c.id + '\')">'
            + '<span class="pin-icon">📌</span>'
            + '<div class="pinned-body">'
            + '<div class="pinned-title">' + escapeHtml(c.title || '新对话') + '</div>'
            + '<div class="pinned-meta"><span>' + fmtRelative(c.updatedAt) + '</span>' + folderTag + '</div>'
            + '</div>'
            + '</div>';
    }).join('');
}

function renderMessages() {
    const container = document.getElementById('messages');
    const conv = getCurrent();
    if (!conv || !conv.messages || conv.messages.length === 0) {
        container.innerHTML = '<div class="empty"><div class="logo">🐱</div><h2>你好！我是 DeepSeek</h2><p>有什么可以帮你的吗？</p></div>';
        return;
    }
    container.innerHTML = conv.messages.map((m, i) => {
        const isUser = m.role === 'user';
        const avatar = isUser ? '我' : 'DS';
        const html = renderMarkdown(m.content);
        let r = '';
        if (!isUser && m.reasoning_content) {
            const rid = 'reasoning_' + i;
            r = '<div class="reasoning-toggle" onclick="var c=document.getElementById(\'' + rid + '\');var t=this;c.classList.toggle(\'open\');t.textContent=c.classList.contains(\'open\')?\'🧠 收起思考过程\':\'🧠 查看思考过程\';">🧠 查看思考过程</div><div class="reasoning-content" id="' + rid + '">' + escapeHtml(m.reasoning_content) + '</div>';
        }
        return '<div class="msg ' + m.role + '" oncontextmenu="onMsgCtx(event,' + i + ')"><div class="msg-side"><div class="avatar">' + avatar + '</div><div class="msg-time">' + fmtTime(m.timestamp) + '</div></div><div class="bubble">' + r + html + '</div>'
            + ((!isUser && i === conv.messages.length - 1 && !state.loading) ? '<div class="msg-actions"><button class="regenerate-btn" onclick="regenerate()" title="重新生成">🔄</button></div>' : '')
            + '</div>';
    }).join('');
    container.scrollTop = container.scrollHeight;
    addCodeCopyButtons();
    // 为纯文本短回答应用窄气泡样式
    container.querySelectorAll('.msg.assistant .bubble').forEach(function(b) {
        var msg = b.closest('.msg');
        if (isNarrowContent(b)) { msg.classList.add('narrow'); }
        else { msg.classList.remove('narrow'); }
    });
}

// ==================== 代码块复制 ====================
function addCodeCopyButtons() {
    document.querySelectorAll('.bubble pre').forEach(pre => {
        if (pre.querySelector('.code-copy-btn')) return;
        pre.style.position = 'relative';
        var btn = document.createElement('button');
        btn.className = 'code-copy-btn';
        btn.textContent = '📋';
        btn.title = '复制代码';
        btn.onclick = function() {
            var clone = pre.cloneNode(true);
            var btnInClone = clone.querySelector('.code-copy-btn');
            if (btnInClone) btnInClone.remove();
            pywebview.api.copyToClipboard(clone.textContent || '');
            btn.textContent = '✅';
            setTimeout(function() { btn.textContent = '📋'; }, 1500);
        };
        pre.appendChild(btn);
    });
}

function setLoading(on) {
    state.loading = on;
    document.getElementById('btnSend').style.display = on ? 'none' : '';
    document.getElementById('btnStop').style.display = on ? '' : 'none';
    document.getElementById('btnSend').disabled = on;
}

async function stopGeneration() {
    if (pywebview.api) pywebview.api.stopGeneration();
}
