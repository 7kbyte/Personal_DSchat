"""
对话历史持久化模块
"""

import json
import os

from config import get_history_path


def save(conversations: list, current_id: str):
    """保存对话列表（跳过空对话）"""
    non_empty = [c for c in conversations if c.get("messages")]
    data = {"conversations": non_empty, "current_id": current_id}
    try:
        with open(get_history_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load() -> tuple:
    """返回 (conversations, current_id)"""
    path = get_history_path()
    if not os.path.exists(path):
        return [], None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("conversations", []), data.get("current_id")
    except Exception:
        return [], None
