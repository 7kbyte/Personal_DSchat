"""
Storage service — 对话历史、提示词、配置、API Key 的持久化读写
"""
import json
import os

from config import (
    load_prompts, save_prompts,
    load_api_key, save_api_key,
    load_sidebar_width, save_sidebar_width,
    load_theme, save_theme,
    load_setting, save_setting, save_settings,
    save_window_geometry,
)
from storage.history import load as load_history, save as save_history


class StorageService:
    """统一存储层，管理所有持久化数据"""

    def __init__(self):
        self.conversations, self.folders, self.current_id = load_history()
        load_api_key()  # 确保 API Key 已加载到全局变量
        self._log("loaded", f"{len(self.conversations)} conversations, "
                  f"{len(self.folders)} folders, "
                  f"API Key {'set' if load_api_key() else 'not set'}")

    # ── API Key ─────────────────────────────────────────────
    def has_api_key(self) -> bool:
        key = load_api_key()
        return bool(key)

    def get_api_key(self) -> str:
        return load_api_key() or ""

    def set_api_key(self, key: str) -> None:
        save_api_key(key)

    # ── 侧栏宽度 ────────────────────────────────────────────
    def get_sidebar_width(self) -> int:
        return load_sidebar_width()

    def set_sidebar_width(self, width: int) -> None:
        save_sidebar_width(int(width))

    # ── 主题 ────────────────────────────────────────────────
    def get_theme(self) -> str:
        return load_theme()

    def set_theme(self, theme: str) -> None:
        save_theme(theme)

    # ── 通用设置 ────────────────────────────────────────────
    def get_setting(self, key: str) -> str:
        return load_setting(key, "")

    def put_setting(self, key: str, value: str) -> None:
        save_setting(key, value)

    def put_settings(self, data: dict) -> None:
        save_settings(data)

    # ── 提示词 ──────────────────────────────────────────────
    def get_prompts(self) -> list:
        return load_prompts()

    def put_prompts(self, prompts: list) -> None:
        save_prompts(prompts)

    # ── 窗口几何 ────────────────────────────────────────────
    def save_window_rect(self, x: int, y: int, w: int, h: int) -> None:
        save_window_geometry(x, y, w, h)

    # ── 对话状态 ────────────────────────────────────────────
    def get_state(self) -> dict:
        return {
            "conversations": self.conversations,
            "folders": self.folders,
            "currentId": self.current_id,
        }

    def put_state(self, conversations: list, folders: list,
                  current_id: str) -> None:
        self.conversations = conversations
        self.folders = folders
        self.current_id = current_id
        save_history(conversations, folders, current_id)
        self._log("saved", f"{len(conversations)} conversations, "
                  f"{len(folders)} folders")

    # ── helpers ─────────────────────────────────────────────
    @staticmethod
    def _log(action: str, detail: str) -> None:
        print(f"[Storage] {action}: {detail}")
