// Fonctions utilitaires partagées
(function () {
  const STORAGE_KEY = 'axa_docs';

  function getStoredDocs() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      console.error('Lecture localStorage échouée', e);
      return [];
    }
  }

  function saveStoredDocs(list) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    } catch (e) {
      console.error('Écriture localStorage échouée', e);
    }
  }

  function addDocumentMetadata(meta) {
    const list = getStoredDocs();
    list.push(meta);
    saveStoredDocs(list);
  }

  function clearAll() {
    localStorage.removeItem(STORAGE_KEY);
  }

  function formatBytes(bytes) {
    if (bytes === 0) return '0 o';
    const k = 1024;
    const sizes = ['o', 'Ko', 'Mo', 'Go', 'To'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  function formatDate(ts) {
    try {
      return new Date(ts).toLocaleString('fr-FR');
    } catch {
      return '' + ts;
    }
  }

  // Expose en global de façon contrôlée
  window.AXAStore = {
    getStoredDocs,
    addDocumentMetadata,
    clearAll,
    formatBytes,
    formatDate,
  };
})();

