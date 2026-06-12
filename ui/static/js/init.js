// ==================== 初始化 ====================
var _maximized = false;
var _dragInfo = null;
var _winX = 0, _winY = 0, _winW = 800, _winH = 600;
var _movePending = false;

async function onMaximizeToggle() {
    if (typeof pywebview === 'undefined' || !pywebview.api) return;
    try {
        if (_maximized) {
            await pywebview.api.restoreWindow();
        } else {
            await pywebview.api.maximizeWindow();
        }
        _maximized = !_maximized;
        var btn = document.getElementById('btnMaximize');
        if (btn) { btn.textContent = _maximized ? '❐' : '□'; }
    } catch(e) {}
}

function _flushMove() {
    if (!_movePending) return;
    _movePending = false;
    if (_dragInfo) {
        pywebview.api.moveWindow(_dragInfo.nx, _dragInfo.ny);
    } else if (_resizeDir) {
        pywebview.api.resizeWindow(_resizeGeo.nx, _resizeGeo.ny, _resizeGeo.nw, _resizeGeo.nh);
    }
}

function setupWindowDrag() {
    var header = document.querySelector('.chat-header');
    if (!header) return;
    header.addEventListener('mousedown', function(e) {
        if (_maximized) return;
        if (e.target.closest('.win-btn')) return;
        if (e.target.closest('.status-prompt')) return;
        if (e.target.closest('button')) return;
        if (e.target.closest('input') || e.target.closest('textarea')) return;
        if (e.button !== 0) return;
        e.preventDefault();
        _dragInfo = { mx: e.screenX, my: e.screenY, wx: _winX, wy: _winY };
    });
    document.addEventListener('mousemove', function(e) {
        if (!_dragInfo) return;
        if (typeof pywebview === 'undefined' || !pywebview.api) return;
        var nx = Math.round(_dragInfo.wx + (e.screenX - _dragInfo.mx));
        var ny = Math.round(_dragInfo.wy + (e.screenY - _dragInfo.my));
        if (nx === _winX && ny === _winY) return;
        _winX = nx; _winY = ny;
        _dragInfo.nx = nx; _dragInfo.ny = ny;
        if (!_movePending) { _movePending = true; requestAnimationFrame(_flushMove); }
    });
    document.addEventListener('mouseup', function() { _dragInfo = null; });
}

// ==================== 窗口缩放 ====================
var _resizeDir = null, _resizeGeo = null, _resizeMouse = null;
var MIN_W = 600, MIN_H = 400;

function onResizeStart(dir, e) {
    if (_maximized) return;
    e.preventDefault();
    _resizeDir = dir;
    _resizeMouse = { mx: e.screenX, my: e.screenY };
    _resizeGeo = { x: _winX, y: _winY, w: _winW, h: _winH };
}

document.addEventListener('mousemove', function(e) {
    if (!_resizeDir) return;
    if (typeof pywebview === 'undefined' || !pywebview.api) return;
    var dx = e.screenX - _resizeMouse.mx;
    var dy = e.screenY - _resizeMouse.my;
    var g = _resizeGeo;
    var nx = g.x, ny = g.y, nw = g.w, nh = g.h;
    switch (_resizeDir) {
        case 'top':    ny = g.y + dy; nh = g.h - dy; break;
        case 'bottom': nh = g.h + dy; break;
        case 'left':   nx = g.x + dx; nw = g.w - dx; break;
        case 'right':  nw = g.w + dx; break;
        case 'tl':     nx = g.x + dx; ny = g.y + dy; nw = g.w - dx; nh = g.h - dy; break;
        case 'tr':     ny = g.y + dy; nw = g.w + dx; nh = g.h - dy; break;
        case 'bl':     nx = g.x + dx; nw = g.w - dx; nh = g.h + dy; break;
        case 'br':     nw = g.w + dx; nh = g.h + dy; break;
    }
    if (nw < MIN_W) { if (_resizeDir.indexOf('l') >= 0) nx = g.x + g.w - MIN_W; nw = MIN_W; }
    if (nh < MIN_H) { if (_resizeDir.indexOf('t') >= 0) ny = g.y + g.h - MIN_H; nh = MIN_H; }
    nx = Math.round(nx); ny = Math.round(ny); nw = Math.round(nw); nh = Math.round(nh);
    _winX = nx; _winY = ny; _winW = nw; _winH = nh;
    _resizeGeo.nx = nx; _resizeGeo.ny = ny; _resizeGeo.nw = nw; _resizeGeo.nh = nh;
    if (!_movePending) { _movePending = true; requestAnimationFrame(_flushMove); }
});

document.addEventListener('mouseup', function() { _resizeDir = null; });

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
    // 初始化窗口位置缓存
    if (apiReady()) {
        try {
            var r = JSON.parse(await pywebview.api.getWindowRect());
            _winX = r.x; _winY = r.y; _winW = r.w; _winH = r.h;
        } catch(e) {}
    }
    setupWindowDrag();

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

    // 加载提示词
    try {
        const promptsRaw = await pywebview.api.loadPrompts();
        if (promptsRaw) state.prompts = JSON.parse(promptsRaw);
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
