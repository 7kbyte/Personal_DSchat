// ==================== 窗口拖拽/缩放 + 键盘 ====================
// Alpine 负责所有业务逻辑初始化 ($store.app.init())
var _maximized = false;
var _dragInfo = null;
var _winX = 0, _winY = 0, _winW = 800, _winH = 600;
var _movePending = false;

async function onMaximizeToggle() {
    if (typeof pywebview === 'undefined' || !pywebview.api) return;
    try {
        if (_maximized) { await pywebview.api.restoreWindow(); }
        else { await pywebview.api.maximizeWindow(); }
        _maximized = !_maximized;
        var btn = document.getElementById('btnMaximize');
        if (btn) { btn.textContent = _maximized ? '\u2750' : '\u25A1'; }
    } catch(e) {}
}

function _flushMove() {
    if (!_movePending) return;
    _movePending = false;
    if (_dragInfo) {
        pywebview.api.moveWindow(_dragInfo.nx, _dragInfo.ny);
    } else if (typeof _resizeDir !== 'undefined' && _resizeDir) {
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

// Helper functions called from Alpine template
function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
}
function autoResize(e) {
    var ta = e ? e.target : document.getElementById('input');
    if (ta) { ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight, 140) + 'px'; }
}
function fmtTime(ts) {
    if (!ts) return '';
    var d = new Date(ts);
    return d.getHours().toString().padStart(2,'0') + ':' + d.getMinutes().toString().padStart(2,'0');
}

// 启动 Alpine 初始化（在 Alpine 就绪后）
document.addEventListener('alpine:initialized', function() {
    $store.app.init();
});
