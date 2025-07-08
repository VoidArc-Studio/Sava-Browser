const webview = document.getElementById('webview');
const tabBar = document.getElementById('tab-bar');
let tabs = [];

function openSection(section) {
  const content = document.getElementById('content');
  switch (section) {
    case 'tabs':
      content.innerHTML = '<h2>Zarządzanie zakładkami</h2>';
      break;
    case 'adblock':
      content.innerHTML = '<h2>Bloker reklam</h2>';
      break;
    case 'ai':
      content.innerHTML = '<h2>Sava AI</h2><input id="ai-input" placeholder="Zadaj pytanie AI..."><button onclick="askAI()">Zapytaj</button>';
      break;
    case 'downloads':
      content.innerHTML = '<h2>Pobieranie</h2>';
      break;
    case 'notes':
      content.innerHTML = '<h2>Notatnik</h2><textarea id="notes"></textarea>';
      break;
    case 'email':
      content.innerHTML = '<h2>Poczta</h2>';
      break;
    case 'streaming':
      content.innerHTML = '<h2>Streaming</h2><iframe src="https://open.spotify.com/embed"></iframe>';
      break;
    case 'settings':
      content.innerHTML = `
        <h2>Ustawienia</h2>
        <label>Silnik wyszukiwania:</label>
        <select id="search-engine">
          <option value="https://www.startpage.com">Startpage</option>
          <option value="https://www.google.com">Google</option>
          <option value="https://duckduckgo.com">DuckDuckGo</option>
        </select>
        <label>Motyw:</label>
        <select id="theme">
          <option value="light">Jasny</option>
          <option value="dark">Ciemny</option>
        </select>
      `;
      break;
  }
}

function addTab(url = 'https://www.startpage.com') {
  const tab = document.createElement('div');
  tab.className = 'tab';
  tab.innerText = url;
  tab.onclick = () => switchTab(url);
  tabBar.appendChild(tab);
  tabs.push({ url, tab });
  switchTab(url);
}

function switchTab(url) {
  webview.src = url;
}
