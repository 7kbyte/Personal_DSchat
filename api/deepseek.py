"""
DeepSeek API 调用模块
"""

import json
import http.client
import urllib.request
import urllib.error
from typing import Tuple, Generator

from config import load_api_key, DEEPSEEK_API_URL


def chat(messages: list, model: str, thinking: bool,
         reasoning_effort: str = "high") -> Tuple[str, str]:
    """
    调用 DeepSeek Chat API（非流式）。

    Returns:
        (content, reasoning_content) — 最终回答 + 思维链（无思考时为空字符串）
    """
    api_key = load_api_key()
    if not api_key:
        raise RuntimeError("请先设置 API Key")

    body = _build_body(messages, model, thinking, reasoning_effort, stream=False)

    req = _build_request(body, api_key)

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            msg = data["choices"][0]["message"]
            content = msg.get("content", "")
            reasoning = msg.get("reasoning_content", "")
            return content, reasoning
    except http.client.IncompleteRead:
        raise RuntimeError("连接中断：服务器响应不完整，请重试")
    except urllib.error.HTTPError as e:
        raise _http_error(e)
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络错误: {e.reason}")


def chat_stream(messages: list, model: str, thinking: bool,
                reasoning_effort: str = "high") -> Generator[Tuple[str, str, dict | None], None, None]:
    """
    调用 DeepSeek Chat API（流式 SSE）。

    Yields:
        (delta_content, delta_reasoning, usage) — usage 仅在最后一个 chunk 非 None
    """
    api_key = load_api_key()
    if not api_key:
        raise RuntimeError("请先设置 API Key")

    body = _build_body(messages, model, thinking, reasoning_effort, stream=True)
    req = _build_request(body, api_key)

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            for line in resp:
                line = line.decode("utf-8").strip()
                if not line or not line.startswith("data:"):
                    continue
                data_str = line[5:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "") or ""
                    reasoning = delta.get("reasoning_content", "") or ""
                    usage = chunk.get("usage", None)
                    if content or reasoning or usage:
                        yield content, reasoning, usage
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
    except http.client.IncompleteRead:
        # 连接在 chunked 传输中意外中断，已接收的数据仍有效
        pass
    except urllib.error.HTTPError as e:
        raise _http_error(e)
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络错误: {e.reason}")


def verify_api_key(api_key: str) -> tuple:
    """验证 API Key。返回 (ok: bool, error: str|None)
    error 可能为 'network'（网络不通）或 'auth'（Key 无效）"""
    if not api_key:
        return False, None
    body = {
        "model": "deepseek-v4-flash",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 1,
        "stream": False,
    }
    req = urllib.request.Request(
        DEEPSEEK_API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200, None
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return False, 'auth'
        return False, 'network'
    except Exception:
        return False, 'network'


# ==================== 内部辅助 ====================

def _build_body(messages: list, model: str, thinking: bool,
                reasoning_effort: str, stream: bool) -> dict:
    body = {
        "model": model,
        "messages": messages,
        "stream": stream,    }
    if not thinking:
        body["thinking"] = {"type": "disabled"}
    else:
        body["reasoning_effort"] = reasoning_effort
    return body


def _build_request(body: dict, api_key: str) -> urllib.request.Request:
    return urllib.request.Request(
        DEEPSEEK_API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )


def _http_error(e: urllib.error.HTTPError) -> RuntimeError:
    try:
        detail = json.loads(e.read().decode("utf-8"))
        msg = detail.get("error", {}).get("message", str(e))
    except Exception:
        msg = f"HTTP {e.code}"
    return RuntimeError(f"API 错误: {msg}")
