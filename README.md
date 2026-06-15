# 💬 DeepSeek Chat

一个基于 [DeepSeek API](https://platform.deepseek.com/) 的现代化桌面聊天应用，使用 pywebview + KaTeX + marked.js 实现与官网一致的 Markdown 与 LaTeX 渲染效果。无边框窗口、毛玻璃侧栏、几何矢量背景、10 套主题配色，打造媲美原生应用的桌面体验。

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ 功能特性

- 🤖 **多模型支持** — DeepSeek-V4 Flash / DeepSeek-V4 Pro
- 🧠 **深度思考模式** — 支持查看模型思维链（reasoning_content），可调节思考强度
- � **自定义提示词** — 创建/编辑/删除系统提示词，每个对话可独立选择，系统消息隐藏不显示
- 📝 **Markdown 渲染** — 代码块高亮（一键复制）、表格、列表、引用、标题
- 🔢 **LaTeX 公式** — 行内公式 `$...$` 与块级公式 `$$...$$`，基于 KaTeX 渲染
- � **收藏夹管理** — 新建/重命名/删除收藏夹，Emoji 图标选择，对话分组收纳
- 📌 **侧栏置顶** — 置顶对话直接显示在侧边栏顶部，显示所属收藏夹，一键跳转
- 📂 **抽屉面板** — 点击收藏夹弹出侧边抽屉，实时搜索过滤对话
- ↔️ **拖拽管理** — 文件夹排序拖拽、对话跨文件夹拖拽移动
- 🎨 **10 套主题** — 简约白 / 天蓝 / 青叶 / 玫瑰 / 晚霞 / 简约黑 / 深海 / 深林 / 盛放 / 星穹
- 🖼️ **几何矢量装饰** — 空心圆/方/三角几何图案，每套主题专属配色，侧栏与对话区共用幕布
- 🪟 **无边框窗口** — 自绘最小化/最大化/关闭按钮，标题栏拖拽移动，八向边缘拖拽缩放
- 🔄 **对话回退** — 右键可将对话回退到任意历史消息位置
- 📋 **一键复制** — 复制单条消息或包含思维链的全部对话内容
- 🔑 **安全设计** — API Key 首次启动时弹窗输入，验证通过后本地保存
- 📐 **可调侧栏** — 拖拽侧栏右边缘自由调整宽度（180~500px），宽度自动记忆
- 💾 **本地存储** — 对话历史、收藏夹、提示词、配置保存在 `%APPDATA%\DeepSeekChat\`
- 📦 **单文件打包** — 支持 PyInstaller 打包为独立 EXE

## � 快速开始

### 环境要求

- Python 3.10+
- Windows 10/11（WebView2 运行时随 Edge 预装）

### 安装与运行

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd ds

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
npm install

# 4. 编译 TypeScript
npm run build

# 5. 运行
python main.py
```

首次启动时会弹出 API Key 输入框，前往 [DeepSeek 开放平台](https://platform.deepseek.com/api_keys) 注册获取 Key 后粘贴即可。

## 📦 打包为 EXE

```bash
npm run build    # 先编译 TypeScript
build.bat        # PyInstaller 打包
```

打包完成后 EXE 位于 `dist\DeepSeekChat.exe`。

## 📁 项目结构

```
ds/
├── main.py              # 入口文件
├── config.py            # 全局配置（API、模型、窗口、存储路径）
├── requirements.txt     # Python 依赖
├── package.json         # Node.js 依赖（TypeScript）
├── tsconfig.json        # TypeScript 编译配置
├── build.bat            # PyInstaller 打包脚本
│
├── api/
│   └── deepseek.py      # DeepSeek API 流式调用 + Key 验证
│
├── services/            # 服务层
│   ├── storage_service.py  # 持久化读写
│   ├── api_service.py      # API 流式调用
│   └── window_service.py   # 无边框窗口控制
│
├── ui/
│   ├── web_ui.py        # WebView 窗口创建（无边框、DPI 感知）
│   ├── bridge.py        # Python ↔ JS 桥接（轻量转发层）
│   ├── page.py          # 页面组装（HTML 模板 + CSS + JS 注入）
│   └── static/          # 前端资源
│       ├── index-alpine.html  # Alpine.js HTML 模板
│       ├── css/                # 组件化 CSS（14 个文件）
│       │   ├── base/           # 变量、reset、滚动条
│       │   ├── components/     # 侧栏、消息、模态框等
│       │   └── layout/         # 布局、装饰
│       └── js/                 # 编译后的 JS（由 ts/ 生成）
│
├── ts/                  # TypeScript 源码
│   ├── globals.d.ts     # 全局类型声明
│   ├── alpine-store.ts  # Alpine.js 全局 Store
│   ├── markdown.ts      # Markdown + KaTeX 渲染
│   ├── messages.ts      # 消息渲染 + 代码复制
│   ├── stream.ts        # 流式传输 + 发送
│   ├── drag.ts          # 拖拽排序 + 侧栏宽度
│   └── init.ts          # 窗口拖拽/缩放 + 键盘
│
├── storage/
|   └── history.py       # 对话 + 收藏夹持久化（JSON，原子写入）
```

## ⚙️ 配置说明

`config.py` 主要配置项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 空（首次启动弹窗输入） |
| `DEEPSEEK_API_URL` | API 端点 | `https://api.deepseek.com/chat/completions` |
| `MODEL_OPTIONS` | 可用模型 | V4 Flash / V4 Pro |
| `REASONING_EFFORT_OPTIONS` | 思考强度 | high / max |
| `WIN_WIDTH` / `WIN_HEIGHT` | 窗口默认尺寸 | 1280 × 840 |
| `WIN_MIN_W` / `WIN_MIN_H` | 窗口最小尺寸 | 600 × 400 |
| `SIDEBAR_WIDTH` | 侧栏初始宽度 | 260px |

> 用户偏好保存在 `%APPDATA%\DeepSeekChat\`：
> - `config.conf` — 主题、侧栏宽度、窗口位置/大小、思考模式（key=value 格式）
> - `prompts.json` — 自定义提示词
> - `chat_history.json` — 对话历史 + 收藏夹
> - `apikey.txt` — API Key
>
> 所有写入均使用原子操作（临时文件 + `os.replace`）防止数据损坏。

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| [pywebview](https://pywebview.flowrl.com/) | 桌面 WebView 容器（WebView2） |
| [Alpine.js](https://alpinejs.dev/) | 响应式 UI 框架（15 KB） |
| [TypeScript](https://www.typescriptlang.org/) | 类型安全前端开发 |
| [KaTeX](https://katex.org/) | LaTeX 数学公式渲染 |
| [marked.js](https://marked.js.org/) | Markdown → HTML 转换 |
| [PyInstaller](https://pyinstaller.org/) | 打包为独立 EXE |
| CSS Custom Properties | 10 套主题 CSS 变量动态切换 |
| SVG + CSS | 空心几何矢量背景装饰 |
| HTML5 Drag & Drop | 拖拽排序与移动 |
| Win32 API | 无边框窗口控制（DPI 感知最大化、原子移动/缩放） |
| `backdrop-filter` | 侧栏毛玻璃效果 |

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
