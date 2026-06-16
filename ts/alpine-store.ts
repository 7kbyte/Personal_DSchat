/**
 * Alpine.js 全局 Store — 单一响应式状态源 (TypeScript)
 */
document.addEventListener('alpine:init', () => {
  Alpine.store('app', {
    // ── 核心数据 ─────────────────────────────────
    conversations: [] as ConvData[],
    folders: [] as FolderData[],
    prompts: [] as PromptData[],
    currentId: null as string | null,
    loading: false,

    // ── 设置 ─────────────────────────────────────
    model: 'deepseek-v4-pro',
    thinking: true,
    effort: 'high',
    theme: 'light',
    settingsCollapsed: false,

    // ── UI 状态 ──────────────────────────────────
    drawerOpen: false,
    drawerFolderId: null as string | null,
    drawerSearch: '',

    showFolderModal: false,
    folderModalEditId: null as string | null,
    folderModalName: '',
    folderModalIcon: '📁',
    folderModalError: '',

    showConfirmModal: false,
    confirmTitle: '',
    confirmMsg: '',
    confirmAction: null as (() => void) | null,

    showApiKeyModal: false,
    apiKeyInput: '',
    apiKeyError: '',

    showPromptModal: false,
    promptSearch: '',
    promptEditing: false,
    promptEditId: null as string | null,
    promptEditName: '',
    promptEditContent: '',

    showViewPromptModal: false,
    viewPromptContent: '',

    showRollbackModal: false,
    rollbackIdx: -1,

    ctxMenu: null as HTMLElement | null,
    ctxMsgIdx: -1,
    ctxConvId: null as string | null,
    ctxFolderId: null as string | null,

    defaultPromptId: null as string | null,
    defaultPromptName: null as string | null,

    // Token 统计
    globalTokens: 0,

    // 联网状态（由 API 调用结果更新）
    online: true,

    presetIcons: ['📁','💼','🏠','🎓','💡','🚀','🎮','🎵','📚','❤️','🌟','🔥','🌈','🍕','🐱','💰','⚡','🎯','🌍','📝'],

    // ═══════════════════════════════════════════════
    // 计算属性
    // ═══════════════════════════════════════════════

    get current(): ConvData | undefined {
      return this.conversations.find((c: ConvData) => c.id === this.currentId);
    },

    get pinnedConversations(): ConvData[] {
      return this.conversations.filter((c: ConvData) => c.pinned && c.messages && c.messages.length > 0);
    },

    get currentFolder(): FolderData | undefined {
      const f = this.folders.find((f: FolderData) => f.id === this.drawerFolderId);
      return f ? { ...f, displayName: f.name.replace(/^.\s/, '') } as any : undefined;
    },

    get drawerConversations(): ConvData[] {
      const q = (this.drawerSearch || '').toLowerCase();
      let convs = this.conversations.filter((c: ConvData) => c.folderId === this.drawerFolderId);
      if (q) convs = convs.filter((c: ConvData) => (c.title || '新对话').toLowerCase().includes(q));
      return convs;
    },

    get visibleMessages(): MessageData[] {
      const conv = this.current;
      if (!conv || !conv.messages) return [];
      return conv.messages.filter((m: MessageData) => m.role !== 'system');
    },

    get hasMessages(): boolean {
      return this.visibleMessages.length > 0;
    },

    get currentPromptName(): string {
      const conv = this.current;
      if (!conv || !conv.promptId) return '无提示词';
      if (conv.promptName) return conv.promptName;
      const p = this.prompts.find((p: PromptData) => p.id === conv.promptId);
      return p ? p.name : '无提示词';
    },

    get filteredPrompts(): PromptData[] {
      const q = (this.promptSearch || '').toLowerCase();
      if (!q) return this.prompts;
      return this.prompts.filter((p: PromptData) =>
        p.name.toLowerCase().includes(q) || p.content.toLowerCase().includes(q)
      );
    },

    get statusText(): string {
      const names: Record<string, string> = { 'deepseek-v4-pro': 'V4 Pro', 'deepseek-v4-flash': 'V4 Flash' };
      return names[this.model] || this.model;
    },

    // ═══════════════════════════════════════════════
    // 初始化
    // ═══════════════════════════════════════════════

    async init(): Promise<void> {
      if (!this._apiReady()) {
        setTimeout(() => this.init(), 300);
        return;
      }
      try {
        const raw = await pywebview!.api.loadState();
        const data = JSON.parse(raw);
        this.conversations = data.conversations || [];
        this.folders = data.folders || [];
        this.currentId = data.currentId || null;

        if (this.folders.length === 0) {
          this.folders = [{ id: 'f_default', name: '默认收藏夹', icon: '📁', order: 0 }];
        }

        const theme = await pywebview!.api.getTheme();
        if (theme) this.setTheme(theme);
        const model = await pywebview!.api.loadSetting('model');
        if (model) this.model = model;
        const thinking = await pywebview!.api.loadSetting('thinking');
        if (thinking) this.thinking = thinking === '1';
        const effort = await pywebview!.api.loadSetting('effort');
        if (effort) this.effort = effort;
        const sc = await pywebview!.api.loadSetting('settings_collapsed');
        if (sc) this.settingsCollapsed = sc === '1';

        const gt = await pywebview!.api.loadSetting('global_tokens');
        if (gt) this.globalTokens = parseInt(gt) || 0;

        const promptsRaw = await pywebview!.api.loadPrompts();
        if (promptsRaw) this.prompts = JSON.parse(promptsRaw);

        const rect = await pywebview!.api.getWindowRect();
        if (rect) {
          const r = JSON.parse(rect);
          window._winX = r.x; window._winY = r.y;
          window._winW = r.w; window._winH = r.h;
        }

        const sw = await pywebview!.api.getSidebarWidth();
        if (sw && typeof setSidebarWidth === 'function') setSidebarWidth(sw);
        const dw = await pywebview!.api.loadSetting('drawer_width');
        if (dw && typeof setDrawerWidth === 'function') setDrawerWidth(parseInt(dw));

        if (this.conversations.length === 0) {
          this.newConv();
        } else {
          if (!this.conversations.find((c: ConvData) => c.id === this.currentId)) {
            this.currentId = this.conversations[0].id;
          }
        }

        const hasKey = JSON.parse(await pywebview!.api.hasApiKey());
        if (hasKey.error !== 'network') this.online = true;
        if (!hasKey.ok) {
          if (hasKey.error === 'network') {
            this.online = false;
          } else {
            this.showApiKeyModal = true;
          }
        }

        this._restoreSettingsUI();

        if (typeof renderMessages === 'function') {
          requestAnimationFrame(() => renderMessages());
        }
      } catch (e) {
        console.error('[Alpine] init:', e);
      }

      setupWindowDrag();
      window.pywebviewReady = true;
    },

    _restoreSettingsUI(): void {
      // 分段控件现在由 Alpine :class 绑定驱动，此方法仅作兼容保留
      const modelBtns = document.querySelectorAll('#modelSeg .seg-btn');
      if (modelBtns.length > 0) {
        modelBtns.forEach(b => { b.classList.toggle('active', (b as HTMLElement).dataset.val === this.model); });
      }
      const effortBtns = document.querySelectorAll('#effortSeg .seg-btn');
      if (effortBtns.length > 0) {
        effortBtns.forEach(b => { b.classList.toggle('active', (b as HTMLElement).dataset.val === this.effort); });
      }
      const thinkToggle = document.getElementById('thinkToggle') as HTMLInputElement | null;
      if (thinkToggle) thinkToggle.checked = this.thinking;
    },

    _apiReady(): boolean {
      return typeof pywebview !== 'undefined' && !!(pywebview && pywebview.api);
    },

    // ═══════════════════════════════════════════════
    // 对话管理
    // ═══════════════════════════════════════════════

    newConv(): void {
      const cur = this.current;
      if (cur && (!cur.messages || cur.messages.length === 0)) {
        document.getElementById('input')?.focus();
        return;
      }
      const id = Date.now().toString() + Math.random().toString(36).slice(2, 8);
      const conv: ConvData = { id, title: '新对话', messages: [], pinned: false };
      if (this.defaultPromptId) {
        conv.promptId = this.defaultPromptId;
        conv.promptName = this.defaultPromptName;
      }
      this.conversations.unshift(conv);
      this.currentId = id;
      this._save();
      if (typeof renderMessages === 'function') renderMessages();
    },

    switchConv(id: string): void {
      const container = document.getElementById('messages');
      if (container) container.style.opacity = '0';
      requestAnimationFrame(() => {
        this.currentId = id;
        this.drawerOpen = false;
        if (container) { container.offsetHeight; container.style.opacity = '1'; }
        if (typeof renderMessages === 'function') renderMessages();
        this._save();
      });
    },

    deleteConversation(convId: string): void {
      const idx = this.conversations.findIndex((c: ConvData) => c.id === convId);
      if (idx < 0) return;
      const title = this.conversations[idx].title || '新对话';
      this.confirmTitle = '删除对话';
      this.confirmMsg = '确定删除 "' + title + '" 吗？';
      this.confirmAction = () => {
        this.conversations.splice(idx, 1);
        if (this.currentId === convId) {
          this.currentId = this.conversations.length > 0 ? this.conversations[0].id : null;
          if (!this.currentId) this.newConv();
          else if (typeof renderMessages === 'function') renderMessages();
        }
        this._save();
      };
      this.showConfirmModal = true;
    },

    // ═══════════════════════════════════════════════
    // 收藏夹管理
    // ═══════════════════════════════════════════════

    openFolderModal(editId?: string): void {
      if (editId) {
        const f = this.folders.find((f: FolderData) => f.id === editId);
        if (!f) return;
        this.folderModalEditId = editId;
        this.folderModalName = f.name.replace(/^.\s/, '');
        this.folderModalIcon = f.icon;
      } else {
        this.folderModalEditId = null;
        this.folderModalName = '';
        this.folderModalIcon = '📁';
      }
      this.folderModalError = '';
      this.showFolderModal = true;
    },

    closeFolderModal(): void {
      this.showFolderModal = false;
      this.folderModalEditId = null;
      this.folderModalError = '';
    },

    submitFolder(): void {
      const name = this.folderModalName.trim();
      if (!name) { this.folderModalError = '请输入名称'; return; }
      if (name.length > 20) { this.folderModalError = '名称不能超过 20 个字符'; return; }

      if (this.folderModalEditId) {
        const f = this.folders.find((f: FolderData) => f.id === this.folderModalEditId);
        if (f) { f.name = name; f.icon = this.folderModalIcon; }
      } else {
        const id = 'f_' + Date.now().toString(36);
        this.folders.push({ id, name, icon: this.folderModalIcon, order: this.folders.length });
      }
      this.closeFolderModal();
      this._save();
    },

    deleteFolder(): void {
      const f = this.folders.find((f: FolderData) => f.id === this.ctxFolderId);
      if (!f) return;
      if (f.id === 'f_default') return;
      this.confirmTitle = '删除收藏夹';
      this.confirmMsg = '确定删除 "' + f.name + '" 吗？\n其中的对话将移至默认收藏夹。';
      this.confirmAction = () => {
        this.conversations.forEach((c: ConvData) => { if (c.folderId === f.id) c.folderId = 'f_default'; });
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

    openDrawer(folderId: string): void {
      this.drawerFolderId = folderId;
      this.drawerSearch = '';
      this.drawerOpen = true;
    },

    closeDrawer(): void {
      this.drawerOpen = false;
      this.drawerFolderId = null;
    },

    moveConvToFolder(convId: string, targetFolderId: string): void {
      const conv = this.conversations.find((c: ConvData) => c.id === convId);
      if (conv) conv.folderId = targetFolderId;
      this._save();
    },

    togglePin(convId?: string): void {
      const id = convId || this.ctxConvId;
      const conv = this.conversations.find((c: ConvData) => c.id === id);
      if (conv) conv.pinned = !conv.pinned;
      this._save();
    },

    // ═══════════════════════════════════════════════
    // 提示词
    // ═══════════════════════════════════════════════

    openPromptModal(): void {
      this.promptSearch = '';
      this.promptEditing = false;
      this.promptEditId = null;
      this.promptEditName = '';
      this.promptEditContent = '';
      this.showPromptModal = true;
    },

    closePromptModal(): void {
      this.showPromptModal = false;
      this.promptEditing = false;
      this.promptSearch = '';
    },

    selectPrompt(id: string | null): void {
      this.defaultPromptId = id || null;
      if (id) {
        const p = this.prompts.find((p: PromptData) => p.id === id);
        this.defaultPromptName = p ? p.name : null;
      } else {
        this.defaultPromptName = null;
      }
      const conv = this.current;
      if (conv && (!conv.messages || conv.messages.length === 0)) {
        conv.promptId = id || null;
        conv.promptName = this.defaultPromptName;
        this._save();
      }
    },

    startAddPrompt(): void {
      this.promptEditId = null;
      this.promptEditName = '';
      this.promptEditContent = '';
      this.promptEditing = true;
    },

    startEditPrompt(id: string): void {
      const p = this.prompts.find((p: PromptData) => p.id === id);
      if (!p) return;
      this.promptEditId = id;
      this.promptEditName = p.name;
      this.promptEditContent = p.content;
      this.promptEditing = true;
    },

    cancelEditPrompt(): void {
      this.promptEditing = false;
      this.promptEditId = null;
      this.promptEditName = '';
      this.promptEditContent = '';
    },

    savePrompt(): void {
      const name = this.promptEditName.trim();
      const content = this.promptEditContent.trim();
      if (!name || !content) return;
      if (this.promptEditId) {
        const p = this.prompts.find((p: PromptData) => p.id === this.promptEditId);
        if (p) { p.name = name; p.content = content; }
      } else {
        const id = 'p_' + Date.now().toString(36);
        this.prompts.push({ id, name, content });
      }
      this.promptEditing = false;
      this.promptEditId = null;
      this.promptEditName = '';
      this.promptEditContent = '';
      this._savePrompts();
    },

    deletePrompt(id: string): void {
      const p = this.prompts.find((p: PromptData) => p.id === id);
      if (!p) return;
      this.confirmTitle = '删除提示词';
      const usageCount = this.conversations.filter((c: ConvData) => c.promptId === id).length;
      let msg = '确定删除 "' + p.name + '" 吗？';
      if (usageCount > 0) msg += '\n有 ' + usageCount + ' 个对话正在使用此提示词，删除后将恢复为无提示词。';
      this.confirmMsg = msg;
      this.confirmAction = () => {
        const idx = this.prompts.findIndex((pr: PromptData) => pr.id === id);
        if (idx < 0) return;
        this.prompts.splice(idx, 1);
        this.conversations.forEach((c: ConvData) => { if (c.promptId === id) { c.promptId = null; c.promptName = null; } });
        if (this.defaultPromptId === id) { this.defaultPromptId = null; this.defaultPromptName = null; }
        this._savePrompts();
        this._save();
      };
      this.showConfirmModal = true;
    },

    _savePrompts(): void {
      if (!this._apiReady()) return;
      try { pywebview!.api.savePrompts(JSON.stringify(this.prompts)); } catch (e) {}
    },

    viewCurrentPrompt(): void {
      const conv = this.current;
      if (!conv || !conv.promptId) return;
      const p = this.prompts.find((p: PromptData) => p.id === conv.promptId);
      if (!p) return;
      this.viewPromptContent = p.content;
      this.showViewPromptModal = true;
    },

    closeViewPrompt(): void {
      this.showViewPromptModal = false;
    },

    // ═══════════════════════════════════════════════
    // 主题 / 设置
    // ═══════════════════════════════════════════════

    setTheme(t: string): void {
      this.theme = t;
      document.body.setAttribute('data-theme', t);
      if (this._apiReady()) {
        try { pywebview!.api.setTheme(t); } catch (e) {}
      }
    },

    pickModel(val: string): void {
      this.model = val;
      this._saveSettings();
    },

    toggleThinking(): void {
      this.thinking = !this.thinking;
      this._saveSettings();
    },

    pickEffort(val: string): void {
      this.effort = val;
      this._saveSettings();
    },

    toggleSettingsPanel(): void {
      this.settingsCollapsed = !this.settingsCollapsed;
      this._saveSettings();
    },

    _saveSettings(): void {
      if (!this._apiReady()) return;
      try {
        pywebview!.api.saveSettings(JSON.stringify({
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

    copyMessageText(idx: number): void {
      const msgs = this.visibleMessages;
      if (idx < 0 || idx >= msgs.length) return;
      if (this._apiReady()) {
        try { pywebview!.api.copyToClipboard(msgs[idx].content); } catch (e) {}
      }
    },

    copyAllText(): void {
      const conv = this.current;
      if (!conv) return;
      let text = '';
      conv.messages.filter((m: MessageData) => m.role !== 'system').forEach((m: MessageData) => {
        text += (m.role === 'user' ? '👤 我' : '🤖 DeepSeek') + '\n';
        if (m.reasoning_content) text += '[思考过程]\n' + m.reasoning_content + '\n';
        text += m.content + '\n\n';
      });
      if (this._apiReady()) {
        try { pywebview!.api.copyToClipboard(text.trim()); } catch (e) {}
      }
    },

    rollbackTo(idx: number): void {
      const msgs = this.visibleMessages;
      if (!msgs[idx] || msgs[idx].role !== 'assistant') return;
      this.rollbackIdx = idx;
      let preview = '';
      for (let i = idx + 1; i < msgs.length; i++) {
        if (msgs[i].role === 'user') { preview = msgs[i].content?.substring(0, 60) || ''; break; }
      }
      const hint = document.getElementById('rollbackHint');
      if (hint) hint.textContent = '将恢复输入框：\n"' + preview + '..."\n并删除此回复之后的所有消息';
      this.showRollbackModal = true;
    },

    confirmRollback(): void {
      const conv = this.current;
      if (!conv) return;
      const idx = this.rollbackIdx;
      if (idx < 0) return;
      const visible = this.visibleMessages;
      if (visible[idx]?.role !== 'assistant') return;
      let nextUserIdx = -1;
      for (let i = idx + 1; i < visible.length; i++) {
        if (visible[i].role === 'user') { nextUserIdx = i; break; }
      }
      if (nextUserIdx < 0) return;
      const input = document.getElementById('input') as HTMLTextAreaElement | null;
      if (input) { input.value = visible[nextUserIdx].content; autoResize(); }
      const realIdx = conv.messages.indexOf(visible[nextUserIdx]);
      if (realIdx >= 0) {
        conv.messages = conv.messages.slice(0, realIdx);
      }
      this.showRollbackModal = false;
      this._save();
      if (typeof renderMessages === 'function') renderMessages();
    },

    closeRollbackModal(): void { this.showRollbackModal = false; },

    // ═══════════════════════════════════════════════
    // 消息右键菜单
    // ═══════════════════════════════════════════════

    onMsgCtx(e: MouseEvent, idx: number): void {
      e.preventDefault();
      this.ctxMsgIdx = idx;
      const menu = document.getElementById('msgCtxMenu');
      if (menu) {
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

    hideAllMenus(): void {
      document.querySelectorAll('.context-menu').forEach(m => ((m as HTMLElement).style.display = 'none'));
      this.ctxMenu = null;
    },

    // ═══════════════════════════════════════════════
    // API Key
    // ═══════════════════════════════════════════════

    closeApiKeyModal(): void { this.showApiKeyModal = false; },

    async submitApiKey(): Promise<void> {
      const key = this.apiKeyInput.trim();
      if (!key || !key.startsWith('sk-')) {
        this.apiKeyError = '请输入有效的 API Key（以 sk- 开头）';
        return;
      }
      this.apiKeyError = '';
      if (!this._apiReady()) return;
      try {
        const result = JSON.parse(await pywebview!.api.setApiKey(key));
        if (result.ok) {
          this.showApiKeyModal = false;
        } else if (result.error === 'network') {
          this.apiKeyError = '网络连接失败，请检查网络后重试';
        } else {
          this.apiKeyError = 'API Key 无效，请检查后重试';
        }
      } catch (e) {
        this.apiKeyError = '验证出错：' + e;
      }
    },

    // ═══════════════════════════════════════════════
    // 确认对话框
    // ═══════════════════════════════════════════════

    confirmConfirm(): void {
      if (this.confirmAction) this.confirmAction();
      this.showConfirmModal = false;
    },

    closeConfirmModal(): void { this.showConfirmModal = false; },

    // ═══════════════════════════════════════════════
    // 工具方法
    // ═══════════════════════════════════════════════

    _save(): void {
      if (!this._apiReady()) return;
      try {
        pywebview!.api.saveState(
          JSON.stringify(this.conversations),
          JSON.stringify(this.folders),
          this.currentId!
        );
      } catch (e) {}
    },

    _scrollMessages(): void {
      requestAnimationFrame(() => {
        const container = document.getElementById('messages');
        if (container) container.scrollTop = container.scrollHeight;
      });
    },

    fmtRelative(ts: string | number): string {
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

    fmtTime(ts: string | number): string {
      if (!ts) return '';
      const d = new Date(ts);
      return d.getHours().toString().padStart(2, '0') + ':' +
             d.getMinutes().toString().padStart(2, '0');
    },

    escapeHtml(str: string): string {
      if (!str) return '';
      const d = document.createElement('div');
      d.textContent = str;
      return d.innerHTML;
    },

    folderDisplayName(f: FolderData): string {
      if (!f) return '';
      return f.name.replace(/^.[\u{1F000}-\u{1FFFF}]\s?/u, '').replace(/^.\s/, '');
    },
  });
});
