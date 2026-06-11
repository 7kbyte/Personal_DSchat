// ==================== 辅助 ====================
function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
    if (e.key === 'Escape') { closeDrawer(); hideAllMenus(); }
}
function autoResize() { const ta = document.getElementById('input'); ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight, 140) + 'px'; }
function toggleThink() { const cb = document.getElementById('thinkToggle'); cb.checked = !cb.checked; onSettingsChange(); saveAllSettings(); }
function toggleSettings() {
    var card = document.getElementById('settingsCard');
    card.classList.toggle('collapsed');
    saveAllSettings();
}
function pickModel(btn) {
    document.querySelectorAll('#modelSeg .seg-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    onSettingsChange();
    saveAllSettings();
}
function pickEffort(btn) {
    document.querySelectorAll('#effortSeg .seg-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    onSettingsChange();
    saveAllSettings();
}
function getModel() { return document.querySelector('#modelSeg .seg-btn.active').dataset.val; }
function getEffort() { return document.querySelector('#effortSeg .seg-btn.active').dataset.val; }

// 统一保存所有设置（一次原子写入）
function saveAllSettings() {
    if (typeof pywebview === 'undefined' || !pywebview.api) return;
    try {
        var data = {
            model: getModel(),
            thinking: document.getElementById('thinkToggle').checked ? '1' : '0',
            effort: getEffort(),
            settings_collapsed: document.getElementById('settingsCard').classList.contains('collapsed') ? '1' : '0'
        };
        pywebview.api.saveSettings(JSON.stringify(data));
    } catch(e) {}
}

function onSettingsChange() { updateStatus(); }
function updateStatus() {
    var activeBtn = document.querySelector('#modelSeg .seg-btn.active');
    var modelName = activeBtn ? activeBtn.textContent : 'V4 Pro';
    var thinking = document.getElementById('thinkToggle').checked;
    document.getElementById('statusModel').textContent = modelName + (thinking ? ' · 🧠' : '');
    
    var conv = getCurrent();
    var promptEl = document.getElementById('statusPrompt');
    if (conv && conv.promptName) {
        promptEl.textContent = '💬 ' + conv.promptName;
        promptEl.style.display = '';
    } else {
        promptEl.textContent = '';
        promptEl.style.display = 'none';
    }
    
    var metaEl = document.getElementById('statusMeta');
    if (conv && conv.updatedAt) {
        metaEl.textContent = fmtDate(conv.updatedAt);
    } else {
        metaEl.textContent = '';
    }
}

function viewCurrentPrompt() {
    var conv = getCurrent();
    if (!conv || conv.messages.length === 0 || conv.messages[0].role !== 'system') return;
    var content = conv.messages[0].content;
    document.getElementById('viewPromptContent').textContent = content;
    document.getElementById('viewPromptModal').style.display = 'flex';
}
function closeViewPrompt() {
    document.getElementById('viewPromptModal').style.display = 'none';
}

function fmtDate(ts) {
    if (!ts) return '';
    var d = new Date(ts);
    return (d.getMonth()+1) + '/' + d.getDate() + ' ' + 
           String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0');
}

document.addEventListener('click', (e) => { if (!e.target.closest('.context-menu')) hideAllMenus(); });

// ==================== 主题切换 ====================
function setTheme(name) {
    document.body.dataset.theme = name || 'light';
    document.querySelectorAll('.theme-dot').forEach(d => d.classList.remove('active'));
    var dot = document.querySelector('.theme-dot[onclick*=\"' + name + '\"]');
    if (dot) dot.classList.add('active');
    if (typeof pywebview !== 'undefined' && pywebview.api) {
        try { pywebview.api.setTheme(name || 'light'); } catch(e) {}
    }
}
