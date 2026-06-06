"""
WebView 聊天界面 —— 使用 pywebview + KaTeX + marked.js
"""

import json
import sys
import threading
import traceback
import webview

from config import WIN_WIDTH, WIN_HEIGHT, WIN_MIN_W, WIN_MIN_H, load_api_key, save_api_key, APP_VERSION
from api.deepseek import chat_stream, verify_api_key
from storage.history import save as save_history, load as load_history


# ==================== Python API 桥接类 ====================

class Bridge:
    """暴露给 JS 的 Python API —— pywebview 要求 js_api 实例在 create_window 时传入"""

    def __init__(self):
        self.conversations, self.current_id = load_history()
        self._lock = threading.Lock()
        self._loading = False
        load_api_key()
        print(f"[Bridge] 已加载 {len(self.conversations)} 条历史对话，"
              f"API Key {'已设置' if load_api_key() else '未设置'}")

    # ---- API Key 管理 ----
    def hasApiKey(self) -> bool:
        """检查是否有可用的 API Key（从文件加载并验证）"""
        key = load_api_key()
        if not key:
            return False
        return verify_api_key(key)

    def setApiKey(self, key: str) -> bool:
        """设置 API Key（先验证再保存），返回是否成功"""
        key = key.strip()
        if not key or not key.startswith("sk-"):
            return False
        if not verify_api_key(key):
            return False
        save_api_key(key)
        print("[Bridge] API Key 验证通过，已保存")
        return True

    # ---- 历史管理 ----
    def loadState(self) -> str:
        data = json.dumps({
            "conversations": self.conversations,
            "currentId": self.current_id,
        }, ensure_ascii=False)
        return data

    def saveState(self, convs_json: str, current_id: str):
        try:
            self.conversations = json.loads(convs_json)
            self.current_id = current_id
            save_history(self.conversations, self.current_id)
            print(f"[Bridge] 已保存 {len(self.conversations)} 条对话")
        except Exception as e:
            print(f"[Bridge] 保存失败: {e}")
            traceback.print_exc()

    # ---- API 调用（异步） ----
    def sendMessage(self, params_json: str):
        """JS 调用：启动后台线程调用 API，通过 evaluate_js 回传结果"""
        with self._lock:
            if self._loading:
                return
            self._loading = True

        try:
            data = json.loads(params_json)
        except Exception as e:
            print(f"[Bridge] sendMessage 解析失败: {e}")
            with self._lock:
                self._loading = False
            return
        threading.Thread(target=self._do_send, args=(data,), daemon=True).start()

    def _do_send(self, data: dict):
        try:
            msgs = data["messages"]
            model = data["model"]
            thinking = data.get("thinking", True)
            effort = data.get("reasoning_effort", "high")
            print(f"[Bridge] 调用 API (stream): model={model}, thinking={thinking}, effort={effort}, msgs={len(msgs)}")

            for delta_content, delta_reasoning in chat_stream(msgs, model, thinking, effort):
                chunk = json.dumps({
                    "type": "chunk",
                    "content": delta_content,
                    "reasoning_content": delta_reasoning,
                }, ensure_ascii=False)
                self._eval_js(f"window._onStreamChunk({chunk})")

            # 流结束
            result = json.dumps({"type": "done", "ok": True}, ensure_ascii=False)
            self._eval_js(f"window._onStreamDone({result})")
            print(f"[Bridge] 流式响应完成")

        except Exception as e:
            print(f"[Bridge] API 错误: {e}")
            traceback.print_exc()
            result = json.dumps({"type": "done", "ok": False, "error": str(e)}, ensure_ascii=False)
            self._eval_js(f"window._onStreamDone({result})")
        finally:
            with self._lock:
                self._loading = False

    def _eval_js(self, code: str):
        """线程安全地执行 JS 代码"""
        try:
            if webview.windows:
                webview.windows[0].evaluate_js(code)
        except Exception as e:
            print(f"[Bridge] evaluate_js 失败: {e}")

    # ---- 剪贴板 ----
    def copyToClipboard(self, text: str):
        """复制文本到系统剪贴板（Windows 原生 API）"""
        try:
            import ctypes
            import ctypes.wintypes as wt

            # 分配全局内存 (Unicode)
            size = (len(text) + 1) * 2
            hmem = ctypes.windll.kernel32.GlobalAlloc(0x2000, size)
            ptr = ctypes.windll.kernel32.GlobalLock(hmem)
            ctypes.cdll.msvcrt.memcpy(ptr, text.encode("utf-16-le"), size - 2)
            ctypes.windll.kernel32.GlobalUnlock(hmem)

            # 设置剪贴板
            ctypes.windll.user32.OpenClipboard(0)
            ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.SetClipboardData(13, hmem)  # CF_UNICODETEXT
            ctypes.windll.user32.CloseClipboard()
        except Exception:
            pass


