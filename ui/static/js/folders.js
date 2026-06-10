// ==================== 文件夹渲染 ====================
function renderFolderList() {
    const list = document.getElementById('folderList');
    const sorted = [...state.folders].sort((a,b) => (a.order||0) - (b.order||0));
    list.innerHTML = sorted.map(f => {
        const count = state.conversations.filter(c => c.folderId === f.id && c.messages && c.messages.length > 0).length;
        const active = state.drawerOpen && state.drawerFolderId === f.id;
        return '<div class="folder-item' + (active ? ' active' : '') + '" draggable="true" data-folder-id="' + f.id + '"'
            + ' onclick="openDrawer(\'' + f.id + '\')"'
            + ' oncontextmenu="onFolderCtx(event,\'' + f.id + '\')"'
            + ' ondragstart="onFolderDragStart(event,\'' + f.id + '\')"'
            + ' ondragend="onFolderDragEnd(event)"'
            + ' ondragover="onFolderDragOver(event)"'
            + ' ondragleave="onFolderDragLeave(event)"'
            + ' ondrop="onFolderDrop(event,\'' + f.id + '\')">'
            + '<span class="folder-icon">' + (f.icon || '📁') + '</span>'
            + '<span class="folder-name">' + escapeHtml(f.name) + '</span>'
            + '<span class="folder-count">' + count + '</span></div>';
    }).join('');
}

function openDrawer(folderId) {
    if (state.drawerOpen && state.drawerFolderId === folderId) { closeDrawer(); return; }
    state.drawerOpen = true; state.drawerFolderId = folderId;
    const panel = document.getElementById('drawerPanel');
    panel.style.display = 'flex';
    document.getElementById('drawerOverlay').style.display = 'block';
    requestAnimationFrame(() => panel.classList.add('open'));
    renderDrawer(); renderFolderList();
}

function closeDrawer() {
    state.drawerOpen = false; state.drawerFolderId = null;
    document.getElementById('drawerSearch').value = '';
    const panel = document.getElementById('drawerPanel');
    panel.classList.remove('open');
    setTimeout(() => { if (!state.drawerOpen) { panel.style.display = 'none'; document.getElementById('drawerOverlay').style.display = 'none'; } }, 200);
    renderFolderList();
}

function renderDrawer() {
    const folder = state.folders.find(f => f.id === state.drawerFolderId);
    if (!folder) return;
    document.getElementById('drawerTitle').innerHTML = folder.icon + ' ' + escapeHtml(folder.name);
    document.getElementById('drawerSearch').value = '';
    renderDrawerConvs();
}

function renderDrawerConvs() {
    const folderId = state.drawerFolderId;
    if (!folderId) return;
    const query = (document.getElementById('drawerSearch').value || '').toLowerCase();
    let convs = state.conversations.filter(c => c.folderId === folderId);
    convs.sort((a, b) => { if (a.pinned && !b.pinned) return -1; if (!a.pinned && b.pinned) return 1; return 0; });
    if (query) convs = convs.filter(c => (c.title || '新对话').toLowerCase().includes(query));

    const container = document.getElementById('drawerConvList');
    if (convs.length === 0) {
        container.innerHTML = '<div class="drawer-empty">' + (query ? '未找到匹配的对话' : '暂无对话') + '</div>';
        return;
    }
    container.innerHTML = convs.map(c =>
        '<div class="drawer-conv-item' + (c.id === state.currentId ? ' active' : '') + '" draggable="true" data-conv-id="' + c.id + '"'
        + ' onclick="switchConv(\'' + c.id + '\')"'
        + ' oncontextmenu="onDrawerConvCtx(event,\'' + c.id + '\')"'
        + ' ondragstart="onDrawerConvDragStart(event,\'' + c.id + '\')"'
        + ' ondragend="onDrawerConvDragEnd(event)"'
        + ' ondragover="onDrawerConvDragOver(event)"'
        + ' ondragleave="onDrawerConvDragLeave(event)"'
        + ' ondrop="onDrawerConvDrop(event,\'' + c.id + '\')">'
        + (c.pinned ? '<span class="pin-icon">📌</span>' : '')
        + '<span class="conv-name">' + escapeHtml(c.title || '新对话').slice(0, 30) + '</span>'
        + '<span class="conv-time">' + fmtRelative(c.updatedAt) + '</span>'
        + '</div>'
    ).join('');
}

// ==================== 文件夹 CRUD ====================
function showFolderModal(edit) {
    state.folderModalId = edit ? state.ctxFolderId : null;
    const input = document.getElementById('folderNameInput');
    const errEl = document.getElementById('folderModalError');
    document.getElementById('folderModalTitle').textContent = edit ? '编辑收藏夹' : '新建收藏夹';
    errEl.style.display = 'none';
    if (edit) {
        const folder = state.folders.find(f => f.id === state.ctxFolderId);
        input.value = folder ? folder.name : '';
        state._fi = folder ? folder.icon : '📁';
    } else { input.value = ''; state._fi = '📁'; }
    renderIconPicker();
    document.getElementById('folderModal').style.display = 'flex';
    setTimeout(() => input.focus(), 100);
}

function renderIconPicker() {
    const picker = document.getElementById('iconPicker');
    picker.innerHTML = PRESET_ICONS.map(icon =>
        '<span class="' + (icon === state._fi ? 'sel' : '') + '" onclick="pickIcon(\'' + icon + '\')">' + icon + '</span>'
    ).join('');
}

function pickIcon(icon) { state._fi = icon; renderIconPicker(); }
function closeFolderModal() { document.getElementById('folderModal').style.display = 'none'; state.folderModalId = null; }

function submitFolder() {
    const name = document.getElementById('folderNameInput').value.trim();
    const errEl = document.getElementById('folderModalError');
    if (!name) { errEl.textContent = '请输入名称'; errEl.style.display = 'block'; return; }
    if (state.folderModalId) {
        const folder = state.folders.find(f => f.id === state.folderModalId);
        if (folder) { folder.name = name; folder.icon = state._fi; }
    } else {
        const id = 'f_' + Date.now() + Math.random().toString(36).slice(2,6);
        state.folders.push({ id, name, icon: state._fi, order: state.folders.length });
    }
    closeFolderModal(); renderFolderList();
    if (state.drawerOpen) renderDrawer(); save();
}

function deleteFolder() {
    const folderId = state.ctxFolderId;
    if (folderId === 'f_default') return;
    const folder = state.folders.find(f => f.id === folderId);
    if (!folder) return;
    const count = state.conversations.filter(c => c.folderId === folderId).length;
    const msg = '确定删除 "' + folder.name + '" 吗？' + (count > 0 ? '\n' + count + ' 个对话将移至默认收藏夹。' : '');
    showConfirm('删除收藏夹', msg, '删除', function() {
        state.conversations.forEach(c => { if (c.folderId === folderId) c.folderId = 'f_default'; });
        state.folders = state.folders.filter(f => f.id !== folderId);
        if (state.drawerFolderId === folderId) closeDrawer();
        renderFolderList(); save();
    });
}
