// In-page PDF reader. Cursor's embedded Chromium paints the native PDF plugin as a
// dark frame with no pages, so this viewer draws each page onto a canvas with PDF.js.
// The library is the unmodified Mozilla build in static/vendor/pdfjs/ (Apache-2.0).

(function () {
  const LIB = '/static/vendor/pdfjs/pdf.min.mjs';
  const WORKER = '/static/vendor/pdfjs/pdf.worker.min.mjs';
  const ZOOM_STEPS = [0.5, 0.75, 1, 1.25, 1.5, 2, 3, 4];
  const ICONS = {
    prev: '<i class="fa-solid fa-chevron-up" aria-hidden="true"></i>',
    next: '<i class="fa-solid fa-chevron-down" aria-hidden="true"></i>',
    minus: '<i class="fa-solid fa-minus" aria-hidden="true"></i>',
    plus: '<i class="fa-solid fa-plus" aria-hidden="true"></i>',
    width: '<i class="fa-solid fa-arrows-left-right" aria-hidden="true"></i>',
    page: '<i class="fa-solid fa-expand" aria-hidden="true"></i>',
    rotate: '<i class="fa-solid fa-rotate-right" aria-hidden="true"></i>',
    download: '<i class="fa-solid fa-download" aria-hidden="true"></i>'
  };
  let library;

  async function pdfjs() {
    if (library) return library;
    library = await import(LIB);
    library.GlobalWorkerOptions.workerSrc = WORKER;
    return library;
  }

  function fileName(url) {
    try {
      const parsed = new URL(url, window.location.origin);
      const parts = parsed.pathname.split('/').filter(Boolean);
      if (parts.at(-1) === 'pdf' && parts.length >= 2) return `${parts.at(-2)}.pdf`;
      return decodeURIComponent(parts.at(-1) || 'paper.pdf');
    } catch {
      return 'paper.pdf';
    }
  }

  function toolbarMarkup() {
    return `<div class="pdf-toolbar" role="toolbar" aria-label="PDF controls">
      <div class="pdf-toolbar-group">
        <button type="button" data-pdf-act="prev" aria-label="Previous page" title="Previous page">${ICONS.prev}</button>
        <label class="pdf-page-control">
          <input data-pdf-page inputmode="numeric" aria-label="Page number">
          <span>/ <em data-pdf-total>1</em></span>
        </label>
        <button type="button" data-pdf-act="next" aria-label="Next page" title="Next page">${ICONS.next}</button>
      </div>
      <div class="pdf-toolbar-group pdf-toolbar-zoom">
        <button type="button" data-pdf-act="zoom-out" aria-label="Zoom out" title="Zoom out">${ICONS.minus}</button>
        <span class="pdf-zoom-label" data-pdf-zoom>100%</span>
        <button type="button" data-pdf-act="zoom-in" aria-label="Zoom in" title="Zoom in">${ICONS.plus}</button>
        <button type="button" data-pdf-act="fit-width" aria-label="Fit to width" title="Fit to width">${ICONS.width}</button>
        <button type="button" data-pdf-act="fit-page" aria-label="Fit to page" title="Fit to page">${ICONS.page}</button>
      </div>
      <div class="pdf-toolbar-group">
        <button type="button" data-pdf-act="rotate" aria-label="Rotate clockwise" title="Rotate clockwise">${ICONS.rotate}</button>
        <a class="pdf-download" data-pdf-download download aria-label="Download PDF" title="Download">${ICONS.download}</a>
      </div>
    </div>
    <div class="pdf-stage">
      <p class="pdf-status">Loading PDF…</p>
      <div class="pdf-pages" hidden></div>
    </div>`;
  }

  function pageViewport(page, scale, rotation) {
    return page.getViewport({ scale, rotation: (page.rotate + rotation) % 360 });
  }

  function computeScale(state) {
    const base = state.base;
    const pad = 32;
    const availW = Math.max(240, state.stage.clientWidth - pad);
    const availH = Math.max(240, state.stage.clientHeight - pad);
    if (state.mode === 'width') return availW / base.width;
    if (state.mode === 'page') return Math.min(availW / base.width, availH / base.height);
    return state.scale;
  }

  function syncChrome(state) {
    const percent = Math.round(state.currentScale * 100);
    state.root.querySelector('[data-pdf-zoom]').textContent = `${percent}%`;
    state.root.querySelector('[data-pdf-total]').textContent = String(state.pdf.numPages);
    const pageInput = state.root.querySelector('[data-pdf-page]');
    if (document.activeElement !== pageInput) pageInput.value = String(state.currentPage);
    state.root.querySelector('[data-pdf-act="prev"]').disabled = state.currentPage <= 1;
    state.root.querySelector('[data-pdf-act="next"]').disabled = state.currentPage >= state.pdf.numPages;
    state.root.querySelector('[data-pdf-act="fit-width"]').classList.toggle('active', state.mode === 'width');
    state.root.querySelector('[data-pdf-act="fit-page"]').classList.toggle('active', state.mode === 'page');
  }

  async function paintPage(state, number) {
    const item = state.pages[number - 1];
    if (!item || item.drawn === state.paintKey) return;
    const page = await state.pdf.getPage(number);
    if (item.drawn === state.paintKey) return;
    const viewport = pageViewport(page, state.currentScale, state.rotation);
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    const canvas = item.canvas;
    canvas.width = Math.floor(viewport.width * ratio);
    canvas.height = Math.floor(viewport.height * ratio);
    canvas.style.width = `${Math.floor(viewport.width)}px`;
    canvas.style.height = `${Math.floor(viewport.height)}px`;
    const context = canvas.getContext('2d', { alpha: false });
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    if (item.task) {
      try { item.task.cancel(); } catch { /* already finished */ }
    }
    const task = page.render({ canvasContext: context, viewport });
    item.task = task;
    try {
      await task.promise;
      item.drawn = state.paintKey;
    } catch (error) {
      if (error?.name !== 'RenderingCancelledException') throw error;
    }
  }

  async function paintVisible(state) {
    const stage = state.stage.getBoundingClientRect();
    const visible = [];
    state.pages.forEach((item, index) => {
      const box = item.wrap.getBoundingClientRect();
      if (box.bottom >= stage.top - 400 && box.top <= stage.bottom + 400) visible.push(index + 1);
    });
    const order = visible.length ? visible : [state.currentPage];
    for (const number of order) await paintPage(state, number);
  }

  function updateCurrentPage(state) {
    const mid = state.stage.getBoundingClientRect().top + state.stage.clientHeight / 3;
    let current = 1;
    state.pages.forEach((item, index) => {
      if (item.wrap.getBoundingClientRect().top <= mid) current = index + 1;
    });
    if (current !== state.currentPage) {
      state.currentPage = current;
      syncChrome(state);
    }
  }

  async function relayout(state) {
    const page = await state.pdf.getPage(1);
    state.base = pageViewport(page, 1, state.rotation);
    state.currentScale = computeScale(state);
    state.paintKey = `${state.currentScale}:${state.rotation}:${state.root.clientWidth}`;
    syncChrome(state);
    await paintVisible(state);
  }

  function goToPage(state, number) {
    const target = Math.min(Math.max(1, number), state.pdf.numPages);
    state.currentPage = target;
    state.pages[target - 1].wrap.scrollIntoView({ block: 'start' });
    syncChrome(state);
    paintVisible(state);
  }

  function changeZoom(state, nextScale) {
    const clamped = Math.min(4, Math.max(0.4, nextScale));
    state.mode = 'custom';
    state.scale = clamped;
    relayout(state);
  }

  function stepZoom(state, direction) {
    const current = state.currentScale;
    const next = direction < 0
      ? [...ZOOM_STEPS].reverse().find(step => step < current - 0.01)
      : ZOOM_STEPS.find(step => step > current + 0.01);
    changeZoom(state, next || (direction < 0 ? Math.max(0.4, current / 1.25) : Math.min(4, current * 1.25)));
  }

  function bind(state) {
    state.root.addEventListener('click', event => {
      const button = event.target.closest('[data-pdf-act]');
      if (!button || !state.root.contains(button)) return;
      const act = button.dataset.pdfAct;
      if (act === 'prev') goToPage(state, state.currentPage - 1);
      if (act === 'next') goToPage(state, state.currentPage + 1);
      if (act === 'zoom-out') stepZoom(state, -1);
      if (act === 'zoom-in') stepZoom(state, 1);
      if (act === 'fit-width') { state.mode = 'width'; relayout(state); }
      if (act === 'fit-page') { state.mode = 'page'; relayout(state); }
      if (act === 'rotate') { state.rotation = (state.rotation + 90) % 360; relayout(state); }
    });
    state.root.querySelector('[data-pdf-page]').addEventListener('change', event => {
      goToPage(state, Number.parseInt(event.target.value, 10) || 1);
    });
    state.stage.addEventListener('scroll', () => {
      updateCurrentPage(state);
      window.clearTimeout(state.scrollTimer);
      state.scrollTimer = window.setTimeout(() => paintVisible(state), 80);
    }, { passive: true });
    state.root.tabIndex = 0;
    state.root.addEventListener('keydown', event => {
      if (event.target.closest('input, textarea')) return;
      if (event.key === 'ArrowUp' || event.key === 'PageUp') { event.preventDefault(); goToPage(state, state.currentPage - 1); }
      if (event.key === 'ArrowDown' || event.key === 'PageDown') { event.preventDefault(); goToPage(state, state.currentPage + 1); }
      if (event.key === '+' || event.key === '=') { event.preventDefault(); state.root.querySelector('[data-pdf-act="zoom-in"]').click(); }
      if (event.key === '-' || event.key === '_') { event.preventDefault(); state.root.querySelector('[data-pdf-act="zoom-out"]').click(); }
      if (event.key === '0') { event.preventDefault(); state.mode = 'width'; relayout(state); }
    });
  }

  async function mount(container, url) {
    if (!container || !url) return;
    const generation = Number(container.dataset.pdfGeneration || 0) + 1;
    container.dataset.pdfGeneration = String(generation);
    container.classList.add('pdf-shell');
    container.innerHTML = toolbarMarkup();
    const status = container.querySelector('.pdf-status');
    const pagesNode = container.querySelector('.pdf-pages');
    const download = container.querySelector('[data-pdf-download]');
    download.href = url;
    download.setAttribute('download', fileName(url));
    try {
      const pdfjsLib = await pdfjs();
      if (container.dataset.pdfGeneration !== String(generation)) return;
      const pdf = await pdfjsLib.getDocument({ url, verbosity: 0 }).promise;
      if (container.dataset.pdfGeneration !== String(generation)) return;
      const state = {
        root: container,
        stage: container.querySelector('.pdf-stage'),
        pdf,
        pages: [],
        mode: 'width',
        scale: 1,
        currentScale: 1,
        rotation: 0,
        currentPage: 1,
        paintKey: '',
        base: { width: 1, height: 1 }
      };
      for (let number = 1; number <= pdf.numPages; number += 1) {
        const wrap = document.createElement('div');
        wrap.className = 'pdf-page';
        wrap.dataset.page = String(number);
        const canvas = document.createElement('canvas');
        canvas.setAttribute('aria-label', `Page ${number}`);
        wrap.appendChild(canvas);
        pagesNode.appendChild(wrap);
        state.pages.push({ wrap, canvas, drawn: '', task: null });
      }
      pagesNode.hidden = false;
      status.remove();
      bind(state);
      if (container._pdfResize) container._pdfResize.disconnect();
      let timer = 0;
      const observer = new ResizeObserver(() => {
        window.clearTimeout(timer);
        timer = window.setTimeout(() => relayout(state), 120);
      });
      observer.observe(container);
      container._pdfResize = observer;
      container._pdfState = state;
      await relayout(state);
    } catch (error) {
      if (container.dataset.pdfGeneration !== String(generation)) return;
      status.textContent = `PDF viewer failed to render this file. ${String(error.message || error)} `;
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName(url));
      link.textContent = 'Download PDF';
      status.appendChild(link);
    }
  }

  window.SciCodePdfViewer = { mount };
})();