# ==================== HTML 页面 ====================


# ==================== HTML 页面 ====================

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
}
* { margin:0; padding:0; box-sizing:border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
    background: var(--bg); color: var(--text); height: 100vh; display: flex;
    overflow: hidden; font-size: 14px;
}

/* 侧边栏 */
.sidebar {
    width: 260px; background: var(--sidebar-bg); display: flex;
    flex-direction: column; border-right: 1px solid var(--border); flex-shrink: 0;
}
.sidebar-header { padding: 18px 16px 10px; }
.sidebar-header h1 { font-size: 16px; font-weight: 700; color: var(--text); }
.sidebar-header p { font-size: 11px; color: var(--sub); margin-top: 2px; }
.btn-new {
    margin: 6px 14px 10px; padding: 8px 14px; border: 1px solid var(--border);
    border-radius: 8px; background: #fff; color: var(--text); font-size: 13px;
    cursor: pointer; transition: .15s; text-align: center;
}
.btn-new:hover { background: #e8e8e8; }
.conv-list { flex:1; overflow-y:auto; padding: 4px 6px; }
.conv-item {
    padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 13px;
    color: var(--sub); margin: 2px 0; white-space: nowrap; overflow: hidden;
    text-overflow: ellipsis; transition: .1s;
}
.conv-item:hover { background: rgba(0,0,0,0.05); }
.conv-item.active { background: rgba(7,193,96,0.1); color: var(--accent); font-weight: 600; }
.conv-item.dragging { opacity: 0.4; }
.conv-item.drag-over { border-top: 2px solid var(--accent); }

.sidebar-settings { padding: 10px 14px 14px; border-top: 1px solid var(--border); }
.sidebar-settings label { font-size: 12px; color: var(--sub); display: block; margin-bottom: 4px; }
.sidebar-settings select, .sidebar-settings .think-row {
    width: 100%; padding: 6px 8px; border: 1px solid var(--border); border-radius: 6px;
    background: #fff; font-size: 12px; margin-bottom: 8px; outline: none;
}
.think-row { display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px; }
.think-row input { cursor: pointer; }
.sidebar-footer { padding: 8px 14px; font-size: 10px; color: #bbb; text-align: center; border-top:1px solid var(--border); }

/* 主区域 */
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

/* 思考过程折叠 */
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

/* 滚动条 */
::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#ccc; border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:#aaa; }

/* 删除确认 */
.modal-overlay {
    position:fixed; inset:0; background:rgba(0,0,0,0.3); z-index:1000;
    display:none; align-items:center; justify-content:center;
}
.modal {
    background:#fff; border-radius:12px; padding:24px; max-width:360px; width:90%;
    box-shadow:0 8px 32px rgba(0,0,0,0.18);
}
.modal h3 { margin-bottom:8px; }
.modal p { color:var(--sub); font-size:13px; margin-bottom:16px; }
.modal .btns { display:flex; gap:8px; justify-content:flex-end; }
.modal .btns button {
    padding:7px 18px; border-radius:6px; border:1px solid var(--border); cursor:pointer; font-size:13px;
}
.modal .btn-danger { background:#e74c3c; color:#fff; border-color:#e74c3c; }
</style>
</head>
<body>

<!-- 侧边栏 -->
<div class="sidebar">
    <div class="sidebar-header">
        <h1>💬 DeepSeek Chat</h1>
        <p>Powered by DeepSeek API</p>
    </div>
    <button class="btn-new" onclick="newConv()">＋ 新对话</button>
    <div class="conv-list" id="convList"></div>
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
</div>

<!-- 主区域 -->
<div class="main">
    <div class="chat-header">
        <span class="dot"></span>
        <span id="statusText">DeepSeek-V4 Flash · 🧠 深度思考</span>
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

<!-- 右键菜单 -->
<div class="context-menu" id="ctxMenu">
    <div class="item" onclick="copyMessage()">📋 复制此消息</div>
    <div class="item" onclick="copyAll()">📋 复制全部对话</div>
    <div style="height:1px;background:var(--border);margin:2px 8px"></div>
    <div class="item" id="rollbackItem" onclick="rollbackTo()">↩ 回退到此处</div>
</div>

<!-- 删除确认 -->
<div class="modal-overlay" id="deleteModal">
    <div class="modal">
        <h3>删除对话</h3>
        <p id="deleteTitle"></p>
        <div class="btns">
            <button onclick="closeDeleteModal()">取消</button>
            <button class="btn-danger" onclick="confirmDelete()">删除</button>
        </div>
    </div>
</div>

<!-- 回退确认 -->
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

<!-- API Key 设置 -->
<div class="modal-overlay" id="apiKeyModal">
    <div class="modal">
        <h3>🔑 设置 API Key</h3>
        <p>请输入你的 DeepSeek API Key：</p>
        <input type="password" id="apiKeyInput" placeholder="sk-..."
            style="width:100%;padding:8px 12px;border:1px solid var(--border);border-radius:6px;font-size:13px;margin:8px 0;outline:none;box-sizing:border-box">
        <p style="font-size:11px;color:var(--sub)">Key 将加密保存在本地，仅用于调用 DeepSeek API</p>
        <p id="apiKeyError" style="font-size:12px;color:#e74c3c;display:none"></p>
        <div class="btns" style="margin-top:8px">
            <button onclick="closeApiKeyModal()">取消</button>
            <button style="background:var(--accent);color:#fff;border-color:var(--accent)" onclick="submitApiKey()">确认</button>
        </div>
    </div>
</div>

<script>
// ==================== KaTeX + marked 配置 ====================
marked.setOptions({ breaks: true, gfm: true });

// 渲染 Markdown 为 HTML，并处理 LaTeX
function renderMarkdown(text) {
    // 保护 LaTeX 公式不被 marked 破坏（支持 \[ \] \( \) $$ $ 四种写法）
    const latexBlocks = [];
    let processed = text
        .replace(/\\\[([\s\S]*?)\\\]/g, (_, tex) => {
            latexBlocks.push({ type: 'block', tex: tex.trim() });
            return `\x00LATEX_BLOCK_${latexBlocks.length - 1}\x00`;
        })
        .replace(/\\\(([\s\S]*?)\\\)/g, (_, tex) => {
            latexBlocks.push({ type: 'inline', tex: tex.trim() });
            return `\x00LATEX_INLINE_${latexBlocks.length - 1}\x00`;
        })
        .replace(/\$\$([\s\S]*?)\$\$/g, (_, tex) => {
            latexBlocks.push({ type: 'block', tex: tex.trim() });
            return `\x00LATEX_BLOCK_${latexBlocks.length - 1}\x00`;
        })
        .replace(/\$([^$]+?)\$/g, (_, tex) => {
            latexBlocks.push({ type: 'inline', tex: tex.trim() });
            return `\x00LATEX_INLINE_${latexBlocks.length - 1}\x00`;
        });

    // 用 marked 渲染
    let html = marked.parse(processed);

    // 还原 LaTeX
    html = html.replace(/\x00LATEX_BLOCK_(\d+)\x00/g, (_, i) => {
        const lb = latexBlocks[parseInt(i)];
        try { return katex.renderToString(lb.tex, { displayMode: true, throwOnError: false }); }
        catch(e) { return `<code>${escapeHtml(lb.tex)}</code>`; }
    });
    html = html.replace(/\x00LATEX_INLINE_(\d+)\x00/g, (_, i) => {
        const lb = latexBlocks[parseInt(i)];
        try { return katex.renderToString(lb.tex, { displayMode: false, throwOnError: false }); }
        catch(e) { return `<code>${escapeHtml(lb.tex)}</code>`; }
    });

    return html;
}

function escapeHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
            .replace(/"/g,'&quot;').replace(/'/g,'&#039;');
}

// ==================== 状态 ====================
let state = { conversations: [], currentId: null, loading: false, ctxMsgIdx: -1, deleteIdx: -1 };
let pywebviewReady = false;

// ==================== 初始化 ====================
async function init() {
    try {
        if (window.pywebview && pywebview.api) {
            const raw = await pywebview.api.loadState();
            const data = JSON.parse(raw);
            state.conversations = data.conversations || [];
            state.currentId = data.currentId || null;
        }
    } catch(e) {
        console.error('[init] 加载历史失败:', e);
    }

    if (state.conversations.length === 0) {
        newConv();
    } else {
        const cur = state.conversations.find(c => c.id === state.currentId);
        if (!cur) state.currentId = state.conversations[0].id;
        renderAll();
    }
    pywebviewReady = true;
    console.log('[init] 初始化完成, 对话数:', state.conversations.length);

    // 检查 API Key
    try {
        if (window.pywebview && pywebview.api) {
            const hasKey = await pywebview.api.hasApiKey();
            if (!hasKey) {
                document.getElementById('apiKeyModal').style.display = 'flex';
                document.getElementById('apiKeyError').style.display = 'none';
            }
        }
    } catch(e) {
        console.error('[init] API Key 检查失败:', e);
    }
}

function save() {
    if (!pywebviewReady) return;
    pywebview.api.saveState(
        JSON.stringify(state.conversations),
        state.currentId
    );
}

// ==================== 对话管理 ====================
function newConv() {
    const cur = getCurrent();
    if (cur && (!cur.messages || cur.messages.length === 0)) {
        document.getElementById('input').focus();
        return;
    }
    const id = Date.now().toString() + Math.random().toString(36).slice(2,8);
    const conv = { id, title: '新对话', messages: [] };
    state.conversations.unshift(conv);
    state.currentId = id;
    renderAll();
    save();
}

function switchConv(id) {
    state.currentId = id;
    renderMessages();
    renderConvList();
}

function getCurrent() {
    return state.conversations.find(c => c.id === state.currentId);
}

// ==================== 渲染 ====================
function renderAll() {
    renderConvList();
    renderMessages();
}

function renderConvList() {
    const list = document.getElementById('convList');
    list.innerHTML = state.conversations.map((c, i) =>
        `<div class="conv-item${c.id === state.currentId ? ' active' : ''}"
             draggable="true"
             data-index="${i}"
             onclick="switchConv('${c.id}')"
             oncontextmenu="onConvCtx(event, '${c.id}')"
             ondragstart="onDragStart(event, ${i})"
             ondragend="onDragEnd(event)"
             ondragover="onDragOver(event)"
             ondragleave="onDragLeave(event)"
             ondrop="onDrop(event, ${i})">💬 ${escapeHtml(c.title || '新对话').slice(0, 30)}</div>`
    ).join('');
}

// ---- 拖拽排序 ----
let dragIdx = -1;

function onDragStart(e, idx) {
    dragIdx = idx;
    e.target.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
}

function onDragEnd(e) {
    e.target.classList.remove('dragging');
    document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
    dragIdx = -1;
}

function onDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    e.target.closest('.conv-item')?.classList.add('drag-over');
}

function onDragLeave(e) {
    e.target.closest('.conv-item')?.classList.remove('drag-over');
}

function onDrop(e, toIdx) {
    e.preventDefault();
    e.target.closest('.conv-item')?.classList.remove('drag-over');
    if (dragIdx < 0 || dragIdx === toIdx) return;

    // 移动数组元素
    const item = state.conversations.splice(dragIdx, 1)[0];
    state.conversations.splice(toIdx, 0, item);

    renderAll();
    save();
}

function renderMessages() {
    const container = document.getElementById('messages');
    const conv = getCurrent();

    if (!conv || !conv.messages || conv.messages.length === 0) {
        container.innerHTML = `<div class="empty">
            <div class="logo">🐱</div><h2>你好！我是 DeepSeek</h2><p>有什么可以帮你的吗？</p></div>`;
        return;
    }

    container.innerHTML = conv.messages.map((m, i) => {
        const isUser = m.role === 'user';
        const avatar = isUser ? '我' : 'DS';
        const html = renderMarkdown(m.content);
        let reasoningHTML = '';
        if (!isUser && m.reasoning_content) {
            const rid = 'reasoning_' + i;
            reasoningHTML = `
                <div class="reasoning-toggle" onclick="
                    var c=document.getElementById('${rid}');
                    var t=this;
                    c.classList.toggle('open');
                    t.textContent = c.classList.contains('open') ? '🧠 收起思考过程' : '🧠 查看思考过程';
                ">🧠 查看思考过程</div>
                <div class="reasoning-content" id="${rid}">${escapeHtml(m.reasoning_content)}</div>`;
        }
        return `<div class="msg ${m.role}" oncontextmenu="onMsgCtx(event, ${i})">
            <div class="avatar">${avatar}</div>
            <div class="bubble">${reasoningHTML}${html}</div>
        </div>`;
    }).join('');

    container.scrollTop = container.scrollHeight;
}

// ==================== 发送消息 ====================
async function send() {
    if (state.loading) return;

    const input = document.getElementById('input');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    autoResize();

    const conv = getCurrent();
    if (!conv) return;

    conv.messages.push({ role: 'user', content: text });
    if (conv.messages.length === 1) {
        conv.title = text.slice(0, 30) + (text.length > 30 ? '...' : '');
    }
    conv.messages.push({ role: 'assistant', content: '思考中...' });
    renderAll();
    save();

    state.loading = true;
    document.getElementById('btnSend').disabled = true;
    updateStatus();

    const model = document.getElementById('modelSelect').value;
    const thinking = document.getElementById('thinkToggle').checked;
    const effort = document.getElementById('effortSelect').value;

    pywebview.api.sendMessage(JSON.stringify({
        messages: conv.messages.filter(m => m.content !== '思考中...'),
        model: model,
        thinking: thinking,
        reasoning_effort: effort,
    }));
}

// API 回调 —— 流式增量更新
window._onStreamChunk = function(data) {
    const conv = getCurrent();
    if (!conv) return;
    const lastMsg = conv.messages[conv.messages.length - 1];
    if (!lastMsg || lastMsg.role !== 'assistant') return;

    // 第一个 chunk 时清空占位文本
    if (lastMsg.content === '思考中...') {
        lastMsg.content = '';
        lastMsg.reasoning_content = '';
    }

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
        if (lastMsg && lastMsg.role === 'assistant') {
            lastMsg.content = '❌ 错误: ' + (data.error || '未知错误');
            lastMsg.reasoning_content = '';
        }
    }

    renderAll();
    save();
};

// 只更新最后一条消息（流式渲染优化）
function updateLastMessage() {
    const container = document.getElementById('messages');
    const conv = getCurrent();
    if (!conv || !conv.messages || conv.messages.length === 0) return;

    const lastMsg = conv.messages[conv.messages.length - 1];
    const lastEl = container.querySelector('.msg:last-child .bubble');
    if (!lastEl) { renderMessages(); return; }

    const isUser = lastMsg.role === 'user';
    if (isUser) return;

    const html = renderMarkdown(lastMsg.content);
    let reasoningHTML = '';
    if (lastMsg.reasoning_content) {
        const rid = 'reasoning_' + (conv.messages.length - 1);
        reasoningHTML = `
            <div class="reasoning-toggle" onclick="
                var c=document.getElementById('${rid}');
                var t=this;
                c.classList.toggle('open');
                t.textContent = c.classList.contains('open') ? '🧠 收起思考过程' : '🧠 查看思考过程';
            ">🧠 查看思考过程</div>
            <div class="reasoning-content open" id="${rid}">${escapeHtml(lastMsg.reasoning_content)}</div>`;
    }
    lastEl.innerHTML = reasoningHTML + html;

    // 自动滚动到底部
    container.scrollTop = container.scrollHeight;
}

// ==================== 右键菜单 ====================
function onMsgCtx(e, idx) {
    e.preventDefault();
    state.ctxMsgIdx = idx;
    const conv = getCurrent();
    // 如果是最后一条消息，隐藏回退选项
    const isLast = conv && conv.messages && idx === conv.messages.length - 1;
    document.getElementById('rollbackItem').style.display = isLast ? 'none' : '';
    const menu = document.getElementById('ctxMenu');
    menu.style.display = 'block';
    menu.style.left = Math.min(e.clientX, window.innerWidth - 160) + 'px';
    menu.style.top = Math.min(e.clientY, window.innerHeight - 80) + 'px';
}

function onConvCtx(e, id) {
    e.preventDefault();
    state.deleteIdx = state.conversations.findIndex(c => c.id === id);
    const conv = state.conversations[state.deleteIdx];
    document.getElementById('deleteTitle').textContent =
        '确定要删除 "' + (conv ? conv.title : '') + '" 吗？此操作不可撤销。';
    document.getElementById('deleteModal').style.display = 'flex';
}

function copyMessage() {
    const conv = getCurrent();
    if (!conv || state.ctxMsgIdx < 0) return;
    const msg = conv.messages[state.ctxMsgIdx];
    if (msg) {
        let text = msg.content;
        if (msg.reasoning_content) {
            text = '【思考过程】\n' + msg.reasoning_content + '\n\n【回答】\n' + text;
        }
        pywebview.api.copyToClipboard(text);
    }
    hideCtxMenu();
}

function copyAll() {
    const conv = getCurrent();
    if (!conv) return;
    const text = conv.messages.map(m => {
        let t = '【' + (m.role==='user'?'我':'DeepSeek') + '】' + m.content;
        if (m.reasoning_content) {
            t = '【' + (m.role==='user'?'我':'DeepSeek') + ' · 思考过程】\n' + m.reasoning_content + '\n\n' + t;
        }
        return t;
    }).join('\n\n');
    pywebview.api.copyToClipboard(text);
    hideCtxMenu();
}

function hideCtxMenu() {
    document.getElementById('ctxMenu').style.display = 'none';
}

function confirmDelete() {
    if (state.deleteIdx >= 0 && state.deleteIdx < state.conversations.length) {
        state.conversations.splice(state.deleteIdx, 1);
        if (!state.conversations.find(c => c.id === state.currentId)) {
            if (state.conversations.length > 0) {
                state.currentId = state.conversations[0].id;
            } else {
                newConv();
                closeDeleteModal();
                return;
            }
        }
        renderAll();
        save();
    }
    closeDeleteModal();
}

function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
    state.deleteIdx = -1;
}

