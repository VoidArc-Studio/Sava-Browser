const { ipcRenderer } = require('electron');

function initDownloads() {
  const content = document.getElementById('content');
  content.innerHTML = '<h2>Pobieranie</h2><ul id="download-list"></ul>';

  ipcRenderer.on('download-progress', (event, file) => {
    const list = document.getElementById('download-list');
    list.innerHTML += `<li>${file.name}: ${file.progress}%</li>`;
  });
}
