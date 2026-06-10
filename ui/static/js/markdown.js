// ==================== KaTeX + marked ====================
marked.setOptions({ breaks: true, gfm: true });

function renderMarkdown(text) {
    const latexBlocks = [];
    let processed = text
        .replace(/\\\[([\s\S]*?)\\\]/g, (_, tex) => { latexBlocks.push({ type: 'block', tex: tex.trim() }); return '\x00LB' + (latexBlocks.length - 1) + '\x00'; })
        .replace(/\\\(([\s\S]*?)\\\)/g, (_, tex) => { latexBlocks.push({ type: 'inline', tex: tex.trim() }); return '\x00LI' + (latexBlocks.length - 1) + '\x00'; })
        .replace(/\$\$([\s\S]*?)\$\$/g, (_, tex) => { latexBlocks.push({ type: 'block', tex: tex.trim() }); return '\x00LB' + (latexBlocks.length - 1) + '\x00'; })
        .replace(/\$([^$]+?)\$/g, (_, tex) => { latexBlocks.push({ type: 'inline', tex: tex.trim() }); return '\x00LI' + (latexBlocks.length - 1) + '\x00'; });

    let html = marked.parse(processed);

    html = html.replace(/\x00LB(\d+)\x00/g, (_, i) => {
        const lb = latexBlocks[parseInt(i)];
        try { return katex.renderToString(lb.tex, { displayMode: true, throwOnError: false }); }
        catch(e) { return '<code>' + escapeHtml(lb.tex) + '</code>'; }
    });
    html = html.replace(/\x00LI(\d+)\x00/g, (_, i) => {
        const lb = latexBlocks[parseInt(i)];
        try { return katex.renderToString(lb.tex, { displayMode: false, throwOnError: false }); }
        catch(e) { return '<code>' + escapeHtml(lb.tex) + '</code>'; }
    });
    return html;
}

function escapeHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
}

function isNarrowContent(el) {
    // 包含代码块、公式、表格、引用、列表、标题 → 宽气泡
    if (el.querySelector('pre, .katex, .katex-display, table, blockquote, ul, ol, h1, h2, h3, h4, img')) return false;
    // 去掉思考过程后检查文本长度
    var clone = el.cloneNode(true);
    var t = clone.querySelector('.reasoning-toggle'); if (t) t.remove();
    var c = clone.querySelector('.reasoning-content'); if (c) c.remove();
    var text = clone.textContent.replace(/\s+/g, '');  // 去除所有空白字符
    if (text.length > 300) return false;
    return true;
}
