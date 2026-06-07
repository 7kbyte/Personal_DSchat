"""HTML page for DeepSeek Chat"""

from ui.themes import THEME_CSS

PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DeepSeek Chat</title>

<!-- KaTeX -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>

<!-- marked.js -->
<script src="https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js"></script>

<style>
""" + THEME_CSS + r"""
</style>
</head>
</head>
<body>

<!-- ========== 侧边栏 ========== -->
<div class="sidebar">
    <div class="sidebar-header">
        <h1>💬 DeepSeek Chat</h1>
        <p>Powered by DeepSeek API</p>
    </div>
    <button class="btn-new" onclick="newConv()">＋ 新对话</button>
    <div class="pinned-section" id="pinnedSection" style="display:none">
        <div class="pinned-list" id="pinnedList"></div>
    </div>
    <div class="folder-list" id="folderList"></div>
    <div class="btn-new-folder" onclick="showFolderModal()">📁 ＋ 新建收藏夹</div>
    <div class="sidebar-settings">
        <div class="settings-row">
            <select id="modelSelect" onchange="onSettingsChange()" style="flex:1">
                <option value="deepseek-v4-pro">DS-V4 Pro</option>
                <option value="deepseek-v4-flash">DS-V4 Flash</option>
            </select>
            <div class="think-row" onclick="toggleThink()" style="flex:1">
                <input type="checkbox" id="thinkToggle" checked onchange="onSettingsChange()">
                <span>🧠 深度思考</span>
            </div>
        </div>
        <div class="settings-row">
            <select id="effortSelect" onchange="onSettingsChange()" style="flex:1">
                <option value="high">high</option>
                <option value="max">max</option>
            </select>
            <select id="themeSelect" onchange="setTheme(this.value)" style="flex:1">
                <option value="sunset">🌅 暖阳橙</option>
                <option value="sakura">🌸 樱花粉</option>
                <option value="ocean">🌊 深海蓝</option>
                <option value="cosmic">🌑 宇宙黑</option>
            </select>
        </div>
    </div>
    <div class="sidebar-footer">{VERSION} · 数据保存至本地</div>
    <div class="sidebar-resize-handle" id="resizeHandle"></div>
</div>

<!-- ========== 抽屉面板 ========== -->
<div class="drawer-overlay" id="drawerOverlay" onclick="closeDrawer()"></div>
<div class="drawer-panel" id="drawerPanel">
    <div class="drawer-header">
        <span class="folder-title" id="drawerTitle"></span>
        <button class="drawer-btn-close" onclick="closeDrawer()" title="关闭">✕</button>
    </div>
    <div class="drawer-search">
        <input type="text" id="drawerSearch" placeholder="🔍 过滤对话..." oninput="renderDrawerConvs()">
    </div>
    <div class="drawer-conv-list" id="drawerConvList"></div>
</div>

<!-- ========== 主区域 ========== -->
<div class="main">
    <div class="chat-header">
        <span class="dot"></span>
        <span id="statusText">DS-V4 Pro · 🧠 深度思考</span>
    </div>
    <div class="messages" id="messages">
        <div class="empty">
            <div class="logo">🐱</div>
            <h2>你好！我是 DeepSeek</h2>
            <p>有什么可以帮你的吗？</p>
        </div>
    </div>
    <div class="input-area">
        <div class="input-row">
            <textarea id="input" rows="1" placeholder="输入消息，Enter 发送，Shift+Enter 换行"
                onkeydown="onKeyDown(event)" oninput="autoResize()"></textarea>
            <button class="btn-send" id="btnSend" onclick="send()" title="发送">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13"/><path d="M22 2L15 22L11 13L2 9L22 2Z"/></svg>
            </button>
        </div>
    </div>
</div>

<!-- ========== 消息右键菜单 ========== -->
<div class="context-menu" id="msgCtxMenu">
    <div class="item" onclick="copyMessage()">📋 复制此消息</div>
    <div class="item" onclick="copyAll()">📋 复制全部对话</div>
    <div style="height:1px;background:var(--border);margin:2px 8px"></div>
    <div class="item" id="rollbackItem" onclick="rollbackTo()">↩ 回退到此处</div>
</div>

