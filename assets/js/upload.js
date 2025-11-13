// Logique page Téléverser
(function () {
  const fileInput = document.getElementById('fileInput');
  const uploadBtn = document.getElementById('uploadBtn');
  const feedback = document.getElementById('feedback');

  function notify(msg, type = 'info') {
    feedback.textContent = msg;
    feedback.style.color = type === 'error' ? '#e4002b' : '#64748b';
  }

  function onUpload() {
    const file = fileInput.files && fileInput.files[0];
    if (!file) {
      notify('Veuillez sélectionner un fichier.', 'error');
      return;
    }

    // Métadonnées uniquement (pas de contenu stocké)
    const meta = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      name: file.name,
      size: file.size,
      type: file.type || 'inconnu',
      lastModified: file.lastModified,
      uploadedAt: new Date().toISOString(),
    };

    try {
      window.AXAStore.addDocumentMetadata(meta);
      notify(`“${file.name}” ajouté à l'historique.`);
      fileInput.value = '';
    } catch (e) {
      console.error(e);
      notify("Échec de l'ajout à l'historique.", 'error');
    }
  }

  uploadBtn.addEventListener('click', onUpload);
})();

