const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow = null;
let running = null;

function getRepoRoot() {
  // electron-app/electron/main.cjs -> repo root is two levels up
  return path.resolve(__dirname, '..', '..');
}

function getExportRoot() {
  return path.join(getRepoRoot(), 'export');
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1100,
    height: 720,
    backgroundColor: '#0b0d12',
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  const devUrl = process.env.ELECTRON_RENDERER_URL;
  if (devUrl) {
    mainWindow.loadURL(devUrl);
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  } else {
    // Production build output path
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'));
  }
}

function sendLog(line) {
  if (!mainWindow) return;
  mainWindow.webContents.send('scraper:log', String(line));
}

function sendStatus(status) {
  if (!mainWindow) return;
  mainWindow.webContents.send('scraper:status', status);
}

ipcMain.handle('scraper:run', async (_evt, args) => {
  if (running) {
    return { ok: false, error: 'A scrape is already running.' };
  }

  const tm = args?.tm;
  if (!tm) return { ok: false, error: 'TM form is required.' };

  const repoRoot = getRepoRoot();
  const python = args?.python || 'python';

  // Run in non-interactive mode
  const child = spawn(python, ['main.py', '--tm', tm], {
    cwd: repoRoot,
    windowsHide: true,
    env: process.env,
  });

  running = child;
  sendStatus({ state: 'running', tm });

  child.stdout.on('data', (d) => sendLog(d.toString('utf-8')));
  child.stderr.on('data', (d) => sendLog(d.toString('utf-8')));

  const exit = await new Promise((resolve) => {
    child.on('close', (code) => resolve(code));
  });

  running = null;
  sendStatus({ state: 'idle', tm, exitCode: exit });
  return { ok: true, exitCode: exit };
});

ipcMain.handle('scraper:stop', async () => {
  if (!running) return { ok: true };
  try {
    running.kill();
    running = null;
    sendStatus({ state: 'idle', exitCode: null });
    return { ok: true };
  } catch (e) {
    return { ok: false, error: String(e) };
  }
});

ipcMain.handle('exports:open', async () => {
  const exportRoot = getExportRoot();
  fs.mkdirSync(exportRoot, { recursive: true });
  await shell.openPath(exportRoot);
  return { ok: true };
});

ipcMain.handle('exports:listSessions', async (_evt, args) => {
  const exportRoot = getExportRoot();
  const tm = args?.tm;
  const sessionsDir = path.join(exportRoot, 'sessions');

  if (!fs.existsSync(sessionsDir)) return { ok: true, sessions: [] };

  const timestamps = fs
    .readdirSync(sessionsDir, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort()
    .reverse();

  const sessions = [];
  for (const ts of timestamps) {
    const tmDir = tm ? path.join(sessionsDir, ts, tm) : path.join(sessionsDir, ts);
    if (!fs.existsSync(tmDir)) continue;

    const summaryPath = path.join(tmDir, 'session_summary.json');
    let summary = null;
    if (fs.existsSync(summaryPath)) {
      try {
        summary = JSON.parse(fs.readFileSync(summaryPath, 'utf-8'));
      } catch {
        summary = null;
      }
    }

    const files = fs
      .readdirSync(tmDir, { withFileTypes: true })
      .filter((e) => e.isFile())
      .map((e) => e.name)
      .sort();

    sessions.push({
      timestamp: ts,
      tm: tm || null,
      dir: tmDir,
      files,
      summary,
    });
  }

  return { ok: true, sessions };
});

app.whenReady().then(() => {
  // Vite dev server URL hook
  if (process.env.VITE_DEV_SERVER_URL) {
    process.env.ELECTRON_RENDERER_URL = process.env.VITE_DEV_SERVER_URL;
  } else {
    process.env.ELECTRON_RENDERER_URL = 'http://localhost:5173';
  }

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
