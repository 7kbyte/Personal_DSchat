"""
DeepSeek API 调用模块 — httpx 异步 HTTP 客户端
"""
import json
from typing import AsyncGenerator

import httpx

from config import load_api_key, DEEPSEEK_API_URL


async def chat_stream(
    messages: list,
    model: str,
    thinking: bool,
    reasoning_effort: str = "high",
) -> AsyncGenerator[tuple, None]:
    """
    流式 SSE。Yields: (delta_content, delta_reasoning, usage)
    """
    api_key = load_api_key()
    if not api_key:
        raise RuntimeError("请先设置 API Key")

    body = _build_body(messages, model, thinking, reasoning_effort, stream=True)
    headers = _headers(api_key)

    async with httpx.AsyncClient(timeout=300) as client:
        async with client.stream("POST", DEEPSEEK_API_URL, json=body,
                                  headers=headers) as resp:
            if resp.status_code != 200:
                raise RuntimeError(f"API error: {resp.status_code}")
            async for line in resp.aiter_lines():
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


async def verify_api_key(api_key: str) -> tuple:
    """验证 API Key。返回 (ok: bool, error: str|None)"""
    if not api_key:
        return False, None
    body = {
        "model": "deepseek-v4-flash",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 1,
        "stream": False,
    }
    headers = _headers(api_key)
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(DEEPSEEK_API_URL, json=body, headers=headers)
            return resp.status_code == 200, None
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (401, 403):
            return False, 'auth'
        return False, 'network'
    except Exception:
        return False, 'network'


def _headers(api_key: str) -> dict:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }


def _build_body(messages: list, model: str, thinking: bool,
                reasoning_effort: str, stream: bool) -> dict:
    body = {"model": model, "messages": messages, "stream": stream}
    if not thinking:
        body["thinking"] = {"type": "disabled"}
    else:
        body["reasoning_effort"] = reasoning_effort
    return body
