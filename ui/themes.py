"""DeepSeek Chat themes"""

THEME_CSS = r"""
:root{--bg:linear-gradient(160deg,#fef9f0 0%,#fce0b0 40%,#f5b860 100%);--sidebar-bg:#f5e0c0;--surface:rgba(255,255,255,.92);--surface-secondary:rgba(250,240,225,.9);--user-bubble:rgba(255,224,178,.85);--ai-bubble:rgba(255,255,255,.9);--text:#1a1a1a;--sub:#8b7355;--border:#e0c8a8;--accent:#e67e22;--accent-hover:#d35400;--accent-soft:rgba(230,126,34,.12);--accent-alt:#f39c12;--on-accent:#fff;--input-bg:rgba(255,255,255,.92);--code-bg:#2c1810;--code-fg:#f0c8a0;--shadow:0 1px 3px rgba(0,0,0,.08);--danger:#e74c3c;--sidebar-footer:#b8936a}body[data-theme=sakura]{--bg:linear-gradient(160deg,#fef5f7 0%,#fce0e8 40%,#f0a0b8 100%);--sidebar-bg:#f5d5e0;--surface:rgba(255,255,255,.92);--surface-secondary:rgba(253,240,245,.9);--user-bubble:rgba(252,228,236,.85);--ai-bubble:rgba(255,255,255,.9);--text:#1a1a1a;--sub:#9e7777;--border:#e8c8d4;--accent:#e91e63;--accent-hover:#c2185b;--accent-soft:rgba(233,30,99,.12);--accent-alt:#ec407a;--on-accent:#fff;--input-bg:rgba(255,255,255,.92);--code-bg:#2d1520;--code-fg:#f0c0d0;--shadow:0 1px 3px rgba(0,0,0,.08);--danger:#e74c3c;--sidebar-footer:#c4909a}body[data-theme=ocean]{--bg:linear-gradient(160deg,#243850 0%,#152535 40%,#081520 100%);--sidebar-bg:#0d1625;--surface:rgba(36,52,71,.94);--surface-secondary:rgba(30,49,68,.92);--user-bubble:rgba(26,82,118,.78);--ai-bubble:rgba(36,52,71,.88);--text:#dce4ec;--sub:#7f8c8d;--border:#263545;--accent:#3498db;--accent-hover:#2980b9;--accent-soft:rgba(52,152,219,.18);--accent-alt:#1abc9c;--on-accent:#fff;--input-bg:rgba(36,52,71,.92);--code-bg:#0a0f17;--code-fg:#c9d1d9;--shadow:0 1px 3px rgba(0,0,0,.5);--danger:#e74c3c;--sidebar-footer:#3d5568}body[data-theme=cosmic]{--bg:linear-gradient(160deg,#1a1030 0%,#0d0820 40%,#040210 100%);--sidebar-bg:#06040c;--surface:rgba(26,26,26,.94);--surface-secondary:rgba(18,18,18,.92);--user-bubble:rgba(26,26,46,.82);--ai-bubble:rgba(22,33,62,.88);--text:#e0e0e0;--sub:#666;--border:#1c1c1c;--accent:#bb86fc;--accent-hover:#9b59b6;--accent-soft:rgba(187,134,252,.18);--accent-alt:#818cf8;--on-accent:#0d0d0d;--input-bg:rgba(22,33,62,.92);--code-bg:#000;--code-fg:#e0e0e0;--shadow:0 1px 3px rgba(0,0,0,.7);--danger:#cf6679;--sidebar-footer:#333}*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Microsoft YaHei,sans-serif;background:var(--bg);background-attachment:fixed;color:var(--text);height:100vh;display:flex;overflow:hidden;font-size:14px;position:relative;transition:background .5s,color .3s}
.sidebar{width:260px;background:var(--sidebar-bg);display:flex;flex-direction:column;border-right:1px solid var(--border);flex-shrink:0;z-index:10;position:relative;transition:background .5s}
.sidebar-header{padding:18px 16px 10px}
.sidebar-header h1{font-size:16px;font-weight:700;color:var(--text)}
.sidebar-header h1 span{color:var(--accent-alt)}
.sidebar-header p{font-size:11px;color:var(--sub);margin-top:2px}
.btn-new{margin:6px 14px 4px;padding:8px 14px;border:1px solid var(--border);border-radius:8px;background:var(--surface);color:var(--text);font-size:13px;cursor:pointer;transition:all .15s;text-align:center}
.btn-new:hover{background:var(--surface-secondary)}
.pinned-section{margin:0 6px 6px;padding:6px 6px 2px;background:var(--accent-soft);border-radius:10px;border:1px solid var(--accent-soft)}
.pinned-list{padding:0}
.pinned-item{padding:6px 10px;border-radius:6px;cursor:pointer;font-size:12px;color:var(--text);margin:1px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;transition:all .15s;display:flex;align-items:center;gap:6px}
.pinned-item:hover{background:rgba(255,255,255,.15)}
.pinned-item.active{color:var(--accent);font-weight:600}
.pinned-item .pin-icon{font-size:11px;flex-shrink:0;opacity:.8}
.pinned-time{font-size:10px;color:var(--sub);margin-left:6px;flex-shrink:0;opacity:.7}
.pinned-folder{font-size:10px;color:var(--sub);margin-left:auto;flex-shrink:0;opacity:.7}
.folder-list{flex:1;overflow-y:auto;padding:4px 6px}
.folder-item{padding:8px 10px;border-radius:8px;cursor:pointer;font-size:13px;color:var(--text);margin:1px 0;display:flex;align-items:center;gap:8px;transition:all .15s;user-select:none}
.folder-item:hover{background:var(--accent-soft)}
.folder-item.active{background:var(--accent-soft);color:var(--accent);font-weight:600}
.folder-item .folder-icon{font-size:16px;flex-shrink:0}
.folder-item .folder-name{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.folder-item .folder-count{font-size:11px;color:var(--accent);background:var(--accent-soft);padding:2px 8px;border-radius:10px;flex-shrink:0;font-weight:500}
.folder-item.drag-over{background:var(--accent-soft);border:1px dashed var(--accent)}
.folder-item.dragging{opacity:.4}
.btn-new-folder{margin:4px 6px 8px;padding:8px 12px;border:1px dashed var(--border);border-radius:8px;background:transparent;color:var(--sub);font-size:12px;cursor:pointer;transition:all .15s;text-align:center}
.btn-new-folder:hover{background:var(--accent-soft);color:var(--accent);border-color:var(--accent)}
.sidebar-settings{padding:12px 14px 14px;border-top:1px solid var(--border)}
.sidebar-settings select,.sidebar-settings .think-row{padding:6px 8px;border:1px solid var(--border);border-radius:8px;background:var(--surface);color:var(--text);font-size:12px;outline:none;transition:border-color .2s;cursor:pointer;line-height:1.4;box-sizing:border-box}
.sidebar-settings select:focus{border-color:var(--accent)}
.settings-row{display:flex;gap:6px;margin-bottom:6px;align-items:center}
.think-row{display:flex;align-items:center;gap:8px;cursor:pointer;font-size:12px;color:var(--text)}
.think-row input{cursor:pointer;accent-color:var(--accent)}
.sidebar-footer{padding:10px 14px;font-size:10px;color:var(--sidebar-footer);text-align:center;border-top:1px solid var(--border);letter-spacing:.3px}
.sidebar-resize-handle{position:absolute;right:-3px;top:0;bottom:0;width:6px;cursor:col-resize;z-index:20;background:transparent;transition:background .15s}
.sidebar-resize-handle:hover,.sidebar-resize-handle.active{background:var(--accent);opacity:.4}
.drawer-overlay{position:fixed;left:260px;top:0;right:0;bottom:0;background:rgba(0,0,0,.15);z-index:50;display:none}
.drawer-panel{position:fixed;left:260px;top:0;bottom:0;width:300px;background:var(--surface);z-index:51;display:none;flex-direction:column;box-shadow:2px 0 16px rgba(0,0,0,.1);border-right:1px solid var(--border);transform:translateX(-20px);opacity:0;transition:transform .2s,opacity .2s}
.drawer-panel.open{transform:translateX(0);opacity:1}
.drawer-header{display:flex;align-items:center;gap:8px;padding:14px 16px 10px;border-bottom:1px solid var(--border);flex-shrink:0}
.drawer-header .folder-title{flex:1;font-size:15px;font-weight:600;display:flex;align-items:center;gap:6px}
.drawer-btn-close{width:28px;height:28px;border:none;background:none;font-size:18px;cursor:pointer;color:var(--sub);border-radius:6px;display:flex;align-items:center;justify-content:center;transition:.1s}
.drawer-btn-close:hover{background:var(--accent-soft);color:var(--text)}
.drawer-search{padding:8px 14px;border-bottom:1px solid var(--border);flex-shrink:0}
.drawer-search input{width:100%;padding:7px 10px;border:1px solid var(--border);border-radius:8px;font-size:12px;outline:none;background:var(--surface-secondary);color:var(--text)}
.drawer-search input:focus{border-color:var(--accent);background:var(--surface)}
.drawer-conv-list{flex:1;overflow-y:auto;padding:4px 6px}
.drawer-conv-item{padding:8px 12px;border-radius:8px;cursor:pointer;font-size:13px;color:var(--sub);margin:2px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;transition:all .15s;display:flex;align-items:center;gap:4px}
.drawer-conv-item:hover{background:var(--accent-soft);color:var(--text)}
.drawer-conv-item.active{background:var(--accent-soft);color:var(--accent);font-weight:600}
.drawer-conv-item .pin-icon{font-size:12px;flex-shrink:0}
.drawer-conv-item .conv-name{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.drawer-conv-item .conv-time{font-size:10px;color:var(--sub);flex-shrink:0;margin-left:4px;opacity:.7}
.drawer-conv-item.dragging{opacity:.4}
.drawer-empty{padding:40px 20px;text-align:center;color:var(--sub);font-size:13px}
.main{flex:1;display:flex;flex-direction:column;min-width:0;transition:background .5s}
.chat-header{padding:10px 20px;border-bottom:1px solid var(--border);font-size:12px;color:var(--sub);display:flex;align-items:center;gap:8px;background:var(--surface);transition:background .5s}
.chat-header .dot{width:7px;height:7px;border-radius:50%;background:var(--accent-alt)}
.messages{flex:1;overflow-y:auto;padding:16px 20px;display:flex;flex-direction:column;gap:14px;user-select:text;-webkit-user-select:text}
.msg{display:flex;gap:10px;max-width:82%;animation:fadeIn .2s}
@keyframes fadeIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
.msg.user{align-self:flex-end;flex-direction:row-reverse}
.msg.assistant{align-self:flex-start}
.avatar{width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;flex-shrink:0;font-weight:600}
.msg-side .avatar{width:32px;height:32px}
.msg.user .avatar{background:var(--accent);color:var(--on-accent)}
.msg.assistant .avatar{background:var(--accent-alt);color:#fff}
.bubble{padding:10px 14px;border-radius:12px;font-size:14px;line-height:1.65;word-break:break-word;box-shadow:var(--shadow);user-select:text;-webkit-user-select:text}
.msg.user .bubble{background:var(--user-bubble);border-bottom-right-radius:4px}
.msg.assistant .bubble{background:var(--ai-bubble);border-bottom-left-radius:4px}
.msg-side{display:flex;flex-direction:column;align-items:center;gap:2px;flex-shrink:0}
.msg-time{font-size:10px;color:var(--sub);opacity:0;transition:opacity .2s;white-space:nowrap}
.msg:hover .msg-time{opacity:.7}
.bubble p{margin:4px 0}
.bubble pre{background:var(--code-bg);color:var(--code-fg);border-radius:8px;padding:14px;overflow-x:auto;margin:8px 0;font-size:13px;line-height:1.5;white-space:pre-wrap;word-wrap:break-word;overflow-wrap:break-word;user-select:text}
.bubble code{font-family:Cascadia Code,Fira Code,Consolas,monospace;font-size:13px}
.bubble :not(pre)>code{background:var(--accent-soft);padding:2px 6px;border-radius:4px;font-size:12px;color:var(--accent)}
.bubble ul,.bubble ol{margin:6px 0;padding-left:22px}
.bubble li{margin:2px 0}
.bubble h1,.bubble h2,.bubble h3,.bubble h4{margin:10px 0 4px}
.bubble h1{font-size:1.3em}.bubble h2{font-size:1.15em}.bubble h3{font-size:1.05em}
.bubble blockquote{border-left:3px solid var(--accent);margin:6px 0;padding:8px 14px;color:var(--text);opacity:.85;background:var(--accent-soft);border-radius:0 6px 6px 0}
.bubble table{border-collapse:collapse;margin:6px 0;width:100%}
.bubble th,.bubble td{border:1px solid var(--border);padding:6px 10px;text-align:left;font-size:13px}
.bubble th{background:var(--surface-secondary);font-weight:600}
.bubble img{max-width:100%;border-radius:6px}
.katex-display{overflow-x:auto;overflow-y:hidden;padding:4px 0}
.reasoning-toggle{cursor:pointer;color:var(--accent);font-size:12px;font-weight:600;user-select:none;padding:4px 0;display:inline-flex;align-items:center;gap:4px}
.reasoning-content{margin-top:6px;padding:10px 14px;background:var(--accent-soft);border-left:3px solid var(--accent);border-radius:0 6px 6px 0;font-size:12px;color:var(--sub);line-height:1.6;display:none;max-height:300px;overflow-y:auto;user-select:text}
.reasoning-content.open{display:block}
.input-area{padding:12px 20px;border-top:1px solid var(--border);background:var(--surface);transition:background .5s}
.input-row{display:flex;gap:10px;align-items:flex-end}
.input-row textarea{flex:1;border:1px solid var(--border);border-radius:12px;padding:10px 14px;font-size:14px;font-family:inherit;resize:none;outline:none;min-height:42px;max-height:140px;line-height:1.5;transition:border-color .2s;background:var(--input-bg);color:var(--text)}
.input-row textarea:focus{border-color:var(--accent)}
.btn-send{width:42px;height:42px;border-radius:10px;border:none;background:linear-gradient(135deg,var(--accent),var(--accent-alt));color:var(--on-accent);font-size:16px;cursor:pointer;transition:all .15s;flex-shrink:0;display:flex;align-items:center;justify-content:center}
.btn-send:hover{opacity:.9;transform:scale(1.05)}
.btn-send:disabled{background:var(--surface-secondary);color:var(--sub);cursor:not-allowed;transform:none}
.empty{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;color:var(--sub);gap:8px;padding:40px}
.empty .logo{font-size:48px;opacity:.5}
.empty h2{font-size:18px;color:var(--text)}
.empty p{font-size:13px}
.context-menu{position:fixed;background:var(--surface);border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,.12);padding:6px;z-index:999;display:none;min-width:150px;border:1px solid var(--border)}
.context-menu .item{padding:9px 14px;border-radius:7px;cursor:pointer;font-size:13px;transition:background .1s;color:var(--text)}
.context-menu .item:hover{background:var(--accent-soft);color:var(--accent)}
.context-menu .item.danger{color:var(--danger)}
.context-menu .item.danger:hover{background:rgba(231,76,60,.1)}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:1000;display:none;align-items:center;justify-content:center;backdrop-filter:blur(2px)}
.modal{background:var(--surface);border-radius:14px;padding:28px;max-width:400px;width:90%;box-shadow:0 12px 40px rgba(0,0,0,.2);border:1px solid var(--border)}
.modal h3{margin-bottom:8px;font-size:17px;color:var(--text)}
.modal p{color:var(--sub);font-size:13px;margin-bottom:16px}
.modal .btns{display:flex;gap:8px;justify-content:flex-end}
.modal .btns button{padding:8px 20px;border-radius:8px;border:1px solid var(--border);cursor:pointer;font-size:13px;background:var(--surface);color:var(--text);transition:all .15s}
.modal .btns button:hover{background:var(--surface-secondary)}
.modal .btn-danger{background:var(--danger);color:#fff;border-color:var(--danger)}
.modal .btn-danger:hover{opacity:.9}
.modal input[type=text],.modal input[type=password]{width:100%;padding:10px 14px;border:1px solid var(--border);border-radius:8px;font-size:13px;margin:8px 0;outline:none;box-sizing:border-box;background:var(--surface-secondary);color:var(--text)}
.modal input:focus{border-color:var(--accent);background:var(--surface)}
.icon-picker{display:flex;flex-wrap:wrap;gap:4px;margin:8px 0}
.icon-picker span{width:36px;height:36px;display:flex;align-items:center;justify-content:center;font-size:20px;border-radius:8px;cursor:pointer;transition:all .15s;border:2px solid transparent;background:var(--surface-secondary)}
.icon-picker span:hover{background:var(--accent-soft);transform:scale(1.1)}
.icon-picker span.sel{border-color:var(--accent);background:var(--accent-soft)}
::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--sub)}
"""
