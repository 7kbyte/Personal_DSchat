// ==================== 右键菜单 ====================
function onMsgCtx(e, idx) {
    e.preventDefault();
    state.ctxMsgIdx = idx;
    const conv = getCurrent();
    document.getElementById('rollbackItem').style.display = (conv && conv.messages && idx === conv.messages.length - 1) ? 'none' : '';
    showMenu('msgCtxMenu', e.clientX, e.clientY);
}
function onFolderCtx(e, folderId) { e.preventDefault(); state.ctxFolderId = folderId; document.getElementById('deleteFolderItem').style.display = folderId === 'f_default' ? 'none' : ''; showMenu('folderCtxMenu', e.clientX, e.clientY); }
function onDrawerConvCtx(e, convId) { e.preventDefault(); state.ctxConvId = convId; showMenu('drawerCtxMenu', e.clientX, e.clientY); }
function onPinnedCtx(e, convId) {
    e.preventDefault();
    state.ctxConvId = convId;
    const conv = state.conversations.find(c => c.id === convId);
    const title = conv ? (conv.title || '新对话') : '此对话';
    showConfirm('取消置顶', '确定将 "' + title + '" 取消置顶吗？', '取消置顶', function() {
        if (conv) conv.pinned = false;
        renderPinned(); renderDrawerConvs(); save();
    });
}

function showMenu(id, x, y) {
    hideAllMenus();
    const menu = document.getElementById(id);
    menu.style.display = 'block';
    menu.style.left = Math.min(x, window.innerWidth - 180) + 'px';
    menu.style.top = Math.min(y, window.innerHeight - 120) + 'px';
}
function hideAllMenus() { ['msgCtxMenu','folderCtxMenu','drawerCtxMenu'].forEach(id => document.getElementById(id).style.display = 'none'); }

function copyMessage() {
    const conv = getCurrent();
    if (!conv || state.ctxMsgIdx < 0) return;
    const msg = conv.messages[state.ctxMsgIdx];
    if (msg) { let t = msg.content; if (msg.reasoning_content) t = '【思考过程】\n' + msg.reasoning_content + '\n\n【回答】\n' + t; pywebview.api.copyToClipboard(t); }
    hideAllMenus();
}
function copyAll() {
    const conv = getCurrent(); if (!conv) return;
    const text = conv.messages.map(m => { let t = '【' + (m.role==='user'?'我':'DeepSeek') + '】' + m.content; if (m.reasoning_content) t = '【' + (m.role==='user'?'我':'DeepSeek') + ' · 思考过程】\n' + m.reasoning_content + '\n\n' + t; return t; }).join('\n\n');
    pywebview.api.copyToClipboard(text); hideAllMenus();
}
