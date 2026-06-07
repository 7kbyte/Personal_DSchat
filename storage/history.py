"""
对话历史持久化模块
"""

import json
import os
import time

from config import get_history_path, DEFAULT_FOLDER_NAME, DEFAULT_FOLDER_ID


def save(conversations: list, folders: list, current_id: str):
    """保存对话列表和文件夹列表（跳过空对话）"""
    non_empty = [c for c in conversations if c.get("messages")]
    data = {
        "conversations": non_empty,
        "folders": folders,
        "current_id": current_id,
    }
    try:
        with open(get_history_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load() -> tuple:
    """返回 (conversations, folders, current_id)，自动迁移旧数据"""
    path = get_history_path()
    if not os.path.exists(path):
        return [], _default_folders(), None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return [], _default_folders(), None

    conversations = data.get("conversations", [])
    folders = data.get("folders", [])
    current_id = data.get("current_id")

    # ---- 旧数据迁移 ----
    migrated = False

    # 无 folders 字段 → 创建默认文件夹
    if not folders:
        folders = _default_folders()
        migrated = True

    # 确保默认文件夹存在
    if not any(f["id"] == DEFAULT_FOLDER_ID for f in folders):
        folders.insert(0, _make_folder(DEFAULT_FOLDER_NAME, DEFAULT_FOLDER_ID))
        migrated = True

    # 对话缺少 folderId → 归入默认文件夹
    for c in conversations:
        if "folderId" not in c:
            c["folderId"] = DEFAULT_FOLDER_ID
            migrated = True
        if "pinned" not in c:
            c["pinned"] = False
            migrated = True

    if migrated:
        print("[history] 旧数据已自动迁移到文件夹结构")

    return conversations, folders, current_id


def _default_folders() -> list:
    return [_make_folder(DEFAULT_FOLDER_NAME, DEFAULT_FOLDER_ID)]


def _make_folder(name: str, fid: str = None, icon: str = "📁") -> dict:
    return {
        "id": fid or ("f_" + str(int(time.time() * 1000))),
        "name": name,
        "icon": icon,
        "order": 0,
    }
