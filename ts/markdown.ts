// ==================== KaTeX + marked (TypeScript) ====================
// @ts-ignore - marked is loaded from CDN
marked.setOptions({ breaks: true, gfm: true });

function renderMarkdown(text: string): string {
  const latexBlocks: { type: 'block' | 'inline'; tex: string }[] = [];
  let processed = text
    .replace(/\\\[([\s\S]*?)\\\]/g, (_, tex: string) => { latexBlocks.push({ type: 'block', tex: tex.trim() }); return '\x00LB' + (latexBlocks.length - 1) + '\x00'; })
    .replace(/\\\(([\s\S]*?)\\\)/g, (_, tex: string) => { latexBlocks.push({ type: 'inline', tex: tex.trim() }); return '\x00LI' + (latexBlocks.length - 1) + '\x00'; })
    .replace(/\$\$([\s\S]*?)\$\$/g, (_, tex: string) => { latexBlocks.push({ type: 'block', tex: tex.trim() }); return '\x00LB' + (latexBlocks.length - 1) + '\x00'; })
    .replace(/\$([^$]+?)\$/g, (_, tex: string) => { latexBlocks.push({ type: 'inline', tex: tex.trim() }); return '\x00LI' + (latexBlocks.length - 1) + '\x00'; });

  // @ts-ignore - marked is loaded from CDN
  let html: string = marked.parse(processed);

  html = html.replace(/\x00LB(\d+)\x00/g, (_, i: string) => {
    const lb = latexBlocks[parseInt(i)];
    try {
      // @ts-ignore - katex from CDN
      return katex.renderToString(lb.tex, { displayMode: true, throwOnError: false });
    } catch (e) {
      return '<code>' + escapeHtml(lb.tex) + '</code>';
    }
  });
  html = html.replace(/\x00LI(\d+)\x00/g, (_, i: string) => {
    const lb = latexBlocks[parseInt(i)];
    try {
      // @ts-ignore - katex from CDN
      return katex.renderToString(lb.tex, { displayMode: false, throwOnError: false });
    } catch (e) {
      return '<code>' + escapeHtml(lb.tex) + '</code>';
    }
  });
  return html;
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

function isNarrowContent(el: HTMLElement): boolean {
  if (el.querySelector('pre, .katex, .katex-display, table, blockquote, ul, ol, h1, h2, h3, h4, img')) return false;
  const clone = el.cloneNode(true) as HTMLElement;
  const reasoning = clone.querySelector('.reasoning-toggle, .reasoning-content');
  if (reasoning) reasoning.remove();
  const text = clone.textContent || '';
  return text.length < 180 && !text.includes('\n');
}
