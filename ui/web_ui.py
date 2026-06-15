"""
DeepSeek Chat 桌面应用 —— 使用 pywebview + KaTeX + marked.js
"""

import os
import sys
import webview

_STATIC = os.path.join(os.path.dirname(__file__), 'static')

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

    # 写入 HTML 到 static 目录以支持 vendor/ 相对路径
    html_path = os.path.join(_STATIC, 'index_generated.html')
    with open(html_path, 'w', encoding='utf-8') as _f:
        _f.write(PAGE.replace("{VERSION}", APP_VERSION))

    window = webview.create_window(
        "DeepSeek Chat",
        url='file:///' + html_path.replace('\\', '/'),
        js_api=bridge,
        width=geo.get("w", WIN_WIDTH),
        height=geo.get("h", WIN_HEIGHT),
        x=geo.get("x", None),
        y=geo.get("y", None),
        min_size=(WIN_MIN_W, WIN_MIN_H),
        frameless=True,
        easy_drag=False,
    )

    def on_closing():
        try:
            save_window_geometry(window.x, window.y, window.width, window.height)
        except Exception:
            pass

    window.events.closing += on_closing
    webview.start()
