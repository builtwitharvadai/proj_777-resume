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

  async searchConversations(
    query: string,
    filters?: { category?: string; dateRange?: { from: string; to: string } },
    offset = 0,
    limit = 10
  ): Promise<{ messages: unknown[]; total: number; offset: number; limit: number }> {
    try {
      console.warn('[QA Service] Search conversations request initiated', {
        query,
        filters,
        offset,
        limit,
        timestamp: new Date().toISOString(),
      })

      const params: Record<string, unknown> = {
        query: query.trim(),
        offset,
        limit,
      }

      if (filters?.category) {
        params.category = filters.category
      }

      if (filters?.dateRange?.from) {
        params.date_from = filters.dateRange.from
      }

      if (filters?.dateRange?.to) {
        params.date_to = filters.dateRange.to
      }

      const response = await api.get('/qa/search', { params })

      console.warn('[QA Service] Search conversations successful', {
        total: response.data.total,
        count: response.data.messages?.length || 0,
        timestamp: new Date().toISOString(),
      })

      return response.data
    } catch (error) {
      console.error('[QA Service] Search conversations failed', {
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  async exportConversation(
    conversationId: string,
    format: 'pdf' | 'json' = 'pdf'
  ): Promise<Blob> {
    try {
      console.warn('[QA Service] Export conversation request initiated', {
        conversationId,
        format,
        timestamp: new Date().toISOString(),
      })

      const response = await api.get(`/qa/export/${conversationId}`, {
        params: { format },
        responseType: 'blob',
      })

      console.warn('[QA Service] Export conversation successful', {
        conversationId,
        format,
        timestamp: new Date().toISOString(),
      })

      return response.data
    } catch (error) {
      console.error('[QA Service] Export conversation failed', {
        conversationId,
        format,
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  async bulkExport(
    conversationIds: string[],
    onProgress?: (current: number, total: number) => void
  ): Promise<Blob> {
    try {
      console.warn('[QA Service] Bulk export request initiated', {
        conversationCount: conversationIds.length,
        timestamp: new Date().toISOString(),
      })

      const response = await api.post(
        '/qa/export/bulk',
        { conversation_ids: conversationIds },
        {
          responseType: 'blob',
          onDownloadProgress: (progressEvent) => {
            if (onProgress && progressEvent.total) {
              const percentCompleted = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              )
              onProgress(progressEvent.loaded, progressEvent.total)

              console.warn('[QA Service] Bulk export progress', {
                loaded: progressEvent.loaded,
                total: progressEvent.total,
                percentCompleted,
                timestamp: new Date().toISOString(),
              })
            }
          },
        }
      )

      console.warn('[QA Service] Bulk export successful', {
        conversationCount: conversationIds.length,
        timestamp: new Date().toISOString(),
      })

      return response.data
    } catch (error) {
      console.error('[QA Service] Bulk export failed', {
        conversationCount: conversationIds.length,
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  async archiveConversations(conversationIds: string[]): Promise<void> {
    try {
      console.warn('[QA Service] Archive conversations request initiated', {
        conversationCount: conversationIds.length,
        timestamp: new Date().toISOString(),
      })

      await api.post('/qa/archive', {
        conversation_ids: conversationIds,
      })

      console.warn('[QA Service] Archive conversations successful', {
        conversationCount: conversationIds.length,
        timestamp: new Date().toISOString(),
      })
    } catch (error) {
      console.error('[QA Service] Archive conversations failed', {
        conversationCount: conversationIds.length,
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
