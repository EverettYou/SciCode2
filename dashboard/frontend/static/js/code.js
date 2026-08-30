const codeParams = new URLSearchParams(window.location.search);
const codePath = codeParams.get('path') || '';
const codeEl = id => document.getElementById(id);

function codeResourceUrl(path) {
  return `/api/resources/${path.split('/').map(encodeURIComponent).join('/')}`;
}

function sourceTitle(path) {
  return path.split('/').pop()?.replace(/\.py$/i, '') || 'Python source';
}

function showCodeError(message) {
  codeEl('code-title').textContent = 'Source unavailable';
  codeEl('code-content').textContent = message;
  codeEl('code-raw').hidden = true;
}

function configureCodeNavigation() {
  codeEl('code-raw').href = codeResourceUrl(codePath);
  codeEl('code-back').addEventListener('click', () => {
    if (window.history.length > 1) window.history.back();
    else window.location.href = 'papers.html';
  });
}

async function loadCode() {
  if (!/\.py$/i.test(codePath) || codePath.startsWith('/') || codePath.split('/').includes('..')) {
    showCodeError('Invalid source path. Return to the document that linked here.');
    return;
  }
  configureCodeNavigation();
  const title = sourceTitle(codePath);
  document.title = `${title} · Paper to Benchmark`;
  codeEl('code-title').textContent = title;
  codeEl('code-path').textContent = codePath;
  try {
    const response = await fetch(codeResourceUrl(codePath));
    if (!response.ok) throw new Error(response.status === 404 ? 'Source file not found' : 'Source file could not be loaded');
    const content = codeEl('code-content');
    content.textContent = await response.text();
    if (window.hljs) window.hljs.highlightElement(content);
  } catch (error) {
    showCodeError(error.message);
  }
}

loadCode();
