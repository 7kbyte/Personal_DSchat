"""DeepSeek Chat themes — 从 ui/static/themes.css 加载"""
import os

_STATIC = os.path.join(os.path.dirname(__file__), 'static')
with open(os.path.join(_STATIC, 'themes.css'), 'r', encoding='utf-8') as _f:
    THEME_CSS = _f.read()
