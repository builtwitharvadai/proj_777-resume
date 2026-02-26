import { useState, useEffect } from 'react'
import ChatWindow from '../components/qa/ChatWindow'
import { qaService } from '../services/qa'
import { Conversation } from '../types/qa'

const QAPage = () => {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoadingConversations, setIsLoadingConversations] = useState(false)
  const [showSidebar, setShowSidebar] = useState(true)
  const [error, setError] = useState<string | null>(null)

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
  }

  const handleSelectConversation = (conversationId: string) => {
    console.warn('[QAPage] Selecting conversation', {
      conversationId,
      timestamp: new Date().toISOString(),
    })

    setActiveConversationId(conversationId)

    if (window.innerWidth < 768) {
      setShowSidebar(false)
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
        {showSidebar && (
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

        <div className="flex-1 flex flex-col">
          <ChatWindow conversationId={activeConversationId} onConversationCreated={handleConversationCreated} />
        </div>
      </div>
    </div>
  )
}

export default QAPage
