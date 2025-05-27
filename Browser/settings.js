const Store = require('electron-store');
const store = new Store();

async function getSettings() {
  return store.get('settings', { theme: 'dark', vpn: false, fps: 60 });
}

async function setSettings(settings) {
  store.set('settings', settings);
  return settings;
}

module.exports = { getSettings, setSettings };
