(function registerSearchRouting(global) {
  function required(value, label) {
    if (typeof value !== 'string' || !value.trim()) {
      throw new Error(`Search target is missing ${label}`);
    }
    return value;
  }

  function searchTargetHref(target) {
    if (!target || typeof target !== 'object') throw new Error('Search target is missing');
    switch (target.kind) {
      case 'paper':
        return `paper.html?id=${encodeURIComponent(required(target.paper_id, 'paper_id'))}`;
      case 'benchmark':
        return `benchmark.html?id=${encodeURIComponent(required(target.benchmark_id, 'benchmark_id'))}`;
      case 'wiki': {
        const pageId = required(target.page_id, 'page_id');
        const scope = required(target.scope, 'scope');
        const params = new URLSearchParams();
        if (scope !== 'global') params.set('scope', scope);
        params.set('page', pageId);
        return `wiki.html?${params}`;
      }
      case 'talk':
        return `talk.html?thread=${encodeURIComponent(required(target.thread_id, 'thread_id'))}`;
      default:
        throw new Error(`Unsupported search target kind: ${String(target.kind || '')}`);
    }
  }

  global.searchTargetHref = searchTargetHref;
})(window);
