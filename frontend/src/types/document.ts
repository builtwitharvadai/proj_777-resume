export interface Document {
  id: string
  user_id: string
  filename: string
  file_type: string
  file_size: number
  s3_key: string
  upload_status: 'pending' | 'uploading' | 'completed' | 'failed'
  created_at: string
  updated_at: string
}

export interface DocumentUploadResponse {
  document: Document
  message: string
}

export interface UploadProgress {
  filename: string
  progress: number
  status: 'idle' | 'uploading' | 'completed' | 'error'
  error?: string
  estimatedTimeRemaining?: number
}

export interface ValidationError {
  field: string
  message: string
  code: string
}

export interface DocumentListResponse {
  documents: Document[]
  total: number
  page: number
  page_size: number
}

export interface DeleteDocumentResponse {
  message: string
  document_id: string
}
