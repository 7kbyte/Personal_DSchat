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
