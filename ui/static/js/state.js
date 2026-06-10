// ==================== 图标预设 ====================
const PRESET_ICONS = ['📁','💼','🏠','🎓','💡','🚀','🎮','🎵','📚','❤️','🌟','🔥','🌈','🍕','🐱','💰','⚡','🎯','🌍','📝'];

// ==================== 状态 ====================
let state = {
    conversations: [], folders: [], currentId: null, loading: false,
    drawerOpen: false, drawerFolderId: null,
    ctxMsgIdx: -1, deleteIdx: -1, ctxConvId: null, ctxFolderId: null,
    folderModalId: null
};
let pywebviewReady = false;
