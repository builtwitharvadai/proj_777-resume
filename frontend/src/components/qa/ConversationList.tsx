import { useState, useEffect, useRef, useCallback } from 'react'

interface Conversation {
  id: string
  title: string
  message_count: number
  last_message_at: string | null
  category?: string
  created_at: string
}

interface ConversationListProps {
  conversations: Conversation[]
  selectedIds: Set<string>
  onToggleSelect: (id: string) => void
  onSelectAll: () => void
  onDeselectAll: () => void
  onExportSelected: (format: 'pdf' | 'json') => void
  onArchiveSelected: () => void
  onDeleteSelected: () => void
  onLoadMore: () => void
  hasMore: boolean
  isLoading?: boolean
}

const ConversationList = ({
  conversations,
  selectedIds,
  onToggleSelect,
  onSelectAll,
  onDeselectAll,
  onExportSelected,
  onArchiveSelected,
  onDeleteSelected,
  onLoadMore,
  hasMore,
  isLoading = false,
}: ConversationListProps) => {
  const [showBulkActions, setShowBulkActions] = useState(false)
  const observerTarget = useRef<HTMLDivElement>(null)

  // Infinite scrolling
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !isLoading) {
          onLoadMore()
        }
      },
      { threshold: 0.1 }
    )

    const currentTarget = observerTarget.current
    if (currentTarget) {
      observer.observe(currentTarget)
    }

    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget)
      }
    }
  }, [hasMore, isLoading, onLoadMore])

  useEffect(() => {
    setShowBulkActions(selectedIds.size > 0)
  }, [selectedIds.size])

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

  const allSelected = conversations.length > 0 && selectedIds.size === conversations.length

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between p-4 border-b border-secondary-200 bg-white">
        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={allSelected}
            onChange={allSelected ? onDeselectAll : onSelectAll}
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-secondary-300 rounded"
            aria-label={allSelected ? 'Deselect all' : 'Select all'}
          />
          <span className="text-sm font-medium text-secondary-700">
            {selectedIds.size > 0 ? `${selectedIds.size} selected` : 'Select all'}
          </span>
        </div>

        {showBulkActions && (
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => onExportSelected('json')}
              className="px-3 py-1 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors flex items-center gap-1"
              title="Export as JSON"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <span className="hidden sm:inline">JSON</span>
            </button>

            <button
              type="button"
              onClick={() => onExportSelected('pdf')}
              className="px-3 py-1 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors flex items-center gap-1"
              title="Export as PDF"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                />
              </svg>
              <span className="hidden sm:inline">PDF</span>
            </button>

            <button
              type="button"
              onClick={onArchiveSelected}
              className="px-3 py-1 text-sm font-medium text-secondary-600 hover:bg-secondary-100 rounded-lg transition-colors"
              title="Archive"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"
                />
              </svg>
            </button>

            <button
              type="button"
              onClick={onDeleteSelected}
              className="px-3 py-1 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="Delete"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full p-8 text-center">
            <svg
              className="w-16 h-16 text-secondary-300 mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <h3 className="text-lg font-medium text-secondary-900 mb-1">No conversations yet</h3>
            <p className="text-sm text-secondary-500">Start a new conversation to get started</p>
          </div>
        )}

        <div className="divide-y divide-secondary-100">
          {conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`p-4 hover:bg-secondary-50 transition-colors ${
                selectedIds.has(conversation.id) ? 'bg-primary-50' : ''
              }`}
            >
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  checked={selectedIds.has(conversation.id)}
                  onChange={() => onToggleSelect(conversation.id)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-secondary-300 rounded mt-1"
                  aria-label={`Select conversation: ${conversation.title}`}
                />

                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <h4 className="font-medium text-secondary-900 truncate">{conversation.title}</h4>
                    <span className="text-xs text-secondary-500 whitespace-nowrap">
                      {formatTimestamp(conversation.last_message_at)}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 text-sm text-secondary-600">
                    <span className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                        />
                      </svg>
                      {conversation.message_count}
                    </span>

                    {conversation.category && (
                      <span className="px-2 py-0.5 bg-secondary-100 text-secondary-700 rounded text-xs font-medium">
                        {conversation.category.replace('_', ' ')}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div ref={observerTarget} className="h-4" />

        {isLoading && (
          <div className="flex items-center justify-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500" />
          </div>
        )}
      </div>
    </div>
  )
}

export default ConversationList
