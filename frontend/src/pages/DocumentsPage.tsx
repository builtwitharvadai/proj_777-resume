import { useState } from 'react'
import DocumentUpload from '../components/documents/DocumentUpload'
import { useDocuments, useDeleteDocument } from '../hooks/useDocumentUpload'

const DocumentsPage = () => {
  const [page, setPage] = useState(1)
  const pageSize = 10
  const { data: documentsData, isLoading, error } = useDocuments(page, pageSize)
  const deleteDocumentMutation = useDeleteDocument()

  const handleDelete = async (documentId: string, filename: string) => {
    if (window.confirm(`Are you sure you want to delete "${filename}"?`)) {
      console.warn('[DocumentsPage] Deleting document', {
        documentId,
        filename,
        timestamp: new Date().toISOString(),
      })

      try {
        await deleteDocumentMutation.mutateAsync(documentId)
      } catch (error) {
        console.error('[DocumentsPage] Failed to delete document', {
          documentId,
          error,
          timestamp: new Date().toISOString(),
        })
      }
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getFileTypeIcon = (fileType: string) => {
    if (fileType.includes('pdf')) {
      return (
        <svg
          className="w-8 h-8 text-red-500"
          fill="currentColor"
          viewBox="0 0 20 20"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            fillRule="evenodd"
            d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
            clipRule="evenodd"
          />
        </svg>
      )
    }
    if (fileType.includes('word') || fileType.includes('document')) {
      return (
        <svg
          className="w-8 h-8 text-blue-500"
          fill="currentColor"
          viewBox="0 0 20 20"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            fillRule="evenodd"
            d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
            clipRule="evenodd"
          />
        </svg>
      )
    }
    return (
      <svg
        className="w-8 h-8 text-secondary-500"
        fill="currentColor"
        viewBox="0 0 20 20"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          fillRule="evenodd"
          d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
          clipRule="evenodd"
        />
      </svg>
    )
  }

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-secondary-900">Documents</h1>
          <p className="mt-2 text-secondary-600">Manage your uploaded documents</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6 mb-8">
          <DocumentUpload />
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-secondary-200">
          <div className="px-6 py-4 border-b border-secondary-200">
            <h2 className="text-xl font-semibold text-secondary-900">Your Documents</h2>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
            </div>
          ) : error ? (
            <div className="px-6 py-12 text-center">
              <svg
                className="w-12 h-12 text-red-500 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="text-secondary-600">Failed to load documents. Please try again.</p>
            </div>
          ) : documentsData && documentsData.documents.length > 0 ? (
            <>
              <div className="divide-y divide-secondary-200">
                {documentsData.documents.map((document) => (
                  <div
                    key={document.id}
                    className="px-6 py-4 hover:bg-secondary-50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 flex-1 min-w-0">
                        <div className="flex-shrink-0">{getFileTypeIcon(document.file_type)}</div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-secondary-900 truncate">
                            {document.filename}
                          </p>
                          <div className="flex items-center space-x-4 mt-1">
                            <p className="text-xs text-secondary-500">
                              {formatFileSize(document.file_size)}
                            </p>
                            <p className="text-xs text-secondary-500">
                              {formatDate(document.created_at)}
                            </p>
                            <span
                              className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                                document.upload_status === 'completed'
                                  ? 'bg-green-100 text-green-800'
                                  : document.upload_status === 'failed'
                                  ? 'bg-red-100 text-red-800'
                                  : 'bg-yellow-100 text-yellow-800'
                              }`}
                            >
                              {document.upload_status}
                            </span>
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDelete(document.id, document.filename)}
                        disabled={deleteDocumentMutation.isLoading}
                        className="ml-4 text-red-600 hover:text-red-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        aria-label={`Delete ${document.filename}`}
                      >
                        <svg
                          className="w-5 h-5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {documentsData.total > pageSize && (
                <div className="px-6 py-4 border-t border-secondary-200 flex items-center justify-between">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 text-sm font-medium text-secondary-700 bg-white border border-secondary-300 rounded-md hover:bg-secondary-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <span className="text-sm text-secondary-600">
                    Page {page} of {Math.ceil(documentsData.total / pageSize)}
                  </span>
                  <button
                    onClick={() => setPage((p) => p + 1)}
                    disabled={page >= Math.ceil(documentsData.total / pageSize)}
                    className="px-4 py-2 text-sm font-medium text-secondary-700 bg-white border border-secondary-300 rounded-md hover:bg-secondary-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="px-6 py-12 text-center">
              <svg
                className="w-12 h-12 text-secondary-400 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <p className="text-secondary-600">No documents uploaded yet</p>
              <p className="text-sm text-secondary-500 mt-1">Upload your first document to get started</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DocumentsPage
