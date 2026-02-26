import api from './api'
import { Document, DocumentUploadResponse, DocumentListResponse, DeleteDocumentResponse } from '../types/document'

export const documentService = {
  async uploadDocument(
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<DocumentUploadResponse> {
    try {
      console.warn('[Document Service] Upload document request initiated', {
        filename: file.name,
        fileType: file.type,
        fileSize: file.size,
        timestamp: new Date().toISOString(),
      })

      const formData = new FormData()
      formData.append('file', file)

      const response = await api.post<DocumentUploadResponse>('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            console.warn('[Document Service] Upload progress', {
              filename: file.name,
              progress,
              loaded: progressEvent.loaded,
              total: progressEvent.total,
              timestamp: new Date().toISOString(),
            })
            if (onProgress) {
              onProgress(progress)
            }
          }
        },
      })

      console.warn('[Document Service] Upload document successful', {
        documentId: response.data.document.id,
        filename: response.data.document.filename,
        timestamp: new Date().toISOString(),
      })

      return response.data
    } catch (error) {
      console.error('[Document Service] Upload document failed', {
        filename: file.name,
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  async getDocuments(page = 1, pageSize = 10): Promise<DocumentListResponse> {
    try {
      console.warn('[Document Service] Get documents request initiated', {
        page,
        pageSize,
        timestamp: new Date().toISOString(),
      })

      const response = await api.get<DocumentListResponse>('/documents', {
        params: {
          page,
          page_size: pageSize,
        },
      })

      console.warn('[Document Service] Get documents successful', {
        total: response.data.total,
        count: response.data.documents.length,
        timestamp: new Date().toISOString(),
      })

      return response.data
    } catch (error) {
      console.error('[Document Service] Get documents failed', {
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  async deleteDocument(documentId: string): Promise<DeleteDocumentResponse> {
    try {
      console.warn('[Document Service] Delete document request initiated', {
        documentId,
        timestamp: new Date().toISOString(),
      })

      const response = await api.delete<DeleteDocumentResponse>(`/documents/${documentId}`)

      console.warn('[Document Service] Delete document successful', {
        documentId,
        timestamp: new Date().toISOString(),
      })

      return response.data
    } catch (error) {
      console.error('[Document Service] Delete document failed', {
        documentId,
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },
}

export default documentService
