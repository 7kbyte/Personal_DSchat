"""HTML page for DeepSeek Chat — 从 ui/static/ 加载模板、CSS 与 JS 模块"""
import os

_STATIC = os.path.join(os.path.dirname(__file__), 'static')
_JS_DIR = os.path.join(_STATIC, 'js')
_CSS_DIR = os.path.join(_STATIC, 'css')

with open(os.path.join(_STATIC, 'index-alpine.html'), 'r', encoding='utf-8') as _f:
    _html = _f.read()

# CSS 加载顺序（按 css/files.txt）
with open(os.path.join(_CSS_DIR, 'files.txt'), 'r', encoding='utf-8') as _f:
    _css_files = [l.strip() for l in _f if l.strip()]
_css = '\n'.join(
    open(os.path.join(_CSS_DIR, f), 'r', encoding='utf-8').read()
    for f in _css_files
)

# JS 模块加载顺序（Alpine Store 最先，其余为辅助）
_JS_MODULES = [
    'alpine-store.js',  # Alpine.store('app') — 全局状态与方法
    'markdown.js',      # Markdown / LaTeX 渲染
    'messages.js',      # 消息列表渲染（读取 Alpine store）
    'stream.js',        # 流式传输 / 发送 / 重新生成
    'drag.js',          # 拖拽排序
    'init.js',          # 窗口拖拽/缩放 + 键盘事件
]

_parts = []
for _name in _JS_MODULES:
    with open(os.path.join(_JS_DIR, _name), 'r', encoding='utf-8') as _f:
        _parts.append(_f.read())
_js = '\n'.join(_parts)

PAGE = _html.replace('{{CSS}}', _css).replace('{{JS}}', _js)
