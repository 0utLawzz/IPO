const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('ipo', {
  runScraper: (args) => ipcRenderer.invoke('scraper:run', args),
  stopScraper: () => ipcRenderer.invoke('scraper:stop'),
  openExports: () => ipcRenderer.invoke('exports:open'),
  listSessions: (args) => ipcRenderer.invoke('exports:listSessions', args),
  onLog: (cb) => {
    const handler = (_evt, msg) => cb(msg);
    ipcRenderer.on('scraper:log', handler);
    return () => ipcRenderer.removeListener('scraper:log', handler);
  },
  onStatus: (cb) => {
    const handler = (_evt, status) => cb(status);
    ipcRenderer.on('scraper:status', handler);
    return () => ipcRenderer.removeListener('scraper:status', handler);
  },
});
