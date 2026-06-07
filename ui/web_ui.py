"""
DeepSeek Chat 桌面应用 —— 使用 pywebview + KaTeX + marked.js
"""

import sys
import webview

from config import WIN_WIDTH, WIN_HEIGHT, WIN_MIN_W, WIN_MIN_H, APP_VERSION
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
    webview.create_window(
        "DeepSeek Chat",
        html=PAGE.replace("{VERSION}", APP_VERSION),
        js_api=bridge,
        width=WIN_WIDTH,
        height=WIN_HEIGHT,
        min_size=(WIN_MIN_W, WIN_MIN_H),
    )
    webview.start()
