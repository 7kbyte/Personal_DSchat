"""HTML page for DeepSeek Chat — 从 ui/static/ 加载模板与 JS 模块"""
import os

from ui.themes import THEME_CSS

_STATIC = os.path.join(os.path.dirname(__file__), 'static')
_JS_DIR = os.path.join(_STATIC, 'js')

with open(os.path.join(_STATIC, 'index.html'), 'r', encoding='utf-8') as _f:
    _html = _f.read()

# JS 模块加载顺序（依赖关系决定）
_JS_MODULES = [
    'state.js',         # 全局状态
    'utils.js',         # 工具函数
    'markdown.js',      # Markdown / LaTeX 渲染
    'folders.js',       # 文件夹管理
    'messages.js',      # 消息渲染
    'conversations.js', # 对话管理
    'stream.js',        # 流式传输 / 发送
    'context-menu.js',  # 右键菜单
    'drag.js',          # 拖拽排序
    'modals.js',        # 模态框
    'settings.js',      # 设置 / 辅助
    'init.js',          # 初始化
    'main.js',          # 启动入口
]

_parts = []
for _name in _JS_MODULES:
    with open(os.path.join(_JS_DIR, _name), 'r', encoding='utf-8') as _f:
        _parts.append(_f.read())
_js = '\n'.join(_parts)

PAGE = _html.replace('{{CSS}}', THEME_CSS).replace('{{JS}}', _js)
