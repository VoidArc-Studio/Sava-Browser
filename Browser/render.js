const { ipcRenderer } = require('electron');

let tabs = [];
let activeTabId = null;
let currentTheme = 'dark';
let vpnEnabled = false;
let torEnabled = false;

function loadHome() {
  const webview = document.getElementById('webview');
  webview.src = 'https://www.example.com';
  addToHistory(webview.src);
  updateTabs();
}

function openNewTab(url = 'https://www.example.com') {
  const id = Date.now();
  tabs.push({ id, url, tor: false });
  activeTabId = id;
  updateTabs();
  document.getElementById('webview').src = url;
  addToHistory(url);
}

async function openTorTab(url = 'https://www.torproject.org') {
  const id = Date.now();
  tabs.push({ id, url, tor: true });
  activeTabId = id;
  updateTabs();
  torEnabled = true;
  await ipcRenderer.invoke('enable-tor', url);
  document.getElementById('webview').src = url;
  addToHistory(url);
}

function closeTab() {
  if (tabs.length > 1) {
    const closedTab = tabs.find(tab => tab.id === activeTabId);
    if (closedTab.tor) {
      ipcRenderer.invoke('disable-tor');
      torEnabled = false;
    }
    tabs = tabs.filter(tab => tab.id !== activeTabId);
    activeTabId = tabs[tabs.length - 1].id;
    document.getElementById('webview').src = tabs[tabs.length - 1].url;
    updateTabs();
  }
}

function updateTabs() {
  const tabsContainer = document.getElementById('tabs');
  tabsContainer.innerHTML = '';
  tabs.forEach(tab => {
    const tabElement = document.createElement('div');
    tabElement.className = `tab ${tab.id === activeTabId ? 'active' : ''} ${tab.tor ? 'tor' : ''}`;
    tabElement.textContent = tab.tor ? `[TOR] ${tab.url}` : tab.url;
    tabElement.onclick = () => {
      activeTabId = tab.id;
      document.getElementById('webview').src = tab.url;
      if (tab.tor && !torEnabled) {
        ipcRenderer.invoke('enable-tor', tab.url);
        torEnabled = true;
      } else if (!tab.tor && torEnabled) {
        ipcRenderer.invoke('disable-tor');
        torEnabled = false;
      }
      updateTabs();
    };
    tabsContainer.appendChild(tabElement);
  });
}

function openIncognito() {
  const win = window.open('about:blank', '_blank', 'nodeIntegration=no,contextIsolation=yes');
  win.document.write('<h1>Sava Browser - Tryb incognito</h1><style>body{background:#1a1a1a;color:#fff;font-family:Orbitron;}</style>');
}

function handleUrl(event) {
  if (event.key === 'Enter') {
    let url = event.target.value;
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url;
    }
    openNewTab(url);
  }
}

async function showSystemInfo() {
  hidePanels();
  const systemInfoDiv = document.getElementById('system-info');
  systemInfoDiv.style.display = 'block';
  const systemInfo = await ipcRenderer.invoke('get-system-info');
  document.getElementById('cpu-info').textContent = `Procesor: ${systemInfo.cpu} (Użycie: ${systemInfo.cpuUsage.currentLoad.toFixed(2)}%)`;
  document.getElementById('memory-info').textContent = `Pamięć: ${systemInfo.memory.used.toFixed(2)} GB / ${systemInfo.memory.total.toFixed(2)} GB`;
  document.getElementById('gpu-info').textContent = `GPU: ${systemInfo.gpu}`;
}

function limitResources(fps) {
  ipcRenderer.send('limit-resources', fps);
}

async function showBookmarks() {
  hidePanels();
  const bookmarksDiv = document.getElementById('bookmarks');
  bookmarksDiv.style.display = 'block';
  const category = document.getElementById('bookmark-category').value;
  const bookmarks = await ipcRenderer.invoke('get-bookmarks');
  const bookmarkList = document.getElementById('bookmark-list');
  bookmarkList.innerHTML = '';
  bookmarks
    .filter(b => category === 'all' || b.category === category)
    .forEach(bookmark => {
      const li = document.createElement('li');
      li.textContent = `[${bookmark.category}] ${bookmark.name}`;
      li.onclick = () => openNewTab(bookmark.url);
      bookmarkList.appendChild(li);
    });
}

async function addBookmark() {
  const url = document.getElementById('webview').src;
  const name = prompt('Nazwa zakładki:', url);
  const category = prompt('Kategoria (np. praca, rozrywka):', 'praca');
  if (name && category) {
    await ipcRenderer.invoke('add-bookmark', { name, url, category });
    showBookmarks();
  }
}

async function syncBookmarks() {
  await ipcRenderer.invoke('sync-bookmarks');
  showBookmarks();
}

async function showHistory() {
  hidePanels();
  const historyDiv = document.getElementById('history');
  historyDiv.style.display = 'block';
  await searchHistory();
}

async function searchHistory() {
  const query = document.getElementById('history-search').value;
  const history = await ipcRenderer.invoke('search-history', query);
  const historyList = document.getElementById('history-list');
  historyList.innerHTML = '';
  history.forEach(entry => {
    const li = document.createElement('li');
    li.textContent = `${entry.url} (${new Date(entry.timestamp).toLocaleString()})`;
    li.onclick = () => openNewTab(entry.url);
    historyList.appendChild(li);
  });
}

