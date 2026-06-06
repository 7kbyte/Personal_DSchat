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
                reasoning_effort: str = "high") -> Generator[Tuple[str, str], None, None]:
    """
    调用 DeepSeek Chat API（流式 SSE）。

    使用逐行读取 (readline)，每收到一行立即 yield，
    保证流式输出的平滑渲染节奏。

    Yields:
        (delta_content, delta_reasoning) — 每次 yield 一个增量片段
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
                    if content or reasoning:
                        yield content, reasoning
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
    except http.client.IncompleteRead:
        # 连接在 chunked 传输中意外中断，已接收的数据仍有效
        pass
    except urllib.error.HTTPError as e:
        raise _http_error(e)
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络错误: {e.reason}")


def verify_api_key(api_key: str) -> bool:
    """验证 API Key 是否有效（发送最小请求，仅消耗 1 token）"""
    if not api_key:
        return False
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
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        return False
    except Exception:
        return False


# ==================== 内部辅助 ====================

def _build_body(messages: list, model: str, thinking: bool,
                reasoning_effort: str, stream: bool) -> dict:
    body = {
        "model": model,
        "messages": messages,
        "stream": stream,
    }
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
