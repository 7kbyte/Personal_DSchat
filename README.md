# 💬 DeepSeek Chat

一个基于 [DeepSeek API](https://platform.deepseek.com/) 的桌面聊天应用，使用 pywebview + KaTeX + marked.js 实现与官网一致的 Markdown 与 LaTeX 渲染效果。

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ 功能特性

- 🤖 **多模型支持** — DeepSeek-V4 Flash / DeepSeek-V4 Pro
- 🧠 **深度思考模式** — 支持查看模型思维链（reasoning_content），可调节思考强度
- 📝 **Markdown 渲染** — 代码块高亮、表格、列表、引用、标题等完整支持
- 🔢 **LaTeX 公式** — 行内公式 `$...$` 与块级公式 `$$...$$`，基于 KaTeX 渲染
- � **收藏夹管理** — 新建/重命名/删除收藏夹，Emoji 图标选择，对话分组收纳
- 📌 **侧栏置顶** — 置顶对话直接显示在侧边栏顶部，显示所属收藏夹，一键跳转
- 📂 **抽屉面板** — 点击收藏夹弹出侧边抽屉，实时搜索过滤对话
- ↔️ **拖拽管理** — 文件夹排序拖拽、对话跨文件夹拖拽移动
- 🎨 **四种主题** — 🌅暖阳橙 / 🌸樱花粉 / 🌊深海蓝 / 🌑宇宙黑，一键切换自动记忆
- ↩️ **对话回退** — 右键可将对话回退到任意历史消息位置
- 📋 **一键复制** — 复制单条消息或包含思维链的全部对话内容
- 🔑 **安全设计** — API Key 首次启动时弹窗输入，加密保存在本地 `apikey.txt`
- 📐 **可调侧栏** — 拖拽侧栏右边缘自由调整宽度（180~500px），宽度自动记忆
- 💾 **本地存储** — 对话历史、收藏夹、配置自动保存在 `%APPDATA%\DeepSeekChat\`
- 📦 **单文件打包** — 支持 PyInstaller 打包为独立 EXE

## 📸 界面预览

```
┌──────────────┬──────────────────────────────────────────┐
│ 💬 DeepSeek  │  🤖 DeepSeek-V4 Pro · 🧠 深度思考        │
│              │                                          │
│ ＋ 新对话     │  ┌──────────────────────────────────┐    │
│              │  │ 👤 我                             │    │
│ ┌─ 📌 置顶 ─┐│  │ 你好，请帮我写一段 Python 代码     │    │
│ │ Python优化 ││  └──────────────────────────────────┘    │
│ │   默认收藏夹││  ┌──────────────────────────────────┐    │
│ └───────────┘│  │ 🤖 DeepSeek                      │    │
│ 📁 默认 3    │  │ 当然可以！以下是代码：            │    │
│ 💼 工作 2    │  │ ```python                        │    │
│ 📁 个人 1    │  │ def hello():                     │    │
│              │  │     print("Hello!")              │    │
│ ←拖拽调整→   │  │ ```                              │    │
│ 📁 ＋ 新建   │  └──────────────────────────────────┘    │
│ ──────────── │                                          │
│ DS-V4 Pro 🧠  │  ┌──────── 抽屉面板 ─────────┐           │
│ high  🌅暖阳橙│  │ 📁 工作              ✕    │           │
│              │  │ 🔍 过滤对话...            │           │
│              │  │    项目方案               │           │
│              │  │    周报内容               │           │
│              │  └──────────────────────────┘           │
│              ├──────────────────────────────────────────┤
│              │ 输入消息，Enter 发送                     │ 发送 │
└──────────────┴──────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Windows 操作系统

### 安装与运行

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd ds

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行
python main.py
```

首次启动时会弹出 API Key 输入框，前往 [DeepSeek 开放平台](https://platform.deepseek.com/api_keys) 注册获取 Key 后粘贴即可。Key 将以 `sk-` 前缀自动验证，验证通过后加密保存在本地 `%APPDATA%\DeepSeekChat\apikey.txt`。

## 📦 打包为 EXE

运行打包脚本：

```bash
build.bat
```

打包完成后，EXE 文件位于 `dist\DeepSeekChat.exe`（约 10 MB）。

> **注意**：打包后的 EXE 首次启动同样会弹出 API Key 输入框，无需在源码中预设。

## 📁 项目结构

```
ds/
├── main.py              # 入口文件
├── config.py            # 全局配置（API、模型、窗口尺寸、侧栏宽度）
├── requirements.txt     # 依赖列表
├── build.bat            # 打包脚本
├── DeepSeekChat.spec    # PyInstaller 配置文件
├── ds.png               # 应用图标
│
├── api/
│   └── deepseek.py      # DeepSeek API 调用（流式/非流式）+ Key 验证
│
├── ui/
│   ├── web_ui.py        # 入口：导入 Bridge + PAGE，启动 WebView 窗口
│   ├── bridge.py        # Python ↔ JS 桥接类（API 调用、历史、剪贴板、线程安全）
│   ├── page.py          # 前端页面：HTML 结构 + JS 逻辑入口
│   └── themes.py        # 四种主题的 CSS 变量定义（暖阳橙/樱花粉/深海蓝/宇宙黑）
│
├── storage/
│   └── history.py       # 对话 + 收藏夹持久化（JSON，含旧数据自动迁移）
│
└── assets/              # 静态资源（图标、背景图等）
```

## ⚙️ 配置说明

`config.py` 主要配置项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 空（首次启动弹窗输入） |
| `DEEPSEEK_API_URL` | API 端点地址 | `https://api.deepseek.com/chat/completions` |
| `MODEL_OPTIONS` | 可用模型列表 | Flash / Pro |
| `REASONING_EFFORT_OPTIONS` | 思考强度 | high / max |
| `DEFAULT_FOLDER_NAME` | 默认收藏夹名称 | 默认收藏夹 |
| `THEME_OPTIONS` | 可选主题 | 🌅暖阳橙 / 🌸樱花粉 / 🌊深海蓝 / 🌑宇宙黑 |
| `WIN_WIDTH` / `WIN_HEIGHT` | 窗口尺寸 | 1280×840 |
| `SIDEBAR_WIDTH` | 侧栏初始宽度 | 260px |

> API Key、侧栏宽度和主题选择等用户偏好保存在 `%APPDATA%\DeepSeekChat\` 目录下的 `config.json` 中，与源码分离。

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| [pywebview](https://pywebview.flowrl.com/) | 桌面 WebView 容器 |
| [KaTeX](https://katex.org/) | LaTeX 数学公式渲染 |
| [marked.js](https://marked.js.org/) | Markdown → HTML 转换 |
| [PyInstaller](https://pyinstaller.org/) | 打包为独立 EXE |
| CSS Custom Properties | 四种主题 CSS 变量动态切换 |
| HTML5 Drag & Drop | 文件夹/对话拖拽排序与移动 |
| Win32 Clipboard API | 系统剪贴板复制 |

## ⌨️ 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Enter` | 发送消息 |
| `Shift + Enter` | 换行 |
| `Esc` | 关闭抽屉面板 / 关闭右键菜单 |
| 右键消息 | 复制此消息 / 复制全部对话 / 回退到此处 |
| 右键置顶对话 | 取消置顶 |
| 右键收藏夹 | 重命名 / 删除收藏夹 |
| 右键抽屉对话 | 置顶/取消置顶 / 移动到其他收藏夹 / 删除 |
| 拖拽收藏夹 | 收藏夹排序 |
| 拖拽对话到收藏夹 | 移动对话到目标收藏夹 |
| 拖拽侧栏右边缘 | 调整侧栏宽度（自动记忆） |

## 📄 License

MIT
