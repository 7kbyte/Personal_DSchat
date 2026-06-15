// ==================== 拖拽排序 (TypeScript) ====================
let dragFolderId: string | null = null;
let dragConvId: string | null = null;
let dragPinnedId: string | null = null;

function onFolderDragStart(e: DragEvent, folderId: string): void {
  dragFolderId = folderId;
  (e.target as HTMLElement)?.closest('.folder-item')?.classList.add('dragging');
  if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move';
}
function onFolderDragEnd(e: DragEvent): void {
  (e.target as HTMLElement)?.closest('.folder-item')?.classList.remove('dragging');
  document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
  dragFolderId = null;
}
function onFolderDragOver(e: DragEvent): void {
  e.preventDefault();
  if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
  (e.target as HTMLElement)?.closest('.folder-item')?.classList.add('drag-over');
}
function onFolderDragLeave(e: DragEvent): void {
  (e.target as HTMLElement)?.closest('.folder-item')?.classList.remove('drag-over');
}
function onFolderDrop(e: DragEvent, targetFolderId: string): void {
  e.preventDefault();
  (e.target as HTMLElement)?.closest('.folder-item')?.classList.remove('drag-over');
  if (!dragFolderId || dragFolderId === targetFolderId) return;
  const app = Alpine.store('app');
  const fromIdx = app.folders.findIndex((f: FolderData) => f.id === dragFolderId);
  const toIdx = app.folders.findIndex((f: FolderData) => f.id === targetFolderId);
  if (fromIdx < 0 || toIdx < 0) return;
  const item = app.folders.splice(fromIdx, 1)[0];
  app.folders.splice(toIdx, 0, item);
  app.folders.forEach((f: FolderData, i: number) => f.order = i);
  app._save();
}

function onPinnedDragStart(e: DragEvent, convId: string): void {
  dragPinnedId = convId;
  (e.target as HTMLElement)?.closest('.pinned-item')?.classList.add('dragging');
  if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move';
}
function onPinnedDragEnd(e: DragEvent): void {
  (e.target as HTMLElement)?.closest('.pinned-item')?.classList.remove('dragging');
  document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
  dragPinnedId = null;
}
function onPinnedDragOver(e: DragEvent): void {
  e.preventDefault();
  if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
  (e.target as HTMLElement)?.closest('.pinned-item')?.classList.add('drag-over');
}
function onPinnedDragLeave(e: DragEvent): void {
  (e.target as HTMLElement)?.closest('.pinned-item')?.classList.remove('drag-over');
}
function onPinnedDrop(e: DragEvent, targetConvId: string): void {
  e.preventDefault();
  e.stopPropagation();
  (e.target as HTMLElement)?.closest('.pinned-item')?.classList.remove('drag-over');
  if (!dragPinnedId || dragPinnedId === targetConvId) return;
  const app = Alpine.store('app');
  const fromIdx = app.conversations.findIndex((c: ConvData) => c.id === dragPinnedId);
  const toIdx = app.conversations.findIndex((c: ConvData) => c.id === targetConvId);
  if (fromIdx < 0 || toIdx < 0) return;
  const item = app.conversations.splice(fromIdx, 1)[0];
  app.conversations.splice(toIdx, 0, item);
  app._save();
}

function onDrawerConvDragOver(e: DragEvent): void {
  e.preventDefault();
  if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
  (e.target as HTMLElement)?.closest('.drawer-conv-item')?.classList.add('drag-over');
}
function onDrawerConvDragLeave(e: DragEvent): void {
  (e.target as HTMLElement)?.closest('.drawer-conv-item')?.classList.remove('drag-over');
}
function onDrawerConvDrop(e: DragEvent, targetConvId: string): void {
  e.preventDefault();
  e.stopPropagation();
  (e.target as HTMLElement)?.closest('.drawer-conv-item')?.classList.remove('drag-over');
  if (!dragConvId || dragConvId === targetConvId) return;
  const app = Alpine.store('app');
  const fromIdx = app.conversations.findIndex((c: ConvData) => c.id === dragConvId);
  const toIdx = app.conversations.findIndex((c: ConvData) => c.id === targetConvId);
  if (fromIdx < 0 || toIdx < 0) return;
  const item = app.conversations.splice(fromIdx, 1)[0];
  app.conversations.splice(toIdx, 0, item);
  app._save();
}
function onDrawerConvDragEnd(e: DragEvent): void {
  (e.target as HTMLElement)?.closest('.drawer-conv-item')?.classList.remove('dragging');
  document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
  dragConvId = null;
}
function onDrawerConvDragStart(e: DragEvent, convId: string): void {
  dragConvId = convId;
  (e.target as HTMLElement)?.closest('.drawer-conv-item')?.classList.add('dragging');
  if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move';
}

