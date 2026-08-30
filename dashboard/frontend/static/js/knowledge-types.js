/* Shared visual taxonomy for knowledge pages and the home-page graph. */
window.SCICODE_KNOWLEDGE_TYPE_COLORS = Object.freeze({
  paper: '#8b5a3c',
  concept: '#cf3f4f',
  method: '#e07a2d',
  comparison: '#c49a00',
  topic: '#00a6a6',
  implementation: '#4d8b45',
  model: '#386cb0',
  reference: '#7b4fa3',
  collection: '#7b4fa3',
  idea: '#b34587',
  ideas: '#b34587',
  question: '#b34587',
  // Workspace context is intentionally neutral, so it does not compete with scientific knowledge.
  project: '#98a4aa',
  thesis: '#425058',
});

window.scicodeKnowledgeTypeColor = type =>
  window.SCICODE_KNOWLEDGE_TYPE_COLORS[String(type || 'reference').toLowerCase()]
  || window.SCICODE_KNOWLEDGE_TYPE_COLORS.reference;
