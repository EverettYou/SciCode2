const papers = window.SCICODE_PAPERS || [];
const benchmarks = window.SCICODE_BENCHMARKS || [];
const levelWeight = { high: 3, medium: 2, low: 1 };
const feasibilityWeight = { yes: 2, uncertain: 1, no: 0 };
const stageOrder = { reviewed: 4, assessed: 3, fetched: 2, listed: 1, linked: 0 };
const sortLabels = { year: 'newest', score: 'score', title: 'title', stage: 'stage' };
let selectedPaperStage = 'all';
let selectedPaperSort = 'year';
const benchmarkSortLabels = { stage: 'stage', title: 'title', papers: 'papers' };
let selectedBenchmarkStage = 'all';
let selectedBenchmarkSort = 'stage';
const catalogSearchState = {
  query: '', scope: '', stage: 'all', mode: 'local', results: new Map(),
  searching: false, refining: false, timer: null, controller: null, sequence: 0
};
const benchmarkOrder = {
  verified: 4,
  'solution-drafted': 3,
  researching: 2,
  'problem-opened': 1
};

const byId = (id) => document.getElementById(id);
const escapeHtml = (value = '') => String(value).replace(/[&<>"']/g, character => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
})[character]);
const normalizeRatingValue = value => value === true ? 'yes' : value === false ? 'no' : value;
const normalizePaperStage = value => ({ fresh: 'listed', rated: 'assessed' }[value] || (stageOrder[value] ? value : 'listed'));
const benchmarkStage = benchmark => benchmark.stage || 'problem-opened';
const benchmarkStageLabel = value => ({
  'problem-opened': 'problem opened',
  researching: 'researching',
  'solution-drafted': 'solution drafted',
  verified: 'verified'
}[value] || String(value || '').replaceAll('-', ' '));

function rawPaperScore(paper) {
  const required = [
    paper.computational_depth,
    paper.scientific_judgment,
    paper.validation_ease,
    normalizeRatingValue(paper.workstation_feasible),
    normalizeRatingValue(paper.reference_solution_feasible),
    normalizeRatingValue(paper.non_searchable_extension_possible),
    paper.supervision_confidence
  ];
  if (!paper.has_assessment || required.some(value => !value)) return null;
  return (levelWeight[paper.computational_depth] || 0) +
    (levelWeight[paper.scientific_judgment] || 0) +
    (levelWeight[paper.validation_ease] || 0) +
    (feasibilityWeight[normalizeRatingValue(paper.workstation_feasible)] || 0) +
    (feasibilityWeight[normalizeRatingValue(paper.reference_solution_feasible)] || 0) +
    (feasibilityWeight[normalizeRatingValue(paper.non_searchable_extension_possible)] || 0) +
    (levelWeight[paper.supervision_confidence] || 0);
}

function paperScore(paper) {
  const raw = rawPaperScore(paper);
  return raw === null ? null : Math.round(raw / 18 * 100);
}

function renderMath(element) {
  if (!window.renderMathInElement || !element) return;
  renderMathInElement(element, {
    delimiters: [
      { left: '\\(', right: '\\)', display: false },
      { left: '\\[', right: '\\]', display: true },
      { left: '$$', right: '$$', display: true }
    ],
    throwOnError: false
  });
}

function paperSearchText(paper) {
  return [
    paper.paper_id, paper.title, paper.authors, paper.venue, paper.summary,
    paper.computational_core, paper.ai_assessment, paper.stage,
    paper.workstation_feasible, paper.reference_solution_feasible, paper.validation_ease,
    ...(paper.research_area || []), ...(paper.followup_ideas || []),
    ...(paper.potential_pitfalls || []), ...(paper.suggested_task_types || [])
  ].join(' ').toLowerCase();
}

function currentCatalogStage(scope) {
  return scope === 'papers' ? selectedPaperStage : selectedBenchmarkStage;
}

function catalogSearchIsCurrent(scope, query) {
  return catalogSearchState.scope === scope &&
    catalogSearchState.query === query &&
    catalogSearchState.stage === currentCatalogStage(scope);
}

function catalogSearchResult(scope, id, query) {
  if (!query || !catalogSearchIsCurrent(scope, query) || catalogSearchState.mode === 'local') return null;
  return catalogSearchState.results.get(id) || null;
}

function catalogSearchStatus(scope, query) {
  if (!query || !catalogSearchIsCurrent(scope, query)) return '';
  if (catalogSearchState.refining) return ' · refining natural-language query…';
  if (catalogSearchState.searching) return ' · searching concepts…';
  if (catalogSearchState.mode === 'llm-refined') return ' · natural-language ranking';
  if (catalogSearchState.mode.startsWith('hybrid')) return ' · semantic ranking';
  return '';
}

function catalogMatchNote(scope, id, query) {
  const match = catalogSearchResult(scope, id, query);
  return match?.reason ? `<p class="search-match"><i class="fa-solid fa-wand-magic-sparkles" aria-hidden="true"></i>${escapeHtml(match.reason)}</p>` : '';
}

function updateSearchBusyState() {
  const control = document.querySelector('.search-control');
  if (control) control.classList.toggle('searching', catalogSearchState.searching || catalogSearchState.refining);
}

function renderCatalogScope(scope) {
  if (scope === 'papers') renderPapers(); else renderBenchmarks();
  updateSearchBusyState();
}

async function fetchCatalogSearch(scope, query, stage, sequence, refine = false) {
  const params = new URLSearchParams({ q: query, scope, stage, limit: '100', refine: String(refine) });
  const response = await fetch(`/api/catalog/search?${params}`, {
    cache: 'no-store', signal: catalogSearchState.controller.signal
  });
  if (!response.ok) throw new Error('Semantic search unavailable');
  const payload = await response.json();
  if (sequence !== catalogSearchState.sequence || !catalogSearchIsCurrent(scope, query)) return null;
  catalogSearchState.results = new Map(payload.results.map((item, rank) => [item.entity_id, { ...item, rank }]));
  catalogSearchState.mode = payload.mode;
  catalogSearchState.searching = false;
  catalogSearchState.refining = false;
  renderCatalogScope(scope);
  return payload;
}

async function enhanceCatalogSearch(scope, query, stage, sequence) {
  try {
    const payload = await fetchCatalogSearch(scope, query, stage, sequence, false);
    if (!payload?.complex_query || sequence !== catalogSearchState.sequence) return;
    catalogSearchState.refining = true;
    renderCatalogScope(scope);
    await fetchCatalogSearch(scope, query, stage, sequence, true);
  } catch (error) {
    if (error.name === 'AbortError' || sequence !== catalogSearchState.sequence) return;
    catalogSearchState.mode = 'local';
    catalogSearchState.results = new Map();
    catalogSearchState.searching = false;
    catalogSearchState.refining = false;
    renderCatalogScope(scope);
  }
}