async function syncHistory() {
  await ipcRenderer.invoke('sync-history');
  showHistory();
}

async function addToHistory(url) {
  if (!torEnabled) {
    await ipcRenderer.invoke('add-history', url);
  }
}

async function showNotes() {
  hidePanels();
  const notesDiv = document.getElementById('notes');
  notesDiv.style.display = 'block';
  const notes = await ipcRenderer.invoke('get-notes');
  const noteList = document.getElementById('note-list');
  noteList.innerHTML = '';
  notes.forEach(note => {
    const li = document.createElement('li');
    li.textContent = note;
    noteList.appendChild(li);
  });
}

async function addNote() {
  const note = document.getElementById('note-input').value;
  if (note) {
    await ipcRenderer.invoke('add-note', note);
    document.getElementById('note-input').value = '';
    showNotes();
  }
}

async function showSearch() {
  hidePanels();
  const searchDiv = document.getElementById('search');
  searchDiv.style.display = 'block';
}

async function handleSearch(event) {
  if (event.key === 'Enter') {
    const query = event.target.value;
    const results = await ipcRenderer.invoke('search', query);
    const searchResults = document.getElementById('search-results');
    searchResults.innerHTML = '';
    results.forEach(result => {
      const li = document.createElement('li');
      li.textContent = `${result.title} (${result.score.toFixed(2)})`;
      li.onclick = () => openNewTab(result.url);
      searchResults.appendChild(li);
    });
  }
}

async function showLyraAI() {
  hidePanels();
  const aiDiv = document.getElementById('lyra-ai');
  aiDiv.style.display = 'block';
}

async function handleAIQuery(event) {
  if (event.key === 'Enter') {
    const query = event.target.value;
    const response = await ipcRenderer.invoke('query-lyra-ai', query);
    document.getElementById('ai-response').textContent = response;
    event.target.value = '';
  }
}

async function showDownloads() {
  hidePanels();
  const downloadsDiv = document.getElementById('downloads');
  downloadsDiv.style.display = 'block';
  const downloads = await ipcRenderer.invoke('get-downloads');
  const downloadList = document.getElementById('download-list');
  downloadList.innerHTML = '';
  downloads.forEach(download => {
    const li = document.createElement('li');
    li.textContent = `${download.name} (${download.status})`;
    downloadList.appendChild(li);
  });
}

async function addDownload(url) {
  const name = url.split('/').pop();
  await ipcRenderer.invoke('add-download', { name, url, status: 'pending' });
  showDownloads();
}

async function toggleVPN() {
  vpnEnabled = !vpnEnabled;
  const status = document.getElementById('vpn-status');
  status.textContent = vpnEnabled ? 'Wł.' : 'Wył.';
  if (vpnEnabled) {
    await ipcRenderer.invoke('enable-vpn');
  } else {
    await ipcRenderer.invoke('disable-vpn');
  }
}

async function showSettings() {
  hidePanels();
  const settingsDiv = document.getElementById('settings');
  settingsDiv.style.display = 'block';
  const settings = await ipcRenderer.invoke('get-settings');
  document.getElementById('auto-vpn').checked = settings.vpn;
  document.getElementById('fps-limit').value = settings.fps || 60;
  document.getElementById('theme-select').value = settings.theme || 'dark';
}

async function saveSettings() {
  const settings = {
    theme: document.getElementById('theme-select').value,
    vpn: document.getElementById('auto-vpn').checked,
    fps: parseInt(document.getElementById('fps-limit').value),
  };
  await ipcRenderer.invoke('set-settings', settings);
  limitResources(settings.fps);
  if (settings.vpn && !vpnEnabled) toggleVPN();
  toggleTheme(settings.theme);
}

function toggleFullScreen() {
  const webview = document.getElementById('webview');
  webview.style.height = webview.style.height === '100%' ? 'calc(100% - 40px)' : '100%';
}

function toggleTheme(theme) {
  currentTheme = theme || currentTheme;
  document.body.className = `theme-${currentTheme}`;
  document.querySelectorAll('.sidebar-item, .tab, button').forEach(el => {
    el.style.setProperty('--primary-color', currentTheme === 'dark' ? '#ff4d4d' : '#ff00ff');
    el.style.setProperty('--secondary-color', currentTheme === 'dark' ? '#ff6666' : '#ff66ff');
  });
}

function hidePanels() {
  document.querySelectorAll('.panel').forEach(panel => panel.style.display = 'none');
}

document.addEventListener('DOMContentLoaded', async () => {
  openNewTab();
  const settings = await ipcRenderer.invoke('get-settings');
  currentTheme = settings.theme || 'dark';
  document.body.className = `theme-${currentTheme}`;
  toggleTheme(currentTheme);
  if (settings.vpn) toggleVPN();
  document.getElementById('webview').addEventListener('did-finish-load', () => {
    addToHistory(document.getElementById('webview').src);
  });
  document.getElementById('webview').addEventListener('will-download', (event, item) => {
    addDownload(item.getURL());
  });
});
