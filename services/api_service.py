"""
API service — DeepSeek API 流式调用与 Key 验证 (httpx async)
"""
import asyncio
import threading

from api.deepseek import chat_stream, verify_api_key
from config import load_api_key


class ApiService:
    """封装 DeepSeek API 的流式聊天与 Key 验证"""

    def __init__(self):
        self._lock = threading.Lock()
        self._loading = False
        self._stop_flag = False

    # ── Key 验证 ────────────────────────────────────────────
    def verify_key(self, key: str):
        """返回 (ok: bool, error: str|None)"""
        return asyncio.run(verify_api_key(key))

    def has_valid_key(self):
        """返回 (ok: bool, error: str|None)"""
        key = load_api_key()
        if not key:
            return False, None
        return asyncio.run(verify_api_key(key))

    # ── 流式聊天 ────────────────────────────────────────────
    def send_message(self, params: dict, on_chunk, on_done):
        """异步发起流式请求。on_chunk(content, reasoning), on_done(ok, error, usage)"""
        with self._lock:
            if self._loading:
                return False
            self._loading = True
            self._stop_flag = False

        async def _run():
            final_usage = None
            try:
                msgs = params["messages"]
                model = params["model"]
                thinking = params.get("thinking", True)
                effort = params.get("reasoning_effort", "high")
                print(f"[API] call: model={model}, thinking={thinking}, "
                      f"effort={effort}, msgs={len(msgs)}")

                async for delta_content, delta_reasoning, usage in chat_stream(
                        msgs, model, thinking, effort):
                    with self._lock:
                        if self._stop_flag:
                            break
                    on_chunk(delta_content, delta_reasoning)
                    if usage is not None:
                        final_usage = usage

                on_done(True, None, final_usage)
                print("[API] stream complete")

            except Exception as e:
                print(f"[API] error: {e}")
                import traceback
                traceback.print_exc()
                on_done(False, str(e))
            finally:
                with self._lock:
                    self._loading = False

        threading.Thread(target=lambda: asyncio.run(_run()), daemon=True).start()
        return True

    def stop(self):
        with self._lock:
            self._stop_flag = True
        print("[API] stop requested")

    @property
    def is_loading(self) -> bool:
        with self._lock:
            return self._loading
        with self._lock:
            return self._loading
