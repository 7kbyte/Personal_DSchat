"""
Window service — 无边框窗口的移动、缩放、最大化/还原/最小化/关闭
"""
import ctypes
import json

import webview


class WindowService:
    """封装所有 Win32 窗口操作，统一处理 DPI 缩放"""

    _TITLE = "DeepSeek Chat"

    def __init__(self):
        self._restore_geo = None  # (x, y, w, h) in pywebview coords

    # ── helpers ─────────────────────────────────────────────
    @staticmethod
    def _hwnd():
        return ctypes.windll.user32.FindWindowW(None, WindowService._TITLE)

    def _dpi_scale(self):
        """返回物理像素 / pywebview 逻辑像素的比值"""
        if not webview.windows:
            return 1.0
        win = webview.windows[0]
        hwnd = self._hwnd()
        if not hwnd:
            return 1.0
        r = (ctypes.c_long * 4)()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(r))
        return (r[2] - r[0]) / max(win.width, 1)

    # ── 窗口控制 ────────────────────────────────────────────
    def minimize(self):
        if webview.windows:
            webview.windows[0].minimize()

    def maximize(self):
        """任务栏感知最大化"""
        if not webview.windows:
            return
        win = webview.windows[0]
        hwnd = self._hwnd()
        if not hwnd:
            return

        scale = self._dpi_scale()
        self._restore_geo = (win.x, win.y, win.width, win.height)

        wa = (ctypes.c_long * 4)()
        ctypes.windll.user32.SystemParametersInfoW(0x0030, 0,
                                                    ctypes.byref(wa), 0)
        win.move(int(wa[0] / scale), int(wa[1] / scale))
        win.resize(int((wa[2] - wa[0]) / scale),
                   int((wa[3] - wa[1]) / scale))

    def restore(self):
        if webview.windows and self._restore_geo:
            x, y, w, h = self._restore_geo
            webview.windows[0].move(x, y)
            webview.windows[0].resize(w, h)
            self._restore_geo = None

    def close(self):
        if webview.windows:
            webview.windows[0].destroy()

    # ── 移动 / 缩放 ─────────────────────────────────────────
    def move(self, x: int, y: int):
        if webview.windows:
            webview.windows[0].move(int(x), int(y))

    def resize(self, x: int, y: int, w: int, h: int):
        if webview.windows:
            win = webview.windows[0]
            win.move(int(x), int(y))
            win.resize(int(w), int(h))

    def get_rect(self) -> str:
        try:
            if webview.windows:
                win = webview.windows[0]
                return json.dumps(
                    {"x": win.x, "y": win.y, "w": win.width, "h": win.height})
        except Exception:
            pass
        return '{"x":0,"y":0,"w":800,"h":600}'

    # ── 剪贴板 ──────────────────────────────────────────────
    @staticmethod
    def copy_to_clipboard(text: str):
        try:
            size = (len(text) + 1) * 2
            hmem = ctypes.windll.kernel32.GlobalAlloc(0x2000, size)
            ptr = ctypes.windll.kernel32.GlobalLock(hmem)
            ctypes.cdll.msvcrt.memcpy(ptr, text.encode("utf-16-le"), size - 2)
            ctypes.windll.kernel32.GlobalUnlock(hmem)
            ctypes.windll.user32.OpenClipboard(0)
            ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.SetClipboardData(13, hmem)
            ctypes.windll.user32.CloseClipboard()
        except Exception:
            pass
