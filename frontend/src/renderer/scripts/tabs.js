let currentTabId = 0;
const tabs = new Map();

function createTab(url = 'https://www.startpage.com') {
  const tabId = currentTabId++;
  const webview = document.createElement('webview');
  webview.src = url;
  webview.style.display = 'none';
  document.getElementById('content').appendChild(webview);

  const tabElement = document.createElement('div');
  tabElement.className = 'tab';
  tabElement.innerText = new URL(url).hostname;
  tabElement.onclick = () => switchTab(tabId);
  document.getElementById('tab-bar').appendChild(tabElement);

  tabs.set(tabId, { webview, tabElement, url });
  switchTab(tabId);
}

function switchTab(tabId) {
  tabs.forEach((tab, id) => {
    tab.webview.style.display = id === tabId ? 'block' : 'none';
    tab.tabElement.classList.toggle('active', id === tabId);
  });
}

function closeTab(tabId) {
  const tab = tabs.get(tabId);
  if (tab) {
    tab.webview.remove();
    tab.tabElement.remove();
    tabs.delete(tabId);
  }
}
