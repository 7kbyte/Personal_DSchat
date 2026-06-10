// ==================== 启动 ====================
window.addEventListener('pywebviewready', () => init());
setTimeout(() => { if (!pywebviewReady) init(); }, 1500);
updateStatus();
