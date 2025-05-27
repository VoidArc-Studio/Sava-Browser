const { app, BrowserWindow, ipcMain, session } = require('electron');
const path = require('path');
const si = require('systeminformation');
const { ElectronBlocker } = require('@cliqz/adblocker-electron');
const fetch = require('node-fetch');
const Store = require('electron-store');
const { searchWeb, crawlPage } = require('./search');
const { enableVPN, disableVPN } = require('./vpn');
const { enableTor, disableTor } = require('./tor');
const { getBookmarks, addBookmark } = require('./bookmarks');
const { getHistory, searchHistory, addHistory } = require('./history');
const { getNotes, addNote } = require('./notes');
const { getSettings, setSettings } = require('./settings');
const { queryLyraAI } = require('./lyra-ai');
const { getDownloads, addDownload } = require('./downloads');
const { initializeFirebase, syncBookmarks, syncHistory } = require('./firebase-config');

const store = new Store();

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1600,
    height: 1000,
    webPreferences: {
      preload: path.join(__dirname, 'renderer.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
    icon: path.join(__dirname, 'assets/icon.png'),
    frame: false,
  });

  mainWindow.loadFile('index.html');

  // Adblocker
  ElectronBlocker.fromPrebuiltAdsAndTracking(fetch).then((blocker) => {
    blocker.enableBlockingInSession(mainWindow.webContents.session);
  });

  // Zakładki
  ipcMain.handle('get-bookmarks', async () => await getBookmarks());
  ipcMain.handle('add-bookmark', async (event, bookmark) => await addBookmark(bookmark));
  ipcMain.handle('sync-bookmarks', async () => await syncBookmarks());

  // Historia
  ipcMain.handle('get-history', async () => await getHistory());
  ipcMain.handle('search-history', async (event, query) => await searchHistory(query));
  ipcMain.handle('add-history', async (event, url) => await addHistory(url));
  ipcMain.handle('sync-history', async () => await syncHistory());

  // Notatki
  ipcMain.handle('get-notes', async () => await getNotes());
  ipcMain.handle('add-note', async (event, note) => await addNote(note));

  // Ustawienia
  ipcMain.handle('get-settings', async () => await getSettings());
  ipcMain.handle('set-settings', async (event, settings) => await setSettings(settings));

  // Zasoby systemowe
  ipcMain.handle('get-system-info', async () => {
    try {
      const cpu = await si.cpu();
      const mem = await si.mem();
      const gpu = await si.graphics();
      return {
        cpu: cpu.brand,
        cpuUsage: await si.currentLoad(),
        memory: {
          total: mem.total / (1024 * 1024 * 1024),
          used: mem.used / (1024 * 1024 * 1024),
        },
        gpu: gpu.controllers[0]?.model || 'Brak danych GPU',
      };
    } catch (error) {
      console.error('Błąd monitorowania zasobów:', error);
      return {};
    }
  });

  // Ograniczenie zasobów
  ipcMain.on('limit-resources', (event, fps) => {
    mainWindow.webContents.setFrameRate(fps);
  });

  // Wyszukiwanie
  ipcMain.handle('search', async (event, query) => await searchWeb(query));

  // VPN
  ipcMain.handle('enable-vpn', async () => await enableVPN());
  ipcMain.handle('disable-vpn', async () => await disableVPN());

  // Tor
  ipcMain.handle('enable-tor', async (event, url) => await enableTor(mainWindow, url));
  ipcMain.handle('disable-tor', async () => await disableTor(mainWindow));

  // Lyra AI
  ipcMain.handle('query-lyra-ai', async (event, query) => await queryLyraAI(query));

  // Pobieranie
  ipcMain.handle('get-downloads', async () => await getDownloads());
  ipcMain.handle('add-download', async (event, download) => await addDownload(download));

  // Rozszerzenia Chrome
  session.defaultSession.loadExtension(path.join(__dirname, 'extensions/ublock-origin'), { allowFileAccess: true })
    .then(() => console.log('uBlock Origin załadowany'))
    .catch(err => console.error('Błąd ładowania rozszerzenia:', err));

  // Inicjalizacja Firebase
  initializeFirebase();
}

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
