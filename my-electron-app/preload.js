const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openCSVDialog: () => ipcRenderer.invoke('open-csv-dialog'),
  readCSVFile: (filePath) => ipcRenderer.invoke('read-csv-file', filePath)
});