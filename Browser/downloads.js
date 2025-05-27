const Store = require('electron-store');
const store = new Store();

async function getDownloads() {
  return store.get('downloads', []);
}

async function addDownload(download) {
  const downloads = store.get('downloads', []);
  downloads.push(download);
  store.set('downloads', downloads);
  return downloads;
}

module.exports = { getDownloads, addDownload };
