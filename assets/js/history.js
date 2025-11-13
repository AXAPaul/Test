// Logique page Historique
(function () {
  const tableBody = document.querySelector('#historyTable tbody');
  const emptyState = document.getElementById('emptyState');
  const clearBtn = document.getElementById('clearHistoryBtn');

  function render() {
    const items = window.AXAStore.getStoredDocs();
    tableBody.innerHTML = '';

    if (!items.length) {
      emptyState.style.display = 'block';
      return;
    }
    emptyState.style.display = 'none';

    // Tri du plus récent au plus ancien
    items
      .slice()
      .sort((a, b) => new Date(b.uploadedAt) - new Date(a.uploadedAt))
      .forEach((doc) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td title="${doc.name}">${doc.name}</td>
          <td>${window.AXAStore.formatBytes(doc.size)}</td>
          <td>${doc.type}</td>
          <td>${window.AXAStore.formatDate(doc.lastModified)}</td>
          <td>${window.AXAStore.formatDate(doc.uploadedAt)}</td>
        `;
        tableBody.appendChild(tr);
      });
  }

  clearBtn.addEventListener('click', () => {
    const ok = confirm("Effacer l'historique des documents ?");
    if (ok) {
      window.AXAStore.clearAll();
      render();
    }
  });

  render();
})();

