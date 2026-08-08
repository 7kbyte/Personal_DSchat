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
        """写入 UTF-16 文本到系统剪贴板（CF_UNICODETEXT）。

        注意：必须显式声明 Win32 函数的 argtypes/restype，
        否则 64 位句柄/指针会被 ctypes 截断为 32 位，
        导致 GlobalLock 返回无效指针、memcpy 访问冲突、剪贴板为空。
        """
        try:
            if not text:
                return False

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            user32 = ctypes.WinDLL("user32", use_last_error=True)
            msvcrt = ctypes.WinDLL("msvcrt")

            kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
            kernel32.GlobalAlloc.restype = ctypes.c_void_p
            kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
            kernel32.GlobalLock.restype = ctypes.c_void_p
            kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
            kernel32.GlobalUnlock.restype = ctypes.c_int
            msvcrt.memcpy.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
            msvcrt.memcpy.restype = ctypes.c_void_p
            user32.OpenClipboard.argtypes = [ctypes.c_void_p]
            user32.OpenClipboard.restype = ctypes.c_int
            user32.EmptyClipboard.argtypes = []
            user32.EmptyClipboard.restype = ctypes.c_int
            user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
            user32.SetClipboardData.restype = ctypes.c_void_p
            user32.CloseClipboard.argtypes = []
            user32.CloseClipboard.restype = ctypes.c_int

            # GMEM_MOVEABLE | GMEM_ZEROINIT，末尾补 UTF-16 空终止符
            data = text.encode("utf-16-le") + b"\x00\x00"
            hmem = kernel32.GlobalAlloc(0x0042, len(data))
            if not hmem:
                return False

            ptr = kernel32.GlobalLock(hmem)
            if not ptr:
                kernel32.GlobalFree(hmem)
                return False
            msvcrt.memcpy(ptr, data, len(data))
            kernel32.GlobalUnlock(hmem)

            if not user32.OpenClipboard(0):
                return False
            user32.EmptyClipboard()
            res = user32.SetClipboardData(13, hmem)  # 13 = CF_UNICODETEXT
            user32.CloseClipboard()
            return bool(res)
        except Exception:
            return False
