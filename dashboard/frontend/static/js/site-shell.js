const dashboardNav = [
  ['index.html', 'Home', ['home']],
  ['papers.html', 'Papers', ['papers', 'paper-detail']],
  ['benchmarks.html', 'Benchmarks', ['benchmarks', 'benchmark-detail', 'benchmark-document', 'benchmark-code']],
  ['wiki.html', 'Wiki', ['wiki']],
  ['talk.html', 'Talk', ['project-talk']],
];

const dashboardBrandSvg = '<svg viewBox="0 0 24 24"><path d="M4.5 2.75h7.25l3.5 3.5v4.55"/><path d="M11.7 18.75H4.5a2 2 0 0 1-2-2v-12a2 2 0 0 1 2-2"/><path d="M11.75 2.75v3.5h3.5"/><path d="M6 10h5.25M6 13h3.5"/><circle cx="17.5" cy="16.5" r="3.4"/><circle cx="17.5" cy="16.5" r="1.05"/><path d="M17.5 11.8v1.3M17.5 19.9v1.3M12.8 16.5h1.3M20.9 16.5h1.3M14.18 13.18l.92.92M19.9 18.9l.92.92M20.82 13.18l-.92.92M15.1 18.9l-.92.92"/></svg>';

function renderSiteHeader() {
  const mount = document.getElementById('site-header');
  if (!mount) return;
  const page = document.body.dataset.page;
  const navigation = dashboardNav.map(([href, label, pages]) => {
    const active = pages.includes(page);
    return `<a${active ? ' class="active" aria-current="page"' : ''} href="${href}">${label}</a>`;
  }).join('');
  mount.outerHTML = `<header class="site-header"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">${dashboardBrandSvg}</span><span>Paper to Benchmark</span></a><nav aria-label="Primary navigation">${navigation}</nav></header>`;
}

renderSiteHeader();
