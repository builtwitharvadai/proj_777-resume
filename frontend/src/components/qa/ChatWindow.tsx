import { useState, useEffect, useRef, useCallback } from 'react'
import { useWebSocket } from '../../hooks/useWebSocket'
import MessageBubble from './MessageBubble'
import MessageInput from './MessageInput'
import TypingIndicator from './TypingIndicator'
import { qaService } from '../../services/qa'
import { Message, WebSocketMessage } from '../../types/qa'

interface ChatWindowProps {
  conversationId?: string | null
  onConversationCreated?: (conversationId: string) => void
}

const ChatWindow = ({ conversationId, onConversationCreated }: ChatWindowProps) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)
  const shouldScrollRef = useRef(true)

  const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws/qa`

  const handleWebSocketMessage = useCallback((wsMessage: WebSocketMessage) => {
    console.warn('[ChatWindow] WebSocket message received', {
      type: wsMessage.type,
      timestamp: new Date().toISOString(),
    })

    if (wsMessage.type === 'message' && wsMessage.payload?.message) {
      const newMessage = wsMessage.payload.message

      setMessages((prev) => {
        const exists = prev.some((m) => m.id === newMessage.id)
        if (exists) {
          return prev.map((m) => (m.id === newMessage.id ? newMessage : m))
        }
        return [...prev, newMessage]
      })

      setIsTyping(false)
      shouldScrollRef.current = true
    } else if (wsMessage.type === 'typing' && wsMessage.payload?.is_typing !== undefined) {
      setIsTyping(wsMessage.payload.is_typing)
      if (wsMessage.payload.is_typing) {
        shouldScrollRef.current = true
      }
    } else if (wsMessage.type === 'error' && wsMessage.payload?.error) {
      console.error('[ChatWindow] WebSocket error', {
        error: wsMessage.payload.error,
        timestamp: new Date().toISOString(),
      })

      setError(wsMessage.payload.error)
      setIsTyping(false)
    }
  }, [])

  const { connectionState, sendMessage } = useWebSocket(wsUrl, {
    onMessage: handleWebSocketMessage,
  })

  const scrollToBottom = useCallback(() => {
    if (shouldScrollRef.current && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
      shouldScrollRef.current = false
    }
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping, scrollToBottom])

  const handleScroll = useCallback(() => {
    if (!messagesContainerRef.current) return

    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 100

    shouldScrollRef.current = isNearBottom
  }, [])

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) {
      return
    }

    try {
      setIsLoading(true)
      setError(null)

      const tempId = `temp-${Date.now()}`
      const tempMessage: Message = {
        id: tempId,
        conversation_id: conversationId || '',
        content: content.trim(),
        role: 'user',
        status: 'sending',
        rating: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, tempMessage])
      shouldScrollRef.current = true

      console.warn('[ChatWindow] Sending message', {
        conversationId,
        contentLength: content.length,
        timestamp: new Date().toISOString(),
      })

      const response = await qaService.askQuestion({
        question: content.trim(),
        conversation_id: conversationId,
      })

      setMessages((prev) => prev.filter((m) => m.id !== tempId))

      if (!conversationId && response.conversation.id && onConversationCreated) {
        console.warn('[ChatWindow] New conversation created', {
          conversationId: response.conversation.id,
          timestamp: new Date().toISOString(),
        })

        onConversationCreated(response.conversation.id)
      }

      const sent = sendMessage({
        type: 'message',
        payload: {
          message: response.message,
          conversation_id: response.conversation.id,
        },
        timestamp: new Date().toISOString(),
      })

      if (!sent) {
        console.error('[ChatWindow] Failed to send WebSocket message', {
          timestamp: new Date().toISOString(),
        })
      }

      setMessages((prev) => {
        const exists = prev.some((m) => m.id === response.message.id)
        if (!exists) {
          return [...prev, response.message]
        }
        return prev
      })

      setIsTyping(true)
    } catch (err) {
      console.error('[ChatWindow] Failed to send message', {
        error: err,
        timestamp: new Date().toISOString(),
      })

      setMessages((prev) =>
        prev.map((m) =>
          m.status === 'sending'
            ? {
                ...m,
                status: 'failed' as const,
              }
            : m
        )
      )

      setError('Failed to send message. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRateMessage = async (messageId: string, rating: number) => {
    try {
      console.warn('[ChatWindow] Rating message', {
        messageId,
        rating,
        timestamp: new Date().toISOString(),
      })

      const response = await qaService.rateMessage(messageId, { rating })

      setMessages((prev) => prev.map((m) => (m.id === messageId ? response.message : m)))

      console.warn('[ChatWindow] Message rated successfully', {
        messageId,
        rating,
        timestamp: new Date().toISOString(),
      })
    } catch (err) {
      console.error('[ChatWindow] Failed to rate message', {
        messageId,
        error: err,
        timestamp: new Date().toISOString(),
      })

      setError('Failed to rate message. Please try again.')
    }
  }

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="border-b border-secondary-200 p-4 bg-white shadow-sm">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <h2 className="text-lg font-semibold text-secondary-900">AI Assistant</h2>
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                connectionState === 'connected'
                  ? 'bg-green-500'
                  : connectionState === 'connecting'
                  ? 'bg-yellow-500 animate-pulse'
                  : 'bg-red-500'
              }`}
            />
            <span className="text-sm text-secondary-600 capitalize">{connectionState}</span>
          </div>
        </div>
      </div>

      <div ref={messagesContainerRef} onScroll={handleScroll} className="flex-1 overflow-y-auto p-4 bg-secondary-50">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 && !isLoading && (
            <div className="flex flex-col items-center justify-center h-full text-center py-12">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-secondary-900 mb-2">Start a conversation</h3>
              <p className="text-secondary-600 max-w-md">
                Ask me anything about your resume, career advice, or job search strategies. I'm here to help!
              </p>
            </div>
          )}

          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} onRate={handleRateMessage} />
          ))}

          {isTyping && <TypingIndicator />}

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <svg className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
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

          <div ref={messagesEndRef} />
        </div>
      </div>

      <MessageInput onSend={handleSendMessage} disabled={isLoading || connectionState !== 'connected'} />
    </div>
  )
}

export default ChatWindow