function queueCatalogSearch(scope) {
  const query = byId('search').value.trim();
  const stage = currentCatalogStage(scope);
  window.clearTimeout(catalogSearchState.timer);
  catalogSearchState.controller?.abort();
  catalogSearchState.controller = new AbortController();
  catalogSearchState.sequence += 1;
  catalogSearchState.query = query;
  catalogSearchState.scope = scope;
  catalogSearchState.stage = stage;
  catalogSearchState.mode = 'local';
  catalogSearchState.results = new Map();
  catalogSearchState.searching = query.length >= 2;
  catalogSearchState.refining = false;
  renderCatalogScope(scope);
  if (query.length < 2) return;
  const sequence = catalogSearchState.sequence;
  catalogSearchState.timer = window.setTimeout(
    () => enhanceCatalogSearch(scope, query, stage, sequence), 350
  );
}

function ratingRows(paper) {
  if (!paper.has_assessment) return '';
  const rows = [
    ['Computational depth', paper.computational_depth],
    ['Scientific judgment', paper.scientific_judgment],
    ['Validation ease', paper.validation_ease],
    ['Workstation feasible', normalizeRatingValue(paper.workstation_feasible)],
    ['Reference feasible', normalizeRatingValue(paper.reference_solution_feasible)],
    ['New extension possible', normalizeRatingValue(paper.non_searchable_extension_possible)],
    ['Supervision confidence', paper.supervision_confidence]
  ];
  return `<dl class="rating-grid">${rows.map(([label, value]) => `
    <div><dt>${escapeHtml(label)}</dt><dd class="value-${escapeHtml(value || 'pending')}">${escapeHtml(value || 'pending')}</dd></div>`).join('')}
  </dl>`;
}

