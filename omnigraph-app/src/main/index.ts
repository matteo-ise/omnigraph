import { app, shell, BrowserWindow, ipcMain, globalShortcut, Tray, Menu } from 'electron'
import { join } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'
import { spawn, ChildProcess } from 'child_process'

let mainWindow: BrowserWindow | null = null
let tray: Tray | null = null
let pythonProcess: ChildProcess | null = null

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 750,
    height: 450,
    show: false,
    frame: false,
    transparent: true,
    vibrancy: 'hud', // macOS vibrancy effect
    visualEffectState: 'active',
    resizable: false,
    center: true,
    autoHideMenuBar: true,
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false
    }
  })

  // Hide window when it loses focus (Spotlight behavior)
  mainWindow.on('blur', () => {
    mainWindow?.hide()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

function startPythonBackend() {
  if (app.isPackaged) {
    const backendPath = join(process.resourcesPath, 'backend', 'omnigraph-backend')
    pythonProcess = spawn(backendPath, ['serve', '--port', '8765'], {
      stdio: 'ignore'
    })
  } else {
    // Development mode
    pythonProcess = spawn('python', ['-m', 'omnigraph', 'serve', '--port', '8765'], {
      stdio: 'ignore'
    })
  }
}

function stopPythonBackend() {
  if (pythonProcess) {
    pythonProcess.kill()
    pythonProcess = null
  }
}

function createTray() {
  // In a real app, use a proper 16x16 or 32x32 template image for macOS tray
  // Here we use the default icon, but ideally it should be a monochrome NativeImage
  tray = new Tray(icon)
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Show Omnigraph', click: () => {
      mainWindow?.show()
      mainWindow?.focus()
    }},
    { type: 'separator' },
    { label: 'Quit', click: () => {
      stopPythonBackend()
      app.quit()
    }}
  ])
  tray.setToolTip('Omnigraph')
  tray.setContextMenu(contextMenu)
}

function toggleWindow() {
  if (mainWindow) {
    if (mainWindow.isVisible()) {
      mainWindow.hide()
    } else {
      mainWindow.show()
      mainWindow.focus()
    }
  }
}

app.whenReady().then(() => {
  electronApp.setAppUserModelId('com.matteoise.omnigraph')

  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  // Hide the dock icon to make it a pure menu-bar / background app
  if (app.dock) {
    app.dock.hide()
  }

  startPythonBackend()
  createTray()
  createWindow()

  // IPC listener for Graph Window
  ipcMain.on('open-graph-window', () => {
    const graphWindow = new BrowserWindow({
      width: 1024,
      height: 768,
      title: 'Omnigraph Explorer',
      ...(process.platform === 'linux' ? { icon } : {})
    })
    
    // In a real Mac app we might want to show the dock icon if a real window is open
    if (app.dock) app.dock.show()
      
    graphWindow.loadURL('http://localhost:8765/')
    
    graphWindow.on('closed', () => {
      // Hide dock again if no other windows are visible
      if (app.dock && BrowserWindow.getAllWindows().length <= 1) {
        app.dock.hide()
      }
    })
  })

  // Register a global shortcut listener
  globalShortcut.register('CommandOrControl+Shift+O', toggleWindow)

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('will-quit', () => {
  // Unregister all shortcuts.
  globalShortcut.unregisterAll()
  stopPythonBackend()
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    stopPythonBackend()
    app.quit()
  }
})
