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
- 💬 **多对话管理** — 新建、切换、删除对话，支持拖拽排序
- ↩️ **对话回退** — 右键可将对话回退到任意历史消息位置
- 📋 **一键复制** — 复制单条消息或全部对话内容
- 💾 **本地存储** — 对话历史自动保存在 `%APPDATA%\DeepSeekChat\`
- 📦 **单文件打包** — 支持 PyInstaller 打包为独立 EXE

## 📸 界面预览

```
┌──────────────┬─────────────────────────────────────┐
│  💬 对话列表  │  🤖 DeepSeek · 🧠 深度思考           │
│              │                                     │
│  ＋ 新对话    │  ┌─────────────────────────────┐    │
│              │  │ 👤 我                        │    │
│  💬 对话1    │  │ 你好，请帮我写一段代码        │    │
│  💬 对话2    │  └─────────────────────────────┘    │
│  💬 对话3    │  ┌─────────────────────────────┐    │
│              │  │ 🤖 DeepSeek                 │    │
│  ─────────── │  │ 当然可以！以下是代码：       │    │
│  模型选择    │  │ ```python                   │    │
│  DeepSeek-V4 │  │ def hello():                │    │
│  ☑ 深度思考  │  │     print("Hello!")         │    │
│              │  │ ```                         │    │
│              │  └─────────────────────────────┘    │
│              ├─────────────────────────────────────┤
│              │ 输入消息，Enter 发送                │ 发送 │
└──────────────┴─────────────────────────────────────┘
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

# 5. 配置 API Key
# 编辑 config.py，将 DEEPSEEK_API_KEY 设置为你的 API Key

# 6. 运行
python main.py
```

### 获取 API Key

前往 [DeepSeek 开放平台](https://platform.deepseek.com/api_keys) 注册并获取 API Key，然后在 `config.py` 中替换：

```python
DEEPSEEK_API_KEY = "sk-your-api-key-here"
```

## 📦 打包为 EXE

运行打包脚本：

```bash
build.bat
```

打包完成后，EXE 文件位于 `dist\DeepSeekChat.exe`（约 10 MB）。

> **注意**：打包前请确保 `config.py` 中的 API Key 已正确配置。

## 📁 项目结构

```
ds/
├── main.py              # 入口文件
├── config.py            # API Key、模型、主题色、窗口尺寸等配置
├── requirements.txt     # 依赖列表
├── build.bat            # 打包脚本
├── DeepSeekChat.spec    # PyInstaller 配置文件
├── ds.png               # 应用图标
│
├── api/
│   └── deepseek.py      # DeepSeek API 调用封装
│
├── ui/
│   ├── web_ui.py        # WebView 主界面（HTML/CSS/JS + Python Bridge）
│   ├── app.py           # Tkinter 主应用（备选 UI）
│   ├── sidebar.py       # 侧边栏（对话列表 + 设置）
│   ├── chat_area.py     # 聊天显示区（Markdown/LaTeX 渲染）
│   └── input_area.py    # 底部输入区
│
├── utils/
│   └── renderer.py      # Tkinter Markdown/LaTeX 渲染工具
│
├── storage/
│   └── history.py       # 对话历史持久化（JSON）
│
└── assets/              # 静态资源（背景图等）
```

## ⚙️ 配置说明

`config.py` 主要配置项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 需自行填写 |
| `DEEPSEEK_API_URL` | API 端点地址 | `https://api.deepseek.com/chat/completions` |
| `MODEL_OPTIONS` | 可用模型列表 | Flash / Pro |
| `REASONING_EFFORT_OPTIONS` | 思考强度 | high / max |
| `WIN_WIDTH` / `WIN_HEIGHT` | 窗口尺寸 | 980×660 |
| `C_ACCENT` | 主题色 | `#6dbd72`（柔和绿） |

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| [pywebview](https://pywebview.flowrl.com/) | 桌面 WebView 容器 |
| [KaTeX](https://katex.org/) | LaTeX 数学公式渲染 |
| [marked.js](https://marked.js.org/) | Markdown → HTML 转换 |
| [PyInstaller](https://pyinstaller.org/) | 打包为独立 EXE |
| tkinter | 备选原生 UI |
| matplotlib | Tkinter 模式下 LaTeX 渲染 |

## ⌨️ 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Enter` | 发送消息 |
| `Shift + Enter` | 换行 |
| `Ctrl + C` | 复制选中文本 |
| 右键消息 | 复制 / 回退对话 |
| 右键对话 | 删除对话 |

## 📄 License

MIT
