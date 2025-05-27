const Store = require('electron-store');
const store = new Store();

async function getNotes() {
  return store.get('notes', []);
}

async function addNote(note) {
  const notes = store.get('notes', []);
  notes.push(note);
  store.set('notes', notes);
  return notes;
}

module.exports = { getNotes, addNote };
