// ==================== 初始化 ====================
async function init() {
    if (pywebviewReady) return;

    const apiReady = function() { return typeof pywebview !== 'undefined' && pywebview.api; };

    // 1. 加载对话状态
    if (apiReady()) {
        try {
            const raw = await pywebview.api.loadState();
            const data = JSON.parse(raw);
            state.conversations = data.conversations || [];
            state.folders = data.folders || [];
            state.currentId = data.currentId || null;
        } catch(e) { console.error('[init] loadState:', e); }
    }

    if (state.folders.length === 0) {
        state.folders = [{ id: 'f_default', name: '\u{1F4C1} \u9ED8\u8BA4\u6536\u85CF\u5939', icon: '\u{1F4C1}', order: 0 }];
    }
    if (state.conversations.length === 0) {
        newConv();
    } else {
        const cur = state.conversations.find(c => c.id === state.currentId);
        if (!cur) state.currentId = state.conversations[0].id;
        renderAll();
    }

    // 2. API 未就绪则延迟重试
    if (!apiReady()) {
        setTimeout(function() { init(); }, 200);
        return;
    }

    pywebviewReady = true;

    // 侧栏宽度
    try { const w = await pywebview.api.getSidebarWidth(); if (w) setSidebarWidth(w); } catch(e) {}
    // 抽屉宽度
    try { const dw = await pywebview.api.loadSetting('drawer_width'); if (dw) setDrawerWidth(parseInt(dw)); } catch(e) {}

    // 主题
    try {
        const theme = await pywebview.api.getTheme();
        const valid = ['light','dark','sky','ocean','leaf','forest','rose','bloom','sunset','cosmos'];
        const name = valid.includes(theme) ? theme : 'light';
        document.body.dataset.theme = name;
        var dot = document.querySelector('.theme-dot[onclick*=\"' + name + '\"]');
        if (dot) dot.classList.add('active');
    } catch(e) {}

    // 设置栏折叠状态
    try { const v = await pywebview.api.loadSetting('settings_collapsed'); if (v === '1') document.getElementById('settingsCard').classList.add('collapsed'); } catch(e) {}

    // 模型设置
    try {
        const model = await pywebview.api.loadSetting('model');
        if (model) { var btn = document.querySelector('#modelSeg .seg-btn[data-val=\"' + model + '\"]'); if (btn) pickModel(btn); }
        const thinking = await pywebview.api.loadSetting('thinking');
        document.getElementById('thinkToggle').checked = (thinking === '1');
        const effort = await pywebview.api.loadSetting('effort');
        if (effort) { var ebtn = document.querySelector('#effortSeg .seg-btn[data-val=\"' + effort + '\"]'); if (ebtn) pickEffort(ebtn); }
        updateStatus();
    } catch(e) {}

    // API Key 检查
    try {
        const hasKey = await pywebview.api.hasApiKey();
        if (!hasKey) document.getElementById('apiKeyModal').style.display = 'flex';
    } catch(e) {}

    // 确保默认设置已写入磁盘
    if (typeof saveAllSettings === 'function') saveAllSettings();
}

// ---- 全局持久化 ----
function save() {
    if (typeof pywebview === 'undefined' || !pywebview.api) return;
    try { pywebview.api.saveState(JSON.stringify(state.conversations), JSON.stringify(state.folders), state.currentId); } catch(e) {}
}
