/**
 * Alpine.js 全局 Store — 单一响应式状态源
 * 替代 state.js + 各模块中的分散状态
 */
document.addEventListener('alpine:init', () => {
    Alpine.store('app', {
        // ── 核心数据 ─────────────────────────────────
        conversations: [],
        folders: [],
        prompts: [],
        currentId: null,
        loading: false,

        // ── 设置 ─────────────────────────────────────
        model: 'deepseek-v4-pro',
        thinking: true,
        effort: 'high',
        theme: 'light',
        settingsCollapsed: false,

        // ── UI 状态 ──────────────────────────────────
        drawerOpen: false,
        drawerFolderId: null,
        drawerSearch: '',

        // 模态框
        showFolderModal: false,
        folderModalEditId: null,
        folderModalName: '',
        folderModalIcon: '📁',
        folderModalError: '',

        showConfirmModal: false,
        confirmTitle: '',
        confirmMsg: '',
        confirmAction: null,

        showApiKeyModal: false,
        apiKeyInput: '',
        apiKeyError: '',

        showPromptModal: false,
        promptListOpen: true,
        promptEditorOpen: false,
        promptEditId: null,
        promptEditName: '',
        promptEditContent: '',

        // 新对话默认提示词（不影响已有对话）
        defaultPromptId: null,
        defaultPromptName: null,

        showViewPromptModal: false,
        viewPromptContent: '',

        showRollbackModal: false,
        rollbackIdx: -1,

        // 右键菜单
        ctxMenu: null,
        ctxMsgIdx: -1,
        ctxConvId: null,
        ctxFolderId: null,

        // ── icon 预设 ───────────────────────────────
        presetIcons: ['📁','💼','🏠','🎓','💡','🚀','🎮','🎵','📚','❤️','🌟','🔥','🌈','🍕','🐱','💰','⚡','🎯','🌍','📝'],

        // ═══════════════════════════════════════════════
        // 计算属性
        // ═══════════════════════════════════════════════

        get current() {
            return this.conversations.find(c => c.id === this.currentId);
        },

        get pinnedConversations() {
            return this.conversations.filter(c => c.pinned && c.messages && c.messages.length > 0);
        },

        get currentFolder() {
            const f = this.folders.find(f => f.id === this.drawerFolderId);
            return f ? { ...f, displayName: f.name.replace(/^.\s/, '') } : null;
        },

        get drawerConversations() {
            const q = (this.drawerSearch || '').toLowerCase();
            let convs = this.conversations.filter(c => c.folderId === this.drawerFolderId);
            if (q) convs = convs.filter(c => (c.title || '新对话').toLowerCase().includes(q));
            return convs;
        },

        get visibleMessages() {
            const conv = this.current;
            if (!conv || !conv.messages) return [];
            return conv.messages.filter(m => m.role !== 'system');
        },

        get hasMessages() {
            return this.visibleMessages.length > 0;
        },

        get currentPromptName() {
            const conv = this.current;
            if (!conv || !conv.promptId) return '未设置';
            // 优先使用冻结名称（选择时保存的快照）
            if (conv.promptName) return conv.promptName;
            const p = this.prompts.find(p => p.id === conv.promptId);
            return p ? p.name : '未设置';
        },

        get statusText() {
            const modelNames = { 'deepseek-v4-pro': 'V4 Pro', 'deepseek-v4-flash': 'V4 Flash' };
            return modelNames[this.model] || this.model;
        },

        // ═══════════════════════════════════════════════
        // 初始化
        // ═══════════════════════════════════════════════

        async init() {
            if (!this._apiReady()) {
                // pywebview bridge 尚未就绪，延迟重试
                var self = this;
                setTimeout(function() { self.init(); }, 300);
                return;
            }
            try {
                const raw = await pywebview.api.loadState();
                const data = JSON.parse(raw);
                this.conversations = data.conversations || [];
                this.folders = data.folders || [];
                this.currentId = data.currentId || null;

                if (this.folders.length === 0) {
                    this.folders = [{ id: 'f_default', name: '默认收藏夹', icon: '📁', order: 0 }];
                }

                // 加载设置
                const theme = await pywebview.api.getTheme();
                if (theme) this.setTheme(theme);
                const model = await pywebview.api.loadSetting('model');
                if (model) this.model = model;
                const thinking = await pywebview.api.loadSetting('thinking');
                if (thinking) this.thinking = thinking === '1';
                const effort = await pywebview.api.loadSetting('effort');
                if (effort) this.effort = effort;
                const sc = await pywebview.api.loadSetting('settings_collapsed');
                if (sc) this.settingsCollapsed = sc === '1';

                // 加载提示词
                const promptsRaw = await pywebview.api.loadPrompts();
                if (promptsRaw) this.prompts = JSON.parse(promptsRaw);

                // 初始化窗口位置
                const rect = await pywebview.api.getWindowRect();
                if (rect) {
                    const r = JSON.parse(rect);
                    window._winX = r.x; window._winY = r.y;
                    window._winW = r.w; window._winH = r.h;
                }

                // 恢复侧栏 / 抽屉宽度
                const sw = await pywebview.api.getSidebarWidth();
                if (sw && typeof setSidebarWidth === 'function') setSidebarWidth(sw);
                const dw = await pywebview.api.loadSetting('drawer_width');
                if (dw && typeof setDrawerWidth === 'function') setDrawerWidth(parseInt(dw));

                if (this.conversations.length === 0) {
                    this.newConv();
                } else {
                    if (!this.conversations.find(c => c.id === this.currentId)) {
                        this.currentId = this.conversations[0].id;
                    }
                }

                // API Key 检查
                const hasKey = await pywebview.api.hasApiKey();
                if (!hasKey) this.showApiKeyModal = true;

                // 恢复设置面板 UI
                this._restoreSettingsUI();

                // 初次渲染
                if (typeof renderMessages === 'function') renderMessages();
            } catch (e) {
                console.error('[Alpine] init:', e);
            }

            window.setupWindowDrag();
            window.pywebviewReady = true;
        },

        _restoreSettingsUI() {
            // 恢复模型按钮状态
            document.querySelectorAll('#modelSeg .seg-btn').forEach(b => {
                b.classList.toggle('active', b.dataset.val === this.model);
            });
            document.querySelectorAll('#effortSeg .seg-btn').forEach(b => {
                b.classList.toggle('active', b.dataset.val === this.effort);
            });
            const thinkToggle = document.getElementById('thinkToggle');
            if (thinkToggle) thinkToggle.checked = this.thinking;
        },

        _apiReady() {
            return typeof pywebview !== 'undefined' && pywebview.api;
        },

        // ═══════════════════════════════════════════════
        // 对话管理
        // ═══════════════════════════════════════════════

        newConv() {
            const cur = this.current;
            if (cur && (!cur.messages || cur.messages.length === 0)) {
                document.getElementById('input')?.focus();
                return;
            }
            const id = Date.now().toString() + Math.random().toString(36).slice(2, 8);
            const conv = { id, title: '新对话', messages: [], pinned: false };
            // 应用默认提示词
            if (this.defaultPromptId) {
                conv.promptId = this.defaultPromptId;
                conv.promptName = this.defaultPromptName;
            }
            this.conversations.unshift(conv);
            this.currentId = id;
            this._save();
            if (typeof renderMessages === 'function') renderMessages();
        },

        switchConv(id) {
            var container = document.getElementById('messages');
            if (container) container.style.opacity = '0';
            requestAnimationFrame(() => {
                this.currentId = id;
                this.drawerOpen = false;
                if (container) { container.offsetHeight; container.style.opacity = '1'; }
                if (typeof renderMessages === 'function') renderMessages();
                this._save();
            });
        },

        deleteConversation(convId) {
            const idx = this.conversations.findIndex(c => c.id === convId);
            if (idx < 0) return;
            const title = this.conversations[idx].title || '新对话';
            this.confirmTitle = '删除对话';
            this.confirmMsg = '确定删除 "' + title + '" 吗？';
            this.confirmAction = () => {
                this.conversations.splice(idx, 1);
                if (this.currentId === convId) {
                    this.currentId = this.conversations.length > 0 ? this.conversations[0].id : null;
                    if (!this.currentId) this.newConv(); else if (typeof renderMessages === 'function') renderMessages();
                }
                this._save();
            };
            this.showConfirmModal = true;
        },

        // ═══════════════════════════════════════════════
        // 收藏夹管理
        // ═══════════════════════════════════════════════

        openFolderModal(editId) {
            if (editId) {
                const f = this.folders.find(f => f.id === editId);
                if (!f) return;
                this.folderModalEditId = editId;
                this.folderModalName = f.name.replace(/^.\s/, ''); // strip emoji prefix
                this.folderModalIcon = f.icon;
            } else {
                this.folderModalEditId = null;
                this.folderModalName = '';
                this.folderModalIcon = '📁';
            }
            this.folderModalError = '';
            this.showFolderModal = true;
        },

        closeFolderModal() {
            this.showFolderModal = false;
            this.folderModalEditId = null;
            this.folderModalError = '';
        },

        submitFolder() {
            const name = this.folderModalName.trim();
            if (!name) { this.folderModalError = '请输入名称'; return; }
            if (name.length > 20) { this.folderModalError = '名称不能超过 20 个字符'; return; }

            if (this.folderModalEditId) {
                const f = this.folders.find(f => f.id === this.folderModalEditId);
                if (f) { f.name = name; f.icon = this.folderModalIcon; }
            } else {
                const id = 'f_' + Date.now().toString(36);
                this.folders.push({ id, name, icon: this.folderModalIcon, order: this.folders.length });
            }
            this.closeFolderModal();
            this._save();
        },

        deleteFolder() {
            const f = this.folders.find(f => f.id === this.ctxFolderId);
            if (!f) return;
            if (f.id === 'f_default') return; // 不能删默认收藏夹
            this.confirmTitle = '删除收藏夹';
            this.confirmMsg = '确定删除 "' + f.name + '" 吗？\n其中的对话将移至默认收藏夹。';
            this.confirmAction = () => {
                this.conversations.forEach(c => { if (c.folderId === f.id) c.folderId = 'f_default'; });
                const idx = this.folders.indexOf(f);
                this.folders.splice(idx, 1);
                if (this.drawerFolderId === f.id) this.drawerOpen = false;
                this._save();
            };
            this.showConfirmModal = true;
        },

        // ═══════════════════════════════════════════════
        // 抽屉
        // ═══════════════════════════════════════════════

        openDrawer(folderId) {
            this.drawerFolderId = folderId;
            this.drawerSearch = '';
            this.drawerOpen = true;
        },

        closeDrawer() {
            this.drawerOpen = false;
            this.drawerFolderId = null;
        },

        moveConvToFolder(convId, targetFolderId) {
            const conv = this.conversations.find(c => c.id === convId);
            if (conv) conv.folderId = targetFolderId;
            this._save();
        },

        togglePin(convId) {
            const conv = this.conversations.find(c => c.id === (convId || this.ctxConvId));
            if (conv) conv.pinned = !conv.pinned;
            this._save();
        },

        // ═══════════════════════════════════════════════
        // 提示词
        // ═══════════════════════════════════════════════

        openPromptModal() {
            this.promptListOpen = true;
            this.promptEditorOpen = false;
            this.showPromptModal = true;
        },

        closePromptModal() {
            this.showPromptModal = false;
            this.promptEditorOpen = false;
        },

        selectPrompt(id) {
            // 设置新对话默认提示词
            this.defaultPromptId = id || null;
            if (id) {
                const p = this.prompts.find(p => p.id === id);
                this.defaultPromptName = p ? p.name : null;
            } else {
                this.defaultPromptName = null;
            }
            // 如果当前对话是空的（无消息），同步更新当前对话和标题
            const conv = this.current;
            if (conv && (!conv.messages || conv.messages.length === 0)) {
                conv.promptId = id || null;
                conv.promptName = this.defaultPromptName;
                this._save();
            }
        },

        startAddPrompt() {
            this.promptEditId = null;
            this.promptEditName = '';
            this.promptEditContent = '';
            this.promptEditorOpen = true;
            this.promptListOpen = false;
        },

        startEditPrompt(id) {
            const p = this.prompts.find(p => p.id === id);
            if (!p) return;
            this.promptEditId = id;
            this.promptEditName = p.name;
            this.promptEditContent = p.content;
            this.promptEditorOpen = true;
            this.promptListOpen = false;
        },

        cancelEditPrompt() {
            this.promptEditorOpen = false;
            this.promptListOpen = true;
        },

        savePrompt() {
            const name = this.promptEditName.trim();
            const content = this.promptEditContent.trim();
            if (!name || !content) return;
            if (this.promptEditId) {
                const p = this.prompts.find(p => p.id === this.promptEditId);
                if (p) { p.name = name; p.content = content; }
            } else {
                const id = 'p_' + Date.now().toString(36);
                this.prompts.push({ id, name, content });
            }
            this.promptEditorOpen = false;
            this.promptListOpen = true;
            this._savePrompts();
        },

        deletePrompt(id) {
            const idx = this.prompts.findIndex(p => p.id === id);
            if (idx < 0) return;
            this.prompts.splice(idx, 1);
            // 清除引用此提示词的对话
            this.conversations.forEach(c => { if (c.promptId === id) c.promptId = null; });
            this._savePrompts();
            this._save();
        },

        _savePrompts() {
            if (!this._apiReady()) return;
            try { pywebview.api.savePrompts(JSON.stringify(this.prompts)); } catch (e) {}
        },

        viewCurrentPrompt() {
            const conv = this.current;
            if (!conv || !conv.promptId) return;
            const p = this.prompts.find(p => p.id === conv.promptId);
            if (!p) return;
            this.viewPromptContent = p.content;
            this.showViewPromptModal = true;
        },

        closeViewPrompt() {
            this.showViewPromptModal = false;
        },

        // ═══════════════════════════════════════════════
        // 主题 / 设置
        // ═══════════════════════════════════════════════

        setTheme(t) {
            this.theme = t;
            document.body.setAttribute('data-theme', t);
            if (this._apiReady()) {
                try { pywebview.api.setTheme(t); } catch (e) {}
            }
        },

        pickModel(val) {
            this.model = val;
            this._saveSettings();
        },

        toggleThinking() {
            this.thinking = !this.thinking;
            this._saveSettings();
        },

        pickEffort(val) {
            this.effort = val;
            this._saveSettings();
        },

        toggleSettingsPanel() {
            this.settingsCollapsed = !this.settingsCollapsed;
            this._saveSettings();
        },

        _saveSettings() {
            if (!this._apiReady()) return;
            try {
                pywebview.api.saveSettings(JSON.stringify({
                    model: this.model,
                    thinking: this.thinking ? '1' : '0',
                    effort: this.effort,
                    settings_collapsed: this.settingsCollapsed ? '1' : '0'
                }));
            } catch (e) {}
        },

        // ═══════════════════════════════════════════════
        // 消息操作
        // ═══════════════════════════════════════════════

        copyMessageText(idx) {
            const msgs = this.visibleMessages;
            if (idx < 0 || idx >= msgs.length) return;
            if (this._apiReady()) {
                try { pywebview.api.copyToClipboard(msgs[idx].content); } catch (e) {}
            }
        },

        copyAllText() {
            const conv = this.current;
            if (!conv) return;
            let text = '';
            conv.messages.filter(m => m.role !== 'system').forEach(m => {
                text += (m.role === 'user' ? '👤 我' : '🤖 DeepSeek') + '\n';
                if (m.reasoning_content) text += '[思考过程]\n' + m.reasoning_content + '\n';
                text += m.content + '\n\n';
            });
            if (this._apiReady()) {
                try { pywebview.api.copyToClipboard(text.trim()); } catch (e) {}
            }
        },

        rollbackTo(idx) {
            const msgs = this.visibleMessages;
            if (!msgs[idx] || msgs[idx].role !== 'assistant') return;
            this.rollbackIdx = idx;
            // 显示下一条用户消息的预览
            let preview = '';
            for (let i = idx + 1; i < msgs.length; i++) {
                if (msgs[i].role === 'user') { preview = msgs[i].content?.substring(0, 60) || ''; break; }
            }
            const hint = document.getElementById('rollbackHint');
            if (hint) hint.textContent = '将恢复输入框：\n"' + preview + '..."\n并删除此回复之后的所有消息';
            this.showRollbackModal = true;
        },

        confirmRollback() {
            const conv = this.current;
            if (!conv) return;
            const idx = this.rollbackIdx;
            if (idx < 0) return;
            // 在 visibleMessages 中找到被回退的 assistant 消息及其下一条 user 消息
            const visible = this.visibleMessages;
            if (visible[idx]?.role !== 'assistant') return;
            // 找下一条 user 消息
            let nextUserIdx = -1;
            for (let i = idx + 1; i < visible.length; i++) {
                if (visible[i].role === 'user') { nextUserIdx = i; break; }
            }
            if (nextUserIdx < 0) return;
            // 把下一条 user 消息内容放回输入框
            const input = document.getElementById('input');
            if (input) { input.value = visible[nextUserIdx].content; autoResize(); }
            // 在原始消息列表中找到该 user 消息的位置，删除它及之后所有内容
            const realIdx = conv.messages.indexOf(visible[nextUserIdx]);
            if (realIdx >= 0) {
                conv.messages = conv.messages.slice(0, realIdx);
            }
            this.showRollbackModal = false;
            this._save();
            if (typeof renderMessages === 'function') renderMessages();
        },

        closeRollbackModal() { this.showRollbackModal = false; },

        // ═══════════════════════════════════════════════
        // 消息右键菜单
        // ═══════════════════════════════════════════════

        onMsgCtx(e, idx) {
            e.preventDefault();
            this.ctxMsgIdx = idx;
            const menu = document.getElementById('msgCtxMenu');
            if (menu) {
                // 只有模型回复可以回退
                const msgs = this.visibleMessages;
                const isAssistant = msgs[idx] && msgs[idx].role === 'assistant';
                const rollbackItem = document.getElementById('rollbackItem');
                if (rollbackItem) rollbackItem.style.display = isAssistant ? '' : 'none';
                menu.style.display = 'block';
                menu.style.left = e.clientX + 'px';
                menu.style.top = e.clientY + 'px';
                this.ctxMenu = menu;
            }
        },

        hideAllMenus() {
            document.querySelectorAll('.context-menu').forEach(m => m.style.display = 'none');
            this.ctxMenu = null;
        },

        // ═══════════════════════════════════════════════
        // API Key
        // ═══════════════════════════════════════════════

        closeApiKeyModal() { this.showApiKeyModal = false; },

        async submitApiKey() {
            const key = this.apiKeyInput.trim();
            if (!key || !key.startsWith('sk-')) {
                this.apiKeyError = '请输入有效的 API Key（以 sk- 开头）';
                return;
            }
            this.apiKeyError = '';
            if (!this._apiReady()) return;
            try {
                const ok = await pywebview.api.setApiKey(key);
                if (ok) {
                    this.showApiKeyModal = false;
                } else {
                    this.apiKeyError = 'API Key 验证失败，请检查后重试';
                }
            } catch (e) {
                this.apiKeyError = '验证出错：' + e;
            }
        },

        // ═══════════════════════════════════════════════
        // 确认对话框
        // ═══════════════════════════════════════════════

        confirmConfirm() {
            if (this.confirmAction) this.confirmAction();
            this.showConfirmModal = false;
        },

        closeConfirmModal() { this.showConfirmModal = false; },

        // ═══════════════════════════════════════════════
        // 工具方法
        // ═══════════════════════════════════════════════

        _save() {
            if (!this._apiReady()) return;
            try {
                pywebview.api.saveState(
                    JSON.stringify(this.conversations),
                    JSON.stringify(this.folders),
                    this.currentId
                );
            } catch (e) {}
        },

        _scrollMessages() {
            requestAnimationFrame(() => {
                const container = document.getElementById('messages');
                if (container) container.scrollTop = container.scrollHeight;
            });
        },

        fmtRelative(ts) {
            if (!ts) return '';
            const diff = Date.now() - new Date(ts).getTime();
            const mins = Math.floor(diff / 60000);
            if (mins < 1) return '刚刚';
            if (mins < 60) return mins + '分钟前';
            const hours = Math.floor(mins / 60);
            if (hours < 24) return hours + '小时前';
            const days = Math.floor(hours / 24);
            if (days < 7) return days + '天前';
            return new Date(ts).toLocaleDateString('zh-CN');
        },

        fmtTime(ts) {
            if (!ts) return '';
            const d = new Date(ts);
            return d.getHours().toString().padStart(2,'0') + ':' +
                   d.getMinutes().toString().padStart(2,'0');
        },

        escapeHtml(str) {
            if (!str) return '';
            const d = document.createElement('div');
            d.textContent = str;
            return d.innerHTML;
        },

        folderDisplayName(f) {
            if (!f) return '';
            // strip emoji prefix if name starts with icon pattern (emoji + space)
            return f.name.replace(/^.[\u{1F000}-\u{1FFFF}]\s?/u, '').replace(/^.\s/, '');
        }
    });
});
