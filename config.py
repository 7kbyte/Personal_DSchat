"""
全局配置 —— API Key、模型、窗口尺寸、存储路径
"""

import os
import sys

# ==================== API 配置 ====================
# API Key 从本地文件加载，首次启动时由用户输入
DEEPSEEK_API_KEY = ""
DEEPSEEK_API_URL  = "https://api.deepseek.com/chat/completions"

MODEL_OPTIONS = {
    "DeepSeek-V4 Pro":   "deepseek-v4-pro",
    "DeepSeek-V4 Flash": "deepseek-v4-flash",
}

# 思考强度（reasoning_effort）：high 默认，max 最强
REASONING_EFFORT_OPTIONS = ["high", "max"]

# ==================== 存储路径 ====================
def get_app_dir() -> str:
    """返回保存数据的固定目录（用户 AppData 下）"""
    base = os.environ.get("APPDATA", os.path.expanduser("~"))
    return os.path.join(base, "DeepSeekChat")

def get_history_path() -> str:
    d = get_app_dir()
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "chat_history.json")

def get_key_path() -> str:
    return os.path.join(get_app_dir(), "apikey.txt")

def load_api_key() -> str:
    """从本地文件加载 API Key，返回加载后的值（空字符串表示未设置）"""
    global DEEPSEEK_API_KEY
    path = get_key_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                DEEPSEEK_API_KEY = f.read().strip()
        except Exception:
            pass
    return DEEPSEEK_API_KEY

def save_api_key(key: str):
    """保存 API Key 到本地文件"""
    global DEEPSEEK_API_KEY
    DEEPSEEK_API_KEY = key.strip()
    d = get_app_dir()
    os.makedirs(d, exist_ok=True)
    with open(get_key_path(), "w", encoding="utf-8") as f:
        f.write(DEEPSEEK_API_KEY)

def get_assets_dir() -> str:
    """资源目录：开发时用 assets/，打包后用 exe 旁边的 assets/"""
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "assets")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ==================== 窗口尺寸 ====================
TITLE = "💬 DeepSeek Chat"
APP_VERSION = "v1.0"

WIN_WIDTH  = 980
WIN_HEIGHT = 660
WIN_MIN_W  = 720
WIN_MIN_H  = 460
