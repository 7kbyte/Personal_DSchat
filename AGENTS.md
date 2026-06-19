# AGENTS.md — DeepSeek Chat

A Python + TypeScript desktop chat app using pywebview (WebView2), Alpine.js, KaTeX, and marked.js. Windows-only.

## Build & Run

```bash
# First-time setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
npm install

# Development
npm run build          # Compile TypeScript (ts/ → ui/static/js/)
python main.py         # Launch the app

# Production EXE packaging
npm run build && build.bat   # PyInstaller via DeepSeekChat.spec
```

## Architecture (see [README.md](README.md) for full structure)

```
main.py → ui/web_ui.py (pywebview window) → ui/bridge.py (Python↔JS)
                                              ├── services/api_service.py (httpx SSE)
                                              ├── services/storage_service.py
                                              └── services/window_service.py
           ui/static/ (frontend)
              ├── index.html (Alpine.js template)
              ├── css/ (14 modular files, 10 themes)
              └── js/ (compiled from ts/)
```

## Key Conventions

### Python
- **Snake_case** for files, functions, properties; **PascalCase** for classes
- Services use **composition**: `Bridge` holds `StorageService`/`ApiService`/`WindowService` instances
- Storage uses **atomic writes**: write `.tmp` → `os.replace()` → final path
- Config is `.conf` key=value format, migrated from old `config.json`
- API Key stored as `apikey.txt`, chat history as `chat_history.json`, prompts as `prompts.json`
- All data stored at `%APPDATA%\DeepSeekChat\`
- Proxy auto-detection: Windows `https://` scheme proxies are corrected to `http://` for httpx

### TypeScript (ts/ → compiles to ui/static/js/)
- **Strict mode**, ES2020 target, bundler module resolution
- All Python bridge calls via `pywebview!.api.<methodName>(...)`
- Global functions on `window`: `onResizeStart`, `onKeyDown`, `autoResize`
- Stream callbacks injected as `window._onStreamChunk` / `window._onStreamDone`
- Alpine.js `Alpine.store('app')` is the single source of truth for all UI state

### CSS
- 14 modular files loaded in `files.txt` order
- **Kebab-case** class names, 10 themes via CSS custom properties in `base/variables.css`
- Theme class applied to `<html>`, all colors reference `var(--xxx)`

### Naming Summary
| Context | Convention | Example |
|---------|-----------|---------|
| Python files | snake_case | `api_service.py` |
| TS files | kebab-case | `alpine-store.ts` |
| CSS classes | kebab-case | `.sidebar-header` |
| Alpine methods | camelCase | `switchConv()` |
| Bridge API methods | camelCase | `setApiKey()` |

## Important Patterns

### LaTeX Rendering Pipeline (markdown.ts)
1. Replace all math delimiters (`$$`, `$`, `\[`, `\(`) with placeholder tokens `\x00LB`/`\x00LI`
2. Run marked.js to convert markdown → HTML
3. Replace placeholders with KaTeX-rendered HTML
4. Detect narrow messages: no code block/table/katex + <180 chars → add `.narrow` class

### Frontend Data Flow
User input → Alpine store → `bridge.sendMessage()` → `ApiService` (runs in separate thread via `threading.Thread` + `asyncio.run()`) → httpx SSE stream → `_on_chunk` callback → `bridge._eval_js("window._onStreamChunk(...)")` → `stream.ts` → Alpine store → `messages.ts` render

### Window Management (init.ts, web_ui.py)
- Frameless window with custom title bar (HTML/CSS)
- 8-direction edge resize handles, DPI-aware via ctypes Win32 API
- Taskbar-aware maximize (respects taskbar position)

## Pitfalls

- **Never** edit `ui/static/js/*.js` directly — those are TypeScript compile output. Edit `ts/*.ts` instead.
- When adding Python dependencies, also update `DeepSeekChat.spec` hidden imports if needed
- The PyInstaller spec bundles `ui/static` as data — new static files are auto-included, but new Python packages may need `hiddenimports`
- CSS file load order matters (defined in `ui/static/css/files.txt`)
- `Alpine.store('app')` must be initialized before any Alpine component references it
