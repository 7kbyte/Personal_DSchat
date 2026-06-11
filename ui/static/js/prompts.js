// ==================== 提示词管理 ====================
let _editingPromptId = null;

function showPromptModal() {
    renderPromptList();
    document.getElementById('promptModal').style.display = 'flex';
    document.getElementById('promptEditor').style.display = 'none';
}

function closePromptModal() {
    document.getElementById('promptModal').style.display = 'none';
    _editingPromptId = null;
}

function renderPromptList() {
    var list = document.getElementById('promptList');
    var conv = getCurrent();
    var activeId = conv ? conv.promptId : null;
    var html = '';
    // "无提示词" 选项
    html += '<div class="prompt-item' + (!activeId ? ' active' : '') + '" onclick="selectPrompt(null)">'
        + '<span class="prompt-name" style="font-style:italic;color:var(--sub)">无提示词</span></div>';
    if (state.prompts && state.prompts.length > 0) {
        html += state.prompts.map(function(p) {
            var isActive = p.id === activeId;
            var preview = p.content ? p.content.replace(/\n/g, ' ').slice(0, 50) : '';
            if (p.content && p.content.length > 50) preview += '...';
            return '<div class="prompt-item' + (isActive ? ' active' : '') + '" onclick="selectPrompt(\'' + p.id + '\')">'
                + '<div style="flex:1;min-width:0">'
                + '<div class="prompt-name">' + escapeHtml(p.name) + '</div>'
                + (preview ? '<div class="prompt-content-preview">' + escapeHtml(preview) + '</div>' : '')
                + '</div>'
                + '<div class="prompt-actions" onclick="event.stopPropagation()">'
                + '<button class="prompt-act" onclick="editPrompt(\'' + p.id + '\')" title="编辑">✏️</button>'
                + '<button class="prompt-act del" onclick="deletePrompt(\'' + p.id + '\')" title="删除">🗑</button>'
                + '</div></div>';
        }).join('');
    }
    list.innerHTML = html;
    updatePromptCurrent();
}

function updatePromptCurrent() {
    var el = document.getElementById('promptCurrent');
    var conv = getCurrent();
    // 优先使用冻结的 promptName（对话开始时的提示词）
    if (conv && conv.promptName) {
        el.textContent = conv.promptName;
        el.style.color = 'var(--accent)';
    } else if (conv && conv.promptId) {
        var p = state.prompts.find(function(x) { return x.id === conv.promptId; });
        el.textContent = p ? p.name : '未设置';
        el.style.color = p ? 'var(--accent)' : 'var(--sub)';
    } else {
        el.textContent = '未设置';
        el.style.color = 'var(--sub)';
    }
}

function selectPrompt(id) {
    var conv = getCurrent();
    if (conv) {
        conv.promptId = id || null;
        renderPromptList();
        save();
        updateStatus();
    }
}

function addPrompt() {
    _editingPromptId = null;
    document.getElementById('promptNameInput').value = '';
    document.getElementById('promptContentInput').value = '';
    document.getElementById('promptEditor').style.display = 'block';
}

function editPrompt(id) {
    _editingPromptId = id;
    var p = state.prompts.find(function(x) { return x.id === id; });
    if (p) {
        document.getElementById('promptNameInput').value = p.name;
        document.getElementById('promptContentInput').value = p.content;
        document.getElementById('promptEditor').style.display = 'block';
    }
}

function cancelEditPrompt() {
    _editingPromptId = null;
    document.getElementById('promptEditor').style.display = 'none';
}

function savePrompt() {
    var name = document.getElementById('promptNameInput').value.trim();
    var content = document.getElementById('promptContentInput').value.trim();
    if (!name) return;
    if (_editingPromptId) {
        var p = state.prompts.find(function(x) { return x.id === _editingPromptId; });
        if (p) { p.name = name; p.content = content; }
    } else {
        var id = 'p_' + Date.now() + Math.random().toString(36).slice(2, 6);
        state.prompts.push({ id: id, name: name, content: content });
    }
    _editingPromptId = null;
    document.getElementById('promptEditor').style.display = 'none';
    renderPromptList();
    savePrompts();
}

function deletePrompt(id) {
    showConfirm('删除提示词', '确定删除此提示词吗？', '删除', function() {
        state.prompts = state.prompts.filter(function(p) { return p.id !== id; });
        state.conversations.forEach(function(c) { if (c.promptId === id) c.promptId = null; });
        renderPromptList();
        savePrompts();
        save();
    });
}

function savePrompts() {
    if (typeof pywebview === 'undefined' || !pywebview.api) return;
    try { pywebview.api.savePrompts(JSON.stringify(state.prompts)); } catch(e) {}
}

// 获取当前对话的提示词内容
function getCurrentPrompt() {
    var conv = getCurrent();
    if (!conv || !conv.promptId) return '';
    var p = state.prompts.find(function(x) { return x.id === conv.promptId; });
    return p ? p.content : '';
}
