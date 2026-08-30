if (location.protocol === 'file:') {
  const page = location.pathname.split('/').pop() || 'index.html';
  location.replace(`http://localhost:8000/${page}${location.search}${location.hash}`);
}
