const wikiState = {
  catalog: [], current: 'index', scope: 'global', scopeTitle: 'Global knowledge', browse: '',
  searchQuery: '', searchResults: [], searchMode: 'local', searching: false, refining: false,
  searchTimer: null, searchController: null, searchSequence: 0
};
let wikiSearchTimer;
const wikiEl = id => document.getElementById(id);
const wikiEscape = (value = '') => String(value).replace(/[&<>"']/g, character => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
})[character]);

function normalizePath(parts) {
  const normalized = [];
  parts.forEach(part => {
    if (!part || part === '.') return;
    if (part === '..') normalized.pop();
    else normalized.push(part);
  });
  return normalized;
}

function wikiRoute(pageId, scope = wikiState.scope) {
  return searchTargetHref({ kind: 'wiki', page_id: pageId, scope });
}

function wikiPageFromSearchResult(result) {
  if (result?.target?.kind !== 'wiki') throw new Error('Wiki search returned a non-wiki target');
  return {
    page_id: result.target.page_id,
    title: result.title,
    status: result.stage || 'active',
    search_result: result,
  };
}

function documentReaderHref(path, fragment = '') {
  const benchmark = path.match(/^benchmarks\/([^/]+)\//)?.[1];
  return `document.html?path=${encodeURIComponent(path)}${benchmark ? `&benchmark=${encodeURIComponent(benchmark)}` : ''}${fragment ? `#${encodeURIComponent(fragment)}` : ''}`;
}

function codeReaderHref(path, fragment = '') {
  return `code.html?path=${encodeURIComponent(path)}${fragment ? `#${encodeURIComponent(fragment)}` : ''}`;
}

function workspaceReadableResource(target = '') {
  try {
    const resource = new URL(target, window.location.href);
    const localHosts = new Set(['localhost', '127.0.0.1', '[::1]']);
    const sameWorkspace = resource.origin === window.location.origin
      || (localHosts.has(resource.hostname) && localHosts.has(window.location.hostname) && resource.port === window.location.port);
    if (!sameWorkspace || !resource.pathname.startsWith('/api/resources/')) return null;
    const path = resource.pathname.slice('/api/resources/'.length).split('/').map(decodeURIComponent).join('/');
    return /\.(?:md|py)$/i.test(path) ? { path, fragment: resource.hash.slice(1) } : null;
  } catch {
    return null;
  }
}

const WIKI_APP_PAGES = new Set([
  'index.html', 'papers.html', 'paper.html', 'benchmarks.html', 'benchmark.html',
  'wiki.html', 'talk.html', 'document.html', 'code.html',
]);

function wikiAppHref(path, suffix = '') {
  const normalized = String(path || '').replace(/^\/+/, '');
  const match = normalized.match(/^(?:dashboard\/(?:frontend\/pages\/)?)?([^/]+\.html)$/);
  return match && WIKI_APP_PAGES.has(match[1]) ? `/${match[1]}${suffix}` : '';
}

function wikiHref(target, pageId) {
  if (/^(mailto:|#)/.test(target)) return target;
  const resource = workspaceReadableResource(target);
  if (resource) return /\.py$/i.test(resource.path) ? codeReaderHref(resource.path, resource.fragment) : documentReaderHref(resource.path, resource.fragment);
  if (/^https?:/.test(target)) return target;
  const match = target.match(/^([^?#]*)([?#].*)?$/);
  const path = match?.[1] || target;
  const suffix = match?.[2] || '';
  const directAppHref = wikiAppHref(path, suffix);
  if (directAppHref) return directAppHref;
  const benchmarkId = wikiState.scope.startsWith('benchmark:') ? wikiState.scope.slice('benchmark:'.length) : '';
  const scopeRoot = benchmarkId ? ['benchmarks', benchmarkId, 'wiki'] : ['wiki'];
  const base = [...scopeRoot, ...pageId.split('/').slice(0, -1)];
  const resolved = normalizePath([...base, ...path.split('/')]);
  const joined = resolved.join('/');
  if (/\.md$/i.test(joined)) return documentReaderHref(joined, suffix.replace(/^#/, ''));
  if (/\.py$/i.test(joined)) return codeReaderHref(joined, suffix.replace(/^#/, ''));
  const resolvedAppHref = wikiAppHref(joined, suffix);
  if (resolvedAppHref) return resolvedAppHref;
  return `/api/resources/${resolved.map(encodeURIComponent).join('/')}${suffix}`;
}

function wikiSourceHref(ref) {
  if (/^https?:/.test(ref)) return ref;
  const [path, fragment = ''] = ref.split('#', 2);
  if (/\.md$/i.test(path)) return documentReaderHref(path, fragment);
  if (/\.py$/i.test(path)) return codeReaderHref(path, fragment);
  return `/api/resources/${path.split('/').map(encodeURIComponent).join('/')}${fragment ? `#${fragment}` : ''}`;
}

function inlineWikiMarkdown(raw, pageId) {
  const code = [];
  let text = String(raw).replace(/`([^`]+)`/g, (_, value) => {
    code.push(`<code>${wikiEscape(value)}</code>`);
    return `\u0000${code.length - 1}\u0000`;
  });
  text = wikiEscape(text);
  text = text.replace(/\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]/g, (_, target, label) => {
    const cleanTarget = target.trim();
    const scope = cleanTarget.startsWith('wiki/') ? 'global' : wikiState.scope;
    const page = cleanTarget.startsWith('wiki/') ? cleanTarget.slice(5) : cleanTarget;
    return `<a class="wikilink" href="${wikiRoute(page, scope)}">${(label || target).trim()}</a>`;
  });
  text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, target) => {
    const href = wikiHref(target, pageId);
    const external = /^https?:/.test(href) ? ' target="_blank" rel="noreferrer"' : '';
    return `<a href="${wikiEscape(href)}"${external}>${label}</a>`;
  });
  text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  return text.replace(/\u0000(\d+)\u0000/g, (_, index) => code[Number(index)]);
}

function renderWikiMarkdown(markdown, pageId) {
  const lines = markdown.split('\n');
  const html = [];
  let paragraph = [];
  let list = [];
  let code = [];
  let inCode = false;
  const flushParagraph = () => {
    if (!paragraph.length) return;
    html.push(`<p>${inlineWikiMarkdown(paragraph.join(' '), pageId)}</p>`);
    paragraph = [];
  };
  const flushList = () => {
    if (!list.length) return;
    html.push(`<ul>${list.map(item => `<li>${inlineWikiMarkdown(item, pageId)}</li>`).join('')}</ul>`);
    list = [];
  };
  lines.forEach(line => {
    if (line.startsWith('```')) {
      flushParagraph(); flushList();
      if (inCode) {
        html.push(`<pre><code>${wikiEscape(code.join('\n'))}</code></pre>`);
        code = [];
      }
      inCode = !inCode;
      return;
    }
    if (inCode) { code.push(line); return; }
    const heading = line.match(/^(#{1,4})\s+(.+)$/);
    const bullet = line.match(/^[-*]\s+(.+)$/);
    if (heading) {
      flushParagraph(); flushList();
      const level = Math.min(heading[1].length + 1, 5);
      html.push(`<h${level}>${inlineWikiMarkdown(heading[2], pageId)}</h${level}>`);
    } else if (bullet) {
      flushParagraph();
      list.push(bullet[1]);
    } else if (/^---+$/.test(line.trim())) {
      flushParagraph(); flushList(); html.push('<hr>');
    } else if (!line.trim()) {
      flushParagraph(); flushList();
    } else {
      paragraph.push(line.trim());
    }
  });
  flushParagraph(); flushList();
  if (code.length) html.push(`<pre><code>${wikiEscape(code.join('\n'))}</code></pre>`);
  return html.join('');
}

function typesetWikiMath(container) {
  if (typeof renderMathInElement !== 'function') return;
  renderMathInElement(container, {
    delimiters: [
      { left: '$$', right: '$$', display: true },
      { left: '$', right: '$', display: false },
      { left: '\\(', right: '\\)', display: false },
      { left: '\\[', right: '\\]', display: true },
    ],
    throwOnError: false,
  });
}

function wikiSearchStatus(query) {
  if (!query || wikiState.searchQuery !== query) return '';
  if (wikiState.refining) return ' · refining natural-language query…';
  if (wikiState.searching) return ' · searching concepts…';
  if (wikiState.searchMode === 'llm-refined') return ' · natural-language ranking';
  if (wikiState.searchMode.startsWith('hybrid')) return ' · semantic ranking';
  return '';
}

function setWikiListHtml(html) {
  const list = wikiEl('wiki-page-list');
  list.innerHTML = html;
  typesetWikiMath(list);
}

function wikiEntryBullet(page) {
  const type = String(page.page_type || 'reference');
  const label = `${type} knowledge page`;
  return `<i class="fa-solid fa-file-lines wiki-entry-bullet wiki-page-bullet" style="--wiki-type-color:${scicodeKnowledgeTypeColor(type)}" title="${wikiEscape(label)}" aria-label="${wikiEscape(label)}"></i>`;
}

function renderWikiList() {
  const query = wikiEl('wiki-search').value.trim().toLowerCase();
  wikiEl('wiki-search').closest('.search-control')?.classList.toggle('searching', wikiState.searching || wikiState.refining);
  const localWiki = wikiState.scope.startsWith('benchmark:');
  const pageLink = page => {
    const pageId = page.page_id;
    const status = page.status || '';
    const browseScore = !page.search_result && page.score !== undefined
      ? `<small>${Number(page.score).toFixed(1)}</small>`
      : '';
    const bullet = wikiEntryBullet(page);
    const inlineStatus = localWiki && pageId !== 'index' && status && status !== 'active'
      ? `<span class="wiki-page-status"> · ${wikiEscape(status)}</span>`
      : '';
    const title = `<span class="wiki-page-link-main">${bullet}<span class="wiki-page-link-title">${wikiEscape(page.title)}${inlineStatus}</span></span>`;
    return `<a href="${wikiRoute(pageId)}" data-wiki-page="${wikiEscape(pageId)}" class="${page.search_result ? 'wiki-search-result ' : ''}${pageId === wikiState.current ? 'active' : ''}">${title}${localWiki ? '' : browseScore}</a>`;
  };
  const browseButton = (label, value, count) => `<button type="button" class="wiki-browse-button ${wikiState.browse === value ? 'active' : ''}" data-wiki-browse="${wikiEscape(value)}"><span class="wiki-browse-label"><i class="fa-solid fa-folder" aria-hidden="true"></i><span>${wikiEscape(label)}</span></span>${count === undefined ? '' : `<small>${count}</small>`}</button>`;
  if (query) {
    const localFallback = wikiState.catalog.filter(page => `${page.title} ${page.summary} ${page.page_type} ${(page.topics || []).join(' ')}`.toLowerCase().includes(query));
    const results = wikiState.searchQuery === query ? wikiState.searchResults : localFallback;
    const status = wikiSearchStatus(query);
    const heading = wikiState.searchMode === 'local' ? 'Token + graph results' : `Knowledge results${status}`;
    setWikiListHtml(`<section><h2>${wikiEscape(heading)}</h2>${results.map(pageLink).join('') || '<p class="wiki-no-results">No matching pages.</p>'}</section>`);
    return;
  }
  if (localWiki) {
    const byId = id => wikiState.catalog.find(page => page.page_id === id);
    const ordered = pages => [...pages].sort((left, right) => String(right.updated).localeCompare(String(left.updated)) || left.title.localeCompare(right.title));
    const section = (heading, pages) => pages.length ? `<section><h2>${heading}</h2>${pages.map(pageLink).join('')}</section>` : '';
    const index = byId('index');
    const thesis = byId('thesis');
    const ideas = ordered(wikiState.catalog.filter(page => page.page_type === 'ideas'));
    const questions = ordered(wikiState.catalog.filter(page => page.page_type === 'question' || page.page_id.startsWith('questions/')));
    const claimed = new Set(['index', 'thesis', ...ideas.map(page => page.page_id), ...questions.map(page => page.page_id)]);
    const supporting = ordered(wikiState.catalog.filter(page => !claimed.has(page.page_id)));
    setWikiListHtml([
      section('Research map', index ? [index] : []),
      section('Current synthesis', thesis ? [thesis] : []),
      section('Ideas & hypotheses', ideas),
      section('Questions to resolve', questions),
      section('Supporting knowledge', supporting),
    ].join(''));
    return;
  }
  if (wikiState.browse) {
    const [kind, value] = wikiState.browse.split(':');
    const results = wikiState.catalog.filter(page => kind === 'topic' ? (page.topics || []).includes(value) : page.page_type === value);
    const heading = kind === 'topic' ? value : value;
    setWikiListHtml(`<section><button type="button" class="wiki-back-button" data-wiki-browse="">← Explore</button><h2>${wikiEscape(heading)}</h2>${results.map(pageLink).join('') || '<p class="wiki-no-results">No pages yet.</p>'}</section>`);
    return;
  }
  const topicOrder = ['Correlated Systems', 'Topological Phases', 'Quantum Information', 'Machine Learning'];
  const formatOrder = [['concept', 'Concepts'], ['method', 'Methods'], ['comparison', 'Comparisons'], ['model', 'Models'], ['implementation', 'Implementations']];
  const collections = wikiState.catalog.filter(page => ['papers/index', 'benchmarks/index'].includes(page.page_id));
  const projects = wikiState.catalog.filter(page => page.page_type === 'project');
  setWikiListHtml(`
    <section><h2>Start</h2>${['index', 'thesis'].map(id => wikiState.catalog.find(page => page.page_id === id)).filter(Boolean).map(pageLink).join('')}</section>
    <section><h2>Browse by topic</h2>${topicOrder.map(topic => browseButton(topic, `topic:${topic}`, wikiState.catalog.filter(page => (page.topics || []).includes(topic)).length)).join('')}</section>
    <section><h2>Browse by format</h2>${formatOrder.map(([type, label]) => browseButton(label, `type:${type}`, wikiState.catalog.filter(page => page.page_type === type).length)).join('')}</section>
    <section><h2>Collections</h2>${collections.map(pageLink).join('')}</section>
    <section><h2>Project</h2>${projects.map(pageLink).join('')}</section>
  `);
}

function scheduleWikiSearch() {
  clearTimeout(wikiSearchTimer);
  wikiState.searchController?.abort();
  const query = wikiEl('wiki-search').value.trim();
  wikiState.searchSequence += 1;
  const sequence = wikiState.searchSequence;
  wikiState.searchQuery = query.toLowerCase();
  wikiState.searchResults = [];
  wikiState.searchMode = 'local';
  wikiState.searching = query.length >= 2;
  wikiState.refining = false;
  if (!query) {
    wikiState.searchQuery = '';
    renderWikiList();
    return;
  }
  renderWikiList();
  if (query.length < 2) return;
  wikiSearchTimer = setTimeout(async () => {
    wikiState.searchController = new AbortController();
    try {
      const params = new URLSearchParams({ q: query, scope: wikiState.scope, limit: '20', refine: 'false' });
      const response = await fetch(`/api/wiki/search?${params}`, { cache: 'no-store', signal: wikiState.searchController.signal });
      if (!response.ok || sequence !== wikiState.searchSequence) throw new Error('Semantic search unavailable');
      const data = await response.json();
      if (wikiEl('wiki-search').value.trim() !== query || sequence !== wikiState.searchSequence) return;
      wikiState.searchResults = data.results.map(wikiPageFromSearchResult);
      wikiState.searchMode = data.mode || 'local';
      wikiState.searching = false;
      renderWikiList();
      if (!data.complex_query || wikiState.searchMode === 'local') return;
      wikiState.refining = true;
      renderWikiList();
      const refinedParams = new URLSearchParams({ q: query, scope: wikiState.scope, limit: '20', refine: 'true' });
      const refinedResponse = await fetch(`/api/wiki/search?${refinedParams}`, { cache: 'no-store', signal: wikiState.searchController.signal });
      if (!refinedResponse.ok || sequence !== wikiState.searchSequence) throw new Error('LLM refinement unavailable');
      const refined = await refinedResponse.json();
      if (wikiEl('wiki-search').value.trim() !== query || sequence !== wikiState.searchSequence) return;
      wikiState.searchResults = refined.results.map(wikiPageFromSearchResult);
      wikiState.searchMode = refined.mode || wikiState.searchMode;
      wikiState.refining = false;
      renderWikiList();
    } catch (error) {
      if (error.name === 'AbortError' || sequence !== wikiState.searchSequence) return;
      wikiState.searchMode = 'local';
      wikiState.searchResults = [];
      wikiState.searching = false;
      wikiState.refining = false;
      renderWikiList();
    }
  }, 180);
}

function sourceLabel(ref) {
  const parts = ref.split('#')[0].split('/');
  return parts[parts.length - 1] || ref;
}

async function loadWikiPage(pageId, push = false) {
  const benchmarkId = wikiState.scope.startsWith('benchmark:') ? wikiState.scope.slice('benchmark:'.length) : '';
  const endpoint = benchmarkId
    ? `/api/wiki/benchmark/${encodeURIComponent(benchmarkId)}/page/${pageId.split('/').map(encodeURIComponent).join('/')}`
    : `/api/wiki/page/${pageId.split('/').map(encodeURIComponent).join('/')}`;
  const response = await fetch(endpoint, { cache: 'no-store' });
  if (!response.ok) throw new Error('Wiki page not found');
  const page = await response.json();
  wikiState.current = page.page_id;
  if (push) history.pushState({ page: page.page_id, scope: wikiState.scope }, '', wikiRoute(page.page_id));
  renderWikiList();
  const article = wikiEl('wiki-article');
  article.innerHTML = `<div class="wiki-article-meta"><span>${wikiEscape(page.page_type)}</span>${page.updated ? `<time>${wikiEscape(page.updated)}</time>` : ''}</div>${renderWikiMarkdown(page.markdown, page.page_id)}`;
  typesetWikiMath(article);
  const sources = (page.source_refs || []).map(ref => `<a href="${wikiEscape(wikiSourceHref(ref))}" target="_blank">${wikiEscape(sourceLabel(ref))}<small>${wikiEscape(ref)}</small></a>`).join('');
  const backlinks = (page.backlinks || []).map(item => `<a href="${wikiRoute(item.page_id)}" data-wiki-page="${wikiEscape(item.page_id)}">${wikiEscape(item.title)}</a>`).join('');
  wikiEl('wiki-context').innerHTML = `
    <section><h2>Sources</h2>${sources || '<p>No registered sources.</p>'}</section>
    <section><h2>Linked from</h2>${backlinks || '<p>No backlinks yet.</p>'}</section>
  `;
  typesetWikiMath(wikiEl('wiki-context'));
  document.title = `${page.title} · Wiki · Paper to Benchmark`;
  window.scrollTo({ top: 0, behavior: 'auto' });
}

async function initializeWiki() {
  try {
    const params = new URLSearchParams(location.search);
    const requestedScope = params.get('scope') || 'global';
    wikiState.scope = /^benchmark:[a-z0-9]+(?:-[a-z0-9]+)*$/.test(requestedScope) ? requestedScope : 'global';
    const benchmarkId = wikiState.scope.startsWith('benchmark:') ? wikiState.scope.slice('benchmark:'.length) : '';
    const catalogEndpoint = benchmarkId ? `/api/wiki/benchmark/${encodeURIComponent(benchmarkId)}` : '/api/wiki';
    const response = await fetch(catalogEndpoint, { cache: 'no-store' });
    if (!response.ok) throw new Error('Could not load the wiki');
    const data = await response.json();
    wikiState.catalog = data.pages;
    wikiState.scopeTitle = data.title;
    wikiEl('wiki-scope-label').textContent = benchmarkId ? 'BENCHMARK WIKI' : 'GLOBAL WIKI';
    wikiEl('wiki-scope-title').textContent = benchmarkId ? data.title : 'Knowledge';
    if (benchmarkId) {
      wikiEl('wiki-search').placeholder = 'Search this benchmark';
      wikiEl('wiki-search').setAttribute('aria-label', 'Search benchmark research');
    }
    const requested = params.get('page') || 'index';
    wikiEl('wiki-search').addEventListener('input', scheduleWikiSearch);
    document.addEventListener('click', event => {
      const browse = event.target.closest('[data-wiki-browse]');
      if (browse) {
        event.preventDefault();
        wikiState.browse = browse.dataset.wikiBrowse;
        renderWikiList();
        return;
      }
      const link = event.target.closest('[data-wiki-page]');
      if (!link) return;
      event.preventDefault();
      loadWikiPage(link.dataset.wikiPage, true).catch(showWikiError);
    });
    window.addEventListener('popstate', () => loadWikiPage(new URLSearchParams(location.search).get('page') || 'index').catch(showWikiError));
    await loadWikiPage(requested);
  } catch (error) {
    showWikiError(error);
  }
}

function showWikiError(error) {
  wikiEl('wiki-article').innerHTML = `<div class="empty-state"><strong>${wikiEscape(error.message)}</strong><a href="wiki.html">Open the wiki index</a></div>`;
}

window.addEventListener('DOMContentLoaded', initializeWiki);
