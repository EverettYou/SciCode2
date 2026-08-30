const params = new URLSearchParams(window.location.search);
const benchmarkId = params.get('id');
const globalTalk = document.body.dataset.page === 'project-talk';
let benchmarkState = null;
let selectedThreadId = params.get('thread');
const BENCHMARK_STAGE_OPTIONS = ['problem-opened', 'researching', 'solution-drafted', 'verified'];
let benchmarkStageMenuBound = false;

const byId = id => document.getElementById(id);
const escapeHtml = (value = '') => String(value).replace(/[&<>"']/g, character => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
})[character]);

function protectDisplayMath(value = '') {
  const codeTokens = [];
  const mathBlocks = [];
  const codeToken = index => `\uE000DASHBOARDCODE${index}\uE001`;
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
    .replace(/\uE000DASHBOARDCODE(\d+)\uE001/g, (_, index) => codeTokens[Number(index)]);
  return { markdown, mathBlocks };
}

function renderMarkdown(value = '') {
  const source = String(value || '');
  if (!window.marked || !window.DOMPurify) return escapeHtml(source).replace(/\n/g, '<br>');
  const { markdown, mathBlocks } = protectDisplayMath(source);
  const safeHtml = DOMPurify.sanitize(marked.parse(markdown, { breaks: true, gfm: true }), {
    USE_PROFILES: { html: true }
  });
  if (!mathBlocks.length) return safeHtml;
  const template = document.createElement('template');
  template.innerHTML = safeHtml;
  template.content.querySelectorAll('[data-display-math]').forEach(placeholder => {
    const math = mathBlocks[Number(placeholder.dataset.displayMath)];
    if (math === undefined) return;
    placeholder.removeAttribute('data-display-math');
    placeholder.textContent = math;
  });
  return template.innerHTML;
}

function normalizeProjectPath(parts) {
  const output = [];
  parts.forEach(part => {
    if (!part || part === '.') return;
    if (part === '..') output.pop();
    else output.push(part);
  });
  return output;
}