// ---- 回退功能 ----
function rollbackTo() {
    const conv = getCurrent();
    if (!conv || state.ctxMsgIdx < 0 || state.ctxMsgIdx >= conv.messages.length - 1) return;
    const msg = conv.messages[state.ctxMsgIdx];
    const who = msg.role === 'user' ? '我' : 'DeepSeek';
    const preview = (msg.content || '').replace(/\n/g, ' ').slice(0, 60);
    const remainCount = conv.messages.length - state.ctxMsgIdx - 1;
    document.getElementById('rollbackHint').innerHTML =
        '将删除此消息之后的 <b>' + remainCount + '</b> 条消息，<br>对话回退到 <b>【' + who + '】</b>：<br><span style="color:var(--sub);font-size:12px">"' + escapeHtml(preview) + '"</span>';
    document.getElementById('rollbackModal').style.display = 'flex';
    hideCtxMenu();
}

function confirmRollback() {
    const conv = getCurrent();
    if (!conv || state.ctxMsgIdx < 0) return;
    // 保留选中消息及之前的所有消息（包含当前消息）
    conv.messages = conv.messages.slice(0, state.ctxMsgIdx + 1);
    closeRollbackModal();
    renderAll();
    save();
}

function closeRollbackModal() {
    document.getElementById('rollbackModal').style.display = 'none';
    state.ctxMsgIdx = -1;
}

