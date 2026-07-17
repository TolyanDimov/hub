(() => {
  document.querySelectorAll('[data-year]').forEach((node) => {
    node.textContent = new Date().getFullYear();
  });

  const markdownRoot = document.querySelector('[data-markdown-src]');
  if (!markdownRoot) return;

  const source = markdownRoot.dataset.markdownSrc;
  const toc = document.querySelector('[data-toc]');

  const slugify = (value) => value
    .toLocaleLowerCase('ru')
    .trim()
    .replace(/[“”"'`.,:;!?()[\]{}$\\/]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-');

  const escapeHtml = (value) => value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  const protectMath = (markdown) => {
    const formulas = [];
    const pattern = /\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\]|(?<!\$)\$(?!\$)[^\n$]+?\$(?!\$)/g;
    const text = markdown.replace(pattern, (formula) => {
      const token = `MATHX${formulas.length}XPLACEHOLDER`;
      formulas.push({ token, formula });
      return token;
    });
    return { text, formulas };
  };

  const typesetMath = () => {
    if (!window.MathJax) return;
    const render = () => window.MathJax.typesetPromise?.([markdownRoot]);
    if (window.MathJax.startup?.promise) {
      window.MathJax.startup.promise.then(render).catch(() => {});
    } else {
      render();
    }
  };

  fetch(source)
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.text();
    })
    .then((raw) => {
      const withoutFrontMatter = raw.replace(/^---\s*[\r\n]+[\s\S]*?[\r\n]+---\s*[\r\n]+/, '');
      const protectedMarkdown = protectMath(withoutFrontMatter);
      const html = window.marked.parse(protectedMarkdown.text, { gfm: true, breaks: false });
      let sanitized = window.DOMPurify.sanitize(html, {
        ADD_ATTR: ['target'],
        USE_PROFILES: { html: true }
      });
      protectedMarkdown.formulas.forEach(({ token, formula }) => {
        sanitized = sanitized.replaceAll(token, escapeHtml(formula));
      });
      markdownRoot.innerHTML = sanitized;

      const used = new Map();
      const headings = [...markdownRoot.querySelectorAll('h1, h2')];
      headings.forEach((heading) => {
        const base = slugify(heading.textContent) || 'section';
        const count = used.get(base) || 0;
        used.set(base, count + 1);
        heading.id = count ? `${base}-${count + 1}` : base;
      });

      markdownRoot.querySelectorAll('a[href^="#"]').forEach((link) => {
        const wanted = decodeURIComponent(link.getAttribute('href').slice(1));
        const match = headings.find((heading) => heading.id === wanted || slugify(heading.textContent) === slugify(wanted));
        if (match) link.setAttribute('href', `#${match.id}`);
      });

      if (toc) {
        toc.innerHTML = '<strong>Содержание</strong>' + headings
          .slice(0, 80)
          .map((heading) => `<a class="toc-${heading.tagName.toLowerCase()}" href="#${heading.id}">${heading.textContent}</a>`)
          .join('');
      }

      typesetMath();
    })
    .catch(() => {
      markdownRoot.innerHTML = `<div class="notice">Не удалось загрузить текст статьи. <a href="${source}">Открыть исходный Markdown</a>.</div>`;
    });
})();