<!-- ========== 文件夹右键菜单 ========== -->
<div class="context-menu" id="folderCtxMenu">
    <div class="item" onclick="showFolderModal(true)">✏️ 重命名</div>
    <div class="item danger" id="deleteFolderItem" onclick="deleteFolder()">🗑 删除收藏夹</div>
</div>

<!-- ========== 抽屉对话右键菜单 ========== -->
<div class="context-menu" id="drawerCtxMenu">
    <div class="item" onclick="togglePin()">📌 置顶/取消置顶</div>
    <div class="item" onclick="moveConvMenu()">📁 移动到...</div>
    <div class="item danger" onclick="deleteConvFromDrawer()">🗑 删除对话</div>
</div>

<!-- ========== 文件夹编辑模态框 ========== -->
<div class="modal-overlay" id="folderModal">
    <div class="modal">
        <h3 id="folderModalTitle">新建收藏夹</h3>
        <input type="text" id="folderNameInput" placeholder="收藏夹名称" maxlength="20">
        <p style="font-size:12px;color:var(--sub);margin-bottom:4px">选择图标：</p>
        <div class="icon-picker" id="iconPicker"></div>
        <p id="folderModalError" style="font-size:12px;color:var(--danger);display:none"></p>
        <div class="btns" style="margin-top:8px">
            <button onclick="closeFolderModal()">取消</button>
            <button style="background:var(--accent);color: var(--on-accent);border-color:var(--accent)" onclick="submitFolder()">确认</button>
        </div>
    </div>
</div>

<!-- ========== 确认模态框 ========== -->
<div class="modal-overlay" id="confirmModal">
    <div class="modal" style="max-width:340px">
        <h3 id="confirmTitle"></h3>
        <p id="confirmMsg" style="white-space:pre-line"></p>
        <div class="btns">
            <button onclick="closeConfirmModal()">取消</button>
            <button class="btn-danger" id="confirmBtn" onclick="confirmConfirm()">确认</button>
        </div>
    </div>
</div>

<div class="modal-overlay" id="rollbackModal">
    <div class="modal">
        <h3>回退对话</h3>
        <p id="rollbackHint"></p>
        <div class="btns">
            <button onclick="closeRollbackModal()">取消</button>
            <button class="btn-danger" onclick="confirmRollback()">确认回退</button>
        </div>
    </div>
</div>

<div class="modal-overlay" id="apiKeyModal">
    <div class="modal">
        <h3>🔑 设置 API Key</h3>
        <p>请输入你的 DeepSeek API Key：</p>
        <input type="password" id="apiKeyInput" placeholder="sk-...">
        <p style="font-size:11px;color:var(--sub)">Key 将保存在本地，仅用于调用 DeepSeek API</p>
        <p id="apiKeyError" style="font-size:12px;color:var(--danger);display:none"></p>
        <div class="btns" style="margin-top:8px">
            <button onclick="closeApiKeyModal()">取消</button>
            <button style="background:var(--accent);color: var(--on-accent);border-color:var(--accent)" onclick="submitApiKey()">确认</button>
        </div>
    </div>
</div>

<script>
// ==================== KaTeX + marked ====================
marked.setOptions({ breaks: true, gfm: true });

function renderMarkdown(text) {
    const latexBlocks = [];
    let processed = text
        .replace(/\\\[([\s\S]*?)\\\]/g, (_, tex) => { latexBlocks.push({ type: 'block', tex: tex.trim() }); return '\x00LB' + (latexBlocks.length - 1) + '\x00'; })
        .replace(/\\\(([\s\S]*?)\\\)/g, (_, tex) => { latexBlocks.push({ type: 'inline', tex: tex.trim() }); return '\x00LI' + (latexBlocks.length - 1) + '\x00'; })
        .replace(/\$\$([\s\S]*?)\$\$/g, (_, tex) => { latexBlocks.push({ type: 'block', tex: tex.trim() }); return '\x00LB' + (latexBlocks.length - 1) + '\x00'; })
        .replace(/\$([^$]+?)\$/g, (_, tex) => { latexBlocks.push({ type: 'inline', tex: tex.trim() }); return '\x00LI' + (latexBlocks.length - 1) + '\x00'; });

    let html = marked.parse(processed);

    html = html.replace(/\x00LB(\d+)\x00/g, (_, i) => {
        const lb = latexBlocks[parseInt(i)];
        try { return katex.renderToString(lb.tex, { displayMode: true, throwOnError: false }); }
        catch(e) { return '<code>' + escapeHtml(lb.tex) + '</code>'; }
    });
    html = html.replace(/\x00LI(\d+)\x00/g, (_, i) => {
        const lb = latexBlocks[parseInt(i)];
        try { return katex.renderToString(lb.tex, { displayMode: false, throwOnError: false }); }
        catch(e) { return '<code>' + escapeHtml(lb.tex) + '</code>'; }
    });
    return html;
}

function escapeHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
}

// ==================== 图标预设 ====================
const PRESET_ICONS = ['📁','💼','🏠','🎓','💡','🚀','🎮','🎵','📚','❤️','🌟','🔥','🌈','🍕','🐱','💰','⚡','🎯','🌍','📝'];

// ==================== 状态 ====================
let state = {
    conversations: [], folders: [], currentId: null, loading: false,
    drawerOpen: false, drawerFolderId: null,
    ctxMsgIdx: -1, deleteIdx: -1, ctxConvId: null, ctxFolderId: null,
    folderModalId: null
};
let pywebviewReady = false;

// ==================== 初始化 ====================
async function init() {
    try {
        if (window.pywebview && pywebview.api) {
            const raw = await pywebview.api.loadState();
            const data = JSON.parse(raw);
            state.conversations = data.conversations || [];
            state.folders = data.folders || [];
            state.currentId = data.currentId || null;
        }
    } catch(e) { console.error('[init] error:', e); }

    if (state.folders.length === 0) {
        state.folders = [{ id: 'f_default', name: '默认收藏夹', icon: '📁', order: 0 }];
    }
    if (state.conversations.length === 0) {
        newConv();
    } else {
        const cur = state.conversations.find(c => c.id === state.currentId);
        if (!cur) state.currentId = state.conversations[0].id;
        renderAll();
    }
    pywebviewReady = true;

    // 加载保存的侧栏宽度
    if (window.pywebview && pywebview.api) {
        try {
            const w = await pywebview.api.getSidebarWidth();
            if (w) setSidebarWidth(w);
        } catch(e) {}
    }

    // 加载保存的主题
    if (window.pywebview && pywebview.api) {
        try {
            const theme = await pywebview.api.getTheme();
            if (theme) { document.body.dataset.theme = theme; document.getElementById('themeSelect').value = theme; }
        } catch(e) {}
    }

    try {
        if (window.pywebview && pywebview.api) {
            const hasKey = await pywebview.api.hasApiKey();
            if (!hasKey) {
                document.getElementById('apiKeyModal').style.display = 'flex';
            }
        }
    } catch(e) {}
}

function save() {
    if (!pywebviewReady) return;
    pywebview.api.saveState(JSON.stringify(state.conversations), JSON.stringify(state.folders), state.currentId);
}

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
        + ' ondragend="onDragEnd(event)">'
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

// ==================== 对话管理 ====================
function newConv() {
    const cur = getCurrent();
    if (cur && (!cur.messages || cur.messages.length === 0)) { document.getElementById('input').focus(); return; }
    const id = Date.now().toString() + Math.random().toString(36).slice(2,8);
    state.conversations.unshift({ id, title: '新对话', messages: [], pinned: false });
    state.currentId = id;
    renderAll(); save();
}

function switchConv(id) {
    state.currentId = id;
    renderMessages(); renderPinned(); renderFolderList();
    if (state.drawerOpen) renderDrawerConvs();
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
        const folderName = folder ? (folder.icon + ' ' + folder.name) : '';
        return '<div class="pinned-item' + (c.id === state.currentId ? ' active' : '') + '" onclick="switchConv(\'' + c.id + '\')" oncontextmenu="onPinnedCtx(event,\'' + c.id + '\')">'
            + '<span class="pin-icon">📌</span>' + escapeHtml(c.title || '新对话').slice(0, 20)
            + '<span class="pinned-time">' + fmtRelative(c.updatedAt) + '</span>'
            + (folderName ? '<span class="pinned-folder">' + escapeHtml(folderName) + '</span>' : '')
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
        return '<div class="msg ' + m.role + '" oncontextmenu="onMsgCtx(event,' + i + ')"><div class="msg-side"><div class="avatar">' + avatar + '</div><div class="msg-time">' + fmtTime(m.timestamp) + '</div></div><div class="bubble">' + r + html + '</div></div>';
    }).join('');
    container.scrollTop = container.scrollHeight;
    addCodeCopyButtons();
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
            var code = pre.textContent || '';
            pywebview.api.copyToClipboard(code);
            btn.textContent = '✅';
            setTimeout(function() { btn.textContent = '📋'; }, 1500);
        };
        pre.appendChild(btn);
    });
}

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
    document.getElementById('btnSend').disabled = true;
    updateStatus();
    const model = document.getElementById('modelSelect').value;
    const thinking = document.getElementById('thinkToggle').checked;
    const effort = document.getElementById('effortSelect').value;
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
    document.getElementById('btnSend').disabled = false;
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

