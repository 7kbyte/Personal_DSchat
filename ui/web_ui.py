"""
DeepSeek Chat 桌面应用 —— 使用 pywebview + KaTeX + marked.js
"""

import sys
import webview

from config import WIN_WIDTH, WIN_HEIGHT, WIN_MIN_W, WIN_MIN_H, APP_VERSION, load_window_geometry, save_window_geometry
from ui.bridge import Bridge
from ui.page import PAGE


def run():
    """启动 WebView 窗口"""
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

    bridge = Bridge()
    geo = load_window_geometry()
    window = webview.create_window(
        "DeepSeek Chat",
        html=PAGE.replace("{VERSION}", APP_VERSION),
        js_api=bridge,
        width=geo.get("w", WIN_WIDTH),
        height=geo.get("h", WIN_HEIGHT),
        x=geo.get("x", None),
        y=geo.get("y", None),
        min_size=(WIN_MIN_W, WIN_MIN_H),
    )

    def on_closing():
        try:
            save_window_geometry(window.x, window.y, window.width, window.height)
        except Exception:
            pass

    window.events.closing += on_closing
    webview.start()
