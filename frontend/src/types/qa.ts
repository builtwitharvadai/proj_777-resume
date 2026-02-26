export interface Message {
  id: string
  conversation_id: string
  content: string
  role: 'user' | 'assistant'
  status: MessageStatus
  rating?: number | null
  created_at: string
  updated_at: string
}

export type MessageStatus = 'sending' | 'sent' | 'delivered' | 'failed'

export interface Conversation {
  id: string
  user_id: string
  title: string
  message_count: number
  last_message_at: string | null
  created_at: string
  updated_at: string
}

export interface WebSocketMessage {
  type: 'message' | 'typing' | 'error' | 'connection' | 'ping' | 'pong'
  payload?: {
    message?: Message
    conversation_id?: string
    user_id?: string
    is_typing?: boolean
    error?: string
    status?: string
  }
  timestamp: string
}

export interface TypingIndicator {
  conversation_id: string
  user_id: string
  is_typing: boolean
  timestamp: string
}

export interface AskQuestionRequest {
  question: string
  conversation_id?: string | null
}

export interface AskQuestionResponse {
  message: Message
  conversation: Conversation
}

export interface GetConversationsResponse {
  conversations: Conversation[]
  total: number
  page: number
  page_size: number
}

export interface SearchMessagesRequest {
  query: string
  conversation_id?: string | null
  page?: number
  page_size?: number
}

export interface SearchMessagesResponse {
  messages: Message[]
  total: number
  page: number
  page_size: number
}

export interface RateMessageRequest {
  rating: number
}

export interface RateMessageResponse {
  message: Message
}