// ==================== 时间格式化 ====================
function fmtTime(ts) {
    if (!ts) return '';
    var d = new Date(ts), now = new Date();
    var hh = String(d.getHours()).padStart(2,'0'), mm = String(d.getMinutes()).padStart(2,'0');
    var time = hh + ':' + mm;
    if (d.toDateString() === now.toDateString()) return time;
    return String(d.getMonth()+1).padStart(2,'0') + '/' + String(d.getDate()).padStart(2,'0') + ' ' + time;
}

function fmtRelative(ts) {
    if (!ts) return '';
    var diff = Date.now() - ts;
    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return Math.floor(diff/60000) + '分钟前';
    var d = new Date(ts), now = new Date();
    if (d.toDateString() === now.toDateString()) return String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0');
    return String(d.getMonth()+1).padStart(2,'0') + '/' + String(d.getDate()).padStart(2,'0');
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
    container.scrollTop = container.scrollHeight;
    addCodeCopyButtons();
}

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

// ==================== 拖拽 ====================
let dragFolderId = null, dragConvId = null;

function onFolderDragStart(e, folderId) { dragFolderId = folderId; e.target.classList.add('dragging'); e.dataTransfer.effectAllowed = 'move'; }
function onFolderDragEnd(e) { e.target.classList.remove('dragging'); document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over')); dragFolderId = null; }
function onFolderDragOver(e) { e.preventDefault(); e.dataTransfer.dropEffect = 'move'; e.target.closest('.folder-item')?.classList.add('drag-over'); }
function onFolderDragLeave(e) { e.target.closest('.folder-item')?.classList.remove('drag-over'); }
function onFolderDrop(e, targetFolderId) {
    e.preventDefault(); e.target.closest('.folder-item')?.classList.remove('drag-over');
    if (!dragFolderId || dragFolderId === targetFolderId) return;
    const fromIdx = state.folders.findIndex(f => f.id === dragFolderId);
    const toIdx = state.folders.findIndex(f => f.id === targetFolderId);
    if (fromIdx < 0 || toIdx < 0) return;
    const item = state.folders.splice(fromIdx, 1)[0];
    state.folders.splice(toIdx, 0, item);
    state.folders.forEach((f, i) => f.order = i);
    renderFolderList(); save();
}
function onDrawerConvDragStart(e, convId) { dragConvId = convId; e.target.classList.add('dragging'); e.dataTransfer.effectAllowed = 'move'; }
function onDragEnd(e) { e.target.classList.remove('dragging'); document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over')); dragConvId = null; }

document.addEventListener('dragover', function(e) {
    const folderEl = e.target.closest('.folder-item');
    if (folderEl && dragConvId) { e.preventDefault(); folderEl.classList.add('drag-over'); }
});
document.addEventListener('dragleave', function(e) {
    const folderEl = e.target.closest('.folder-item');
    if (folderEl && dragConvId) folderEl.classList.remove('drag-over');
});
document.addEventListener('drop', function(e) {
    const folderEl = e.target.closest('.folder-item');
    if (folderEl && dragConvId) { e.preventDefault(); folderEl.classList.remove('drag-over'); moveConvToFolder(dragConvId, folderEl.dataset.folderId); dragConvId = null; }
});

// ==================== 回退 ====================
function rollbackTo() {
    const conv = getCurrent();
    if (!conv || state.ctxMsgIdx < 0 || state.ctxMsgIdx >= conv.messages.length - 1) return;
    const msg = conv.messages[state.ctxMsgIdx];
    const who = msg.role === 'user' ? '我' : 'DeepSeek';
    const preview = (msg.content || '').replace(/\n/g, ' ').slice(0, 60);
    document.getElementById('rollbackHint').innerHTML = '将删除此消息之后的 <b>' + (conv.messages.length - state.ctxMsgIdx - 1) + '</b> 条消息，<br>对话回退到 <b>【' + who + '】</b>：<br><span style="color:var(--sub);font-size:12px">"' + escapeHtml(preview) + '"</span>';
    document.getElementById('rollbackModal').style.display = 'flex'; hideAllMenus();
}
function confirmRollback() {
    const conv = getCurrent();
    if (!conv || state.ctxMsgIdx < 0) return;
    conv.messages = conv.messages.slice(0, state.ctxMsgIdx + 1);
    closeRollbackModal(); renderAll(); save();
}
function closeRollbackModal() { document.getElementById('rollbackModal').style.display = 'none'; state.ctxMsgIdx = -1; }

// ==================== API Key ====================
async function submitApiKey() {
    const input = document.getElementById('apiKeyInput');
    const btn = document.querySelector('#apiKeyModal .btns button:last-child');
    const key = input.value.trim();
    const errEl = document.getElementById('apiKeyError');
    if (!key) { errEl.textContent = '请输入 API Key'; errEl.style.display = 'block'; return; }
    if (!key.startsWith('sk-')) { errEl.textContent = 'API Key 格式不正确'; errEl.style.display = 'block'; return; }
    errEl.style.display = 'none'; btn.textContent = '验证中...'; btn.disabled = true;
    try {
        const ok = await pywebview.api.setApiKey(key);
        if (ok) document.getElementById('apiKeyModal').style.display = 'none';
        else { errEl.textContent = 'API Key 无效'; errEl.style.display = 'block'; }
    } catch(e) { errEl.textContent = '验证失败: ' + e; errEl.style.display = 'block'; }
    finally { btn.textContent = '确认'; btn.disabled = false; }
}
function closeApiKeyModal() { document.getElementById('apiKeyModal').style.display = 'none'; }

// ==================== 确认模态框 ====================
let _confirmCallback = null;

function showConfirm(title, msg, btnText, callback) {
    document.getElementById('confirmTitle').textContent = title;
    document.getElementById('confirmMsg').textContent = msg;
    document.getElementById('confirmBtn').textContent = btnText || '确认';
    _confirmCallback = callback;
    document.getElementById('confirmModal').style.display = 'flex';
}

function confirmConfirm() {
    document.getElementById('confirmModal').style.display = 'none';
    if (_confirmCallback) { const cb = _confirmCallback; _confirmCallback = null; cb(); }
}

function closeConfirmModal() {
    document.getElementById('confirmModal').style.display = 'none';
    _confirmCallback = null;
}

// ==================== 辅助 ====================
function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
    if (e.key === 'Escape') { closeDrawer(); hideAllMenus(); }
}
function autoResize() { const ta = document.getElementById('input'); ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight, 140) + 'px'; }
function toggleThink() { const cb = document.getElementById('thinkToggle'); cb.checked = !cb.checked; onSettingsChange(); }
function onSettingsChange() { updateStatus(); }
function updateStatus() {
    const model = document.getElementById('modelSelect');
    document.getElementById('statusText').textContent = model.options[model.selectedIndex].text + (document.getElementById('thinkToggle').checked ? ' · 🧠 深度思考' : '');
}

document.addEventListener('click', (e) => { if (!e.target.closest('.context-menu')) hideAllMenus(); });

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
    if (pywebviewReady && pywebview.api) pywebview.api.setSidebarWidth(w);
});

// ==================== 主题切换 ====================
function setTheme(name) {
    document.body.dataset.theme = name || '';
    document.getElementById('themeSelect').value = name || 'sunset';
    if (pywebviewReady && pywebview.api) pywebview.api.setTheme(name || 'sunset');
}

// ==================== 启动 ====================
window.addEventListener('pywebviewready', () => init());
setTimeout(() => { if (!pywebviewReady) init(); }, 1500);
updateStatus();
</script>
</body>
</html>"""