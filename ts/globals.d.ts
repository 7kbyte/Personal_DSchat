// Type declarations for external globals in DeepSeek Chat

// ── pywebview bridge ──────────────────────────────────
declare var pywebview: {
    api: {
        loadState(): Promise<string>;
        saveState(convsJson: string, foldersJson: string, currentId: string): Promise<void>;
        hasApiKey(): Promise<string>;
        setApiKey(key: string): Promise<string>;
        getSidebarWidth(): Promise<number>;
        setSidebarWidth(w: number): Promise<void>;
        getTheme(): Promise<string>;
        setTheme(t: string): Promise<void>;
        loadSetting(key: string): Promise<string>;
        saveSetting(key: string, value: string): Promise<void>;
        saveSettings(json: string): Promise<void>;
        loadPrompts(): Promise<string>;
        savePrompts(json: string): Promise<void>;
        loadTokens(): Promise<string>;
        saveTokens(json: string): Promise<void>;
        getWindowRect(): Promise<string>;
        moveWindow(x: number, y: number): Promise<void>;
        resizeWindow(x: number, y: number, w: number, h: number): Promise<void>;
        minimizeWindow(): Promise<void>;
        maximizeWindow(): Promise<void>;
        restoreWindow(): Promise<void>;
        closeWindow(): Promise<void>;
        sendMessage(paramsJson: string): Promise<void>;
        stopGeneration(): Promise<void>;
        copyToClipboard(text: string): Promise<void>;
        openExternalLink(url: string): Promise<void>;
    };
} | undefined;

// ── Alpine.js globals ─────────────────────────────────
interface AlpineStore {
    conversations: ConvData[];
    folders: FolderData[];
    prompts: PromptData[];
    currentId: string | null;
    loading: boolean;
    model: string;
    thinking: boolean;
    effort: string;
    theme: string;
    settingsCollapsed: boolean;
    drawerOpen: boolean;
    drawerFolderId: string | null;
    drawerSearch: string;
    showFolderModal: boolean;
    folderModalEditId: string | null;
    folderModalName: string;
    folderModalIcon: string;
    folderModalError: string;
    showConfirmModal: boolean;
    confirmTitle: string;
    confirmMsg: string;
    confirmAction: (() => void) | null;
    showApiKeyModal: boolean;
    apiKeyInput: string;
    apiKeyError: string;
    showPromptModal: boolean;
    promptSearch: string;
    promptEditing: boolean;
    promptEditId: string | null;
    promptEditName: string;
    promptEditContent: string;
    showViewPromptModal: boolean;
    viewPromptContent: string;
    showRollbackModal: boolean;
    rollbackIdx: number;
    ctxMenu: HTMLElement | null;
    ctxMsgIdx: number;
    ctxConvId: string | null;
    ctxFolderId: string | null;
    defaultPromptId: string | null;
    defaultPromptName: string | null;
    globalTokens: number;
    globalCacheHitTokens: number;
    globalCacheMissTokens: number;
    globalCompletionTokens: number;
    online: boolean;
    presetIcons: string[];
    readonly current: ConvData | undefined;
    readonly pinnedConversations: ConvData[];
    readonly currentFolder: FolderData | undefined;
    readonly drawerConversations: ConvData[];
    readonly visibleMessages: MessageData[];
    readonly hasMessages: boolean;
    readonly currentPromptName: string;
    readonly filteredPrompts: PromptData[];
    readonly statusText: string;
    init(): Promise<void>;
    newConv(): void;
    switchConv(id: string): void;
    deleteConversation(convId: string): void;
    openFolderModal(editId?: string): void;
    closeFolderModal(): void;
    submitFolder(): void;
    deleteFolder(): void;
    openDrawer(folderId: string): void;
    closeDrawer(): void;
    moveConvToFolder(convId: string, targetFolderId: string): void;
    togglePin(convId?: string): void;
    openPromptModal(): void;
    closePromptModal(): void;
    selectPrompt(id: string | null): void;
    startAddPrompt(): void;
    startEditPrompt(id: string): void;
    cancelEditPrompt(): void;
    savePrompt(): void;
    deletePrompt(id: string): void;
    viewCurrentPrompt(): void;
    closeViewPrompt(): void;
    setTheme(t: string): void;
    pickModel(val: string): void;
    toggleThinking(): void;
    pickEffort(val: string): void;
    toggleSettingsPanel(): void;
    copyMessageText(idx: number): void;
    copyAllText(): void;
    rollbackTo(idx: number): void;
    confirmRollback(): void;
    closeRollbackModal(): void;
    onMsgCtx(e: MouseEvent, idx: number): void;
    hideAllMenus(): void;
    closeApiKeyModal(): void;
    submitApiKey(): Promise<void>;
    confirmConfirm(): void;
    closeConfirmModal(): void;
    _save(): void;
    _savePrompts(): void;
    _saveSettings(): void;
    _apiReady(): boolean;
    _restoreSettingsUI(): void;
    fmtRelative(ts: string | number): string;
    fmtTime(ts: string | number): string;
    escapeHtml(str: string): string;
    folderDisplayName(f: FolderData): string;
    _scrollMessages(): void;
}