// ---- API Key 管理 ----
async function submitApiKey() {
    const input = document.getElementById('apiKeyInput');
    const btn = document.querySelector('#apiKeyModal .btns button:last-child');
    const key = input.value.trim();
    const errEl = document.getElementById('apiKeyError');

    if (!key) {
        errEl.textContent = '请输入 API Key';
        errEl.style.display = 'block';
        return;
    }
    if (!key.startsWith('sk-')) {
        errEl.textContent = 'API Key 格式不正确，应以 sk- 开头';
        errEl.style.display = 'block';
        return;
    }

    // 显示验证中状态
    errEl.style.display = 'none';
    btn.textContent = '验证中...';
    btn.disabled = true;

    try {
        const ok = await pywebview.api.setApiKey(key);
        if (ok) {
            document.getElementById('apiKeyModal').style.display = 'none';
        } else {
            errEl.textContent = 'API Key 无效，无法连接 DeepSeek API，请检查后重试';
            errEl.style.display = 'block';
        }
    } catch(e) {
        errEl.textContent = '验证失败: ' + e;
        errEl.style.display = 'block';
    } finally {
        btn.textContent = '确认';
        btn.disabled = false;
    }
}

function closeApiKeyModal() {
    document.getElementById('apiKeyModal').style.display = 'none';
}