document.addEventListener('dragover', (e) => {
  const folderEl = (e.target as HTMLElement)?.closest('.folder-item');
  if (folderEl && dragConvId) { e.preventDefault(); folderEl.classList.add('drag-over'); }
});
document.addEventListener('dragleave', (e) => {
  const folderEl = (e.target as HTMLElement)?.closest('.folder-item');
  if (folderEl && dragConvId) folderEl.classList.remove('drag-over');
});
document.addEventListener('drop', (e) => {
  const folderEl = (e.target as HTMLElement)?.closest('.folder-item');
  if (folderEl && dragConvId) {
    e.preventDefault();
    folderEl.classList.remove('drag-over');
    Alpine.store('app').moveConvToFolder(dragConvId, (folderEl as HTMLElement).dataset.folderId!);
    dragConvId = null;
  }
});

// ==================== 侧栏拖拽调整宽度 ====================
function setSidebarWidth(w: number): void {
  w = Math.max(180, Math.min(500, w));
  const sidebar = document.querySelector('.sidebar') as HTMLElement | null;
  if (sidebar) sidebar.style.width = w + 'px';
  const overlay = document.querySelector('.drawer-overlay') as HTMLElement | null;
  if (overlay) overlay.style.left = w + 'px';
  const panel = document.querySelector('.drawer-panel') as HTMLElement | null;
  if (panel) panel.style.left = w + 'px';
}

let _resizing = false;
let _resizeStartX = 0;
let _resizeStartW = 0;
document.addEventListener('mousedown', (e) => {
  if (!(e.target as HTMLElement)?.closest('#resizeHandle')) return;
  e.preventDefault();
  _resizing = true;
  _resizeStartX = e.clientX;
  _resizeStartW = parseInt((document.querySelector('.sidebar') as HTMLElement)?.style.width || '260');
});
document.addEventListener('mousemove', (e) => {
  if (!_resizing) return;
  setSidebarWidth(_resizeStartW + e.clientX - _resizeStartX);
});
document.addEventListener('mouseup', () => {
  if (_resizing) {
    _resizing = false;
    const w = parseInt((document.querySelector('.sidebar') as HTMLElement)?.style.width || '260');
    if (typeof pywebview !== 'undefined' && pywebview!.api) {
      try { pywebview!.api.setSidebarWidth(w); } catch (e) {}
    }
  }
});

// ==================== 抽屉拖拽调整宽度 ====================
function setDrawerWidth(w: number): void {
  w = Math.max(220, Math.min(500, w));
  const panel = document.querySelector('.drawer-panel') as HTMLElement | null;
  if (panel) panel.style.width = w + 'px';
}

let _drawerResizing = false;
let _drawerStartX = 0;
let _drawerStartW = 0;
document.addEventListener('mousedown', (e) => {
  if (!(e.target as HTMLElement)?.closest('#drawerResizeHandle')) return;
  e.preventDefault();
  _drawerResizing = true;
  _drawerStartX = e.clientX;
  _drawerStartW = parseInt((document.querySelector('.drawer-panel') as HTMLElement)?.style.width || '310');
});
document.addEventListener('mousemove', (e) => {
  if (!_drawerResizing) return;
  setDrawerWidth(_drawerStartW + (e.clientX - _drawerStartX));
});
document.addEventListener('mouseup', () => {
  if (_drawerResizing) {
    _drawerResizing = false;
    const w = parseInt((document.querySelector('.drawer-panel') as HTMLElement)?.style.width || '310');
    if (typeof pywebview !== 'undefined' && pywebview!.api) {
      try { pywebview!.api.saveSetting('drawer_width', String(w)); } catch (e) {}
    }
  }
});
