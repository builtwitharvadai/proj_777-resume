import api from './api'
import {
  AskQuestionRequest,
  AskQuestionResponse,
  GetConversationsResponse,
  SearchMessagesRequest,
  SearchMessagesResponse,
  RateMessageRequest,
  RateMessageResponse,
} from '../types/qa'

export const qaService = {
  async askQuestion(data: AskQuestionRequest): Promise<AskQuestionResponse> {
    try {
      console.warn('[QA Service] Ask question request initiated', {
        hasConversationId: !!data.conversation_id,
        timestamp: new Date().toISOString(),
      })

      const response = await api.post<AskQuestionResponse>('/qa/ask', {
        question: data.question.trim(),
        conversation_id: data.conversation_id || null,
      })

      console.warn('[QA Service] Ask question successful', {
        conversationId: response.data.conversation.id,
        messageId: response.data.message.id,
        timestamp: new Date().toISOString(),
      })

      return response.data
    } catch (error) {
      console.error('[QA Service] Ask question failed', {
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  async getConversations(page = 1, pageSize = 20): Promise<GetConversationsResponse> {
    try {
      console.warn('[QA Service] Get conversations request initiated', {
        page,
        pageSize,
        timestamp: new Date().toISOString(),
      })

      const response = await api.get<GetConversationsResponse>('/qa/conversations', {
        params: {
          page,
          page_size: pageSize,
        },
      })

      console.warn('[QA Service] Get conversations successful', {
        total: response.data.total,
        count: response.data.conversations.length,
        timestamp: new Date().toISOString(),
      })

      return response.data
    } catch (error) {
      console.error('[QA Service] Get conversations failed', {
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  async searchMessages(data: SearchMessagesRequest): Promise<SearchMessagesResponse> {
    try {
      console.warn('[QA Service] Search messages request initiated', {
        query: data.query,
        hasConversationId: !!data.conversation_id,
        page: data.page,
        pageSize: data.page_size,
        timestamp: new Date().toISOString(),
      })

      const response = await api.get<SearchMessagesResponse>('/qa/search', {
        params: {
          query: data.query.trim(),
          conversation_id: data.conversation_id || null,
          page: data.page || 1,
          page_size: data.page_size || 20,
        },
      })

      console.warn('[QA Service] Search messages successful', {
        total: response.data.total,
        count: response.data.messages.length,
        timestamp: new Date().toISOString(),
      })

      return response.data
    } catch (error) {
      console.error('[QA Service] Search messages failed', {
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  async rateMessage(messageId: string, data: RateMessageRequest): Promise<RateMessageResponse> {
    try {
      console.warn('[QA Service] Rate message request initiated', {
        messageId,
        rating: data.rating,
        timestamp: new Date().toISOString(),
      })

      if (data.rating < 1 || data.rating > 5) {
        throw new Error('Rating must be between 1 and 5')
      }

      const response = await api.post<RateMessageResponse>(`/qa/messages/${messageId}/rate`, {
        rating: data.rating,
      })

      console.warn('[QA Service] Rate message successful', {
        messageId,
        rating: data.rating,
        timestamp: new Date().toISOString(),
      })

      return response.data
    } catch (error) {
      console.error('[QA Service] Rate message failed', {
        messageId,
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },
}

export default qaService
