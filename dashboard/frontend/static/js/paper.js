const paperId = new URLSearchParams(window.location.search).get('id');
const state = {
  paper: null,
  draftItems: { followup_ideas: null, potential_pitfalls: null },
  draggedCard: null
};
const el = (id) => document.getElementById(id);
const levelWeight = { high: 3, medium: 2, low: 1 };
const feasibilityWeight = { yes: 2, uncertain: 1, no: 0 };
const normalizeRatingValue = value => value === true ? 'yes' : value === false ? 'no' : value;
const escapeText = (value = '') => String(value).replace(/[&<>"']/g, character => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
})[character]);

function typeset(element) {
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

function contextCard(text, kind, field, index = '', isDraft = false) {
  const indexAttribute = index === '' ? '' : ` data-context-index="${index}"`;
  const draftAttribute = isDraft ? ' data-context-draft="true"' : '';
  const blankClass = String(text).trim() ? '' : ' blank-context';
  const dragHandle = isDraft ? '' : `<span class="context-drag-handle" draggable="true" role="button" tabindex="0" aria-label="Drag to reorder ${escapeText(kind.toLowerCase())}" title="Drag to reorder" aria-hidden="false">⠿</span>`;
  return `<li class="context-card array-context${blankClass}" tabindex="0" data-context-kind="${escapeText(kind)}" data-context-field="${escapeText(field)}"${indexAttribute}${draftAttribute} data-context-text="${escapeText(text)}">${dragHandle}<span class="context-text">${escapeText(text)}</span><button class="context-delete" type="button" aria-label="Delete ${escapeText(kind.toLowerCase())}">×</button><button class="context-edit" type="button" aria-label="Edit ${escapeText(kind.toLowerCase())}" title="Edit"><i class="fa-regular fa-pen" aria-hidden="true"></i></button></li>`;
}

function editableContext(text, kind, field) {
  const displayText = text || `${kind} pending.`;
  return `<div class="context-card editable-context" tabindex="0" data-context-kind="${escapeText(kind)}" data-context-field="${escapeText(field)}" data-context-text="${escapeText(text)}"><span class="context-text">${escapeText(displayText)}</span><button class="context-edit" type="button" aria-label="Edit ${escapeText(kind.toLowerCase())}" title="Edit"><i class="fa-regular fa-pen" aria-hidden="true"></i></button></div>`;
}

function arrayItems(items, emptyText, kind, field) {
  const values = items || [];
  const draft = state.draftItems[field];
  if (!values.length && draft === null) return `<p class="empty-copy">${escapeText(emptyText)}</p>`;
  const savedCards = values.map((item, index) => contextCard(item, kind, field, index)).join('');
  const draftCard = draft === null ? '' : contextCard(draft, kind, field, values.length, true);
  return `<ul class="context-list context-collection">${savedCards}${draftCard}</ul>`;
}

function listHeading(label, field) {
  return `<div class="assessment-section-heading"><h3>${escapeText(label)}</h3><button class="context-add-item" type="button" data-add-context="${escapeText(field)}" aria-label="Add ${escapeText(label.toLowerCase())}">+</button></div>`;
}

function stage(assessment, hasAssessment, assets) {
  if (!hasAssessment) return assets?.pdf || assets?.source ? 'fetched' : 'listed';
  return ['assessed', 'reviewed'].includes(assessment.stage) ? assessment.stage : 'assessed';
}

function closePickerMenus(except = null) {
  document.querySelectorAll('.assessment-picker .picker-menu').forEach(menu => {
    if (menu === except) return;
    menu.hidden = true;
    menu.previousElementSibling?.setAttribute('aria-expanded', 'false');
  });
}

function bindMenuTrigger(trigger) {
  trigger.addEventListener('click', () => {
    const menu = trigger.nextElementSibling;
    const willOpen = menu.hidden;
    closePickerMenus(menu);
    menu.hidden = !willOpen;
    trigger.setAttribute('aria-expanded', String(willOpen));
  });
}

function renderHeader() {
  const { publication, assessment, assets, has_assessment: hasAssessment } = state.paper;
  const sourceLink = assets.source_url
    ? `<a class="source-button" href="${escapeText(assets.source_url)}" target="_blank" rel="noreferrer">Source paper ↗</a>`
    : '';
  const sourceArchive = assets.source
    ? `<a class="source-button secondary" href="${assets.source}">LaTeX source ↓</a>`
    : '';
  const currentStage = stage(assessment, hasAssessment, assets);
  el('paper-header').innerHTML = `
    <div class="detail-heading-row">
      <div class="row-heading"><div class="assessment-picker stage-picker">
        <button id="stage-trigger" class="stage stage-${currentStage}" type="button" aria-haspopup="menu" aria-expanded="false">${currentStage}</button>
        <div class="picker-menu stage-menu" role="menu" hidden>
          ${['listed', 'fetched', 'assessed', 'reviewed'].map(item => `<button type="button" role="menuitem" data-stage-value="${item}"${item === currentStage ? ' class="selected"' : ''}>${item}</button>`).join('')}
        </div>
      </div><button id="paper-id-copy" class="paper-id paper-id-copy" type="button" aria-label="Copy paper ID ${escapeText(paperId)}" title="Copy paper ID">${escapeText(paperId)}</button></div>
      <div class="source-actions">${sourceLink}${sourceArchive}</div>
    </div>
    <h1>${escapeText(assessment.title || publication.title)}</h1>
    <p class="detail-authors">${escapeText(assessment.authors || (publication.authors || []).map(author => author.name).join(', '))}</p>
    <p class="detail-venue">${escapeText(publication.journal || publication.conference || '')}${publication.year ? ` · ${escapeText(publication.year)}` : ''}</p>
    <div class="task-type-row">${(assessment.suggested_task_types || []).map(item => `<span>${escapeText(item)}</span>`).join('') || '<span class="muted-chip">Task types pending</span>'}</div>`;
  bindMenuTrigger(el('stage-trigger'));
  el('paper-id-copy').addEventListener('click', async () => {
    try {
      await writeClipboard(paperId);
      showCopyNotice('Paper ID copied');
    } catch (error) {
      showCopyNotice(error.message || 'Could not copy paper ID.', true);
    }
  });
  el('paper-header').querySelectorAll('[data-stage-value]').forEach(option => option.addEventListener('click', () => {
    closePickerMenus();
    updateAssessmentField('stage', option.dataset.stageValue, el('stage-trigger'));
  }));
  document.title = `${assessment.title || publication.title} · Paper to Benchmark`;
  typeset(el('paper-header'));
}

function paperScore(assessment) {
  const values = [
    assessment.computational_depth, assessment.scientific_judgment, assessment.validation_ease,
    assessment.workstation_feasible, assessment.reference_solution_feasible,
    assessment.non_searchable_extension_possible, assessment.supervision_confidence
  ].map(normalizeRatingValue);
  if (values.some(value => !value)) return null;
  const weights = [
    levelWeight[values[0]], levelWeight[values[1]], levelWeight[values[2]],
    feasibilityWeight[values[3]], feasibilityWeight[values[4]], feasibilityWeight[values[5]],
    levelWeight[values[6]]
  ];
  if (weights.some(value => !Number.isFinite(value))) return null;
  const raw = weights.reduce((total, value) => total + value, 0);
  return Math.round(raw / 18 * 100);
}

function ratingTable(assessment) {
  const ratings = [
    ['Computational depth', 'computational_depth', normalizeRatingValue(assessment.computational_depth), ['low', 'medium', 'high']],
    ['Scientific judgment', 'scientific_judgment', normalizeRatingValue(assessment.scientific_judgment), ['low', 'medium', 'high']],
    ['Validation ease', 'validation_ease', normalizeRatingValue(assessment.validation_ease), ['low', 'medium', 'high']],
    ['Workstation feasible', 'workstation_feasible', normalizeRatingValue(assessment.workstation_feasible), ['no', 'uncertain', 'yes']],
    ['Reference feasible', 'reference_solution_feasible', normalizeRatingValue(assessment.reference_solution_feasible), ['no', 'uncertain', 'yes']],
    ['New extension possible', 'non_searchable_extension_possible', normalizeRatingValue(assessment.non_searchable_extension_possible), ['no', 'uncertain', 'yes']],
    ['Supervision confidence', 'supervision_confidence', normalizeRatingValue(assessment.supervision_confidence), ['low', 'medium', 'high']]
  ];
  return `<div class="detail-ratings">${ratings.map(([name, field, value, options]) => `
    <div class="rating-control"><span>${escapeText(name)}</span><div class="assessment-picker rating-picker">
      <button type="button" class="rating-value value-${escapeText(value || 'pending')}" data-rating-trigger="${field}" aria-label="Change ${escapeText(name)}" aria-haspopup="menu" aria-expanded="false">${escapeText(value || 'pending')}</button>
      <div class="picker-menu rating-menu" role="menu" hidden>${options.map(option => `<button type="button" role="menuitem" data-rating-field="${field}" data-rating-value="${option}"${option === value ? ' class="selected"' : ''}>${option}</button>`).join('')}</div>
    </div></div>`).join('')}</div>`;
}

function renderAssessment() {
  const { assessment } = state.paper;
  const score = paperScore(assessment);
  const previousScrollTop = el('assessment-panel').querySelector('.assessment-scroll-body')?.scrollTop || 0;
  el('assessment-panel').innerHTML = `
    <div class="panel-heading assessment-heading"><p class="panel-kicker">SciCode assessment</p><div class="assessment-heading-actions"><span id="save-notice" class="save-notice" role="status"></span><div class="detail-score"><strong>${score ?? '—'}</strong><span>/ 100</span></div></div></div>
    ${ratingTable(assessment)}
    <div class="assessment-scroll-body">
      <section class="assessment-section"><h3>Assessment</h3>${editableContext(assessment.ai_assessment, 'Assessment', 'ai_assessment')}</section>
      <section class="assessment-section"><h3>Computational core</h3>${editableContext(assessment.computational_core, 'Computational core', 'computational_core')}</section>
      <div class="assessment-columns">
        <section class="assessment-section">${listHeading('Follow-up ideas', 'followup_ideas')}${arrayItems(assessment.followup_ideas, 'No follow-up ideas yet.', 'Follow-up idea', 'followup_ideas')}</section>
        <section class="assessment-section pitfall-section">${listHeading('Potential pitfalls', 'potential_pitfalls')}${arrayItems(assessment.potential_pitfalls, 'No potential pitfalls recorded yet.', 'Potential pitfall', 'potential_pitfalls')}</section>
      </div>
    </div>
  `;
  el('assessment-panel').querySelector('.assessment-scroll-body').scrollTop = previousScrollTop;
  el('assessment-panel').querySelectorAll('[data-rating-trigger]').forEach(bindMenuTrigger);
  el('assessment-panel').querySelectorAll('[data-rating-value]').forEach(option => {
    option.addEventListener('click', () => {
      const trigger = el('assessment-panel').querySelector(`[data-rating-trigger="${option.dataset.ratingField}"]`);
      closePickerMenus();
      updateAssessmentField(option.dataset.ratingField, option.dataset.ratingValue, trigger);
    });
  });
  el('assessment-panel').querySelectorAll('[data-add-context]').forEach(button => {
    button.addEventListener('click', () => addBlankContextItem(button.dataset.addContext));
  });
  el('assessment-panel').querySelectorAll('.context-card').forEach(bindContextCard);
  typeset(el('assessment-panel'));
}

function renderPdf() {
  const { assets, assessment } = state.paper;
  el('pdf-panel').innerHTML = `
    <div class="panel-heading"><p class="panel-kicker">Full text</p>${assets.pdf ? `<a class="text-button" href="${assets.pdf}" target="_blank">Open separately ↗</a>` : ''}</div>
    ${assets.pdf
      ? `<iframe class="pdf-viewer" title="PDF for ${escapeText(assessment.title)}" src="${assets.pdf}#view=FitH"></iframe>`
      : `<div class="pdf-empty"><strong>Local PDF unavailable</strong><p>Ingest this paper to display its PDF here.</p>${assets.source_url ? `<a class="source-button" href="${escapeText(assets.source_url)}" target="_blank" rel="noreferrer">Open source paper ↗</a>` : ''}</div>`}`;
}

function showNotice(message, isError = false) {
  const notice = el('save-notice');
  if (!notice) return;
  notice.textContent = message;
  notice.classList.toggle('error', isError);
  window.clearTimeout(showNotice.timeout);
  if (!isError) showNotice.timeout = window.setTimeout(() => { notice.textContent = ''; }, 1800);
}

function showCopyNotice(message, isError = false) {
  const notice = el('copy-notice');
  if (!notice) return;
  notice.textContent = message;
  notice.classList.toggle('error', isError);
  notice.classList.add('visible');
  window.clearTimeout(showCopyNotice.timeout);
  showCopyNotice.timeout = window.setTimeout(() => notice.classList.remove('visible'), 1600);
}

async function writeClipboard(text) {
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

async function copyCardContext(card) {
  const text = (card.dataset.contextText || '').trim();
  if (!text) return;
  const kind = card.dataset.contextKind || 'Paper context';
  const payload = `Paper: ${paperId}\n[${kind}]\n${text}\n---\n`;
  try {
    await writeClipboard(payload);
    showCopyNotice('Context copied');
  } catch (error) {
    showCopyNotice(error.message || 'Could not copy context.', true);
  }
}

function bindContextCard(card) {
  card.addEventListener('click', event => {
    if (event.target.closest('.context-delete,.context-edit,.context-drag-handle') || card.classList.contains('editing')) return;
    copyCardContext(card);
  });
  card.addEventListener('keydown', event => {
    if (event.target.closest?.('.context-delete,.context-edit')) return;
    if (event.key === 'Enter' && !card.classList.contains('editing')) {
      event.preventDefault();
      copyCardContext(card);
    }
  });
  card.querySelector('.context-edit')?.addEventListener('click', event => {
    event.preventDefault();
    event.stopPropagation();
    beginCardEdit(card);
  });
  card.querySelector('.context-delete')?.addEventListener('click', event => {
    event.preventDefault();
    event.stopPropagation();
    deleteContextItem(card, event.currentTarget);
  });
  bindCardReordering(card);
}

function bindCardReordering(card) {
  const handle = card.querySelector('.context-drag-handle');
  if (!handle) return;
  handle.addEventListener('click', event => event.stopPropagation());
  handle.addEventListener('dblclick', event => event.stopPropagation());
  handle.addEventListener('dragstart', event => {
    if (card.classList.contains('editing')) {
      event.preventDefault();
      return;
    }
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/plain', card.dataset.contextText || '');
    state.draggedCard = card;
    card.closest('.context-list')?.classList.add('reordering');
    requestAnimationFrame(() => card.classList.add('dragging'));
  });
  card.addEventListener('dragover', event => {
    const dragged = state.draggedCard;
    if (!dragged || dragged === card || dragged.dataset.contextField !== card.dataset.contextField) return;
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
    const list = card.parentElement;
    const insertBefore = event.clientY < card.getBoundingClientRect().top + card.offsetHeight / 2;
    list.insertBefore(dragged, insertBefore ? card : card.nextSibling);
  });
  card.addEventListener('drop', event => {
    if (state.draggedCard?.dataset.contextField === card.dataset.contextField) event.preventDefault();
  });
  handle.addEventListener('dragend', () => finishCardReordering(card));
}

async function finishCardReordering(card) {
  const list = card.closest('.context-list');
  const field = card.dataset.contextField;
  const current = [...(state.paper.assessment[field] || [])];
  const order = [...list.querySelectorAll('.array-context:not([data-context-draft="true"])')]
    .map(item => Number(item.dataset.contextIndex));
  const reordered = order.map(index => current[index]);
  state.draggedCard = null;
  list.classList.remove('reordering');
  card.classList.remove('dragging');
  if (order.every((index, position) => index === position)) return;
  const saved = await saveAssessmentPatch(
    { [field]: reordered },
    null,
    `Could not reorder ${card.dataset.contextKind.toLowerCase()}s.`
  );
  if (!saved) renderAssessment();
}

function addBlankContextItem(field) {
  if (!(field in state.draftItems)) return;
  state.draftItems[field] = state.draftItems[field] ?? '';
  renderAssessment();
  el('assessment-panel').querySelector(`[data-context-field="${field}"][data-context-draft="true"]`)?.scrollIntoView({ block: 'nearest' });
}

async function deleteContextItem(card, button) {
  const field = card.dataset.contextField;
  const label = card.dataset.contextKind.toLowerCase();
  if (!(await confirmDeletion(label))) return;
  if (card.dataset.contextDraft === 'true') {
    state.draftItems[field] = null;
    renderAssessment();
    return;
  }
  const values = [...(state.paper.assessment[field] || [])];
  values.splice(Number(card.dataset.contextIndex), 1);
  await saveAssessmentPatch({ [field]: values }, button, `Could not delete this ${label}.`);
}

function confirmDeletion(label) {
  const dialog = el('delete-dialog');
  el('delete-dialog-message').textContent = `Delete this ${label}?`;
  dialog.returnValue = 'cancel';
  dialog.showModal();
  return new Promise(resolve => {
    dialog.addEventListener('close', () => resolve(dialog.returnValue === 'delete'), { once: true });
  });
}

function placeCaretAtEnd(element) {
  const selection = window.getSelection();
  const endRange = document.createRange();
  endRange.selectNodeContents(element);
  endRange.collapse(false);
  selection.removeAllRanges();
  selection.addRange(endRange);
}

async function beginCardEdit(card) {
  if (card.classList.contains('editing')) return;
  const textNode = card.querySelector('.context-text');
  if (!textNode) return;
  const original = card.dataset.contextText || '';
  textNode.textContent = original;
  textNode.contentEditable = 'true';
  textNode.classList.add('context-editor');
  card.classList.add('editing');
  let finished = false;
  const finish = async () => {
    if (finished) return;
    finished = true;
    const value = textNode.innerText.trim();
    const field = card.dataset.contextField;
    const isDraft = card.dataset.contextDraft === 'true';
    if (!value) {
      if (isDraft) state.draftItems[field] = null;
      renderAssessment();
      return;
    }
    if (value === original && !isDraft) {
      renderAssessment();
      return;
    }
    const index = card.dataset.contextIndex;
    let patch;
    if (index === undefined) {
      patch = { [field]: value };
    } else {
      const values = [...(state.paper.assessment[field] || [])];
      if (isDraft) values.push(value);
      else values[Number(index)] = value;
      patch = { [field]: values };
    }
    if (isDraft) state.draftItems[field] = value;
    const saved = await saveAssessmentPatch(
      patch,
      textNode,
      'Could not save this text.',
      isDraft ? () => { state.draftItems[field] = null; } : null
    );
    if (!saved && isDraft) renderAssessment();
  };
  textNode.addEventListener('blur', finish, { once: true });
  textNode.addEventListener('keydown', keyEvent => {
    if (keyEvent.key === 'Escape') {
      keyEvent.preventDefault();
      textNode.textContent = original;
      textNode.blur();
    }
    if ((keyEvent.metaKey || keyEvent.ctrlKey) && keyEvent.key === 'Enter') {
      keyEvent.preventDefault();
      textNode.blur();
    }
  });
  textNode.focus();
  placeCaretAtEnd(textNode);
}

async function saveAssessmentPatch(patch, control, errorMessage = 'Could not save this change.', beforeRender = null) {
  if (control) control.disabled = true;
  try {
    const response = await fetch(`/api/papers/${encodeURIComponent(paperId)}/assessment/apply`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ patch })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || errorMessage);
    state.paper = data.paper;
    beforeRender?.();
    // Assessment edits are local to the left panel. Keep the PDF iframe alive so
    // its scroll position and browser-managed full-text state are not reset.
    renderHeader(); renderAssessment();
    showNotice('Saved');
    return true;
  } catch (error) {
    if (control) control.disabled = false;
    showNotice(error.message, true);
    return false;
  }
}

async function updateAssessmentField(field, value, control) {
  await saveAssessmentPatch({ [field]: value }, control, 'Could not save this rating.');
}

async function initialize() {
  if (!paperId) {
    el('paper-header').innerHTML = '<div class="empty-state"><strong>No paper selected.</strong><a href="papers.html">Return to the paper list</a></div>';
    return;
  }
  try {
    const response = await fetch(`/api/papers/${encodeURIComponent(paperId)}`);
    if (!response.ok) throw new Error('Paper not found');
    state.paper = await response.json();
    renderHeader(); renderAssessment(); renderPdf();
  } catch (error) {
    el('paper-header').innerHTML = `<div class="empty-state"><strong>${escapeText(error.message)}</strong><a href="papers.html">Return to the paper list</a></div>`;
  }
}

window.addEventListener('DOMContentLoaded', () => {
  document.addEventListener('click', event => {
    if (!event.target.closest('.assessment-picker')) closePickerMenus();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closePickerMenus();
  });
  initialize();
});
