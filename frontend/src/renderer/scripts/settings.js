function showSettings() {
  const content = document.getElementById('content');
  content.innerHTML = `
    <h2>Ustawienia</h2>
    <div>
      <label>Silnik wyszukiwania:</label>
      <select id="search-engine" onchange="saveSettings()">
        <option value="https://www.startpage.com">Startpage</option>
        <option value="https://www.google.com">Google</option>
        <option value="https://duckduckgo.com">DuckDuckGo</option>
      </select>
    </div>
    <div>
      <label>Motyw:</label>
      <select id="theme" onchange="saveSettings()">
        <option value="light">Jasny</option>
        <option value="dark">Ciemny</option>
      </select>
    </div>
    <div>
      <label>Blokowanie reklam:</label>
      <input type="checkbox" id="adblock-enable" checked onchange="saveSettings()">
    </div>
  `;
  loadSettings();
}

function loadSettings() {
  const settings = JSON.parse(localStorage.getItem('sava_settings') || '{}');
  document.getElementById('search-engine').value = settings.searchEngine || 'https://www.startpage.com';
  document.getElementById('theme').value = settings.theme || 'light';
  document.getElementById('adblock-enable').checked = settings.adblock !== false;
}

function saveSettings() {
  const settings = {
    searchEngine: document.getElementById('search-engine').value,
    theme: document.getElementById('theme').value,
    adblock: document.getElementById('adblock-enable').checked
  };
  localStorage.setItem('sava_settings', JSON.stringify(settings));
  applyTheme(settings.theme);
}

function applyTheme(theme) {
  document.body.className = theme;
}
