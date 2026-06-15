// ==================== 窗口拖拽/缩放 + 键盘 (TypeScript) ====================
var _maximized = false;
var _dragInfo: { mx: number; my: number; wx: number; wy: number; nx?: number; ny?: number } | null = null;
var _winX = 0, _winY = 0, _winW = 800, _winH = 600;
var _movePending = false;

async function onMaximizeToggle(): Promise<void> {
  if (typeof pywebview === 'undefined' || !pywebview!.api) return;
  try {
    if (_maximized) { await pywebview!.api.restoreWindow(); }
    else { await pywebview!.api.maximizeWindow(); }
    _maximized = !_maximized;
    const btn = document.getElementById('btnMaximize');
    if (btn) { btn.textContent = _maximized ? '❐' : '□'; }
  } catch (e) {}
}

function _flushMove(): void {
  if (!_movePending) return;
  _movePending = false;
  if (_dragInfo && _dragInfo.nx !== undefined) {
    pywebview!.api.moveWindow(_dragInfo.nx, _dragInfo.ny!);
  } else if (typeof (_resizeGeo as any)?.nx !== 'undefined') {
    const g = _resizeGeo as any;
    if (g && g.nx !== undefined) {
      pywebview!.api.resizeWindow(g.nx, g.ny, g.nw, g.nh);
    }
  }
}

function setupWindowDrag(): void {
  const header = document.querySelector('.chat-header');
  if (!header) return;
  header.addEventListener('mousedown', (e) => {
    if (_maximized) return;
    if ((e.target as HTMLElement)?.closest('.win-btn')) return;
    if ((e.target as HTMLElement)?.closest('.status-prompt')) return;
    if ((e.target as HTMLElement)?.closest('button')) return;
    if ((e.target as HTMLElement)?.closest('input, textarea')) return;
    if ((e as MouseEvent).button !== 0) return;
    e.preventDefault();
    _dragInfo = { mx: (e as MouseEvent).screenX, my: (e as MouseEvent).screenY, wx: _winX, wy: _winY };
  });
  document.addEventListener('mousemove', (e) => {
    if (!_dragInfo) return;
    if (typeof pywebview === 'undefined' || !pywebview!.api) return;
    const nx = Math.round(_dragInfo.wx + ((e as MouseEvent).screenX - _dragInfo.mx));
    const ny = Math.round(_dragInfo.wy + ((e as MouseEvent).screenY - _dragInfo.my));
    if (nx === _winX && ny === _winY) return;
    _winX = nx; _winY = ny;
    _dragInfo.nx = nx; _dragInfo.ny = ny;
    if (!_movePending) { _movePending = true; requestAnimationFrame(_flushMove); }
  });
  document.addEventListener('mouseup', () => { _dragInfo = null; });
}

var _resizeDir: string | null = null;
var _resizeGeo: { x: number; y: number; w: number; h: number; nx?: number; ny?: number; nw?: number; nh?: number } | null = null;
var _resizeMouse: { mx: number; my: number } | null = null;
const MIN_W = 600, MIN_H = 400;

function onResizeStart(dir: string, e: MouseEvent): void {
  if (_maximized) return;
  e.preventDefault();
  _resizeDir = dir;
  _resizeMouse = { mx: e.screenX, my: e.screenY };
  _resizeGeo = { x: _winX, y: _winY, w: _winW, h: _winH };
}

document.addEventListener('mousemove', (e) => {
  if (!_resizeDir || !_resizeMouse || !_resizeGeo) return;
  if (typeof pywebview === 'undefined' || !pywebview!.api) return;
  const dx = (e as MouseEvent).screenX - _resizeMouse.mx;
  const dy = (e as MouseEvent).screenY - _resizeMouse.my;
  const g = _resizeGeo;
  let nx = g.x, ny = g.y, nw = g.w, nh = g.h;
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

document.addEventListener('mouseup', () => { _resizeDir = null; });

// Helper functions called from Alpine template
function onKeyDown(e: KeyboardEvent): void {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
}
function autoResize(e?: Event): void {
  const ta = e ? (e.target as HTMLElement) : document.getElementById('input');
  if (ta) { ta.style.height = 'auto'; ta.style.height = Math.min((ta as HTMLTextAreaElement).scrollHeight, 140) + 'px'; }
}

// 启动 Alpine 初始化
document.addEventListener('alpine:initialized', () => {
  ($store as any).app.init();
});