// Enter 快捷提交
document.addEventListener('keydown', function(e) {
    const modal = document.getElementById('apiKeyModal');
    if (modal.style.display === 'flex' && e.key === 'Enter') {
        e.preventDefault();
        submitApiKey();
    }
});

document.addEventListener('click', (e) => {
    if (!e.target.closest('.context-menu')) hideCtxMenu();
});

// ==================== 辅助 ====================
function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        send();
    }
}

function autoResize() {
    const ta = document.getElementById('input');
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 140) + 'px';
}

function toggleThink() {
    const cb = document.getElementById('thinkToggle');
    cb.checked = !cb.checked;
    onSettingsChange();
}

function onSettingsChange() {
    updateStatus();
}

function updateStatus() {
    const model = document.getElementById('modelSelect');
    const name = model.options[model.selectedIndex].text;
    const thinking = document.getElementById('thinkToggle').checked;
    let txt = name;
    if (thinking) txt += ' · 🧠 深度思考';
    document.getElementById('statusText').textContent = txt;
}

// ==================== 启动 ====================
window.addEventListener('pywebviewready', () => {
    console.log('[event] pywebviewready 触发');
    init();
});
// 兜底：如果 pywebview 未加载（比如直接用浏览器打开），1 秒后强制初始化
setTimeout(() => {
    if (!pywebviewReady) {
        console.log('[fallback] pywebview 未就绪，强制初始化');
        init();
    }
}, 1500);
updateStatus();
</script>
</body>
</html>"""


# ==================== 启动函数 ====================

def run():
    """启动 WebView 窗口"""
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

    bridge = Bridge()
    webview.create_window(
        "DeepSeek Chat",
        html=PAGE.replace("{VERSION}", APP_VERSION),
        js_api=bridge,
        width=WIN_WIDTH,
        height=WIN_HEIGHT,
        min_size=(WIN_MIN_W, WIN_MIN_H),
    )
    webview.start()
