import { useState, useEffect } from 'react'
import { FolderPlus, Trash2, X } from 'lucide-react'
import { motion } from 'framer-motion'

interface SettingsProps {
  onClose: () => void
}

export default function Settings({ onClose }: SettingsProps) {
  const [folders, setFolders] = useState<string[]>([])

  useEffect(() => {
    // In reality, this would fetch from FastMCP / FastAPI config endpoint
    // For now we mock it based on default config
    setFolders([
      '~/Documents',
      '~/Projects'
    ])
  }, [])

  const addFolder = async () => {
    // Here we would call a main process IPC to show OpenDialog
    // Then post to FastAPI to add root and reindex
  }

  const removeFolder = (idx: number) => {
    const newFolders = [...folders]
    newFolders.splice(idx, 1)
    setFolders(newFolders)
  }

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="absolute inset-0 bg-black/80 backdrop-blur-3xl z-50 flex flex-col p-6 text-white"
    >
      <div className="flex items-center justify-between mb-8 non-draggable">
        <h2 className="text-2xl font-semibold">Settings</h2>
        <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition">
          <X className="w-6 h-6" />
        </button>
      </div>

      <div className="flex-1 non-draggable">
        <h3 className="text-lg text-white/70 mb-4">Indexed Folders</h3>
        <div className="space-y-2">
          {folders.map((folder, idx) => (
            <div key={idx} className="flex items-center justify-between bg-white/5 p-3 rounded-lg border border-white/10">
              <span className="font-mono text-sm">{folder}</span>
              <button onClick={() => removeFolder(idx)} className="p-1.5 hover:bg-red-500/20 text-red-400 rounded transition">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
        <button 
          onClick={addFolder}
          className="mt-4 flex items-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg transition"
        >
          <FolderPlus className="w-4 h-4" />
          <span>Add Folder...</span>
        </button>
      </div>
      
      <div className="mt-8 non-draggable">
        <button className="w-full bg-white/10 hover:bg-white/20 text-white px-4 py-3 rounded-lg transition border border-white/10 text-sm">
          Rebuild Index (Full Scan)
        </button>
      </div>
    </motion.div>
  )
}
