const documentParams = new URLSearchParams(window.location.search);
const documentPath = documentParams.get('path') || '';
const requestedBenchmark = documentParams.get('benchmark') || '';
const OUTLINE_PREFERENCE_KEY = 'scicode.documentOutlineCollapsed';
const METADATA_PREFERENCE_KEY = 'scicode.documentMetadataCollapsed';
const documentEl = id => document.getElementById(id);
const documentEscape = (value = '') => String(value).replace(/[&<>"']/g, character => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
})[character]);

function normalizeDocumentPath(parts) {
  const output = [];
  parts.forEach(part => {
    if (!part || part === '.') return;
    if (part === '..') output.pop();
    else output.push(part);
  });
  return output;
}

function splitDocumentTarget(target = '') {
  const match = String(target).match(/^([^?#]*)(\?[^#]*)?(#.*)?$/);
  return { path: match?.[1] || '', query: match?.[2] || '', hash: match?.[3] || '' };
}

function benchmarkForDocument(path = documentPath) {
  const fromPath = path.match(/^benchmarks\/([^/]+)\//)?.[1] || '';
  return requestedBenchmark || fromPath;
}

function documentViewerUrl(path, hash = '') {
  const benchmark = benchmarkForDocument(path);
  return `document.html?path=${encodeURIComponent(path)}${benchmark ? `&benchmark=${encodeURIComponent(benchmark)}` : ''}${hash}`;
}

function codeViewerUrl(path, hash = '') {
  return `code.html?path=${encodeURIComponent(path)}${hash}`;
}

function documentResourceUrl(path) {
  return `/api/resources/${path.split('/').map(encodeURIComponent).join('/')}`;
}

function workspaceReadableResource(target = '') {
  try {
    const resource = new URL(target, window.location.href);
    const localHosts = new Set(['localhost', '127.0.0.1', '[::1]']);
    const sameWorkspace = resource.origin === window.location.origin
      || (localHosts.has(resource.hostname) && localHosts.has(window.location.hostname) && resource.port === window.location.port);
    if (!sameWorkspace || !resource.pathname.startsWith('/api/resources/')) return null;
    const path = resource.pathname.slice('/api/resources/'.length).split('/').map(decodeURIComponent).join('/');
    return /\.(?:md|py)$/i.test(path) ? { path, hash: resource.hash } : null;
  } catch {
    return null;
  }
}

function resolveDocumentUrl(target, sourcePath = documentPath) {
  if (!target || /^(mailto:|#|data:)/.test(target)) return target;
  const resource = workspaceReadableResource(target);
  if (resource) return /\.py$/i.test(resource.path) ? codeViewerUrl(resource.path, resource.hash) : documentViewerUrl(resource.path, resource.hash);
  if (/^https?:/.test(target)) return target;
  const { path, query, hash } = splitDocumentTarget(target);
  if (path.startsWith('/')) return `${path}${query}${hash}`;
  const resolved = normalizeDocumentPath([
    ...sourcePath.split('/').slice(0, -1),
    ...path.split('/'),
  ]).join('/');
  if (/\.md$/i.test(resolved)) return documentViewerUrl(resolved, hash);
  if (/\.py$/i.test(resolved)) return codeViewerUrl(resolved, hash);
  return `${documentResourceUrl(resolved)}${query}${hash}`;
}

function parseDocumentSource(source = '') {
  const raw = String(source || '');
  if (!raw.startsWith('---\n')) return { metadata: {}, markdown: raw };
  const end = raw.indexOf('\n---\n', 4);
  if (end < 0) return { metadata: {}, markdown: raw };
  let metadata = {};
  if (window.jsyaml) {
    try {
      const loaded = window.jsyaml.load(raw.slice(4, end));
      if (loaded && typeof loaded === 'object' && !Array.isArray(loaded)) metadata = loaded;
    } catch (error) {
      console.warn('Document frontmatter could not be parsed.', error);
    }
  }
  return { metadata, markdown: raw.slice(end + 5).replace(/^\s+/, '') };
}

function propertyLabel(key) {
  const labels = {
    status: 'Status', lab_id: 'Lab ID', idea_ids: 'Idea IDs',
    wiki_context: 'Wiki context', related_labs: 'Related labs',
  };
  if (labels[key]) return labels[key];
  return key.replaceAll('_', ' ').replace(/\b\w/g, character => character.toUpperCase());
}

function readableDocumentTarget(target) {
  const filename = String(target).split('/').pop()?.replace(/\.md$/i, '') || String(target);
  return filename.replaceAll('-', ' ').replace(/\b\w/g, character => character.toUpperCase());
}

function renderPropertyValue(key, value) {
  if (value === null || value === undefined || value === '' || (Array.isArray(value) && !value.length)) {
    return '<span class="property-empty">—</span>';
  }
  if (key === 'status') {
    const status = String(value).toLowerCase().replace(/[^a-z0-9-]/g, '-');
    return `<span class="property-status status-${documentEscape(status)}">${documentEscape(String(value).replaceAll('-', ' '))}</span>`;
  }
  const values = Array.isArray(value) ? value : [value];
  if (key === 'wiki_context') {
    return `<span class="property-links">${values.map(target => `<a href="${documentEscape(resolveDocumentUrl(String(target)))}">${documentEscape(readableDocumentTarget(target))}</a>`).join('')}</span>`;
  }
  if (key === 'idea_ids') {
    return `<span class="property-chips">${values.map(item => `<code>${documentEscape(item)}</code>`).join('')}</span>`;
  }
  if (Array.isArray(value)) {
    return `<span class="property-values">${values.map(item => `<span>${documentEscape(typeof item === 'object' ? JSON.stringify(item) : item)}</span>`).join('')}</span>`;
  }
  if (typeof value === 'object') return `<code>${documentEscape(JSON.stringify(value))}</code>`;
  return `<span>${documentEscape(value)}</span>`;
}

function renderDocumentProperties(metadata = {}) {
  const properties = documentEl('document-properties');
  const preferredOrder = ['status', 'lab_id', 'idea_ids', 'wiki_context', 'related_labs'];
  const keys = [
    ...preferredOrder.filter(key => Object.hasOwn(metadata, key)),
    ...Object.keys(metadata).filter(key => key !== 'document_type' && !preferredOrder.includes(key)),
  ];
  if (!keys.length) {
    properties.hidden = true;
    properties.innerHTML = '';
    return;
  }
  properties.innerHTML = `<button id="document-properties-toggle" class="document-properties-toggle" type="button" aria-controls="document-properties-table" aria-expanded="true" aria-label="Collapse document metadata" title="Collapse document metadata"><i class="fa-solid fa-chevron-down" aria-hidden="true"></i></button><table id="document-properties-table"><tbody>${keys.map(key => `<tr><th scope="row">${documentEscape(propertyLabel(key))}</th><td>${renderPropertyValue(key, metadata[key])}</td></tr>`).join('')}</tbody></table>`;
  properties.hidden = false;
  initializeDocumentPropertiesToggle();
}

function setDocumentPropertiesCollapsed(collapsed, persist = true) {
  const properties = documentEl('document-properties');
  const toggle = documentEl('document-properties-toggle');
  properties.classList.toggle('document-properties-collapsed', collapsed);
  toggle.setAttribute('aria-expanded', String(!collapsed));
  const label = collapsed ? 'Expand document metadata' : 'Collapse document metadata';
  toggle.setAttribute('aria-label', label);
  toggle.title = label;
  if (!persist) return;
  try {
    window.localStorage.setItem(METADATA_PREFERENCE_KEY, String(collapsed));
  } catch {
    // The properties table still works if local storage is unavailable.
  }
}

function initializeDocumentPropertiesToggle() {
  let collapsed = false;
  try {
    collapsed = window.localStorage.getItem(METADATA_PREFERENCE_KEY) === 'true';
  } catch {
    // Use the expanded default when local storage is unavailable.
  }
  setDocumentPropertiesCollapsed(collapsed, false);
  documentEl('document-properties-toggle').addEventListener('click', () => {
    setDocumentPropertiesCollapsed(!documentEl('document-properties').classList.contains('document-properties-collapsed'));
  });
}

function protectDocumentMath(value = '') {
  const codeTokens = [];
  const mathBlocks = [];
  const codeToken = index => `\uE000DOCUMENTCODE${index}\uE001`;
  let markdown = String(value || '').replace(/```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]*`/g, match => {
    codeTokens.push(match);
    return codeToken(codeTokens.length - 1);
  });
  const stashMath = match => {
    const index = mathBlocks.push(match) - 1;
    return `\n\n<div data-display-math="${index}"></div>\n\n`;
  };
  markdown = markdown
    .replace(/\$\$[\s\S]*?\$\$/g, stashMath)
    .replace(/\\\[[\s\S]*?\\\]/g, stashMath)
    .replace(/\uE000DOCUMENTCODE(\d+)\uE001/g, (_, index) => codeTokens[Number(index)]);
  return { markdown, mathBlocks };
}

function renderDocumentMarkdown(value = '') {
  const source = String(value || '');
  if (!window.marked || !window.DOMPurify) return `<p>${documentEscape(source)}</p>`;
  const { markdown, mathBlocks } = protectDocumentMath(source);
  const safeHtml = DOMPurify.sanitize(marked.parse(markdown, { breaks: false, gfm: true }), {
    USE_PROFILES: { html: true }
  });
  const template = document.createElement('template');
  template.innerHTML = safeHtml;
  template.content.querySelectorAll('[data-display-math]').forEach(placeholder => {
    const math = mathBlocks[Number(placeholder.dataset.displayMath)];
    if (math === undefined) return;
    placeholder.removeAttribute('data-display-math');
    placeholder.textContent = math;
  });
  template.content.querySelectorAll('a[href]').forEach(link => {
    const original = link.getAttribute('href');
    const href = resolveDocumentUrl(original);
    link.setAttribute('href', href);
    if (/^https?:/.test(href)) {
      link.target = '_blank';
      link.rel = 'noreferrer';
    }
  });
  template.content.querySelectorAll('img[src]').forEach(image => {
    image.setAttribute('src', resolveDocumentUrl(image.getAttribute('src')));
    image.setAttribute('loading', 'lazy');
  });
  return template.innerHTML;
}

function slugDocumentHeading(value, used) {
  const base = String(value).toLowerCase().trim()
    .replace(/[^\p{L}\p{N}\s-]/gu, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-') || 'section';
  const count = used.get(base) || 0;
  used.set(base, count + 1);
  return count ? `${base}-${count + 1}` : base;
}

function buildDocumentOutline(content) {
  const used = new Map();
  const headings = [...content.querySelectorAll('h2, h3')];
  headings.forEach(heading => {
    heading.id = slugDocumentHeading(heading.textContent, used);
  });
  const toc = documentEl('document-toc');
  toc.innerHTML = headings.length
    ? headings.map(heading => `<a class="toc-${heading.tagName.toLowerCase()}" href="#${encodeURIComponent(heading.id)}">${documentEscape(heading.textContent)}</a>`).join('')
    : '<span>No sections</span>';
}

function typesetDocumentMath(content) {
  if (!window.renderMathInElement) return;
  renderMathInElement(content, {
    delimiters: [
      { left: '$$', right: '$$', display: true },
      { left: '\\[', right: '\\]', display: true },
      { left: '\\(', right: '\\)', display: false },
      { left: '$', right: '$', display: false },
    ],
    throwOnError: false,
  });
}

function configureDocumentNavigation() {
  const benchmark = benchmarkForDocument();
  const back = documentEl('document-back');
  if (benchmark) {
    const labDocument = /\/labs\/[^/]+\/(?:PLAN|REPORT)\.md$/i.test(documentPath);
    back.href = `benchmark.html?id=${encodeURIComponent(benchmark)}${labDocument ? '#active-lab' : ''}`;
    back.querySelector('span').textContent = 'Back to benchmark';
  }
  documentEl('document-raw').href = documentResourceUrl(documentPath);
}

function setDocumentOutlineCollapsed(collapsed, persist = true) {
  document.body.classList.toggle('document-outline-collapsed', collapsed);
  const toggle = documentEl('document-outline-toggle');
  toggle.setAttribute('aria-expanded', String(!collapsed));
  const label = collapsed ? 'Show document outline' : 'Hide document outline';
  toggle.setAttribute('aria-label', label);
  toggle.title = label;
  if (!persist) return;
  try {
    window.localStorage.setItem(OUTLINE_PREFERENCE_KEY, String(collapsed));
  } catch {
    // The document reader still works if local storage is unavailable.
  }
}

function initializeDocumentOutlineToggle() {
  let collapsed = false;
  try {
    collapsed = window.localStorage.getItem(OUTLINE_PREFERENCE_KEY) === 'true';
  } catch {
    // Use the expanded default when local storage is unavailable.
  }
  setDocumentOutlineCollapsed(collapsed, false);
  documentEl('document-outline-toggle').addEventListener('click', () => {
    setDocumentOutlineCollapsed(!document.body.classList.contains('document-outline-collapsed'));
  });
}

function documentKind(path, metadata = {}) {
  if (metadata.document_type) return String(metadata.document_type).replaceAll('_', ' ').toUpperCase();
  const filename = path.split('/').pop() || 'document.md';
  if (/^PLAN\.md$/i.test(filename)) return 'LAB EXECUTION PLAN';
  if (/^REPORT\.md$/i.test(filename)) return 'LAB REPORT';
  if (/^TASK\.md$/i.test(filename)) return 'BENCHMARK SPECIFICATION';
  return 'MARKDOWN DOCUMENT';
}

async function loadDocument() {
  const content = documentEl('document-content');
  if (!documentPath || documentPath.startsWith('/') || documentPath.split('/').includes('..')) {
    content.innerHTML = '<div class="document-error"><strong>Invalid document path</strong><p>Return to the benchmark and choose a document again.</p></div>';
    documentEl('document-title').textContent = 'Document unavailable';
    documentEl('document-raw').hidden = true;
    return;
  }
  configureDocumentNavigation();
  documentEl('document-kind').textContent = documentKind(documentPath);
  documentEl('document-path').textContent = documentPath;
  try {
    const response = await fetch(documentResourceUrl(documentPath));
    if (!response.ok) throw new Error(response.status === 404 ? 'Document not found' : 'Document could not be loaded');
    const source = await response.text();
    const { metadata, markdown } = parseDocumentSource(source);
    const title = markdown.match(/^#\s+(.+)$/m)?.[1]?.trim() || documentPath.split('/').pop().replace(/\.md$/i, '');
    document.title = `${title} · Paper to Benchmark`;
    documentEl('document-title').textContent = title;
    documentEl('document-kind').textContent = documentKind(documentPath, metadata);
    renderDocumentProperties(metadata);
    content.innerHTML = renderDocumentMarkdown(markdown);
    const repeatedTitle = content.querySelector(':scope > h1:first-child');
    if (repeatedTitle?.textContent.trim() === title) repeatedTitle.remove();
    buildDocumentOutline(content);
    typesetDocumentMath(content);
    if (window.location.hash) {
      window.requestAnimationFrame(() => document.getElementById(decodeURIComponent(window.location.hash.slice(1)))?.scrollIntoView());
    }
  } catch (error) {
    content.innerHTML = `<div class="document-error"><strong>${documentEscape(error.message)}</strong><p>Use the back button to return to the benchmark.</p></div>`;
    documentEl('document-title').textContent = 'Document unavailable';
  }
}

initializeDocumentOutlineToggle();
loadDocument();
