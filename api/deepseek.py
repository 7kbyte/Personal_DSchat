"""
DeepSeek API 调用模块 — httpx 异步 HTTP 客户端
"""
import json
import ssl
from typing import AsyncGenerator
from urllib.parse import urlparse, urlunparse
from urllib.request import getproxies

import httpx

from config import load_api_key, DEEPSEEK_API_URL

# 使用系统证书存储（行为与浏览器一致，自动信任系统安装的 CA，如 Clash 自签证书）
_SSL_CONTEXT = ssl.create_default_context()


def _get_http_proxy() -> str | None:
    """获取 HTTP 代理地址，自动修复 Windows 上 scheme 错误。

    Windows 上 urllib 会把 HTTPS 代理返回为 ``https://127.0.0.1:7890``，
    但 Clash/V2Ray 等代理工具都是 HTTP 代理，不提供 TLS 端点。
    浏览器不会犯这个错误，因为它知道系统代理就是 HTTP 代理。
    """
    proxies = getproxies()
    # 优先取 https 代理（httpx 请求 api.deepseek.com 时走这个）
    for key in ("https", "http", "all"):
        url = proxies.get(key)
        if not url or "://" not in url:
            continue
        parsed = urlparse(url)
        if parsed.scheme in ("https", "ftp"):
            # 修复：把 https://127.0.0.1:7890 → http://127.0.0.1:7890
            fixed = urlunparse(("http", parsed.netloc, "", "", "", ""))
            print(f"[Proxy] 修复代理 scheme: {url} → {fixed}")
            return fixed
        return url
    return None


def _build_client(**kwargs) -> httpx.AsyncClient:
    """构建 httpx 客户端，行为模拟浏览器：
    - 自动跟随系统代理设置（Clash 开则走代理，关则直连）
    - 自动修复 Windows 上错误的 https:// 代理 scheme
    - 使用系统证书存储验证 TLS
    """
    kwargs.setdefault("verify", _SSL_CONTEXT)

    proxy_url = _get_http_proxy()
    if proxy_url:
        kwargs["proxy"] = proxy_url  # 显式指定，绕过 httpx 内置的错误检测

    return httpx.AsyncClient(**kwargs)


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

    async with _build_client(timeout=300) as client:
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
        async with _build_client(timeout=15) as client:
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