function paperRow(paper, query = '') {
  const score = paperScore(paper);
  const title = escapeHtml(paper.title);
  const citedBy = (paper.benchmark_ids || []).map(id => {
    const benchmark = benchmarks.find(item => item.benchmark_id === id);
    return benchmark ? benchmark.title : id;
  });
  return `<article class="catalog-row paper-row">
    <aside class="score-column">
      ${score === null ? '<span class="score-empty">—</span>' : `<strong>${score}</strong><small>/ 100</small>`}
    </aside>
    <div class="row-main">
      <div class="row-heading">
      <span class="stage stage-${normalizePaperStage(paper.stage)}">${normalizePaperStage(paper.stage)}</span>
        <button type="button" class="paper-id paper-id-copy" data-copy-paper-id="${escapeHtml(paper.paper_id)}" aria-label="Copy paper ID ${escapeHtml(paper.paper_id)}" title="Copy paper ID">${escapeHtml(paper.paper_id)}</button>
      </div>
      <h2><a href="${escapeHtml(searchTargetHref({ kind: 'paper', paper_id: paper.paper_id }))}">${title}</a></h2>
      <p class="authors">${escapeHtml(paper.authors)}</p>
      <p class="venue">${escapeHtml(paper.venue)}${paper.venue ? ' · ' : ''}${escapeHtml(paper.year || '')}${paper.source_url ? ` · <a href="${escapeHtml(paper.source_url)}" target="_blank" rel="noreferrer">source ↗</a>` : ''}</p>
      ${catalogMatchNote('papers', paper.paper_id, query)}
      ${paper.has_assessment ? `<p class="assessment">${escapeHtml(paper.ai_assessment || '')}</p>
        <details><summary>Ratings and follow-up ideas</summary>${ratingRows(paper)}
        <ul>${(paper.followup_ideas || []).map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul></details>` : ''}
      ${citedBy.length ? `<p class="cited-by"><strong>Cited by:</strong> ${citedBy.map(escapeHtml).join(' · ')}</p>` : ''}
    </div>
  </article>`;
}

function renderPaperStats() {
  const counts = { listed: 0, fetched: 0, assessed: 0, reviewed: 0 };
  papers.forEach(paper => { const stage = normalizePaperStage(paper.stage); counts[stage] += 1; });
  const filters = [...Object.entries(counts), ['all', papers.length]];
  byId('paper-stats').innerHTML = filters.map(([stage, count]) => `
    <button type="button" class="stats-filter${selectedPaperStage === stage ? ' active' : ''}" data-paper-stage="${stage}" aria-pressed="${selectedPaperStage === stage}"><strong>${count}</strong><span>${stage === 'all' ? 'All' : stage}</span></button>`).join('');
}

function syncPaperSortMenu() {
  const trigger = byId('sort-trigger');
  trigger.textContent = sortLabels[selectedPaperSort];
  byId('sort-menu').querySelectorAll('[data-sort-value]').forEach(option => {
    option.classList.toggle('selected', option.dataset.sortValue === selectedPaperSort);
  });
}

function closePaperSortMenu() {
  const menu = byId('sort-menu');
  menu.hidden = true;
  byId('sort-trigger').setAttribute('aria-expanded', 'false');
}

function renderPapers() {
  const rawQuery = byId('search').value.trim();
  const query = rawQuery.toLowerCase();
  const stage = selectedPaperStage;
  const sort = selectedPaperSort;
  const matchesStage = paper => stage === 'all'
    || (stage === 'linked' ? (paper.benchmark_ids || []).length > 0 : normalizePaperStage(paper.stage) === stage);
  const semanticActive = rawQuery && catalogSearchIsCurrent('papers', rawQuery) && catalogSearchState.mode !== 'local';
  const visible = papers.filter(paper =>
    (!query || (semanticActive ? catalogSearchState.results.has(paper.paper_id) : paperSearchText(paper).includes(query))) &&
    matchesStage(paper)
  );
  visible.sort((a, b) => {
    if (semanticActive) {
      const relevance = catalogSearchState.results.get(a.paper_id).rank - catalogSearchState.results.get(b.paper_id).rank;
      if (relevance) return relevance;
    }
    if (sort === 'title') return a.title.localeCompare(b.title);
    if (sort === 'score') return (paperScore(b) ?? -1) - (paperScore(a) ?? -1) || (b.year || 0) - (a.year || 0);
    if (sort === 'stage') return stageOrder[normalizePaperStage(b.stage)] - stageOrder[normalizePaperStage(a.stage)] || (b.year || 0) - (a.year || 0);
    return (b.year || 0) - (a.year || 0) || a.title.localeCompare(b.title);
  });
  byId('result-count').textContent = `${visible.length} of ${papers.length} papers${catalogSearchStatus('papers', rawQuery)}`;
  byId('paper-list').innerHTML = visible.map(paper => paperRow(paper, rawQuery)).join('') || '<div class="empty-state">No papers match these filters.</div>';
  renderMath(byId('paper-list'));
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

async function copyPaperId(button) {
  try {
    await copyTextToClipboard(button.dataset.copyPaperId);
    showCopyNotice('Paper ID copied');
  } catch (error) {
    showCopyNotice(error.message || 'Could not copy paper ID.', true);
  }
}

async function copyBenchmarkId(button) {
  try {
    await copyTextToClipboard(button.dataset.copyBenchmarkId);
    showCopyNotice('Benchmark ID copied');
  } catch (error) {
    showCopyNotice(error.message || 'Could not copy benchmark ID.', true);
  }
}

function citedPaperLinks(benchmark) {
  if (!(benchmark.paper_ids || []).length) return '<span class="muted">No papers linked yet</span>';
  return benchmark.paper_ids.map(id => {
    const paper = papers.find(item => item.paper_id === id);
    return paper
      ? `<a href="papers.html?paper=${encodeURIComponent(id)}">${escapeHtml(paper.title)}</a>`
      : `<span class="missing-paper">${escapeHtml(id)} (missing)</span>`;
  }).join('');
}

function benchmarkSearchText(benchmark) {
  const cited = (benchmark.paper_ids || []).map(id => papers.find(paper => paper.paper_id === id)?.title || id);
  return [
    benchmark.benchmark_id, benchmark.title, benchmark.summary, benchmark.central_question,
    benchmark.task_summary, benchmark.stage, benchmark.workstation_feasible,
    ...(benchmark.scientific_domain || []), ...cited
  ].join(' ').toLowerCase();
}

function benchmarkRow(benchmark, query = '') {
  return `<article class="catalog-row benchmark-row">
    <div class="row-main">
      <div class="row-heading"><span class="stage stage-${escapeHtml(benchmarkStage(benchmark))}">${escapeHtml(benchmarkStageLabel(benchmarkStage(benchmark)))}</span><button type="button" class="paper-id paper-id-copy" data-copy-benchmark-id="${escapeHtml(benchmark.benchmark_id)}" aria-label="Copy benchmark ID ${escapeHtml(benchmark.benchmark_id)}" title="Copy benchmark ID">${escapeHtml(benchmark.benchmark_id)}</button></div>
      <h2><a href="${escapeHtml(searchTargetHref({ kind: 'benchmark', benchmark_id: benchmark.benchmark_id }))}">${escapeHtml(benchmark.title)}</a></h2>
      <p class="domain">${(benchmark.scientific_domain || []).map(escapeHtml).join(' · ')}</p>
      <p class="assessment">${escapeHtml(benchmark.summary || '')}</p>
      ${catalogMatchNote('benchmarks', benchmark.benchmark_id, query)}
      <div class="benchmark-meta">
        <span>${benchmark.estimated_active_hours ? `${escapeHtml(benchmark.estimated_active_hours)} active hours` : 'Effort pending'}</span>
        <span>Workstation: ${escapeHtml(benchmark.workstation_feasible || 'uncertain')}</span>
        <span class="talk-count${benchmark.waiting_user_count ? ' has-open' : ''}">${escapeHtml(benchmark.waiting_user_count || 0)} waiting on user</span>
        <span class="talk-count${benchmark.waiting_agent_count ? ' has-pending' : ''}">${escapeHtml(benchmark.waiting_agent_count || 0)} waiting on agent</span>
      </div>
      <div class="citations"><strong>Source papers</strong>${citedPaperLinks(benchmark)}</div>
    </div>
  </article>`;
}

function renderBenchmarks() {
  const rawQuery = byId('search').value.trim();
  const query = rawQuery.toLowerCase();
  const stage = selectedBenchmarkStage;
  const sort = selectedBenchmarkSort;
  const semanticActive = rawQuery && catalogSearchIsCurrent('benchmarks', rawQuery) && catalogSearchState.mode !== 'local';
  const visible = benchmarks.filter(benchmark =>
    (!query || (semanticActive ? catalogSearchState.results.has(benchmark.benchmark_id) : benchmarkSearchText(benchmark).includes(query))) &&
    (stage === 'all' || benchmarkStage(benchmark) === stage)
  );
  visible.sort((a, b) => {
    if (semanticActive) {
      const relevance = catalogSearchState.results.get(a.benchmark_id).rank - catalogSearchState.results.get(b.benchmark_id).rank;
      if (relevance) return relevance;
    }
    if (sort === 'title') return a.title.localeCompare(b.title);
    if (sort === 'papers') return (b.paper_ids || []).length - (a.paper_ids || []).length;
    return (benchmarkOrder[benchmarkStage(b)] || 0) - (benchmarkOrder[benchmarkStage(a)] || 0) || a.title.localeCompare(b.title);
  });
  byId('result-count').textContent = `${visible.length} of ${benchmarks.length} benchmarks${catalogSearchStatus('benchmarks', rawQuery)}`;
  byId('benchmark-list').innerHTML = visible.length
    ? visible.map(benchmark => benchmarkRow(benchmark, rawQuery)).join('')
    : benchmarks.length
      ? '<div class="empty-state">No benchmarks match these filters.</div>'
      : `<div class="empty-state"><strong>No benchmarks yet.</strong><span>Add an entry to <code>benchmarks/benchmarks.yml</code> and create its <code>benchmarks/&lt;slug&gt;/metadata.yml</code>, then rebuild the dashboard data.</span></div>`;
  renderMath(byId('benchmark-list'));
}

function renderBenchmarkStats() {
  const stages = ['problem-opened', 'researching', 'solution-drafted', 'verified'];
  const counts = Object.fromEntries(stages.map(stage => [stage, 0]));
  benchmarks.forEach(benchmark => { const stage = benchmarkStage(benchmark); if (counts[stage] !== undefined) counts[stage] += 1; });
  const filters = [...stages.map(stage => [stage, counts[stage]]), ['all', benchmarks.length]];
  byId('benchmark-stats').innerHTML = filters.map(([stage, count]) => `
    <button type="button" class="stats-filter${selectedBenchmarkStage === stage ? ' active' : ''}" data-benchmark-stage="${stage}" aria-pressed="${selectedBenchmarkStage === stage}"><strong>${count}</strong><span>${stage === 'all' ? 'All' : benchmarkStageLabel(stage)}</span></button>`).join('');
}

function syncBenchmarkSortMenu() {
  const trigger = byId('sort-trigger');
  trigger.textContent = benchmarkSortLabels[selectedBenchmarkSort];
  byId('sort-menu').querySelectorAll('[data-sort-value]').forEach(option => {
    option.classList.toggle('selected', option.dataset.sortValue === selectedBenchmarkSort);
  });
}

function closeBenchmarkSortMenu() {
  const menu = byId('sort-menu');
  menu.hidden = true;
  byId('sort-trigger').setAttribute('aria-expanded', 'false');
}

function renderDashboardStats() {
  const stageCounts = { listed: 0, fetched: 0, assessed: 0, reviewed: 0 };
  papers.forEach(paper => { const stage = normalizePaperStage(paper.stage); stageCounts[stage] = (stageCounts[stage] || 0) + 1; });
  const linked = new Set(benchmarks.flatMap(benchmark => benchmark.paper_ids || []));
  byId('overview-stats').innerHTML = [
    ['Papers', papers.length, 'in inventory', 'papers.html'],
    ['Assessed', stageCounts.assessed + stageCounts.reviewed, 'with assessment', 'papers.html?stage=assessed'],
    ['Benchmarks', benchmarks.length, 'in workspace', 'benchmarks.html?stage=all'],
    ['Linked papers', linked.size, 'cited by benchmarks', 'papers.html?stage=linked']
  ].map(([label, value, note, href]) => `<a class="overview-stat" href="${href}" aria-label="View ${label}"><strong>${value}</strong><span>${label}</span><small>${note}</small></a>`).join('');
}

function renderWorkflowProgress() {
  const counts = { listed: 0, fetched: 0, assessed: 0, reviewed: 0 };
  papers.forEach(paper => { const stage = normalizePaperStage(paper.stage); counts[stage] = (counts[stage] || 0) + 1; });
  const labels = { listed: 'Listed', fetched: 'Fetched', assessed: 'Assessed', reviewed: 'Reviewed' };
  byId('workflow-progress').innerHTML = Object.entries(labels).map(([stage, label]) => {
    const count = counts[stage] || 0;
    const width = papers.length ? Math.round(count / papers.length * 100) : 0;
    return `<div class="progress-row"><div><span>${label}</span><strong>${count}</strong></div><div class="progress-track"><span class="progress-fill progress-${stage}" style="width:${width}%"></span></div></div>`;
  }).join('');
}

function graphHash(value) {
  return [...value].reduce((hash, character) => ((hash * 33) ^ character.charCodeAt(0)) >>> 0, 5381);
}

const knowledgeGraphState = { graph: null, positions: null, colorMode: 'community', pan: null, viewBox: { x: 0, y: 0, width: 980, height: 560 } };

function graphGroupCenters(graph, width, height) {
  const groups = [...new Set(graph.nodes.map(node => String(node.community ?? 'reference')))].sort();
  const groupSizes = graph.nodes.reduce((counts, node) => {
    const group = String(node.community ?? 'reference');
    counts[group] = (counts[group] || 0) + 1;
    return counts;
  }, {});
  const nodeById = new Map(graph.nodes.map(node => [node.id, node]));
  const centers = Object.fromEntries(groups.map(group => {
    const hash = graphHash(`community:${group}`);
    return [group, {
      x: width * (.18 + (hash % 1000) / 1560),
      y: height * (.18 + (Math.floor(hash / 1000) % 1000) / 1560),
      vx: 0, vy: 0,
    }];
  }));
  const links = new Map();
  graph.edges.forEach(edge => {
    const source = String(nodeById.get(edge.source)?.community ?? 'reference');
    const target = String(nodeById.get(edge.target)?.community ?? 'reference');
    if (source === undefined || target === undefined || source === target) return;
    const key = [source, target].sort().join('\u0000');
    links.set(key, (links.get(key) || 0) + edge.weight);
  });
  for (let step = 0; step < 220; step += 1) {
    const items = Object.entries(centers);
    for (let i = 0; i < items.length; i += 1) {
      for (let j = i + 1; j < items.length; j += 1) {
        const [aGroup, a] = items[i]; const [bGroup, b] = items[j];
        const dx = a.x - b.x || .1; const dy = a.y - b.y || .1;
        const distance = Math.max(12, Math.hypot(dx, dy));
        const minimum = 76 + 7 * (Math.sqrt(groupSizes[aGroup]) + Math.sqrt(groupSizes[bGroup]));
        const separation = distance < minimum ? (minimum - distance) * .025 : 0;
        const force = 7200 / (distance * distance) + separation;
        a.vx += dx / distance * force; a.vy += dy / distance * force;
        b.vx -= dx / distance * force; b.vy -= dy / distance * force;
      }
    }
    links.forEach((weight, key) => {
      const [source, target] = key.split('\u0000');
      const a = centers[source]; const b = centers[target];
      const dx = b.x - a.x; const dy = b.y - a.y;
      const distance = Math.max(1, Math.hypot(dx, dy));
      const force = (distance - 190) * .004 * Math.min(3, .7 + Math.log1p(weight));
      a.vx += dx / distance * force; a.vy += dy / distance * force;
      b.vx -= dx / distance * force; b.vy -= dy / distance * force;
    });
    items.forEach(([, point]) => {
      point.vx += (width / 2 - point.x) * .0012;
      point.vy += (height / 2 - point.y) * .0012;
      point.vx *= .76; point.vy *= .76;
      point.x += point.vx;
      point.y += point.vy;
    });
  }
  return centers;
}

function graphLayout(graph, width = 980, height = 560) {
  const cacheKey = `scicode-graph-layout:v10:community:${graph.fingerprint}`;
  try {
    const cached = JSON.parse(localStorage.getItem(cacheKey));
    if (cached && graph.nodes.every(node => cached[node.id] && Number.isFinite(cached[node.id].scale))) return cached;
  } catch (_) { /* Local storage is optional. */ }
  const centers = graphGroupCenters(graph, width, height);
  const positions = Object.fromEntries(graph.nodes.map(node => {
    const center = centers[String(node.community ?? 'reference')] || { x: width / 2, y: height / 2 };
    const hash = graphHash(node.id);
    const angle = (hash % 6283) / 1000;
    const radius = 14 + (Math.floor(hash / 6283) % 72);
    return [node.id, { x: center.x + Math.cos(angle) * radius, y: center.y + Math.sin(angle) * radius, vx: 0, vy: 0 }];
  }));
  const nodeById = new Map(graph.nodes.map(node => [node.id, node]));
  const layoutEdges = graph.edges;
  for (let step = 0; step < 420; step += 1) {
    const cooling = Math.max(.12, 1 - step / 460);
    for (let i = 0; i < graph.nodes.length; i += 1) {
      for (let j = i + 1; j < graph.nodes.length; j += 1) {
        const aNode = graph.nodes[i]; const bNode = graph.nodes[j];
        const a = positions[aNode.id]; const b = positions[bNode.id];
        const dx = a.x - b.x || .1; const dy = a.y - b.y || .1;
        const distance = Math.max(2, Math.hypot(dx, dy));
        const clearance = aNode.size + bNode.size + 12;
        const collision = distance < clearance ? (clearance - distance) * .11 : 0;
        const force = (900 / (distance * distance) + collision) * cooling;
        a.vx += dx / distance * force; a.vy += dy / distance * force;
        b.vx -= dx / distance * force; b.vy -= dy / distance * force;
      }
    }
    layoutEdges.forEach(edge => {
      const a = positions[edge.source]; const b = positions[edge.target];
      const sourceGroup = String(nodeById.get(edge.source)?.community ?? 'reference');
      const targetGroup = String(nodeById.get(edge.target)?.community ?? 'reference');
      const sameGroup = sourceGroup === targetGroup;
      const dx = b.x - a.x; const dy = b.y - a.y;
      const distance = Math.sqrt(dx * dx + dy * dy) || 1;
      const desired = Math.max(54, 108 - edge.weight * 6);
      const force = (distance - desired) * .009 * Math.min(2.4, .65 + edge.weight * .2) * (sameGroup ? 1 : .6) * cooling;
      a.vx += dx / distance * force; a.vy += dy / distance * force;
      b.vx -= dx / distance * force; b.vy -= dy / distance * force;
    });
    const layoutBounds = graph.nodes.reduce((box, node) => {
      const point = positions[node.id];
      box.minX = Math.min(box.minX, point.x);
      box.maxX = Math.max(box.maxX, point.x);
      box.minY = Math.min(box.minY, point.y);
      box.maxY = Math.max(box.maxY, point.y);
      box.centerX += point.x / graph.nodes.length;
      box.centerY += point.y / graph.nodes.length;
      return box;
    }, { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity, centerX: 0, centerY: 0 });
    const currentAspect = Math.max(1, layoutBounds.maxX - layoutBounds.minX) / Math.max(1, layoutBounds.maxY - layoutBounds.minY);
    const targetAspect = width / height;
    const aspectError = Math.max(-.8, Math.min(.8, Math.log(targetAspect / currentAspect)));
    const aspectPull = .05 * cooling;
    graph.nodes.forEach(node => {
      const point = positions[node.id];
      point.vx += (point.x - layoutBounds.centerX) * aspectError * aspectPull;
      point.vy -= (point.y - layoutBounds.centerY) * aspectError * aspectPull;
    });
    graph.nodes.forEach(node => {
      const point = positions[node.id]; const center = centers[String(node.community ?? 'reference')] || { x: width / 2, y: height / 2 };
      point.vx += (center.x - point.x) * .004 * cooling;
      point.vy += (center.y - point.y) * .004 * cooling;
      point.vx += (width / 2 - point.x) * .00035;
      point.vy += (height / 2 - point.y) * .00035;
      point.vx *= .78; point.vy *= .78;
      const speed = Math.hypot(point.vx, point.vy);
      const limit = 1.4 + 6 * cooling;
      if (speed > limit) { point.vx *= limit / speed; point.vy *= limit / speed; }
      point.x += point.vx;
      point.y += point.vy;
    });
  }
  const padding = 34;
  const bounds = graph.nodes.reduce((box, node) => {
    const point = positions[node.id];
    return {
      minX: Math.min(box.minX, point.x - node.size),
      maxX: Math.max(box.maxX, point.x + node.size),
      minY: Math.min(box.minY, point.y - node.size),
      maxY: Math.max(box.maxY, point.y + node.size),
    };
  }, { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity });
  const spanX = Math.max(1, bounds.maxX - bounds.minX);
  const spanY = Math.max(1, bounds.maxY - bounds.minY);
  const scale = Math.min((width - padding * 2) / spanX, (height - padding * 2) / spanY);
  const sourceCenterX = (bounds.minX + bounds.maxX) / 2;
  const sourceCenterY = (bounds.minY + bounds.maxY) / 2;
  const stable = Object.fromEntries(Object.entries(positions).map(([id, point]) => [id, {
    x: +((point.x - sourceCenterX) * scale + width / 2).toFixed(2),
    y: +((point.y - sourceCenterY) * scale + height / 2).toFixed(2),
    scale: +scale.toFixed(4),
  }]));
  try { localStorage.setItem(cacheKey, JSON.stringify(stable)); } catch (_) { /* Optional. */ }
  return stable;
}

function graphColor(node) {
  if (knowledgeGraphState.colorMode === 'type') return scicodeKnowledgeTypeColor(node.type);
  return knowledgeGraphState.graph.communities[node.community]?.color || '#7b8986';
}

function updateGraphColors() {
  const nodeById = new Map(knowledgeGraphState.graph.nodes.map(node => [node.id, node]));
  byId('relation-graph').querySelectorAll('[data-node-id]').forEach(element => {
    const node = nodeById.get(element.dataset.nodeId);
    const circle = element.querySelector('.knowledge-node');
    if (node && circle) circle.style.fill = graphColor(node);
  });
}

function graphApplyZoomInvariantStyles(view) {
  const target = byId('relation-graph');
  const svg = target.querySelector('.knowledge-svg');
  if (!svg) return;
  const matrix = svg.getScreenCTM();
  const currentScreenScale = matrix ? Math.hypot(matrix.a, matrix.b) : 0;
  const fitScreenScale = Math.min(svg.clientWidth / 980, svg.clientHeight / 560);
  const inverseZoom = currentScreenScale > 0 && fitScreenScale > 0 ? fitScreenScale / currentScreenScale : view.width / 980;
  target.querySelectorAll('[data-base-radius]').forEach(circle => {
    circle.setAttribute('r', (Number(circle.dataset.baseRadius) * inverseZoom).toFixed(2));
  });
  target.querySelectorAll('[data-label-node-x]').forEach(label => {
    const x = Number(label.dataset.labelNodeX) + Number(label.dataset.labelOffsetX) * inverseZoom;
    const y = Number(label.dataset.labelNodeY) + Number(label.dataset.labelOffsetY) * inverseZoom;
    label.setAttribute('x', x.toFixed(2));
    label.setAttribute('y', y.toFixed(2));
    label.style.fontSize = `${(9.5 * inverseZoom).toFixed(2)}px`;
    label.style.strokeWidth = `${(4 * inverseZoom).toFixed(2)}px`;
    label.querySelectorAll('tspan').forEach(line => line.setAttribute('x', x.toFixed(2)));
  });
  graphUpdateLabelDensity(view);
}

function graphUpdateLabelDensity(view) {
  const labels = [...byId('relation-graph').querySelectorAll('[data-label-rank]')];
  const linearZoom = 980 / view.width;
  const atMaximumZoom = view.width <= 260;
  const targetCount = atMaximumZoom
    ? labels.length
    : Math.max(3, Math.min(labels.length, Math.round(10 * linearZoom * linearZoom)));
  labels.forEach(label => {
    label.classList.toggle('visible', Number(label.dataset.labelRank) < targetCount);
  });
}

function graphClampViewBox(view) {
  const minimumX = Math.min(0, 980 - view.width);
  const maximumX = Math.max(0, 980 - view.width);
  const minimumY = Math.min(0, 560 - view.height);
  const maximumY = Math.max(0, 560 - view.height);
  return {
    ...view,
    x: Math.max(minimumX, Math.min(maximumX, view.x)),
    y: Math.max(minimumY, Math.min(maximumY, view.y)),
  };
}

function graphSetViewBox(next) {
  const bounded = graphClampViewBox(next);
  knowledgeGraphState.viewBox = bounded;
  const svg = document.querySelector('.knowledge-svg');
  if (svg) svg.setAttribute('viewBox', `${bounded.x} ${bounded.y} ${bounded.width} ${bounded.height}`);
  graphApplyZoomInvariantStyles(bounded);
  requestAnimationFrame(() => graphApplyZoomInvariantStyles(bounded));
}

function graphBeginPan(event) {
  if (event.button !== 0 || event.target.closest('[data-node-id]')) return;
  const target = byId('relation-graph');
  const svg = target.querySelector('.knowledge-svg');
  if (!svg) return;
  const rect = svg.getBoundingClientRect();
  knowledgeGraphState.pan = {
    pointerId: event.pointerId,
    startX: event.clientX,
    startY: event.clientY,
    view: { ...knowledgeGraphState.viewBox },
    pixelWidth: Math.max(1, rect.width),
    pixelHeight: Math.max(1, rect.height),
  };
  target.setPointerCapture?.(event.pointerId);
  target.classList.add('panning');
  event.preventDefault();
}

function graphMovePan(event) {
  const pan = knowledgeGraphState.pan;
  if (!pan || pan.pointerId !== event.pointerId) return;
  const deltaX = (event.clientX - pan.startX) * pan.view.width / pan.pixelWidth;
  const deltaY = (event.clientY - pan.startY) * pan.view.height / pan.pixelHeight;
  graphSetViewBox({
    ...pan.view,
    x: pan.view.x - deltaX,
    y: pan.view.y - deltaY,
  });
}

function graphEndPan(event) {
  const pan = knowledgeGraphState.pan;
  if (!pan || pan.pointerId !== event.pointerId) return;
  const target = byId('relation-graph');
  if (target.hasPointerCapture?.(event.pointerId)) target.releasePointerCapture(event.pointerId);
  target.classList.remove('panning');
  knowledgeGraphState.pan = null;
}

function graphHighlight(nodeIds = []) {
  const selected = new Set(nodeIds);
  const target = byId('relation-graph');
  target.querySelectorAll('[data-node-id]').forEach(element => element.classList.toggle('dimmed', selected.size && !selected.has(element.dataset.nodeId)));
  target.querySelectorAll('[data-edge-source]').forEach(element => {
    const active = selected.has(element.dataset.edgeSource) && selected.has(element.dataset.edgeTarget);
    element.classList.toggle('highlighted', active);
    element.classList.toggle('dimmed', selected.size && !active);
  });
}

function renderGraphLegend() {
  const graph = knowledgeGraphState.graph;
  if (knowledgeGraphState.colorMode === 'community') {
    byId('graph-legend').innerHTML = graph.communities.map(community => `<button type="button" data-graph-community="${community.id}"><i style="background:${community.color}"></i><span>${escapeHtml(community.label)}</span><small>${community.node_count} · ${community.cohesion.toFixed(2)}</small></button>`).join('');
  } else {
    const counts = graph.nodes.reduce((result, node) => ({ ...result, [node.type]: (result[node.type] || 0) + 1 }), {});
    byId('graph-legend').innerHTML = Object.entries(counts).sort((a, b) => b[1] - a[1]).map(([type, count]) => `<div><i style="background:${scicodeKnowledgeTypeColor(type)}"></i><span>${escapeHtml(type)}</span><small>${count}</small></div>`).join('');
  }
}

function renderGraphInsights() {
  const insights = knowledgeGraphState.graph.insights;
  const sections = [
    ['PREDICTED LINKS', insights.predicted_connections || []],
    ['GRAPH ANOMALIES', insights.graph_anomalies || []],
  ];
  const content = sections.map(([label, items]) => {
    if (!items.length) return '';
    const cards = items.slice(0, 4).map(item => `<button type="button" data-graph-insight="${item.node_ids.map(encodeURIComponent).join('|')}"><span>${escapeHtml(item.title)}</span><small>${escapeHtml(item.description)}</small></button>`).join('');
    return `<section class="graph-insight-section"><p>${label}</p>${cards}</section>`;
  }).join('');
  byId('graph-insights').innerHTML = content || '<p class="graph-insight-empty">No predictions or anomalies detected.</p>';
}

function graphLabelWidth(value) {
  return [...value].reduce((width, character) => width + (character.codePointAt(0) > 255 ? 2 : 1), 0);
}

function graphTruncateLabelLine(value, maximumWidth) {
  let result = '';
  for (const character of value) {
    if (graphLabelWidth(result + character) > maximumWidth) break;
    result += character;
  }
  return result.trimEnd();
}

function graphWrappedLabel(label, lineWidth = 24, maxLines = 3) {
  const words = String(label).trim().split(/\s+/).filter(Boolean);
  const lines = [];
  let current = '';
  words.forEach(word => {
    if (graphLabelWidth(word) > lineWidth) {
      if (current) { lines.push(current); current = ''; }
      for (const character of word) {
        if (current && graphLabelWidth(current + character) > lineWidth) {
          lines.push(current);
          current = '';
        }
        current += character;
      }
    } else if (!current) {
      current = word;
    } else if (graphLabelWidth(`${current} ${word}`) <= lineWidth) {
      current = `${current} ${word}`;
    } else {
      lines.push(current);
      current = word;
    }
  });
  if (current) lines.push(current);
  if (!lines.length) return ['Untitled'];
  if (lines.length <= maxLines) return lines;
  const visible = lines.slice(0, maxLines);
  visible[maxLines - 1] = `${graphTruncateLabelLine(visible[maxLines - 1], lineWidth - 1)}…`;
  return visible;
}

function graphSpatialLabelRank(nodes, positions) {
  const diagonal = Math.hypot(980, 560);
  const importance = node => Math.max(.001, node.importance_score ?? node.weighted_degree ?? 0);
  const maximumImportance = Math.max(...nodes.map(importance), .001);
  const remaining = nodes.map(node => ({ node, nearest: Infinity }));
  const ranked = new Map();
  while (remaining.length) {
    const selectedCount = ranked.size;
    remaining.sort((a, b) => {
      const selectionScore = candidate => {
        const importanceTerm = importance(candidate.node) / maximumImportance;
        const spatialTerm = selectedCount === 0
          ? 1
          : Math.max(.02, Math.min(1, candidate.nearest / (diagonal * .35)));
        return Math.pow(importanceTerm, .6) * Math.pow(spatialTerm, .4);
      };
      return selectionScore(b) - selectionScore(a)
        || importance(b.node) - importance(a.node)
        || a.node.label.localeCompare(b.node.label);
    });
    const chosen = remaining.shift();
    ranked.set(chosen.node.id, selectedCount);
    const chosenPosition = positions[chosen.node.id];
    remaining.forEach(candidate => {
      const point = positions[candidate.node.id];
      candidate.nearest = Math.min(
        candidate.nearest,
        Math.hypot(point.x - chosenPosition.x, point.y - chosenPosition.y),
      );
    });
  }
  return ranked;
}

function renderGraphSvg() {
  const graph = knowledgeGraphState.graph;
  const positions = knowledgeGraphState.positions;
  const edgeKey = edge => [edge.source, edge.target].sort().join('\u0000');
  const displayEdges = graph.display_edges || graph.edges;
  const displayedByKey = new Map(displayEdges.map(edge => [edgeKey(edge), edge]));
  const allEdges = [...graph.edges].sort((a, b) => Number(displayedByKey.has(edgeKey(a))) - Number(displayedByKey.has(edgeKey(b))));
  const edges = allEdges.map(edge => {
    const displayed = displayedByKey.get(edgeKey(edge));
    const role = displayed?.display_role || 'context';
    const a = positions[edge.source]; const b = positions[edge.target];
    const classes = `knowledge-edge ${displayed ? 'selected' : 'context'} ${edge.signals.direct ? 'direct' : 'inferred'} ${role}`;
    const relationship = edge.signals.direct ? 'direct wikilink' : 'inferred relevance';
    const baseStrokeWidth = !displayed
      ? Math.min(1.25, .9 + edge.weight * .07)
      : edge.signals.direct
        ? Math.min(1.55, 1.05 + edge.weight * .055)
        : Math.min(1.35, .95 + edge.weight * .075);
    const strokeWidth = baseStrokeWidth;
    return `<line class="${classes}" data-edge-source="${escapeHtml(edge.source)}" data-edge-target="${escapeHtml(edge.target)}" x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" style="stroke-width:${strokeWidth.toFixed(2)}"><title>${escapeHtml(`${relationship} · ${role} · ${edge.reasons.join(' · ')} · ${edge.weight.toFixed(2)}`)}</title></line>`;
  }).join('');
  const labelRank = graphSpatialLabelRank(graph.nodes, positions);
  const nodes = graph.nodes.map(node => {
    const point = positions[node.id];
    const radius = node.size * point.scale * .78;
    const strokeWidth = .75 * point.scale;
    const hoverStrokeWidth = 1.25 * point.scale;
    const labelOffsetX = radius + 5 * point.scale;
    const labelOffsetY = 3 * point.scale;
    const labelX = point.x + labelOffsetX;
    const labelLines = graphWrappedLabel(node.label);
    const labelMarkup = labelLines.map((line, index) => `<tspan x="${labelX.toFixed(2)}" dy="${index ? '1.15em' : '0'}">${escapeHtml(line)}</tspan>`).join('');
    return `<a class="knowledge-node-group" data-node-id="${escapeHtml(node.id)}" href="wiki.html?page=${encodeURIComponent(node.id)}"><circle class="knowledge-node" data-base-radius="${radius.toFixed(2)}" cx="${point.x}" cy="${point.y}" r="${radius.toFixed(2)}" style="fill:${graphColor(node)};--node-stroke-width:${strokeWidth.toFixed(2)};--node-hover-stroke-width:${hoverStrokeWidth.toFixed(2)}"></circle><text class="knowledge-label" data-label-rank="${labelRank.get(node.id)}" data-label-node-x="${point.x}" data-label-node-y="${point.y}" data-label-offset-x="${labelOffsetX.toFixed(2)}" data-label-offset-y="${labelOffsetY.toFixed(2)}" x="${labelX.toFixed(2)}" y="${(point.y + labelOffsetY).toFixed(2)}">${labelMarkup}</text><title>${escapeHtml(node.label)}</title></a>`;
  }).join('');
  const view = knowledgeGraphState.viewBox;
  byId('relation-graph').innerHTML = `<svg class="relation-svg knowledge-svg" viewBox="${view.x} ${view.y} ${view.width} ${view.height}" role="img" aria-label="Weighted project knowledge graph">${edges}${nodes}</svg>`;
  graphApplyZoomInvariantStyles(view);
  byId('relation-graph').querySelectorAll('[data-node-id]').forEach(element => {
    element.addEventListener('mouseenter', () => {
      const id = element.dataset.nodeId;
      const neighbors = new Set([id]);
      graph.edges.forEach(edge => { if (edge.source === id) neighbors.add(edge.target); if (edge.target === id) neighbors.add(edge.source); });
      graphHighlight([...neighbors]);
      const node = graph.nodes.find(item => item.id === id);
      const tooltip = byId('graph-tooltip');
      tooltip.innerHTML = `<strong>${escapeHtml(node.label)}</strong><span>${escapeHtml(node.type)} · ${node.degree} links</span><small>${escapeHtml(node.summary || 'No summary')}</small>`;
      tooltip.hidden = false;
    });
    element.addEventListener('mouseleave', () => { graphHighlight(); byId('graph-tooltip').hidden = true; });
  });
}

function bindGraphControls() {
  document.querySelectorAll('[data-graph-color]').forEach(button => {
    button.onclick = () => {
      knowledgeGraphState.colorMode = button.dataset.graphColor;
      document.querySelectorAll('[data-graph-color]').forEach(item => item.classList.toggle('active', item === button));
      updateGraphColors(); renderGraphLegend();
    };
  });
  document.querySelectorAll('[data-graph-action]').forEach(button => {
    button.onclick = () => {
      const view = knowledgeGraphState.viewBox;
      if (button.dataset.graphAction === 'fit') return graphSetViewBox({ x: 0, y: 0, width: 980, height: 560 });
      const factor = button.dataset.graphAction === 'zoom-in' ? .8 : 1.25;
      const width = Math.max(260, Math.min(1800, view.width * factor));
      const height = width * 560 / 980;
      graphSetViewBox({ x: view.x + (view.width - width) / 2, y: view.y + (view.height - height) / 2, width, height });
    };
  });
  byId('graph-insights').onclick = event => {
    const button = event.target.closest('[data-graph-insight]');
    if (button) graphHighlight(button.dataset.graphInsight.split('|').map(decodeURIComponent));
  };
  byId('graph-legend').onclick = event => {
    const button = event.target.closest('[data-graph-community]');
    if (!button) return;
    const community = Number(button.dataset.graphCommunity);
    graphHighlight(knowledgeGraphState.graph.nodes.filter(node => node.community === community).map(node => node.id));
  };
  byId('relation-graph').onwheel = event => {
    event.preventDefault();
    const view = knowledgeGraphState.viewBox;
    const wheelDelta = Math.max(-24, Math.min(24, event.deltaY));
    const factor = Math.exp(wheelDelta * .0015);
    const width = Math.max(260, Math.min(1800, view.width * factor));
    const height = width * 560 / 980;
    graphSetViewBox({ x: view.x + (view.width - width) / 2, y: view.y + (view.height - height) / 2, width, height });
  };
  const graphTarget = byId('relation-graph');
  graphTarget.onpointerdown = graphBeginPan;
  graphTarget.onpointermove = graphMovePan;
  graphTarget.onpointerup = graphEndPan;
  graphTarget.onpointercancel = graphEndPan;
}

async function renderKnowledgeGraph() {
  byId('relation-graph').innerHTML = '<div class="graph-loading">Building relevance graph…</div>';
  const response = await fetch('/api/wiki', { cache: 'no-store' });
  if (!response.ok) throw new Error('Could not load knowledge graph');
  const wiki = await response.json();
  knowledgeGraphState.graph = wiki.graph;
  knowledgeGraphState.positions = graphLayout(wiki.graph);
  renderGraphSvg(); renderGraphLegend(); renderGraphInsights(); bindGraphControls();
  const emphasizedDirect = wiki.graph.display_edges.filter(edge => edge.signals.direct).length;
  byId('graph-count').textContent = `${wiki.graph.nodes.length} pages · ${wiki.graph.edges.length} links · ${wiki.graph.display_edges.length} emphasized (${emphasizedDirect} direct) · ${wiki.graph.communities.length} communities`;
}

function renderDashboard() {
  renderDashboardStats();
  renderWorkflowProgress();
  renderKnowledgeGraph().catch(error => {
    byId('relation-graph').innerHTML = `<div class="graph-empty"><strong>${escapeHtml(error.message)}</strong><p>Open the wiki directly to browse project knowledge.</p></div>`;
  });
  if (benchmarks.length) {
    const linked = new Set(benchmarks.flatMap(benchmark => benchmark.paper_ids || []));
    byId('next-panel').innerHTML = `<div class="panel-title-row"><div><p class="panel-kicker">BENCHMARK COVERAGE</p><h2>${benchmarks.length} benchmark${benchmarks.length === 1 ? '' : 's'} in workspace</h2></div><span class="empty-dot benchmark-live-dot" aria-hidden="true"></span></div><p>${linked.size} paper${linked.size === 1 ? '' : 's'} currently inform${linked.size === 1 ? 's' : ''} a benchmark. Continue adding relationships to make the graph useful for planning and review.</p><a class="panel-link" href="benchmarks.html">Open benchmark workspace →</a>`;
  }
}

window.addEventListener('DOMContentLoaded', () => {
  if (document.body.dataset.page === 'home') {
    renderDashboard();
  } else if (document.body.dataset.page === 'papers') {
    const params = new URLSearchParams(window.location.search);
    const requestedStage = params.get('stage');
    const requestedSort = params.get('sort');
    if (['all', 'listed', 'fetched', 'assessed', 'reviewed', 'linked'].includes(requestedStage)) selectedPaperStage = requestedStage;
    if (Object.hasOwn(sortLabels, requestedSort)) selectedPaperSort = requestedSort;
    renderPaperStats();
    byId('search').addEventListener('input', () => queueCatalogSearch('papers'));
    byId('paper-list').addEventListener('click', event => {
      const button = event.target.closest('[data-copy-paper-id]');
      if (!button) return;
      event.preventDefault();
      copyPaperId(button);
    });
    syncPaperSortMenu();
    byId('sort-trigger').addEventListener('click', () => {
      const menu = byId('sort-menu');
      const willOpen = menu.hidden;
      closePaperSortMenu();
      menu.hidden = !willOpen;
      byId('sort-trigger').setAttribute('aria-expanded', String(willOpen));
    });
    byId('sort-menu').addEventListener('click', event => {
      const option = event.target.closest('[data-sort-value]');
      if (!option) return;
      selectedPaperSort = option.dataset.sortValue;
      const nextUrl = new URL(window.location.href);
      if (selectedPaperSort === 'year') nextUrl.searchParams.delete('sort');
      else nextUrl.searchParams.set('sort', selectedPaperSort);
      window.history.replaceState(null, '', nextUrl);
      syncPaperSortMenu();
      closePaperSortMenu();
      renderPapers();
    });
    document.addEventListener('click', event => {
      if (!event.target.closest('.sort-picker')) closePaperSortMenu();
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') closePaperSortMenu();
    });
    byId('paper-stats').addEventListener('click', event => {
      const filter = event.target.closest('[data-paper-stage]');
      if (!filter) return;
      selectedPaperStage = filter.dataset.paperStage;
      const nextUrl = new URL(window.location.href);
      if (selectedPaperStage === 'all') nextUrl.searchParams.delete('stage');
      else nextUrl.searchParams.set('stage', selectedPaperStage);
      window.history.replaceState(null, '', nextUrl);
      renderPaperStats();
      queueCatalogSearch('papers');
    });
    const requestedPaper = params.get('paper');
    if (requestedPaper) byId('search').value = requestedPaper;
    queueCatalogSearch('papers');
  } else {
    const params = new URLSearchParams(window.location.search);
    const requestedStage = params.get('stage') || params.get('status');
    const requestedSort = params.get('sort');
    if (['all', 'problem-opened', 'researching', 'solution-drafted', 'verified'].includes(requestedStage)) selectedBenchmarkStage = requestedStage;
    if (Object.hasOwn(benchmarkSortLabels, requestedSort)) selectedBenchmarkSort = requestedSort;
    renderBenchmarkStats();
    byId('search').addEventListener('input', () => queueCatalogSearch('benchmarks'));
    byId('benchmark-list').addEventListener('click', event => {
      const button = event.target.closest('[data-copy-benchmark-id]');
      if (!button) return;
      event.preventDefault();
      copyBenchmarkId(button);
    });
    syncBenchmarkSortMenu();
    byId('sort-trigger').addEventListener('click', () => {
      const menu = byId('sort-menu');
      const willOpen = menu.hidden;
      closeBenchmarkSortMenu();
      menu.hidden = !willOpen;
      byId('sort-trigger').setAttribute('aria-expanded', String(willOpen));
    });
    byId('sort-menu').addEventListener('click', event => {
      const option = event.target.closest('[data-sort-value]');
      if (!option) return;
      selectedBenchmarkSort = option.dataset.sortValue;
      const nextUrl = new URL(window.location.href);
      if (selectedBenchmarkSort === 'stage') nextUrl.searchParams.delete('sort');
      else nextUrl.searchParams.set('sort', selectedBenchmarkSort);
      window.history.replaceState(null, '', nextUrl);
      syncBenchmarkSortMenu();
      closeBenchmarkSortMenu();
      renderBenchmarks();
    });
    document.addEventListener('click', event => {
      if (!event.target.closest('.sort-picker')) closeBenchmarkSortMenu();
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') closeBenchmarkSortMenu();
    });
    byId('benchmark-stats').addEventListener('click', event => {
      const filter = event.target.closest('[data-benchmark-stage]');
      if (!filter) return;
      selectedBenchmarkStage = filter.dataset.benchmarkStage;
      const nextUrl = new URL(window.location.href);
      nextUrl.searchParams.delete('status');
      if (selectedBenchmarkStage === 'all') nextUrl.searchParams.delete('stage');
      else nextUrl.searchParams.set('stage', selectedBenchmarkStage);
      window.history.replaceState(null, '', nextUrl);
      renderBenchmarkStats();
      queueCatalogSearch('benchmarks');
    });
    queueCatalogSearch('benchmarks');
  }
});
