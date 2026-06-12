// ==================== 对话管理 ====================
function newConv() {
    const cur = getCurrent();
    if (cur && (!cur.messages || cur.messages.length === 0)) { document.getElementById('input').focus(); return; }
    var id = Date.now().toString() + Math.random().toString(36).slice(2,8);
    var conv = { id: id, title: '新对话', messages: [], pinned: false };
    state.conversations.unshift(conv);
    state.currentId = id;
    renderAll(); save();
    updateStatus();
    if (typeof updatePromptCurrent === 'function') updatePromptCurrent();
}

function switchConv(id) {
    var container = document.getElementById('messages');
    container.style.opacity = '0';
    requestAnimationFrame(function() {
        state.currentId = id;
        renderMessages(); renderPinned(); renderFolderList();
        if (state.drawerOpen) renderDrawerConvs();
        updateStatus();
        if (typeof updatePromptCurrent === 'function') updatePromptCurrent();
        save();
        container.offsetHeight;
        container.style.opacity = '1';
    });
}

function getCurrent() { return state.conversations.find(c => c.id === state.currentId); }

function togglePin() {
    const conv = state.conversations.find(c => c.id === state.ctxConvId);
    if (conv) conv.pinned = !conv.pinned;
    renderPinned(); renderDrawerConvs(); save(); hideAllMenus();
}

function moveConvToFolder(convId, targetFolderId) {
    const conv = state.conversations.find(c => c.id === convId);
    if (conv) conv.folderId = targetFolderId;
    renderFolderList(); if (state.drawerOpen) renderDrawer(); save();
}

function moveConvMenu() {
    const menu = document.getElementById('drawerCtxMenu');
    const currentFolderId = (state.conversations.find(c => c.id === state.ctxConvId) || {}).folderId;
    let html = '';
    state.folders.forEach(f => {
        if (f.id !== currentFolderId)
            html += '<div class="item" onclick="moveConvToFolder(\'' + state.ctxConvId + '\',\'' + f.id + '\');hideAllMenus()">' + f.icon + ' ' + escapeHtml(f.name) + '</div>';
    });
    const after = menu.querySelector('.item:nth-child(2)');
    menu.querySelectorAll('.item.move-sub').forEach(el => el.remove());
    if (html && after) after.insertAdjacentHTML('afterend', html.replace(/class="item"/g, 'class="item move-sub"'));
}

function deleteConvFromDrawer() {
    const idx = state.conversations.findIndex(c => c.id === state.ctxConvId);
    if (idx < 0) return;
    const title = state.conversations[idx].title || '新对话';
    showConfirm('删除对话', '确定删除 "' + title + '" 吗？', '删除', function() {
        state.conversations.splice(idx, 1);
        if (!state.conversations.find(c => c.id === state.currentId)) {
            state.currentId = state.conversations.length > 0 ? state.conversations[0].id : null;
            if (!state.currentId) { newConv(); hideAllMenus(); return; }
        }
        renderAll(); save(); hideAllMenus();
    });
}
