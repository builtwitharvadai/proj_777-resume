import { useState, useCallback } from 'react'
import { useMutation, useQuery, useQueryClient } from 'react-query'
import { UploadProgress, ValidationError } from '../types/document'
import documentService from '../services/documents'

const MAX_FILE_SIZE = 10 * 1024 * 1024
const ALLOWED_FILE_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']

export const useDocumentUpload = () => {
  const queryClient = useQueryClient()
  const [uploadProgress, setUploadProgress] = useState<Map<string, UploadProgress>>(new Map())
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([])

  const validateFile = useCallback((file: File): ValidationError | null => {
    if (file.size > MAX_FILE_SIZE) {
      console.error('[useDocumentUpload] File size validation failed', {
        filename: file.name,
        size: file.size,
        maxSize: MAX_FILE_SIZE,
        timestamp: new Date().toISOString(),
      })
      return {
        field: 'file_size',
        message: `File size exceeds maximum limit of ${MAX_FILE_SIZE / 1024 / 1024} MB`,
        code: 'FILE_TOO_LARGE',
      }
    }

    if (!ALLOWED_FILE_TYPES.includes(file.type)) {
      console.error('[useDocumentUpload] File type validation failed', {
        filename: file.name,
        type: file.type,
        allowedTypes: ALLOWED_FILE_TYPES,
        timestamp: new Date().toISOString(),
      })
      return {
        field: 'file_type',
        message: 'File type not supported. Please upload PDF, DOCX, or TXT files',
        code: 'INVALID_FILE_TYPE',
      }
    }

    return null
  }, [])

  const uploadMutation = useMutation(
    async ({ file, startTime }: { file: File; startTime: number }) => {
      const fileKey = `${file.name}-${file.size}`

      const handleProgress = (progress: number) => {
        const now = Date.now()
        const elapsed = (now - startTime) / 1000
        const estimatedTotal = elapsed / (progress / 100)
        const estimatedTimeRemaining = estimatedTotal - elapsed

        setUploadProgress((prev) => {
          const updated = new Map(prev)
          updated.set(fileKey, {
            filename: file.name,
            progress,
            status: 'uploading',
            estimatedTimeRemaining: Math.max(0, estimatedTimeRemaining),
          })
          return updated
        })
      }

      return documentService.uploadDocument(file, handleProgress)
    },
    {
      onSuccess: (data, variables) => {
        const fileKey = `${variables.file.name}-${variables.file.size}`

        console.warn('[useDocumentUpload] Upload successful', {
          filename: variables.file.name,
          documentId: data.document.id,
          timestamp: new Date().toISOString(),
        })

        setUploadProgress((prev) => {
          const updated = new Map(prev)
          updated.set(fileKey, {
            filename: variables.file.name,
            progress: 100,
            status: 'completed',
          })
          return updated
        })

        queryClient.invalidateQueries('documents')
      },
      onError: (error, variables) => {
        const fileKey = `${variables.file.name}-${variables.file.size}`

        console.error('[useDocumentUpload] Upload failed', {
          filename: variables.file.name,
          error,
          timestamp: new Date().toISOString(),
        })

        setUploadProgress((prev) => {
          const updated = new Map(prev)
          updated.set(fileKey, {
            filename: variables.file.name,
            progress: 0,
            status: 'error',
            error: error instanceof Error ? error.message : 'Upload failed. Please try again.',
          })
          return updated
        })
      },
    }
  )

  const uploadFiles = useCallback(
    (files: File[]) => {
      console.warn('[useDocumentUpload] Starting file upload', {
        fileCount: files.length,
        timestamp: new Date().toISOString(),
      })

      const errors: ValidationError[] = []

      files.forEach((file) => {
        const fileKey = `${file.name}-${file.size}`
        const validationError = validateFile(file)

        if (validationError) {
          errors.push(validationError)
          setUploadProgress((prev) => {
            const updated = new Map(prev)
            updated.set(fileKey, {
              filename: file.name,
              progress: 0,
              status: 'error',
              error: validationError.message,
            })
            return updated
          })
        } else {
          setUploadProgress((prev) => {
            const updated = new Map(prev)
            updated.set(fileKey, {
              filename: file.name,
              progress: 0,
              status: 'uploading',
            })
            return updated
          })

          const startTime = Date.now()
          uploadMutation.mutate({ file, startTime })
        }
      })

      setValidationErrors(errors)
    },
    [validateFile, uploadMutation]
  )

  const clearProgress = useCallback((filename: string, fileSize: number) => {
    const fileKey = `${filename}-${fileSize}`
    setUploadProgress((prev) => {
      const updated = new Map(prev)
      updated.delete(fileKey)
      return updated
    })
  }, [])

  const clearAllProgress = useCallback(() => {
    setUploadProgress(new Map())
    setValidationErrors([])
  }, [])

  return {
    uploadFiles,
    uploadProgress: Array.from(uploadProgress.values()),
    validationErrors,
    isUploading: uploadMutation.isLoading,
    clearProgress,
    clearAllProgress,
  }
}

export const useDocuments = (page = 1, pageSize = 10) => {
  return useQuery(['documents', page, pageSize], () => documentService.getDocuments(page, pageSize), {
    keepPreviousData: true,
    staleTime: 30000,
    onSuccess: (data) => {
      console.warn('[useDocuments] Documents fetched successfully', {
        total: data.total,
        count: data.documents.length,
        timestamp: new Date().toISOString(),
      })
    },
    onError: (error) => {
      console.error('[useDocuments] Failed to fetch documents', {
        error,
        timestamp: new Date().toISOString(),
      })
    },
  })
}

export const useDeleteDocument = () => {
  const queryClient = useQueryClient()

  return useMutation((documentId: string) => documentService.deleteDocument(documentId), {
    onSuccess: (data) => {
      console.warn('[useDeleteDocument] Document deleted successfully', {
        documentId: data.document_id,
        timestamp: new Date().toISOString(),
      })
      queryClient.invalidateQueries('documents')
    },
    onError: (error, documentId) => {
      console.error('[useDeleteDocument] Failed to delete document', {
        documentId,
        error,
        timestamp: new Date().toISOString(),
      })
    },
  })
}
