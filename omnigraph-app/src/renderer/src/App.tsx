import { useState, useEffect, useRef } from 'react'
import { Search, FileText, Folder, Hash, Image as ImageIcon, Video, Code, LayoutGrid } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import Settings from './Settings'

// Define the shape of search results based on the FastAPI backend
interface SearchResult {
  file_id: string
  path: string
  score: number
  snippet: string
  topics: string[]
  metadata: any
}

function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [showSettings, setShowSettings] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!showSettings) {
      inputRef.current?.focus()
    }
  }, [showSettings])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (showSettings) return
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex(prev => (prev < results.length - 1 ? prev + 1 : prev))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex(prev => (prev > 0 ? prev - 1 : 0))
      } else if (e.key === 'Enter') {
        e.preventDefault()
        if (results[selectedIndex]) {
          openFile(results[selectedIndex].path)
        }
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [results, selectedIndex, showSettings])

  useEffect(() => {
    if (!query.trim()) {
      setResults([])
      return
    }

    const timer = setTimeout(() => {
      performSearch(query)
    }, 150)

    return () => clearTimeout(timer)
  }, [query])

  const performSearch = async (q: string) => {
    setLoading(true)
    try {
      const res = await fetch(`http://localhost:8765/api/search?q=${encodeURIComponent(q)}&limit=10`)
      if (res.ok) {
        const data = await res.json()
        setResults(data)
        setSelectedIndex(0)
      }
    } catch (error) {
      console.error("Search failed:", error)
    } finally {
      setLoading(false)
    }
  }

  const openFile = (path: string) => {
    console.log("Opening file:", path)
  }

  const getIconForPath = (path: string) => {
    const ext = path.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'md': case 'txt': case 'pdf': return <FileText className="w-5 h-5 text-blue-400" />
      case 'png': case 'jpg': case 'jpeg': return <ImageIcon className="w-5 h-5 text-purple-400" />
      case 'mp4': case 'mov': return <Video className="w-5 h-5 text-pink-400" />
      case 'py': case 'js': case 'ts': return <Code className="w-5 h-5 text-yellow-400" />
      default: return <FileText className="w-5 h-5 text-gray-400" />
    }
  }

  return (
    <div className="w-screen h-screen flex flex-col bg-black/40 backdrop-blur-2xl overflow-hidden rounded-xl border border-white/10 shadow-2xl draggable text-white relative">
      <AnimatePresence>
        {showSettings && <Settings onClose={() => setShowSettings(false)} />}
      </AnimatePresence>

      {/* Search Bar Area */}
      <div className="flex items-center px-4 py-4 border-b border-white/10 non-draggable">
        <Search className="w-6 h-6 text-white/50 mr-3" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search your knowledge graph..."
          className="flex-1 bg-transparent border-none outline-none text-2xl font-light text-white placeholder-white/30"
          autoFocus
        />
        {loading && (
          <div className="w-5 h-5 border-2 border-white/20 border-t-white/80 rounded-full animate-spin mr-3"></div>
        )}
        <div className="flex items-center space-x-2 non-draggable">
          <button 
            onClick={() => (window as any).api.openGraphWindow()}
            className="p-2 hover:bg-white/10 rounded-lg text-white/70 hover:text-white transition"
            title="Open Full Graph"
          >
            <Hash className="w-5 h-5" />
          </button>
          <button 
            onClick={() => setShowSettings(true)}
            className="p-2 hover:bg-white/10 rounded-lg text-white/70 hover:text-white transition"
            title="Settings"
          >
            <Folder className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Results Area */}
      <div className="flex-1 overflow-y-auto non-draggable p-2">
        <AnimatePresence>
          {results.length > 0 ? (
            results.map((res, idx) => (
              <motion.div
                key={res.file_id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.15, delay: idx * 0.03 }}
                className={`flex items-center p-3 rounded-lg cursor-pointer transition-colors ${
                  idx === selectedIndex ? 'bg-white/15' : 'hover:bg-white/5'
                }`}
                onClick={() => openFile(res.path)}
              >
                <div className="w-10 h-10 rounded-md bg-white/5 flex items-center justify-center mr-4">
                  {getIconForPath(res.path)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-white font-medium truncate">{res.path.split('/').pop()}</div>
                  <div className="text-white/50 text-sm truncate">{res.snippet || res.path}</div>
                </div>
                {res.topics && res.topics.length > 0 && (
                  <div className="hidden md:flex gap-2">
                    {res.topics.slice(0, 2).map((t, i) => (
                      <span key={i} className="text-xs px-2 py-1 rounded bg-blue-500/20 text-blue-300">
                        {t}
                      </span>
                    ))}
                  </div>
                )}
              </motion.div>
            ))
          ) : query ? (
            <div className="flex flex-col items-center justify-center h-full text-white/40">
              <p className="text-lg">No results found in your graph.</p>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-white/30 space-y-4">
              <LayoutGrid className="w-12 h-12 opacity-50" />
              <p>Type to instantly search documents, code, and notes.</p>
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

export default App
