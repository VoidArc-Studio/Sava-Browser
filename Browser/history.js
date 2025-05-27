const Store = require('electron-store');
const store = new Store();

async function getHistory() {
  return store.get('history', []);
}

async function searchHistory(query) {
  const history = store.get('history', []);
  return history.filter(entry => entry.url.toLowerCase().includes(query.toLowerCase()));
}

async function addHistory(url) {
  const history = store.get('history', []);
  history.unshift({ url, timestamp: new Date().toISOString() });
  store.set('history', history.slice(0, 100));
  return history;
}

module.exports = { getHistory, searchHistory, addHistory };
