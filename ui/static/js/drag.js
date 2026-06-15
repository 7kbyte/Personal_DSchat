// ==================== 拖拽 ====================
// 状态读取自 Alpine.store('app')
var $a = function() { return Alpine.store('app'); };
let dragFolderId = null, dragConvId = null, dragPinnedId = null;

function onFolderDragStart(e, folderId) { dragFolderId = folderId; e.target.closest('.folder-item')?.classList.add('dragging'); e.dataTransfer.effectAllowed = 'move'; }
function onFolderDragEnd(e) { e.target.closest('.folder-item')?.classList.remove('dragging'); document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over')); dragFolderId = null; }
function onFolderDragOver(e) { e.preventDefault(); e.dataTransfer.dropEffect = 'move'; e.target.closest('.folder-item')?.classList.add('drag-over'); }
function onFolderDragLeave(e) { e.target.closest('.folder-item')?.classList.remove('drag-over'); }
function onFolderDrop(e, targetFolderId) {
    e.preventDefault(); e.target.closest('.folder-item')?.classList.remove('drag-over');
    if (!dragFolderId || dragFolderId === targetFolderId) return;
    var a = $a();
    var fromIdx = a.folders.findIndex(f => f.id === dragFolderId);
    var toIdx = a.folders.findIndex(f => f.id === targetFolderId);
    if (fromIdx < 0 || toIdx < 0) return;
    var item = a.folders.splice(fromIdx, 1)[0];
    a.folders.splice(toIdx, 0, item);
    a.folders.forEach((f, i) => f.order = i);
    a._save();
}

function onPinnedDragStart(e, convId) { dragPinnedId = convId; e.target.closest('.pinned-item')?.classList.add('dragging'); e.dataTransfer.effectAllowed = 'move'; }
function onPinnedDragEnd(e) { e.target.closest('.pinned-item')?.classList.remove('dragging'); document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over')); dragPinnedId = null; }
function onPinnedDragOver(e) { e.preventDefault(); e.dataTransfer.dropEffect = 'move'; e.target.closest('.pinned-item')?.classList.add('drag-over'); }
function onPinnedDragLeave(e) { e.target.closest('.pinned-item')?.classList.remove('drag-over'); }
function onPinnedDrop(e, targetConvId) {
    e.preventDefault(); e.stopPropagation(); e.target.closest('.pinned-item')?.classList.remove('drag-over');
    if (!dragPinnedId || dragPinnedId === targetConvId) return;
    var a = $a();
    var fromIdx = a.conversations.findIndex(c => c.id === dragPinnedId);
    var toIdx = a.conversations.findIndex(c => c.id === targetConvId);
    if (fromIdx < 0 || toIdx < 0) return;
    var item = a.conversations.splice(fromIdx, 1)[0];
    a.conversations.splice(toIdx, 0, item);
    a._save();
}

function onDrawerConvDragOver(e) { e.preventDefault(); e.dataTransfer.dropEffect = 'move'; e.target.closest('.drawer-conv-item')?.classList.add('drag-over'); }
function onDrawerConvDragLeave(e) { e.target.closest('.drawer-conv-item')?.classList.remove('drag-over'); }
function onDrawerConvDrop(e, targetConvId) {
    e.preventDefault(); e.stopPropagation(); e.target.closest('.drawer-conv-item')?.classList.remove('drag-over');
    if (!dragConvId || dragConvId === targetConvId) return;
    var a = $a();
    var fromIdx = a.conversations.findIndex(c => c.id === dragConvId);
    var toIdx = a.conversations.findIndex(c => c.id === targetConvId);
    if (fromIdx < 0 || toIdx < 0) return;
    var item = a.conversations.splice(fromIdx, 1)[0];
    a.conversations.splice(toIdx, 0, item);
    a._save();
}
function onDrawerConvDragEnd(e) { e.target.closest('.drawer-conv-item')?.classList.remove('dragging'); document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over')); dragConvId = null; }
function onDrawerConvDragStart(e, convId) { dragConvId = convId; e.target.closest('.drawer-conv-item')?.classList.add('dragging'); e.dataTransfer.effectAllowed = 'move'; }

document.addEventListener('dragover', function(e) {
    var folderEl = e.target.closest('.folder-item');
    if (folderEl && dragConvId) { e.preventDefault(); folderEl.classList.add('drag-over'); }
});
document.addEventListener('dragleave', function(e) {
    var folderEl = e.target.closest('.folder-item');
    if (folderEl && dragConvId) folderEl.classList.remove('drag-over');
});
document.addEventListener('drop', function(e) {
    var folderEl = e.target.closest('.folder-item');
    if (folderEl && dragConvId) { e.preventDefault(); folderEl.classList.remove('drag-over'); $a().moveConvToFolder(dragConvId, folderEl.dataset.folderId); dragConvId = null; }
});

// ==================== 侧栏拖拽调整宽度 ====================
function setSidebarWidth(w) {
    w = Math.max(180, Math.min(500, w));
    document.querySelector('.sidebar').style.width = w + 'px';
    document.querySelector('.drawer-overlay').style.left = w + 'px';
    document.querySelector('.drawer-panel').style.left = w + 'px';
}

let _resizing = false, _resizeStartX = 0, _resizeStartW = 0;
document.addEventListener('mousedown', function(e) {
    if (!e.target.closest('#resizeHandle')) return;
    e.preventDefault();
    _resizing = true;
    _resizeStartX = e.clientX;
    _resizeStartW = parseInt(getComputedStyle(document.querySelector('.sidebar')).width);
    document.getElementById('resizeHandle').classList.add('active');
});
document.addEventListener('mousemove', function(e) {
    if (!_resizing) return;
    setSidebarWidth(_resizeStartW + e.clientX - _resizeStartX);
});
document.addEventListener('mouseup', function() {
    if (!_resizing) return;
    _resizing = false;
    document.getElementById('resizeHandle').classList.remove('active');
    const w = parseInt(getComputedStyle(document.querySelector('.sidebar')).width);
    if (typeof pywebview !== 'undefined' && pywebview.api) { try { pywebview.api.setSidebarWidth(w); } catch(e) {} }
});


// ---- 抽屉宽度拖拽 ----
function setDrawerWidth(w) {
    w = Math.max(220, Math.min(500, w));
    document.querySelector('.drawer-panel').style.width = w + 'px';
}

let _drawerResizing = false, _drawerStartX = 0, _drawerStartW = 0;
document.addEventListener('mousedown', function(e) {
    if (!e.target.closest('#drawerResizeHandle')) return;
    e.preventDefault();
    _drawerResizing = true;
    _drawerStartX = e.clientX;
    _drawerStartW = parseInt(getComputedStyle(document.querySelector('.drawer-panel')).width);
    document.getElementById('drawerResizeHandle').classList.add('active');
});
document.addEventListener('mousemove', function(e) {
    if (!_drawerResizing) return;
    setDrawerWidth(_drawerStartW + (e.clientX - _drawerStartX));
});
document.addEventListener('mouseup', function() {
    if (!_drawerResizing) return;
    _drawerResizing = false;
    document.getElementById('drawerResizeHandle').classList.remove('active');
    const w = parseInt(getComputedStyle(document.querySelector('.drawer-panel')).width);
    if (typeof pywebview !== 'undefined' && pywebview.api) { try { pywebview.api.saveSetting('drawer_width', String(w)); } catch(e) {} }
});
