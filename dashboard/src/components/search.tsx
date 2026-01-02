import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/router'
import { Search, Bot, Workflow, Zap, Loader2, X } from 'lucide-react'

interface SearchResult {
  id: string
  type: 'agent' | 'workflow' | 'execution'
  name: string
  description?: string
  status: string
  score: number
}

export function GlobalSearch() {
  const router = useRouter()
  const [isOpen, setIsOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // Keyboard shortcut to open search (Cmd/Ctrl + K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setIsOpen(true)
      }
      if (e.key === 'Escape') {
        setIsOpen(false)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Focus input when modal opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  // Search as user types
  useEffect(() => {
    if (!query.trim()) {
      setResults([])
      return
    }

    const searchTimeout = setTimeout(async () => {
      setLoading(true)
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${API_URL}/v1/search?q=${encodeURIComponent(query)}`)
        if (response.ok) {
          const data = await response.json()
          setResults(data.results || [])
          setSelectedIndex(0)
        }
      } catch (error) {
        console.error('Search error:', error)
      } finally {
        setLoading(false)
      }
    }, 300)

    return () => clearTimeout(searchTimeout)
  }, [query])

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIndex(i => Math.min(i + 1, results.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIndex(i => Math.max(i - 1, 0))
    } else if (e.key === 'Enter' && results[selectedIndex]) {
      handleSelect(results[selectedIndex])
    }
  }

  const handleSelect = (result: SearchResult) => {
    setIsOpen(false)
    setQuery('')

    switch (result.type) {
      case 'agent':
        router.push(`/agents/${result.id}`)
        break
      case 'workflow':
        router.push(`/workflows/${result.id}`)
        break
      case 'execution':
        router.push(`/executions`)
        break
    }
  }

  const getIcon = (type: string) => {
    switch (type) {
      case 'agent':
        return <Bot className="h-4 w-4" />
      case 'workflow':
        return <Workflow className="h-4 w-4" />
      case 'execution':
        return <Zap className="h-4 w-4" />
      default:
        return <Search className="h-4 w-4" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'agent':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
      case 'workflow':
        return 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300'
      case 'execution':
        return 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <>
      {/* Search trigger button */}
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-3 py-1.5 text-sm text-muted-foreground border rounded-lg hover:bg-muted transition-colors"
      >
        <Search className="h-4 w-4" />
        <span className="hidden md:inline">Search...</span>
        <kbd className="hidden md:inline-flex items-center gap-1 px-1.5 py-0.5 text-xs bg-muted rounded">
          <span className="text-xs">⌘</span>K
        </kbd>
      </button>

      {/* Search modal */}
      {isOpen && (
        <div className="fixed inset-0 z-50">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setIsOpen(false)}
          />

          {/* Modal */}
          <div className="relative mx-auto mt-20 w-full max-w-xl" ref={containerRef}>
            <div className="bg-background rounded-xl shadow-2xl border overflow-hidden">
              {/* Search input */}
              <div className="flex items-center gap-3 px-4 py-3 border-b">
                <Search className="h-5 w-5 text-muted-foreground" />
                <input
                  ref={inputRef}
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Search agents, workflows, executions..."
                  className="flex-1 bg-transparent outline-none text-lg"
                />
                {loading && <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />}
                {query && !loading && (
                  <button onClick={() => setQuery('')}>
                    <X className="h-5 w-5 text-muted-foreground hover:text-foreground" />
                  </button>
                )}
              </div>

              {/* Results */}
              <div className="max-h-96 overflow-y-auto">
                {results.length > 0 ? (
                  <div className="py-2">
                    {results.map((result, index) => (
                      <button
                        key={result.id}
                        onClick={() => handleSelect(result)}
                        className={`w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-muted transition-colors ${
                          index === selectedIndex ? 'bg-muted' : ''
                        }`}
                      >
                        <div className={`p-2 rounded-lg ${getTypeColor(result.type)}`}>
                          {getIcon(result.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-medium truncate">{result.name}</span>
                            <span className={`text-xs px-1.5 py-0.5 rounded ${
                              result.status === 'active'
                                ? 'bg-green-100 text-green-700'
                                : 'bg-gray-100 text-gray-700'
                            }`}>
                              {result.status}
                            </span>
                          </div>
                          {result.description && (
                            <p className="text-sm text-muted-foreground truncate">
                              {result.description}
                            </p>
                          )}
                        </div>
                        <span className="text-xs text-muted-foreground capitalize">
                          {result.type}
                        </span>
                      </button>
                    ))}
                  </div>
                ) : query && !loading ? (
                  <div className="py-12 text-center text-muted-foreground">
                    <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No results found for "{query}"</p>
                  </div>
                ) : !query ? (
                  <div className="py-8 px-4">
                    <p className="text-sm text-muted-foreground mb-4">Quick actions:</p>
                    <div className="grid grid-cols-3 gap-2">
                      <button
                        onClick={() => { setIsOpen(false); router.push('/agents') }}
                        className="flex flex-col items-center gap-2 p-4 rounded-lg border hover:bg-muted"
                      >
                        <Bot className="h-6 w-6 text-blue-500" />
                        <span className="text-sm">Agents</span>
                      </button>
                      <button
                        onClick={() => { setIsOpen(false); router.push('/workflows') }}
                        className="flex flex-col items-center gap-2 p-4 rounded-lg border hover:bg-muted"
                      >
                        <Workflow className="h-6 w-6 text-purple-500" />
                        <span className="text-sm">Workflows</span>
                      </button>
                      <button
                        onClick={() => { setIsOpen(false); router.push('/executions') }}
                        className="flex flex-col items-center gap-2 p-4 rounded-lg border hover:bg-muted"
                      >
                        <Zap className="h-6 w-6 text-green-500" />
                        <span className="text-sm">Executions</span>
                      </button>
                    </div>
                  </div>
                ) : null}
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between px-4 py-2 border-t text-xs text-muted-foreground">
                <div className="flex items-center gap-4">
                  <span className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-muted rounded">↑</kbd>
                    <kbd className="px-1.5 py-0.5 bg-muted rounded">↓</kbd>
                    to navigate
                  </span>
                  <span className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-muted rounded">↵</kbd>
                    to select
                  </span>
                </div>
                <span className="flex items-center gap-1">
                  <kbd className="px-1.5 py-0.5 bg-muted rounded">esc</kbd>
                  to close
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
