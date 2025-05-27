const Store = require('electron-store');
const store = new Store();

async function getBookmarks() {
  return store.get('bookmarks', []);
}

async function addBookmark(bookmark) {
  const bookmarks = store.get('bookmarks', []);
  bookmarks.push(bookmark);
  store.set('bookmarks', bookmarks);
  return bookmarks;
}

module.exports = { getBookmarks, addBookmark };