interface AlpineStatic {
    store(name: string): AlpineStore;
    store(name: string, value: any): void;
}

declare var Alpine: AlpineStatic;
declare var $store: { app: AlpineStore };

// ── App data types ─────────────────────────────────────
interface ConvData {
    id: string;
    title: string;
    messages: MessageData[];
    pinned: boolean;
    folderId?: string;
    promptId?: string | null;
    promptName?: string | null;
    updatedAt?: number;
    promptTokens?: number;
    completionTokens?: number;
    totalTokens?: number;
    cacheHitTokens?: number;
    cacheMissTokens?: number;
}

interface MessageData {
    role: 'user' | 'assistant' | 'system';
    content: string;
    reasoning_content?: string;
    timestamp?: number;
}

interface FolderData {
    id: string;
    name: string;
    icon: string;
    order: number;
}

interface PromptData {
    id: string;
    name: string;
    content: string;
}

// ── Global functions ───────────────────────────────────
declare function renderMarkdown(text: string): string;
declare function renderMessages(): void;
declare function setupWindowDrag(): void;
declare function setSidebarWidth(w: number): void;
declare function setDrawerWidth(w: number): void;
declare function setLoading(on: boolean): void;
declare function stopGeneration(): Promise<void>;
declare function autoResize(e?: Event): void;
declare function onResizeStart(dir: string, e: MouseEvent): void;
declare function onMaximizeToggle(): Promise<void>;
declare function send(): Promise<void>;
declare function regenerate(): void;
declare function onKeyDown(e: KeyboardEvent): void;
declare function onFolderDragStart(e: DragEvent, folderId: string): void;
declare function onFolderDragEnd(e: DragEvent): void;
declare function onFolderDragOver(e: DragEvent): void;
declare function onFolderDragLeave(e: DragEvent): void;
declare function onFolderDrop(e: DragEvent, targetFolderId: string): void;
declare function onPinnedDragStart(e: DragEvent, convId: string): void;
declare function onPinnedDragEnd(e: DragEvent): void;
declare function onPinnedDragOver(e: DragEvent): void;
declare function onPinnedDragLeave(e: DragEvent): void;
declare function onPinnedDrop(e: DragEvent, targetConvId: string): void;
declare function onDrawerConvDragStart(e: DragEvent, convId: string): void;
declare function onDrawerConvDragEnd(e: DragEvent): void;
declare function onDrawerConvDragOver(e: DragEvent): void;
declare function onDrawerConvDragLeave(e: DragEvent): void;
declare function onDrawerConvDrop(e: DragEvent, targetConvId: string): void;

// ── Window globals ─────────────────────────────────────
declare var pywebviewReady: boolean;
declare var _winX: number;
declare var _winY: number;
declare var _winW: number;
declare var _winH: number;
