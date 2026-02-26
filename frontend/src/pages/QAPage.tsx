import { useState, useEffect } from 'react'
import ChatWindow from '../components/qa/ChatWindow'
import SearchBar, { SearchFilters } from '../components/qa/SearchBar'
import SearchResults from '../components/qa/SearchResults'
import ConversationList from '../components/qa/ConversationList'
import { qaService } from '../services/qa'
import { Conversation } from '../types/qa'

const QAPage = () => {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<unknown[]>([])
  const [searchTotal, setSearchTotal] = useState(0)
  const [searchPage, setSearchPage] = useState(1)
  const [searchFilters, setSearchFilters] = useState<SearchFilters>({})
  const [isSearchMode, setIsSearchMode] = useState(false)
  const [isLoadingConversations, setIsLoadingConversations] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [showSidebar, setShowSidebar] = useState(true)
  const [showConversationList, setShowConversationList] = useState(false)
  const [selectedConversationIds, setSelectedConversationIds] = useState<Set<string>>(new Set())
  const [error, setError] = useState<string | null>(null)
  const [hasMoreConversations, setHasMoreConversations] = useState(true)

  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      setIsLoadingConversations(true)
      setError(null)

      console.warn('[QAPage] Loading conversations', {
        timestamp: new Date().toISOString(),
      })

      const response = await qaService.getConversations(1, 50)
      setConversations(response.conversations)
      setHasMoreConversations(response.conversations.length < response.total)

      if (response.conversations.length > 0 && !activeConversationId) {
        setActiveConversationId(response.conversations[0].id)
      }

      console.warn('[QAPage] Conversations loaded', {
        count: response.conversations.length,
        timestamp: new Date().toISOString(),
      })
    } catch (err) {
      console.error('[QAPage] Failed to load conversations', {
        error: err,
        timestamp: new Date().toISOString(),
      })

      setError('Failed to load conversations. Please try again.')
    } finally {
      setIsLoadingConversations(false)
    }
  }

  const handleSearch = async (query: string, filters: SearchFilters) => {
    try {
      setIsSearching(true)
      setError(null)
      setSearchQuery(query)
      setSearchFilters(filters)
      setSearchPage(1)
      setIsSearchMode(true)

      console.warn('[QAPage] Performing search', {
        query,
        filters,
        timestamp: new Date().toISOString(),
      })

      const response = await qaService.searchConversations(query, filters, 0, 10)
      setSearchResults(response.messages || [])
      setSearchTotal(response.total || 0)

      console.warn('[QAPage] Search completed', {
        total: response.total,
        count: response.messages?.length || 0,
        timestamp: new Date().toISOString(),
      })
    } catch (err) {
      console.error('[QAPage] Search failed', {
        error: err,
        timestamp: new Date().toISOString(),
      })

      setError('Search failed. Please try again.')
    } finally {
      setIsSearching(false)
    }
  }

  const handleClearSearch = () => {
    setIsSearchMode(false)
    setSearchQuery('')
    setSearchResults([])
    setSearchTotal(0)
    setSearchFilters({})
    setSearchPage(1)
  }

  const handleSearchPageChange = async (page: number) => {
    try {
      setIsSearching(true)
      setSearchPage(page)

      const offset = (page - 1) * 10
      const response = await qaService.searchConversations(searchQuery, searchFilters, offset, 10)
      setSearchResults(response.messages || [])
      setSearchTotal(response.total || 0)
    } catch (err) {
      console.error('[QAPage] Page change failed', {
        error: err,
        timestamp: new Date().toISOString(),
      })
    } finally {
      setIsSearching(false)
    }
  }

  const handleSearchResultClick = (conversationId: string) => {
    setActiveConversationId(conversationId)
    setIsSearchMode(false)
  }

  const handleConversationCreated = (conversationId: string) => {
    console.warn('[QAPage] New conversation created', {
      conversationId,
      timestamp: new Date().toISOString(),
    })

    setActiveConversationId(conversationId)
    loadConversations()
  }

  const handleNewConversation = () => {
    console.warn('[QAPage] Starting new conversation', {
      timestamp: new Date().toISOString(),
    })

    setActiveConversationId(null)
    setIsSearchMode(false)
  }

  const handleSelectConversation = (conversationId: string) => {
    console.warn('[QAPage] Selecting conversation', {
      conversationId,
      timestamp: new Date().toISOString(),
    })

    setActiveConversationId(conversationId)
    setIsSearchMode(false)

    if (window.innerWidth < 768) {
      setShowSidebar(false)
      setShowConversationList(false)
    }
  }

  const handleToggleSelectConversation = (id: string) => {
    setSelectedConversationIds((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  const handleSelectAllConversations = () => {
    setSelectedConversationIds(new Set(conversations.map((c) => c.id)))
  }

  const handleDeselectAllConversations = () => {
    setSelectedConversationIds(new Set())
  }

  const handleExportSelected = async (format: 'pdf' | 'json') => {
    try {
      console.warn('[QAPage] Exporting conversations', {
        format,
        count: selectedConversationIds.size,
        timestamp: new Date().toISOString(),
      })

      const ids = Array.from(selectedConversationIds)
      const blob = await qaService.bulkExport(ids)

      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `conversations_export.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)

      console.warn('[QAPage] Export completed', {
        format,
        count: selectedConversationIds.size,
        timestamp: new Date().toISOString(),
      })
    } catch (err) {
      console.error('[QAPage] Export failed', {
        error: err,
        timestamp: new Date().toISOString(),
      })

      setError('Export failed. Please try again.')
    }
  }

  const handleArchiveSelected = async () => {
    try {
      console.warn('[QAPage] Archiving conversations', {
        count: selectedConversationIds.size,
        timestamp: new Date().toISOString(),
      })

      const ids = Array.from(selectedConversationIds)
      await qaService.archiveConversations(ids)

      setSelectedConversationIds(new Set())
      await loadConversations()

      console.warn('[QAPage] Archive completed', {
        count: ids.length,
        timestamp: new Date().toISOString(),
      })
    } catch (err) {
      console.error('[QAPage] Archive failed', {
        error: err,
        timestamp: new Date().toISOString(),
      })

      setError('Archive failed. Please try again.')
    }
  }

  const handleDeleteSelected = async () => {
    if (!window.confirm(`Delete ${selectedConversationIds.size} conversation(s)?`)) {
      return
    }

    try {
      console.warn('[QAPage] Deleting conversations', {
        count: selectedConversationIds.size,
        timestamp: new Date().toISOString(),
      })

      setSelectedConversationIds(new Set())
      await loadConversations()
    } catch (err) {
      console.error('[QAPage] Delete failed', {
        error: err,
        timestamp: new Date().toISOString(),
      })

      setError('Delete failed. Please try again.')
    }
  }

  const filteredConversations = conversations.filter((conv) =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const formatTimestamp = (timestamp: string | null) => {
    if (!timestamp) return 'No messages yet'

    const date = new Date(timestamp)
    const now = new Date()
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (diffInSeconds < 60) {
      return 'Just now'
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60)
      return `${minutes}m ago`
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600)
      return `${hours}h ago`
    } else if (diffInSeconds < 604800) {
      const days = Math.floor(diffInSeconds / 86400)
      return `${days}d ago`
    } else {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      })
    }
  }

  return (
    <div className="h-screen flex flex-col bg-secondary-50">
      <div className="border-b border-secondary-200 bg-white shadow-sm">
        <div className="px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setShowSidebar(!showSidebar)}
              className="md:hidden p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-lg transition-colors"
              aria-label="Toggle sidebar"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h1 className="text-xl font-semibold text-secondary-900">Q&A Assistant</h1>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setShowConversationList(!showConversationList)}
              className="px-3 py-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-lg transition-colors flex items-center gap-2 text-sm"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 10h16M4 14h16M4 18h16"
                />
              </svg>
              <span className="hidden sm:inline">Manage</span>
            </button>

            <button
              type="button"
              onClick={handleNewConversation}
              className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors flex items-center gap-2 text-sm font-medium"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span className="hidden sm:inline">New Chat</span>
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="mx-4 mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <svg className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="flex-1">
            <p className="text-sm text-red-800">{error}</p>
          </div>
          <button
            type="button"
            onClick={() => setError(null)}
            className="text-red-600 hover:text-red-800 transition-colors"
            aria-label="Dismiss error"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      <div className="flex-1 flex overflow-hidden">
        {showSidebar && !showConversationList && (
          <div className="w-full md:w-80 bg-white border-r border-secondary-200 flex flex-col absolute md:relative inset-0 md:inset-auto z-10 md:z-0">
            <div className="p-4 border-b border-secondary-200">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search conversations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
                />
                <svg
                  className="w-5 h-5 text-secondary-400 absolute left-3 top-1/2 transform -translate-y-1/2"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto">
              {isLoadingConversations ? (
                <div className="flex items-center justify-center h-32">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500" />
                </div>
              ) : filteredConversations.length === 0 ? (
                <div className="p-4 text-center text-secondary-500 text-sm">
                  {searchQuery ? 'No conversations found' : 'No conversations yet'}
                </div>
              ) : (
                <div className="divide-y divide-secondary-100">
                  {filteredConversations.map((conversation) => (
                    <button
                      key={conversation.id}
                      type="button"
                      onClick={() => handleSelectConversation(conversation.id)}
                      className={`w-full p-4 text-left hover:bg-secondary-50 transition-colors ${
                        activeConversationId === conversation.id ? 'bg-primary-50 border-l-4 border-primary-500' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <h3 className="font-medium text-secondary-900 truncate flex-1">{conversation.title}</h3>
                        <span className="text-xs text-secondary-500 whitespace-nowrap">
                          {formatTimestamp(conversation.last_message_at)}
                        </span>
                      </div>
                      <p className="text-sm text-secondary-600 mt-1">
                        {conversation.message_count} {conversation.message_count === 1 ? 'message' : 'messages'}
                      </p>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {showConversationList && (
          <div className="w-full md:w-96 bg-white border-r border-secondary-200 absolute md:relative inset-0 md:inset-auto z-10 md:z-0">
            <ConversationList
              conversations={conversations}
              selectedIds={selectedConversationIds}
              onToggleSelect={handleToggleSelectConversation}
              onSelectAll={handleSelectAllConversations}
              onDeselectAll={handleDeselectAllConversations}
              onExportSelected={handleExportSelected}
              onArchiveSelected={handleArchiveSelected}
              onDeleteSelected={handleDeleteSelected}
              onLoadMore={loadConversations}
              hasMore={hasMoreConversations}
              isLoading={isLoadingConversations}
            />
          </div>
        )}

        <div className="flex-1 flex flex-col overflow-hidden">
          {isSearchMode ? (
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <SearchBar onSearch={handleSearch} onClear={handleClearSearch} isLoading={isSearching} />
              <SearchResults
                results={searchResults as never[]}
                total={searchTotal}
                query={searchQuery}
                page={searchPage}
                pageSize={10}
                onPageChange={handleSearchPageChange}
                onResultClick={handleSearchResultClick}
                isLoading={isSearching}
              />
            </div>
          ) : (
            <>
              <div className="p-4">
                <SearchBar onSearch={handleSearch} onClear={handleClearSearch} isLoading={isSearching} />
              </div>
              <div className="flex-1 overflow-hidden">
                <ChatWindow conversationId={activeConversationId} onConversationCreated={handleConversationCreated} />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default QAPage
