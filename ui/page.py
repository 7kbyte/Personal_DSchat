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
:root {
    --bg: #f5f5f5;
    --sidebar-bg: #f0f0f0;
    --user-bubble: #d9fdd3;
    --ai-bubble: #ffffff;
    --text: #1a1a1a;
    --sub: #667781;
    --border: #e0e0e0;
    --accent: #07c160;
    --accent-hover: #06ad56;
    --input-bg: #ffffff;
    --code-bg: #1e1e2e;
    --code-fg: #cdd6f4;
    --shadow: 0 1px 3px rgba(0,0,0,0.08);
    --danger: #e74c3c;
}
* { margin:0; padding:0; box-sizing:border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
    background: var(--bg); color: var(--text); height: 100vh; display: flex;
    overflow: hidden; font-size: 14px; position: relative;
}

/* ========== 侧边栏 ========== */
.sidebar {
    width: 260px; background: var(--sidebar-bg); display: flex;
    flex-direction: column; border-right: 1px solid var(--border); flex-shrink: 0; z-index: 10;
    position: relative;
}
.sidebar-header { padding: 18px 16px 10px; }
.sidebar-header h1 { font-size: 16px; font-weight: 700; color: var(--text); }
.sidebar-header p { font-size: 11px; color: var(--sub); margin-top: 2px; }
.btn-new {
    margin: 6px 14px 4px; padding: 8px 14px; border: 1px solid var(--border);
    border-radius: 8px; background: #fff; color: var(--text); font-size: 13px;
    cursor: pointer; transition: .15s; text-align: center;
}
.btn-new:hover { background: #e8e8e8; }

/* 文件夹列表 */
.folder-list { flex:1; overflow-y:auto; padding: 4px 6px; }
.folder-item {
    padding: 8px 10px; border-radius: 6px; cursor: pointer; font-size: 13px;
    color: var(--text); margin: 1px 0; display: flex; align-items: center;
    gap: 8px; transition: .1s; user-select: none;
}
.folder-item:hover { background: rgba(0,0,0,0.05); }
.folder-item.active { background: rgba(7,193,96,0.1); color: var(--accent); font-weight: 600; }
.folder-item .folder-icon { font-size: 16px; flex-shrink: 0; }
.folder-item .folder-name { flex:1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.folder-item .folder-count {
    font-size: 11px; color: var(--sub); background: rgba(0,0,0,0.06);
    padding: 1px 7px; border-radius: 10px; flex-shrink: 0;
}
.folder-item.drag-over { background: rgba(7,193,96,0.15); border: 1px dashed var(--accent); }
.folder-item.dragging { opacity: 0.4; }

.btn-new-folder {
    margin: 4px 6px 8px; padding: 6px 12px; border: 1px dashed var(--border);
    border-radius: 6px; background: transparent; color: var(--sub); font-size: 12px;
    cursor: pointer; transition: .15s; text-align: center;
}
.btn-new-folder:hover { background: rgba(0,0,0,0.03); color: var(--text); }

.sidebar-settings { padding: 10px 14px 14px; border-top: 1px solid var(--border); }
.sidebar-settings label { font-size: 12px; color: var(--sub); display: block; margin-bottom: 4px; }
.sidebar-settings select, .sidebar-settings .think-row {
    width: 100%; padding: 6px 8px; border: 1px solid var(--border); border-radius: 6px;
    background: #fff; font-size: 12px; margin-bottom: 8px; outline: none;
}
.think-row { display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px; }
.think-row input { cursor: pointer; }
.sidebar-footer { padding: 8px 14px; font-size: 10px; color: #bbb; text-align: center; border-top:1px solid var(--border); }

/* 侧栏拖拽调整宽度 */
.sidebar-resize-handle {
    position: absolute; right: -3px; top: 0; bottom: 0; width: 6px;
    cursor: col-resize; z-index: 20; background: transparent;
    transition: background .15s;
}
.sidebar-resize-handle:hover, .sidebar-resize-handle.active { background: rgba(7,193,96,0.3); }

/* ========== 抽屉面板 ========== */
.drawer-overlay {
    position: fixed; left: 260px; top: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.15); z-index: 50;
    display: none;
}
.drawer-panel {
    position: fixed; left: 260px; top: 0; bottom: 0; width: 300px;
    background: #fff; z-index: 51; display: none; flex-direction: column;
    box-shadow: 2px 0 16px rgba(0,0,0,0.1); border-right: 1px solid var(--border);
    transform: translateX(-20px); opacity: 0; transition: transform .2s, opacity .2s;
}
.drawer-panel.open { transform: translateX(0); opacity: 1; }
.drawer-header {
    display: flex; align-items: center; gap: 8px; padding: 14px 16px 10px;
    border-bottom: 1px solid var(--border); flex-shrink: 0;
}
.drawer-header .folder-title { flex:1; font-size: 15px; font-weight: 600; display:flex; align-items:center; gap:6px; }
.drawer-header .folder-title .count { font-size: 12px; color: var(--sub); font-weight: 400; }
.drawer-btn-close {
    width: 28px; height: 28px; border: none; background: none; font-size: 18px;
    cursor: pointer; color: var(--sub); border-radius: 6px; display: flex;
    align-items: center; justify-content: center; transition: .1s;
}
.drawer-btn-close:hover { background: rgba(0,0,0,0.06); color: var(--text); }

.drawer-search {
    padding: 8px 14px; border-bottom: 1px solid var(--border); flex-shrink: 0;
}
.drawer-search input {
    width: 100%; padding: 6px 10px; border: 1px solid var(--border); border-radius: 6px;
    font-size: 12px; outline: none; background: #f8f8f8;
}
.drawer-search input:focus { border-color: var(--accent); background: #fff; }

.drawer-conv-list { flex:1; overflow-y: auto; padding: 4px 6px; }
.drawer-conv-item {
    padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 13px;
    color: var(--sub); margin: 2px 0; white-space: nowrap; overflow: hidden;
    text-overflow: ellipsis; transition: .1s; display: flex; align-items: center; gap: 4px;
}
.drawer-conv-item:hover { background: rgba(0,0,0,0.04); }
.drawer-conv-item.active { background: rgba(7,193,96,0.08); color: var(--accent); font-weight: 600; }
.drawer-conv-item .pin-icon { font-size: 12px; flex-shrink: 0; }
.drawer-conv-item.dragging { opacity: 0.4; }

.drawer-empty { padding: 40px 20px; text-align: center; color: var(--sub); font-size: 13px; }

/* ========== 主区域 ========== */
.main { flex:1; display:flex; flex-direction:column; min-width:0; }
.chat-header {
    padding: 10px 20px; border-bottom: 1px solid var(--border);
    font-size: 12px; color: var(--sub); display: flex; align-items: center; gap: 8px; background:#fff;
}
.chat-header .dot { width:7px; height:7px; border-radius:50%; background: var(--accent); }
.messages { flex:1; overflow-y:auto; padding: 16px 20px; display:flex; flex-direction:column; gap:14px;
    user-select: text; -webkit-user-select: text; }

/* 消息气泡 */
.msg { display:flex; gap:10px; max-width:82%; animation: fadeIn .2s; }
@keyframes fadeIn { from{opacity:0;transform:translateY(6px);} to{opacity:1;transform:translateY(0);} }
.msg.user { align-self:flex-end; flex-direction:row-reverse; }
.msg.assistant { align-self:flex-start; }
.avatar {
    width:32px; height:32px; border-radius:50%; display:flex; align-items:center;
    justify-content:center; font-size:14px; flex-shrink:0; font-weight:600;
}
.msg.user .avatar { background: var(--accent); color: #fff; }
.msg.assistant .avatar { background: #e8e8e8; color: #555; }

.bubble {
    padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.65;
    word-break: break-word; box-shadow: var(--shadow);
    user-select: text; -webkit-user-select: text;
}
.msg.user .bubble { background: var(--user-bubble); border-bottom-right-radius: 4px; }
.msg.assistant .bubble { background: var(--ai-bubble); border-bottom-left-radius: 4px; }
.bubble p { margin: 4px 0; }
.bubble pre { background: var(--code-bg); color: var(--code-fg); border-radius: 8px;
    padding: 14px; overflow-x: auto; margin: 8px 0; font-size: 13px; line-height: 1.5;
    white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word; }
.bubble code { font-family: 'Cascadia Code','Fira Code',Consolas,monospace; font-size: 13px; }
.bubble :not(pre) > code { background: rgba(0,0,0,0.06); padding: 2px 5px; border-radius: 4px;
    font-size: 12px; }
.bubble ul, .bubble ol { margin: 6px 0; padding-left: 22px; }
.bubble li { margin: 2px 0; }
.bubble h1,.bubble h2,.bubble h3,.bubble h4 { margin: 10px 0 4px; }
.bubble h1 { font-size: 1.3em; } .bubble h2 { font-size: 1.15em; } .bubble h3 { font-size: 1.05em; }
.bubble blockquote { border-left: 3px solid var(--accent); margin: 6px 0; padding: 4px 12px;
    color: #666; background: rgba(0,0,0,0.02); border-radius: 0 4px 4px 0; }
.bubble table { border-collapse:collapse; margin:6px 0; width:100%; }
.bubble th,.bubble td { border:1px solid #ddd; padding:6px 10px; text-align:left; font-size:13px; }
.bubble th { background:#f7f7f7; font-weight:600; }
.bubble img { max-width:100%; border-radius:6px; }
.katex-display { overflow-x:auto; overflow-y:hidden; padding:4px 0; }

.reasoning-toggle {
    cursor: pointer; color: var(--accent); font-size: 12px; font-weight: 600;
    user-select: none; padding: 4px 0; display: inline-flex; align-items: center; gap: 4px;
}
.reasoning-content {
    margin-top: 6px; padding: 10px 14px; background: rgba(0,0,0,0.03);
    border-left: 3px solid var(--accent); border-radius: 0 6px 6px 0;
    font-size: 12px; color: #666; line-height: 1.6; display: none; max-height: 300px; overflow-y: auto;
}
.reasoning-content.open { display: block; }

/* 输入区 */
.input-area { padding: 12px 20px; border-top: 1px solid var(--border); background: #fff; }
.input-row { display:flex; gap:10px; align-items:flex-end; }
.input-row textarea {
    flex:1; border:1px solid var(--border); border-radius:12px; padding:10px 14px;
    font-size:14px; font-family:inherit; resize:none; outline:none; min-height:42px;
    max-height:140px; line-height:1.5; transition:border-color .2s;
}
.input-row textarea:focus { border-color: var(--accent); }
.btn-send {
    width:42px; height:42px; border-radius:10px; border:none; background: var(--accent);
    color:#fff; font-size:16px; cursor:pointer; transition:.15s; flex-shrink:0;
    display:flex; align-items:center; justify-content:center;
}
.btn-send:hover { background: var(--accent-hover); transform:scale(1.05); }
.btn-send:disabled { background:#ccc; cursor:not-allowed; transform:none; }

/* 空状态 */
.empty {
    flex:1; display:flex; flex-direction:column; align-items:center;
    justify-content:center; color: var(--sub); gap: 8px; padding: 40px;
}
.empty .logo { font-size: 48px; }
.empty h2 { font-size: 18px; color: var(--text); }
.empty p { font-size: 13px; }

/* 右键菜单 */
.context-menu {
    position:fixed; background:#fff; border-radius:8px; box-shadow:0 4px 16px rgba(0,0,0,0.15);
    padding:4px; z-index:999; display:none; min-width:140px;
}
.context-menu .item {
    padding:8px 14px; border-radius:6px; cursor:pointer; font-size:13px;
    transition:background .1s;
}
.context-menu .item:hover { background: rgba(7,193,96,0.08); }
.context-menu .item.danger { color: var(--danger); }
.context-menu .item.danger:hover { background: rgba(231,76,60,0.08); }

/* 模态框 */
.modal-overlay {
    position:fixed; inset:0; background:rgba(0,0,0,0.3); z-index:1000;
    display:none; align-items:center; justify-content:center;
}
.modal {
    background:#fff; border-radius:12px; padding:24px; max-width:400px; width:90%;
    box-shadow:0 8px 32px rgba(0,0,0,0.18);
}
.modal h3 { margin-bottom:8px; }
.modal p { color:var(--sub); font-size:13px; margin-bottom:16px; }
.modal .btns { display:flex; gap:8px; justify-content:flex-end; }
.modal .btns button {
    padding:7px 18px; border-radius:6px; border:1px solid var(--border); cursor:pointer; font-size:13px;
}
.modal .btn-danger { background:var(--danger); color:#fff; border-color:var(--danger); }
.modal input[type="text"], .modal input[type="password"] {
    width:100%; padding:8px 12px; border:1px solid var(--border); border-radius:6px;
    font-size:13px; margin:8px 0; outline:none; box-sizing:border-box;
}
.modal input:focus { border-color: var(--accent); }

/* 图标选择器 */
.icon-picker { display: flex; flex-wrap: wrap; gap: 4px; margin: 8px 0; }
.icon-picker span {
    width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;
    font-size: 18px; border-radius: 6px; cursor: pointer; transition: .1s;
    border: 2px solid transparent;
}
.icon-picker span:hover { background: rgba(0,0,0,0.06); }
.icon-picker span.sel { border-color: var(--accent); background: rgba(7,193,96,0.1); }

/* 滚动条 */
::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#ccc; border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:#aaa; }
</style>
</head>
<body>

<!-- ========== 侧边栏 ========== -->
<div class="sidebar">
    <div class="sidebar-header">
        <h1>💬 DeepSeek Chat</h1>
        <p>Powered by DeepSeek API</p>
    </div>
    <button class="btn-new" onclick="newConv()">＋ 新对话</button>
    <div class="folder-list" id="folderList"></div>
    <div class="btn-new-folder" onclick="showFolderModal()">📁 ＋ 新建收藏夹</div>
    <div class="sidebar-settings">
        <label>模型选择</label>
        <select id="modelSelect" onchange="onSettingsChange()">
            <option value="deepseek-v4-pro">DeepSeek-V4 Pro</option>
            <option value="deepseek-v4-flash">DeepSeek-V4 Flash</option>
        </select>
        <div class="think-row" onclick="toggleThink()">
            <input type="checkbox" id="thinkToggle" checked onchange="onSettingsChange()">
            <span>🧠 深度思考</span>
        </div>
        <label style="margin-top:8px">思考强度</label>
        <select id="effortSelect" onchange="onSettingsChange()">
            <option value="high">high（默认）</option>
            <option value="max">max（最强）</option>
        </select>
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
        <span id="statusText">DeepSeek-V4 Pro · 🧠 深度思考</span>
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
            <button style="background:var(--accent);color:#fff;border-color:var(--accent)" onclick="submitFolder()">确认</button>
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
            <button style="background:var(--accent);color:#fff;border-color:var(--accent)" onclick="submitApiKey()">确认</button>
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
        + escapeHtml(c.title || '新对话').slice(0, 30) + '</div>'
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
    const folderId = state.drawerOpen ? state.drawerFolderId : 'f_default';
    const id = Date.now().toString() + Math.random().toString(36).slice(2,8);
    state.conversations.unshift({ id, title: '新对话', messages: [], folderId, pinned: false });
    state.currentId = id;
    renderAll(); save();
}

function switchConv(id) {
    state.currentId = id;
    renderMessages(); renderFolderList();
    if (state.drawerOpen) renderDrawerConvs();
}

function getCurrent() { return state.conversations.find(c => c.id === state.currentId); }

function togglePin() {
    const conv = state.conversations.find(c => c.id === state.ctxConvId);
    if (conv) conv.pinned = !conv.pinned;
    renderDrawerConvs(); save(); hideAllMenus();
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
function renderAll() { renderFolderList(); renderMessages(); if (state.drawerOpen) renderDrawer(); }

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
        return '<div class="msg ' + m.role + '" oncontextmenu="onMsgCtx(event,' + i + ')"><div class="avatar">' + avatar + '</div><div class="bubble">' + r + html + '</div></div>';
    }).join('');
    container.scrollTop = container.scrollHeight;
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
    conv.messages.push({ role: 'user', content: text });
    if (conv.messages.length === 1) conv.title = text.slice(0, 30) + (text.length > 30 ? '...' : '');
    conv.messages.push({ role: 'assistant', content: '思考中...' });
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
    }
    renderAll(); save();
};

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

// ==================== 启动 ====================
window.addEventListener('pywebviewready', () => init());
setTimeout(() => { if (!pywebviewReady) init(); }, 1500);
updateStatus();
</script>
</body>
</html>"""