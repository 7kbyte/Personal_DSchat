"""
全局配置 —— API Key、模型、窗口尺寸、存储路径
"""

import os
import sys

# ==================== API 配置 ====================
DEEPSEEK_API_KEY = ""
DEEPSEEK_API_URL  = "https://api.deepseek.com/chat/completions"

MODEL_OPTIONS = {
    "DeepSeek-V4 Pro":   "deepseek-v4-pro",
    "DeepSeek-V4 Flash": "deepseek-v4-flash",
}

REASONING_EFFORT_OPTIONS = ["high", "max"]

DEFAULT_FOLDER_NAME = "默认收藏夹"
DEFAULT_FOLDER_ID = "f_default"

# ==================== 存储路径 ====================
def get_app_dir() -> str:
    base = os.environ.get("APPDATA", os.path.expanduser("~"))
    return os.path.join(base, "DeepSeekChat")

def get_history_path() -> str:
    d = get_app_dir()
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "chat_history.json")

def get_key_path() -> str:
    return os.path.join(get_app_dir(), "apikey.txt")

def load_api_key() -> str:
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
    global DEEPSEEK_API_KEY
    DEEPSEEK_API_KEY = key.strip()
    d = get_app_dir()
    os.makedirs(d, exist_ok=True)
    with open(get_key_path(), "w", encoding="utf-8") as f:
        f.write(DEEPSEEK_API_KEY)

# ==================== .conf 配置文件读写 ====================
CONFIG_FILENAME = "config.conf"

def _conf_path() -> str:
    return os.path.join(get_app_dir(), CONFIG_FILENAME)

def _read_conf() -> dict:
    """读取 config.conf，返回键值对字典。首次运行时自动迁移旧 config.json"""
    path = _conf_path()
    # 迁移旧 JSON 配置
    old_path = os.path.join(get_app_dir(), "config.json")
    if os.path.exists(old_path) and not os.path.exists(path):
        try:
            import json
            with open(old_path, "r", encoding="utf-8") as f:
                old = json.load(f)
            migrated = {}
            for k, v in old.items():
                if k == "window_geometry" and isinstance(v, dict):
                    migrated["window_x"] = str(v.get("x", ""))
                    migrated["window_y"] = str(v.get("y", ""))
                    migrated["window_w"] = str(v.get("w", ""))
                    migrated["window_h"] = str(v.get("h", ""))
                elif k == "drawer-width":
                    migrated["drawer_width"] = str(v)
                else:
                    migrated[k] = str(v)
            _write_conf(migrated)
            os.remove(old_path)
        except Exception:
            pass

    result = {}
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        result[k.strip()] = v.strip()
    except Exception:
        pass
    return result

def _write_conf(data: dict):
    """写入 config.conf（原子写入）"""
    d = get_app_dir()
    os.makedirs(d, exist_ok=True)
    path = _conf_path()
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write("# DeepSeek Chat Configuration\n")
            for k in sorted(data.keys()):
                f.write(f"{k}={data[k]}\n")
        os.replace(tmp, path)
    except Exception:
        pass

def _get_conf(key: str, default: str = "") -> str:
    return _read_conf().get(key, default)

def _set_conf(key: str, value):
    data = _read_conf()
    data[key] = str(value)
    _write_conf(data)

# ==================== 具体设置存取 ====================
def load_sidebar_width() -> int:
    w = _get_conf("sidebar_width", "260")
    return max(180, min(500, int(w)))

def save_sidebar_width(width: int):
    _set_conf("sidebar_width", int(width))

def load_theme() -> str:
    return _get_conf("theme", "light")

def save_theme(theme: str):
    _set_conf("theme", theme)

def load_setting(key: str, default: str = "") -> str:
    return _get_conf(key, default)

def save_setting(key: str, value: str):
    _set_conf(key, str(value))

def save_settings(data: dict):
    """批量保存设置（一次原子写入，避免多次读写竞态）"""
    current = _read_conf()
    for k, v in data.items():
        current[k] = str(v)
    _write_conf(current)

def load_window_geometry() -> dict:
    return {
        "x": int(_get_conf("window_x", "")) if _get_conf("window_x", "") else None,
        "y": int(_get_conf("window_y", "")) if _get_conf("window_y", "") else None,
        "w": int(_get_conf("window_w", "1280")),
        "h": int(_get_conf("window_h", "840")),
    }

def save_window_geometry(x: int, y: int, w: int, h: int):
    _set_conf("window_x", x)
    _set_conf("window_y", y)
    _set_conf("window_w", w)
    _set_conf("window_h", h)

def get_assets_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "assets")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ==================== 窗口尺寸 ====================
TITLE = "💬 DeepSeek Chat"
APP_VERSION = "v3.1"

WIN_WIDTH  = 1280
WIN_HEIGHT = 840
WIN_MIN_W  = 720
WIN_MIN_H  = 460

SIDEBAR_WIDTH = 260