function benchmarkResourceHref(href, sourcePath = '') {
  if (!href || /^(mailto:|#|\/)/.test(href)) return href;
  const resource = workspaceReadableResource(href);
  if (resource) return /\.py$/i.test(resource.path) ? codeViewerHref(resource.path, resource.fragment) : documentViewerHref(resource.path, resource.fragment);
  if (/^https?:/.test(href)) return href;
  const [rawPath, fragment = ''] = href.split('#', 2);
  const resolved = normalizeProjectPath([
    ...sourcePath.split('/').slice(0, -1),
    ...rawPath.split('/'),
  ]).join('/');
  if (/\.md$/i.test(resolved)) return documentViewerHref(resolved, fragment);
  if (/\.py$/i.test(resolved)) return codeViewerHref(resolved, fragment);
  return `/api/resources/${resolved.split('/').map(encodeURIComponent).join('/')}${fragment ? `#${fragment}` : ''}`;
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

function documentViewerHref(path = '', fragment = '') {
  if (!path) return '#';
  const benchmark = benchmarkId ? `&benchmark=${encodeURIComponent(benchmarkId)}` : '';
  return `document.html?path=${encodeURIComponent(path)}${benchmark}${fragment ? `#${encodeURIComponent(fragment)}` : ''}`;
}

function codeViewerHref(path = '', fragment = '') {
  if (!path) return '#';
  return `code.html?path=${encodeURIComponent(path)}${fragment ? `#${encodeURIComponent(fragment)}` : ''}`;
}

function renderDocumentMarkdown(value = '', sourcePath = '') {
  const html = renderMarkdown(value);
  const template = document.createElement('template');
  template.innerHTML = html;
  template.content.querySelectorAll('a[href]').forEach(link => {
    const href = link.getAttribute('href');
    const routedHref = benchmarkResourceHref(href, sourcePath);
    link.setAttribute('href', routedHref);
    if (/^https?:/.test(routedHref)) {
      link.target = '_blank';
      link.rel = 'noreferrer';
    }
  });
  return template.innerHTML;
}

function typesetMath(element) {
  if (!window.renderMathInElement || !element) return;
  renderMathInElement(element, {
    delimiters: [
      { left: '$$', right: '$$', display: true },
      { left: '\\[', right: '\\]', display: true },
      { left: '\\(', right: '\\)', display: false },
      { left: '$', right: '$', display: false }
    ],
    throwOnError: false
  });
}

function statusLabel(value) {
  return escapeHtml(String(value || 'unknown').replaceAll('-', ' '));
}

function messageTypeClass(value) {
  return String(value || 'unknown').toLowerCase().replace(/[^a-z0-9-]/g, '-');
}

function formatLocalTimestamp(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value || '');
  const pad = part => String(part).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} | ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function nextAuthor(thread) {
  if (thread.status !== 'open') return null;
  const latest = [...(thread.messages || [])].reverse().find(message => !message.retracted);
  return latest?.author === 'agent' ? 'user' : 'agent';
}

function benchmarkStage(metadata) {
  return metadata.stage || 'problem-opened';
}

async function copyTextToClipboard(text) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.setAttribute('readonly', '');
  textarea.style.position = 'fixed';
  textarea.style.opacity = '0';
  document.body.appendChild(textarea);
  textarea.select();
  const copied = document.execCommand('copy');
  textarea.remove();
  if (!copied) throw new Error('Clipboard access is unavailable.');
}

function showCopyNotice(message, isError = false) {
  const notice = byId('copy-notice');
  if (!notice) return;
  notice.textContent = message;
  notice.classList.toggle('error', isError);
  notice.classList.add('visible');
  window.clearTimeout(showCopyNotice.timeout);
  showCopyNotice.timeout = window.setTimeout(() => notice.classList.remove('visible'), 1600);
}

const threadOptionDefaults = { category: 'task', priority: 'normal' };

function closeThreadOptionMenus(except = null) {
  document.querySelectorAll('.thread-option-menu').forEach(menu => {
    if (menu !== except) {
      menu.hidden = true;
      menu.parentElement.querySelector('.thread-option-value')?.setAttribute('aria-expanded', 'false');
    }
  });
}

function setThreadOption(kind, value) {
  const trigger = byId(`new-thread-${kind}-trigger`);
  const menu = byId(`new-thread-${kind}-menu`);
  trigger.dataset.value = value;
  trigger.textContent = value;
  trigger.className = `thread-option-value option-${kind}-${value}`;
  menu.querySelectorAll('[data-value]').forEach(option => {
    option.classList.toggle('selected', option.dataset.value === value);
  });
}

function resetThreadOptions() {
  Object.entries(threadOptionDefaults).forEach(([kind, value]) => setThreadOption(kind, value));
  closeThreadOptionMenus();
}

function bindThreadOptionPickers() {
  Object.keys(threadOptionDefaults).forEach(kind => {
    const trigger = byId(`new-thread-${kind}-trigger`);
    const menu = byId(`new-thread-${kind}-menu`);
    trigger.addEventListener('click', event => {
      event.stopPropagation();
      const willOpen = menu.hidden;
      closeThreadOptionMenus(menu);
      menu.hidden = !willOpen;
      trigger.setAttribute('aria-expanded', String(willOpen));
    });
    menu.addEventListener('click', event => {
      const option = event.target.closest(`[data-thread-option="${kind}"]`);
      if (!option) return;
      setThreadOption(kind, option.dataset.value);
      closeThreadOptionMenus();
      trigger.focus();
    });
  });
  document.addEventListener('click', event => {
    if (!event.target.closest('.thread-option-picker')) closeThreadOptionMenus();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeThreadOptionMenus();
  });
}

function renderHeader() {
  if (globalTalk) {
    document.title = 'Project talk · Paper to Benchmark';
    byId('benchmark-header').innerHTML = '<p class="panel-kicker">PROJECT SUPERVISION</p><h1>Research talk</h1><p class="benchmark-detail-summary">One user–agent inbox across all benchmarks. Project-wide and cross-benchmark threads live here.</p>';
    return;
  }
  const metadata = benchmarkState.metadata || {};
  const currentStage = benchmarkStage(metadata);
  document.title = `${metadata.title || benchmarkId} · Benchmark`;
  const papers = (metadata.paper_ids || []).map(id => `<a class="benchmark-source-chip" href="paper.html?id=${encodeURIComponent(id)}"><i class="fa-regular fa-file-lines" aria-hidden="true"></i>${escapeHtml(id)}</a>`).join('') || '<span class="muted">No paper linked</span>';
  byId('benchmark-header').innerHTML = `
    <div class="detail-heading-row">
      <div class="row-heading"><div class="assessment-picker stage-picker"><button id="benchmark-stage-trigger" class="stage stage-${escapeHtml(currentStage)}" type="button" aria-haspopup="menu" aria-expanded="false">${escapeHtml(statusLabel(currentStage))}</button><div id="benchmark-stage-menu" class="picker-menu stage-menu" role="menu" hidden>${BENCHMARK_STAGE_OPTIONS.map(stage => `<button type="button" role="menuitem" data-benchmark-stage="${stage}"${stage === currentStage ? ' class="selected"' : ''}>${escapeHtml(statusLabel(stage))}</button>`).join('')}</div></div><button id="benchmark-id-copy" class="paper-id paper-id-copy" type="button" aria-label="Copy benchmark ID ${escapeHtml(benchmarkId)}" title="Copy benchmark ID">${escapeHtml(benchmarkId)}</button></div>
      <div class="benchmark-header-actions"><a class="source-button secondary" href="wiki.html?scope=${encodeURIComponent(`benchmark:${benchmarkId}`)}&page=thesis">Research wiki</a><a class="source-button" href="${escapeHtml(documentViewerHref(benchmarkState.documents?.task?.path))}">Open task ↗</a></div>
    </div>
    <p class="benchmark-overline">RESEARCH BENCHMARK</p>
    <h1>${escapeHtml(metadata.title || benchmarkId)}</h1>
    <p class="benchmark-detail-summary">${escapeHtml(metadata.summary || '')}</p>
    <div class="benchmark-tag-row">${(metadata.scientific_domain || []).map(item => `<span>${escapeHtml(item)}</span>`).join('')}</div>
    <div class="benchmark-source-row"><strong>Built from</strong>${papers}<span class="benchmark-review-state"><i class="fa-regular fa-circle-check" aria-hidden="true"></i>Expert review ${statusLabel(metadata.expert_review)}</span></div>`;
  byId('benchmark-id-copy').addEventListener('click', async () => {
    try {
      await copyTextToClipboard(benchmarkId);
      showCopyNotice('Benchmark ID copied');
    } catch (error) {
      showCopyNotice(error.message || 'Could not copy benchmark ID.', true);
    }
  });
  bindBenchmarkStagePicker();
}

function closeBenchmarkStageMenu() {
  const menu = byId('benchmark-stage-menu');
  const trigger = byId('benchmark-stage-trigger');
  if (!menu || !trigger) return;
  menu.hidden = true;
  trigger.setAttribute('aria-expanded', 'false');
}

function bindBenchmarkStagePicker() {
  const trigger = byId('benchmark-stage-trigger');
  const menu = byId('benchmark-stage-menu');
  trigger.addEventListener('click', event => {
    event.stopPropagation();
    const willOpen = menu.hidden;
    closeBenchmarkStageMenu();
    menu.hidden = !willOpen;
    trigger.setAttribute('aria-expanded', String(willOpen));
  });
  menu.querySelectorAll('[data-benchmark-stage]').forEach(option => option.addEventListener('click', () => {
    closeBenchmarkStageMenu();
    updateBenchmarkStage(option.dataset.benchmarkStage, trigger);
  }));
  if (benchmarkStageMenuBound) return;
  benchmarkStageMenuBound = true;
  document.addEventListener('click', event => {
    if (!event.target.closest('.stage-picker')) closeBenchmarkStageMenu();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeBenchmarkStageMenu();
  });
}

async function updateBenchmarkStage(stage, trigger) {
  if (!BENCHMARK_STAGE_OPTIONS.includes(stage) || stage === benchmarkStage(benchmarkState.metadata || {})) return;
  trigger.disabled = true;
  try {
    const payload = await requestJson(`/api/benchmarks/${encodeURIComponent(benchmarkId)}/stage`, { stage }, 'PATCH');
    benchmarkState = payload.benchmark;
    renderBenchmarkWorkspace();
  } catch (error) {
    showCopyNotice(error.message || 'Could not update benchmark status.', true);
    trigger.disabled = false;
  }
}

function renderStats() {
  const threads = benchmarkState.threads || [];
  const cards = [
    ['Waiting on user', threads.filter(item => nextAuthor(item) === 'user').length, 'Questions and checkpoints needing supervision'],
    ['Waiting on agent', threads.filter(item => nextAuthor(item) === 'agent').length, 'User guidance or tasks awaiting action'],
    ['Closed', threads.filter(item => item.status === 'closed').length, 'Conversations ended by the user'],
  ];
  byId('talk-stats').innerHTML = cards.map(([label, count, note]) => `<div><strong>${count}</strong><span>${label}</span><small>${note}</small></div>`).join('');
}

function threadSort(a, b) {
  const stateWeight = { open: 2, closed: 1 };
  const waitingWeight = { user: 2, agent: 1 };
  const priorityWeight = { blocking: 4, high: 3, normal: 2, low: 1 };
  return (stateWeight[b.status] || 0) - (stateWeight[a.status] || 0)
    || (waitingWeight[nextAuthor(b)] || 0) - (waitingWeight[nextAuthor(a)] || 0)
    || (priorityWeight[b.priority] || 0) - (priorityWeight[a.priority] || 0)
    || String(b.updated).localeCompare(String(a.updated));
}

function renderThreadList() {
  const threads = [...(benchmarkState.threads || [])].sort(threadSort);
  byId('thread-total').textContent = `${threads.length} thread${threads.length === 1 ? '' : 's'}`;
  if (!selectedThreadId && threads.length) selectedThreadId = threads[0].id;
  if (selectedThreadId && !threads.some(item => item.id === selectedThreadId)) selectedThreadId = threads[0]?.id || null;
  byId('thread-list').innerHTML = threads.length ? threads.map(thread => `
    <button type="button" class="issue-nav-item thread-nav-${escapeHtml(thread.status)}${selectedThreadId === thread.id ? ' selected' : ''}" data-thread-id="${escapeHtml(thread.id)}">
      <span class="issue-nav-top"><strong>${escapeHtml(thread.id)}</strong><span class="thread-status status-${escapeHtml(thread.status)}">${statusLabel(thread.status)}</span></span>
      <span class="issue-nav-title">${escapeHtml(thread.title)}</span>
      <span class="issue-nav-meta"><span class="priority-${escapeHtml(thread.priority)}">${statusLabel(thread.priority)}</span> · ${thread.status === 'open' ? `waiting on ${statusLabel(nextAuthor(thread))}` : 'closed by user'}</span>
    </button>`).join('') : '<div class="forum-empty"><strong>No threads yet</strong><p>The agent or user can start the first research conversation.</p></div>';
  byId('thread-list').querySelectorAll('[data-thread-id]').forEach(button => button.addEventListener('click', () => {
    selectedThreadId = button.dataset.threadId;
    renderThreadList();
    renderThread();
  }));
}

function renderMessage(message, thread) {
  const actorClass = message.author === 'user' ? 'human-message' : 'ai-question-message';
  const actorLabel = message.author === 'user' ? 'User' : 'Agent';
  const editable = message.author === 'user' && thread.status === 'open' && !message.retracted;
  const controls = editable ? `<div class="message-user-controls">
    <button type="button" class="message-control-button" data-edit-user-message="${escapeHtml(message.id)}" aria-label="Edit ${escapeHtml(message.id)}" title="Edit"><i class="fa-solid fa-pen" aria-hidden="true"></i></button>
    <button type="button" class="message-control-button" data-retract-user-message="${escapeHtml(message.id)}" aria-label="Withdraw ${escapeHtml(message.id)}" title="Withdraw"><i class="fa-solid fa-rotate-left" aria-hidden="true"></i></button>
  </div>` : '';
  const revision = message.edited ? '<span class="message-edited-marker">edited</span>' : '';
  const body = message.retracted
    ? '<p class="message-withdrawn">Message withdrawn.</p>'
    : `<div class="markdown-content">${renderMarkdown(message.content)}</div>`;
  const actorRole = message.author === 'user' ? 'actor-user' : 'actor-agent';
  return `<article class="forum-message ${actorClass}${editable ? ' has-message-controls' : ''}${message.retracted ? ' retracted-message' : ''}" data-message-id="${escapeHtml(message.id)}">
    <div class="message-author"><span class="message-author-label"><span class="message-actor ${actorRole}">${actorLabel}</span><span class="message-type message-type-${messageTypeClass(message.type)}">${statusLabel(message.type)}</span>${revision}</span><span class="message-meta"><span class="message-id">${escapeHtml(message.id)}</span><span class="message-meta-separator" aria-hidden="true">|</span><time>${escapeHtml(formatLocalTimestamp(message.created))}</time></span></div>
    <div class="message-body">${body}</div>${controls}
  </article>`;
}

function renderThread() {
  const thread = (benchmarkState.threads || []).find(item => item.id === selectedThreadId);
  const panel = byId('thread-panel');
  if (!thread) {
    panel.innerHTML = '<div class="thread-empty"><p class="panel-kicker">RESEARCH MAILBOX</p><h2>No thread selected</h2><p>Open a conversation from the left. Agent questions and user guidance use the same thread format.</p></div>';
    return;
  }
  const relatedItems = thread.related || [];
  const related = relatedItems.length ? relatedItems.map(value => `<code>${escapeHtml(value)}</code>`).join(' ') : '<span class="muted">No linked artifacts</span>';
  const context = (thread.context || '').trim() || ((thread.benchmark_ids || []).length ? `Benchmark: ${thread.benchmark_ids.join('\nBenchmark: ')}` : '');
  const supportingInfo = context || relatedItems.length ? `<details class="thread-supporting-info">
      <summary>Thread details${relatedItems.length ? ` · ${relatedItems.length} linked artifact${relatedItems.length === 1 ? '' : 's'}` : ''}</summary>
      <div class="thread-supporting-info-body">
        ${context ? `<section class="thread-context"><strong>Context</strong><div class="markdown-content">${renderMarkdown(context)}</div></section>` : ''}
        ${relatedItems.length ? `<section class="thread-related"><strong>Linked artifacts</strong><div>${related}</div></section>` : ''}
      </div>
    </details>` : '';
  const composer = thread.status === 'open' ? `
    <form id="thread-reply-form" class="issue-advice-form">
      <label for="thread-reply-text">Reply as user</label>
      <textarea id="thread-reply-text" rows="5" maxlength="12000" placeholder="Answer, redirect, ask for evidence, or assign the next step." required></textarea>
      <div class="thread-composer-actions">
        <button type="button" id="close-thread-button" class="danger-action">Close thread</button>
        <div class="thread-reply-submit"><span id="thread-reply-notice" class="forum-notice" aria-live="polite"></span><button type="submit">Reply</button></div>
      </div>
    </form>` : '<div class="thread-closed-actions"><button type="button" id="reopen-thread-button" class="secondary-action">Reopen thread</button></div>';
  panel.innerHTML = `
    <header class="thread-header"><div><p class="panel-kicker">${escapeHtml(thread.id)} · started by ${statusLabel(thread.messages?.[0]?.author)}</p><h2>${escapeHtml(thread.title)}</h2></div><div class="thread-badges"><span class="priority-badge priority-${escapeHtml(thread.priority)}">${statusLabel(thread.priority)}</span><span class="thread-status status-${escapeHtml(thread.status)}">${statusLabel(thread.status)}</span>${thread.status === 'open' ? `<span class="waiting-badge">waiting on ${statusLabel(nextAuthor(thread))}</span>` : ''}</div></header>
    ${supportingInfo}
    <div class="thread-messages">${(thread.messages || []).map(message => renderMessage(message, thread)).join('')}</div>
    ${composer}`;
  const replyForm = byId('thread-reply-form');
  if (replyForm) replyForm.addEventListener('submit', submitReply);
  const closeButton = byId('close-thread-button');
  if (closeButton) closeButton.addEventListener('click', closeThread);
  const reopenButton = byId('reopen-thread-button');
  if (reopenButton) reopenButton.addEventListener('click', reopenThread);
  panel.querySelectorAll('[data-edit-user-message]').forEach(button => {
    button.addEventListener('click', () => beginUserMessageEdit(button.dataset.editUserMessage));
  });
  panel.querySelectorAll('[data-retract-user-message]').forEach(button => {
    button.addEventListener('click', () => retractUserMessage(button.dataset.retractUserMessage));
  });
  panel.querySelectorAll('.markdown-content').forEach(typesetMath);
  const messagesPanel = panel.querySelector('.thread-messages');
  if (messagesPanel) messagesPanel.scrollTop = messagesPanel.scrollHeight;
}

async function requestJson(url, body, method = 'POST') {
  const response = await fetch(url, {
    method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || 'Could not update talk');
  return payload;
}

function beginUserMessageEdit(messageId) {
  const thread = (benchmarkState.threads || []).find(item => item.id === selectedThreadId);
  const message = (thread?.messages || []).find(item => item.id === messageId);
  const card = byId('thread-panel').querySelector(`[data-message-id="${messageId}"]`);
  if (!message || !card || message.retracted) return;
  card.classList.add('editing-message');
  card.querySelector('.message-user-controls').hidden = true;
  const body = card.querySelector('.message-body');
  body.innerHTML = `<textarea class="message-inline-editor" rows="5" maxlength="12000" aria-label="Edit ${escapeHtml(messageId)}">${escapeHtml(message.content)}</textarea>
    <div class="message-edit-actions"><button type="button" class="secondary-action" data-cancel-message-edit>Cancel</button><button type="button" data-save-message-edit>Save</button></div>`;
  const editor = body.querySelector('.message-inline-editor');
  const save = () => saveUserMessageEdit(messageId, editor.value, body);
  body.querySelector('[data-save-message-edit]').addEventListener('click', save);
  body.querySelector('[data-cancel-message-edit]').addEventListener('click', renderThread);
  editor.addEventListener('keydown', event => {
    if (event.key === 'Escape') renderThread();
    if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) save();
  });
  editor.focus();
  editor.setSelectionRange(editor.value.length, editor.value.length);
}

async function saveUserMessageEdit(messageId, content, body) {
  const value = content.trim();
  if (!value) {
    body.querySelector('.message-inline-editor').focus();
    return;
  }
  body.querySelectorAll('button').forEach(button => { button.disabled = true; });
  try {
    await mutateUserMessage(messageId, 'edit', value);
  } catch (error) {
    window.alert(error.message);
    body.querySelectorAll('button').forEach(button => { button.disabled = false; });
  }
}

async function retractUserMessage(messageId) {
  if (!window.confirm('Withdraw this response?')) return;
  try {
    await mutateUserMessage(messageId, 'retraction');
  } catch (error) {
    window.alert(error.message);
  }
}

async function mutateUserMessage(messageId, action, content = '') {
  const base = globalTalk ? '/api/talk' : `/api/benchmarks/${encodeURIComponent(benchmarkId)}`;
  const payload = await requestJson(
    `${base}/threads/${encodeURIComponent(selectedThreadId)}/messages/${encodeURIComponent(messageId)}`,
    { action, content },
    'PATCH',
  );
  benchmarkState = globalTalk ? payload.talk : payload.benchmark;
  renderAll();
}

async function submitNewThread(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const notice = byId('new-thread-notice');
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  notice.textContent = 'Opening…';
  notice.classList.remove('error');
  try {
    const payload = await requestJson(globalTalk ? '/api/talk/threads' : `/api/benchmarks/${encodeURIComponent(benchmarkId)}/threads`, {
      title: byId('new-thread-title').value.trim(),
      message: byId('new-thread-message').value.trim(),
      context: byId('new-thread-context').value.trim(),
      category: byId('new-thread-category-trigger').dataset.value,
      priority: byId('new-thread-priority-trigger').dataset.value,
    });
    benchmarkState = globalTalk ? payload.talk : payload.benchmark;
    selectedThreadId = payload.thread.id;
    form.reset();
    resetThreadOptions();
    renderAll();
  } catch (error) {
    notice.textContent = error.message;
    notice.classList.add('error');
  } finally {
    button.disabled = false;
  }
}

async function submitReply(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const text = byId('thread-reply-text');
  const notice = byId('thread-reply-notice');
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  notice.textContent = 'Saving…';
  notice.classList.remove('error');
  try {
    const base = globalTalk ? '/api/talk' : `/api/benchmarks/${encodeURIComponent(benchmarkId)}`;
    const payload = await requestJson(`${base}/threads/${encodeURIComponent(selectedThreadId)}/messages`, {
      message: text.value.trim(), message_type: 'response'
    });
    benchmarkState = globalTalk ? payload.talk : payload.benchmark;
    renderAll();
  } catch (error) {
    notice.textContent = error.message;
    notice.classList.add('error');
  } finally {
    button.disabled = false;
  }
}

async function closeThread() {
  const button = byId('close-thread-button');
  if (button?.disabled) return;
  if (button) button.disabled = true;
  await transitionSelectedThread('closed', 'Closed by user.');
  if (button?.isConnected) button.disabled = false;
}

async function reopenThread() {
  await transitionSelectedThread('open', 'Reopened by user.');
}

async function transitionSelectedThread(status, message) {
  try {
    const base = globalTalk ? '/api/talk' : `/api/benchmarks/${encodeURIComponent(benchmarkId)}`;
    const payload = await requestJson(`${base}/threads/${encodeURIComponent(selectedThreadId)}/transition`, {
      status, message
    });
    benchmarkState = globalTalk ? payload.talk : payload.benchmark;
    renderAll();
  } catch (error) {
    window.alert(error.message);
  }
}

function sectionValue(documentRecord, ...names) {
  const sections = documentRecord?.sections || {};
  for (const name of names) {
    if (sections[name]) return sections[name];
  }
  const wanted = names.map(name => name.toLowerCase());
  const key = Object.keys(sections).find(item => wanted.includes(item.toLowerCase()));
  return key ? sections[key] : '';
}

function metricCard(value, label, detail) {
  return `<div class="benchmark-metric"><strong>${escapeHtml(value)}</strong><span>${escapeHtml(label)}</span><small>${escapeHtml(detail)}</small></div>`;
}

function renderBenchmarkNavigation() {
  const links = [
    ['research-brief', 'Research brief'],
    ['current-thesis', 'Current thesis'],
    ['idea-frontier', 'Idea frontier'],
    ['active-lab', 'Active lab'],
    ['evidence-contract', 'Evidence'],
  ];
  byId('benchmark-section-nav').innerHTML = links.map(([target, label]) => `<a href="#${target}">${label}</a>`).join('');
}

function renderResearchBrief() {
  const metadata = benchmarkState.metadata || {};
  const task = benchmarkState.documents?.task || {};
  const gap = sectionValue(task, 'Knowledge gap');
  const scope = sectionValue(task, 'Scope and approach boundary', 'Model-selection gate', 'Numerical methods');
  return `<section id="research-brief" class="research-card benchmark-brief-card">
    <div class="research-card-heading"><div><p class="panel-kicker">THE SCIENTIFIC JOB</p><h2>Research brief</h2></div><a href="${escapeHtml(documentViewerHref(task.path))}">Full specification ↗</a></div>
    <div class="research-question"><span>Central question</span><p>${escapeHtml(metadata.research_question || metadata.summary || '')}</p></div>
    <div class="brief-columns">
      <div><h3>Why this is unresolved</h3><div class="research-prose">${renderDocumentMarkdown(gap || metadata.summary || '', task.path)}</div></div>
      <div><h3>Scope & approach</h3><div class="research-prose">${renderDocumentMarkdown(scope || 'See the full task specification for the fixed scientific regime and method boundary.', task.path)}</div></div>
    </div>
  </section>`;
}

function renderCurrentThesis() {
  const thesis = benchmarkState.documents?.thesis || {};
  const synthesis = sectionValue(thesis, 'Current synthesis');
  const tensions = sectionValue(thesis, 'Tensions and alternatives', 'Main risks');
  return `<section id="current-thesis" class="research-card">
    <div class="research-card-heading"><div><p class="panel-kicker">WHAT WE CURRENTLY THINK</p><h2>Current thesis</h2></div><a href="wiki.html?scope=${encodeURIComponent(`benchmark:${benchmarkId}`)}&page=thesis">Open in wiki ↗</a></div>
    <div class="research-prose thesis-copy">${renderDocumentMarkdown(synthesis || thesis.markdown || 'Synthesis pending.', thesis.path)}</div>
    ${tensions ? `<details class="research-details"><summary>Risks, tensions, and alternatives</summary><div class="research-prose">${renderDocumentMarkdown(tensions, thesis.path)}</div></details>` : ''}
  </section>`;
}

function renderIdeaFrontier() {
  const frontier = benchmarkState.documents?.frontier || {};
  const active = sectionValue(frontier, 'Active ideas', 'Idea graph');
  const alternatives = sectionValue(frontier, 'Frontier alternatives', 'Qualified default branch');
  const decisions = sectionValue(frontier, 'Decision rules');
  return `<section id="idea-frontier" class="research-card">
    <div class="research-card-heading"><div><p class="panel-kicker">SEARCH STATE</p><h2>Idea frontier</h2></div><a href="wiki.html?scope=${encodeURIComponent(`benchmark:${benchmarkId}`)}&page=ideas%2Fresearch-frontier">Open idea graph ↗</a></div>
    <div class="research-prose frontier-copy">${renderDocumentMarkdown(active || frontier.markdown || 'Frontier pending.', frontier.path)}</div>
    ${alternatives || decisions ? `<div class="frontier-footer">${alternatives ? `<div><h3>Alternatives worth preserving</h3><div class="research-prose">${renderDocumentMarkdown(alternatives, frontier.path)}</div></div>` : ''}${decisions ? `<div><h3>Keep / prune gate</h3><div class="research-prose">${renderDocumentMarkdown(decisions, frontier.path)}</div></div>` : ''}</div>` : ''}
  </section>`;
}

function renderActiveLab() {
  const lab = (benchmarkState.labs || [])[0];
  if (!lab) return `<section id="active-lab" class="research-card"><p class="panel-kicker">ACTIVE EXPERIMENT</p><h2>No lab designed</h2><p class="muted">The idea frontier has not yet been turned into an executable experiment.</p></section>`;
  const objective = sectionValue(lab.plan, 'Objective');
  const steps = sectionValue(lab.plan, 'Steps');
  const completion = sectionValue(lab.plan, 'Completion criteria');
  const stop = sectionValue(lab.plan, 'Stop conditions');
  return `<section id="active-lab" class="research-card active-lab-card">
    <div class="research-card-heading"><div><p class="panel-kicker">ACTIVE EXPERIMENT · ${escapeHtml(lab.lab_id)}</p><h2>${escapeHtml(lab.title.replace(/^Lab \d+:\s*/, ''))}</h2></div><span class="lab-status">${statusLabel(lab.status)}</span></div>
    <div class="lab-objective"><span>Objective</span><div class="research-prose">${renderDocumentMarkdown(objective || 'Objective pending.', lab.plan.path)}</div></div>
    <div class="lab-layout"><div><h3>Execution sequence</h3><div class="research-prose lab-steps">${renderDocumentMarkdown(steps || '', lab.plan.path)}</div></div><div class="lab-gates"><h3>Evidence gate</h3><div class="research-prose">${renderDocumentMarkdown(completion || '', lab.plan.path)}</div></div></div>
    ${stop ? `<details class="research-details"><summary>Stop and redesign conditions</summary><div class="research-prose">${renderDocumentMarkdown(stop, lab.plan.path)}</div></details>` : ''}
    <div class="lab-actions"><a class="source-button" href="${escapeHtml(documentViewerHref(lab.plan.path))}">Open PLAN ↗</a><a class="source-button" href="${escapeHtml(documentViewerHref(lab.report.path))}">Open REPORT ↗</a><span>${escapeHtml(lab.idea_ids.join(' · ') || 'No idea IDs linked')}</span></div>
  </section>`;
}

function renderEvidenceContract() {
  const metadata = benchmarkState.metadata || {};
  const outcomes = metadata.expected_outcomes || [];
  const evidence = metadata.evidence_requirements || [];
  return `<section id="evidence-contract" class="research-card">
    <div class="research-card-heading"><div><p class="panel-kicker">CLAIM DISCIPLINE</p><h2>Hypotheses & evidence contract</h2></div><span class="evidence-progress">0 / ${evidence.length} evidenced</span></div>
    <div class="evidence-columns"><div><h3>Hypotheses to test</h3><ol class="hypothesis-list">${outcomes.map((item, index) => `<li><span>H${index + 1}</span><p>${escapeHtml(item)}</p></li>`).join('')}</ol></div><div><h3>Required before a claim</h3><ul class="evidence-list">${evidence.map(item => `<li><i class="fa-regular fa-circle" aria-hidden="true"></i><span>${escapeHtml(item)}</span></li>`).join('')}</ul></div></div>
  </section>`;
}

function renderBenchmarkMain() {
  byId('benchmark-main').innerHTML = [renderResearchBrief(), renderCurrentThesis(), renderIdeaFrontier(), renderActiveLab(), renderEvidenceContract()].join('');
  byId('benchmark-main').querySelectorAll('.research-prose').forEach(typesetMath);
}

function renderBenchmarkRail() {
  const metadata = benchmarkState.metadata || {};
  const snapshot = benchmarkState.status_snapshot || {};
  const artifacts = benchmarkState.artifacts || {};
  const decisions = [...(benchmarkState.threads || [])].filter(thread => thread.status === 'open').sort(threadSort).slice(0, 3);
  const lab = (benchmarkState.labs || [])[0];
  const nextAction = snapshot.next_decisive_action || (lab ? sectionValue(lab.plan, 'Objective') : 'Define the next decisive experiment.');
  byId('benchmark-rail').innerHTML = `
    <section class="rail-card next-action-card"><p class="panel-kicker">DO NEXT</p><h2>Next decisive action</h2><div class="research-prose">${renderDocumentMarkdown(nextAction, benchmarkState.documents?.readme?.path)}</div>${lab ? `<a class="rail-primary-action" href="#active-lab">Go to active lab <i class="fa-solid fa-arrow-down" aria-hidden="true"></i></a>` : ''}</section>
    <section class="rail-card"><p class="panel-kicker">PROJECT SIGNALS</p><div class="rail-metrics">${metricCard(artifacts.lab_count || 0, 'Labs', artifacts.evidence_file_count ? `${artifacts.evidence_file_count} evidence files` : 'Design stage')}${metricCard(artifacts.wiki_page_count || 0, 'Wiki pages', 'Maintained synthesis')}${metricCard(artifacts.stable_source_file_count || 0, 'Stable files', artifacts.stable_source_file_count ? 'Distilled' : 'Awaiting evidence')}</div><div class="resource-meta"><span><strong>${escapeHtml(metadata.estimated_active_hours || '—')}</strong> active hours</span><span><strong>${statusLabel(metadata.workstation_feasible)}</strong> workstation</span></div></section>
    <section class="rail-card"><p class="panel-kicker">WORKSPACE</p><div class="artifact-links"><a href="${escapeHtml(documentViewerHref(benchmarkState.documents?.task?.path))}"><i class="fa-regular fa-file-lines"></i><span><strong>Problem specification</strong><small>TASK.md</small></span></a><a href="wiki.html?scope=${encodeURIComponent(`benchmark:${benchmarkId}`)}&page=index"><i class="fa-solid fa-diagram-project"></i><span><strong>Research wiki</strong><small>Thesis, ideas, questions</small></span></a>${lab ? `<a href="${escapeHtml(documentViewerHref(lab.plan.path))}"><i class="fa-solid fa-flask"></i><span><strong>Active lab plan</strong><small>${escapeHtml(lab.lab_id)}</small></span></a>` : ''}${(metadata.paper_ids || []).map(id => `<a href="paper.html?id=${encodeURIComponent(id)}"><i class="fa-regular fa-file-pdf"></i><span><strong>Source paper</strong><small>${escapeHtml(id)}</small></span></a>`).join('')}</div></section>
    <section class="rail-card"><div class="rail-heading-row"><div><p class="panel-kicker">DECISIONS & BLOCKERS</p><h2>${decisions.length ? `${decisions.length} open` : 'Clear'}</h2></div><a href="talk.html?benchmark=${encodeURIComponent(benchmarkId)}">Talk ↗</a></div>${decisions.length ? `<div class="decision-list">${decisions.map(thread => `<a href="talk.html?benchmark=${encodeURIComponent(benchmarkId)}&thread=${encodeURIComponent(thread.id)}"><span class="priority-${escapeHtml(thread.priority)}">${escapeHtml(thread.id)} · ${statusLabel(thread.priority)}</span><strong>${escapeHtml(thread.title)}</strong><small>Waiting on ${statusLabel(nextAuthor(thread))}</small></a>`).join('')}</div>` : '<p class="muted">No open decision is blocking the research loop.</p>'}</section>`;
  byId('benchmark-rail').querySelectorAll('.research-prose').forEach(typesetMath);
}

function renderBenchmarkWorkspace() {
  renderHeader();
  renderBenchmarkNavigation();
  renderBenchmarkMain();
  renderBenchmarkRail();
}

function renderAll() {
  if (!globalTalk) {
    renderBenchmarkWorkspace();
    return;
  }
  renderHeader();
  renderStats();
  renderThreadList();
  renderThread();
}

async function loadBenchmark() {
  if (!globalTalk && !benchmarkId) {
    byId('benchmark-header').innerHTML = '<div class="forum-empty"><strong>Missing benchmark ID</strong><p>Return to the benchmark list and choose a record.</p></div>';
    return;
  }
  try {
    const response = await fetch(globalTalk ? '/api/talk' : `/api/benchmarks/${encodeURIComponent(benchmarkId)}`);
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || 'Benchmark unavailable');
    benchmarkState = payload;
    renderAll();
  } catch (error) {
    byId('benchmark-header').innerHTML = `<div class="forum-empty"><strong>Could not load benchmark</strong><p>${escapeHtml(error.message)}</p></div>`;
  }
}

if (globalTalk) {
  bindThreadOptionPickers();
  byId('new-thread-form').addEventListener('submit', submitNewThread);
}
loadBenchmark();
