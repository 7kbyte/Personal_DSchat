"""
Python <-> JavaScript bridge module
Exposes Python backend methods to pywebview JS API
"""

import json
import threading
import traceback
import webview

from config import load_api_key, save_api_key, load_sidebar_width, save_sidebar_width
from api.deepseek import chat_stream, verify_api_key
from storage.history import save as save_history, load as load_history


class Bridge:
    """Python API exposed to JavaScript via pywebview"""

    def __init__(self):
        self.conversations, self.folders, self.current_id = load_history()
        self._lock = threading.Lock()
        self._loading = False
        load_api_key()
        print(f"[Bridge] loaded {len(self.conversations)} conversations, "
              f"{len(self.folders)} folders, "
              f"API Key {'set' if load_api_key() else 'not set'}")

    # ---- API Key ----
    def hasApiKey(self) -> bool:
        key = load_api_key()
        if not key:
            return False
        return verify_api_key(key)

    def setApiKey(self, key: str) -> bool:
        key = key.strip()
        if not key or not key.startswith("sk-"):
            return False
        if not verify_api_key(key):
            return False
        save_api_key(key)
        print("[Bridge] API Key verified and saved")
        return True

    # ---- 侧栏宽度 ----
    def getSidebarWidth(self) -> int:
        return load_sidebar_width()

    def setSidebarWidth(self, width: int):
        save_sidebar_width(int(width))

    # ---- History ----
    def loadState(self) -> str:
        data = json.dumps({
            "conversations": self.conversations,
            "folders": self.folders,
            "currentId": self.current_id,
        }, ensure_ascii=False)
        return data

    def saveState(self, convs_json: str, folders_json: str, current_id: str):
        try:
            self.conversations = json.loads(convs_json)
            self.folders = json.loads(folders_json)
            self.current_id = current_id
            save_history(self.conversations, self.folders, self.current_id)
            print(f"[Bridge] saved {len(self.conversations)} conversations, "
                  f"{len(self.folders)} folders")
        except Exception as e:
            print(f"[Bridge] save failed: {e}")
            traceback.print_exc()

    # ---- API call (async) ----
    def sendMessage(self, params_json: str):
        with self._lock:
            if self._loading:
                return
            self._loading = True

        try:
            data = json.loads(params_json)
        except Exception as e:
            print(f"[Bridge] sendMessage parse error: {e}")
            with self._lock:
                self._loading = False
            return
        threading.Thread(target=self._do_send, args=(data,), daemon=True).start()

    def _do_send(self, data: dict):
        try:
            msgs = data["messages"]
            model = data["model"]
            thinking = data.get("thinking", True)
            effort = data.get("reasoning_effort", "high")
            print(f"[Bridge] API call (stream): model={model}, thinking={thinking}, msgs={len(msgs)}")

            for delta_content, delta_reasoning in chat_stream(msgs, model, thinking, effort):
                chunk = json.dumps({
                    "type": "chunk",
                    "content": delta_content,
                    "reasoning_content": delta_reasoning,
                }, ensure_ascii=False)
                self._eval_js(f"window._onStreamChunk({chunk})")

            result = json.dumps({"type": "done", "ok": True}, ensure_ascii=False)
            self._eval_js(f"window._onStreamDone({result})")
            print(f"[Bridge] stream complete")

        except Exception as e:
            print(f"[Bridge] API error: {e}")
            traceback.print_exc()
            result = json.dumps({"type": "done", "ok": False, "error": str(e)}, ensure_ascii=False)
            self._eval_js(f"window._onStreamDone({result})")
        finally:
            with self._lock:
                self._loading = False

    def _eval_js(self, code: str):
        try:
            if webview.windows:
                webview.windows[0].evaluate_js(code)
        except Exception as e:
            print(f"[Bridge] evaluate_js failed: {e}")

    # ---- Clipboard ----
    def copyToClipboard(self, text: str):
        try:
            import ctypes
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
