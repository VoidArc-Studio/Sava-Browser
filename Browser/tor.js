const tr = require('tor-request');

async function enableTor(window, url) {
  try {
    tr.setTorAddress('127.0.0.1', 9050);
    window.webContents.session.setProxy({ proxyRules: 'socks5://127.0.0.1:9050' });
    console.log('Tor włączony dla:', url);
    return { status: 'enabled', message: 'Tor aktywny' };
  } catch (error) {
    console.error('Błąd Tor:', error);
    return { status: 'error', message: 'Nie udało się włączyć Tor' };
  }
}

async function disableTor(window) {
  try {
    window.webContents.session.setProxy({ proxyRules: '' });
    console.log('Tor wyłączony');
    return { status: 'disabled', message: 'Tor nieaktywny' };
  } catch (error) {
    console.error('Błąd Tor:', error);
    return { status: 'error', message: 'Nie udało się wyłączyć Tor' };
  }
}

module.exports = { enableTor, disableTor };
