"""
Python <-> JavaScript bridge module
轻量桥接层 —— 委托给 services/ 中的各服务
"""
import json
import traceback
import webview

from services.storage_service import StorageService
from services.api_service import ApiService
from services.window_service import WindowService


class Bridge:
    """Python API exposed to JavaScript via pywebview"""

    def __init__(self):
        self.storage = StorageService()
        self.api = ApiService()
        self.win = WindowService()

    # ── API Key ─────────────────────────────────────────────
    def hasApiKey(self) -> bool:
        key = self.storage.get_api_key()
        if not key:
            return False
        return self.api.verify_key(key)

    def setApiKey(self, key: str) -> bool:
        key = key.strip()
        if not key or not key.startswith("sk-"):
            return False
        if not self.api.verify_key(key):
            return False
        self.storage.set_api_key(key)
        print("[Bridge] API Key verified and saved")
        return True

    # ── 侧栏宽度 / 主题 / 设置 ──────────────────────────────
    def getSidebarWidth(self) -> int:
        return self.storage.get_sidebar_width()

    def setSidebarWidth(self, width: int):
        self.storage.set_sidebar_width(int(width))

    def getTheme(self) -> str:
        return self.storage.get_theme()

    def setTheme(self, theme: str):
        self.storage.set_theme(theme)

    def loadSetting(self, key: str) -> str:
        return self.storage.get_setting(key)

    def saveSetting(self, key: str, value: str):
        self.storage.put_setting(key, value)

    def saveSettings(self, settings_json: str):
        try:
            data = json.loads(settings_json)
            self.storage.put_settings(data)
        except Exception:
            pass

    # ── 提示词 ──────────────────────────────────────────────
    def loadPrompts(self) -> str:
        return json.dumps(self.storage.get_prompts(), ensure_ascii=False)

    def savePrompts(self, prompts_json: str):
        try:
            data = json.loads(prompts_json)
            self.storage.put_prompts(data)
        except Exception:
            pass

    # ── 窗口几何保存 ────────────────────────────────────────
    def saveWindowSize(self, w: int, h: int):
        try:
            rect = json.loads(self.win.get_rect())
            self.storage.save_window_rect(rect["x"], rect["y"],
                                          int(w), int(h))
        except Exception:
            pass

    # ── 窗口控制 ────────────────────────────────────────────
    def minimizeWindow(self):
        self.win.minimize()

    def maximizeWindow(self):
        self.win.maximize()

    def restoreWindow(self):
        self.win.restore()

    def getWindowRect(self) -> str:
        return self.win.get_rect()

    def moveWindow(self, x: int, y: int):
        self.win.move(x, y)

    def closeWindow(self):
        self.win.close()

    def resizeWindow(self, x: int, y: int, w: int, h: int):
        self.win.resize(x, y, w, h)

    # ── 剪贴板 ──────────────────────────────────────────────
    def copyToClipboard(self, text: str):
        WindowService.copy_to_clipboard(text)

    # ── 对话状态 ────────────────────────────────────────────
    def loadState(self) -> str:
        return json.dumps(self.storage.get_state(), ensure_ascii=False)

    def saveState(self, convs_json: str, folders_json: str,
                  current_id: str):
        try:
            conversations = json.loads(convs_json)
            folders = json.loads(folders_json)
            self.storage.put_state(conversations, folders, current_id)
        except Exception as e:
            print(f"[Bridge] saveState failed: {e}")
            traceback.print_exc()

    # ── API 流式调用 ────────────────────────────────────────
    def sendMessage(self, params_json: str):
        try:
            data = json.loads(params_json)
        except Exception as e:
            print(f"[Bridge] sendMessage parse error: {e}")
            return

        def _on_chunk(content, reasoning):
            chunk = json.dumps({
                "type": "chunk",
                "content": content,
                "reasoning_content": reasoning,
            }, ensure_ascii=False)
            self._eval_js(f"window._onStreamChunk({chunk})")

        def _on_done(ok, error):
            result = json.dumps(
                {"type": "done", "ok": ok, "error": error},
                ensure_ascii=False,
            )
            self._eval_js(f"window._onStreamDone({result})")

        self.api.send_message(data, _on_chunk, _on_done)

    def stopGeneration(self):
        self.api.stop()

    # ── internal ────────────────────────────────────────────
    @staticmethod
    def _eval_js(code: str):
        try:
            if webview.windows:
                webview.windows[0].evaluate_js(code)
        except Exception as e:
            print(f"[Bridge] evaluate_js failed: {e}")
