import { useState } from 'react'
import { FileRejection } from 'react-dropzone'
import FileDropzone from './FileDropzone'
import UploadProgress from './UploadProgress'
import { useDocumentUpload } from '../../hooks/useDocumentUpload'

const DocumentUpload = () => {
  const { uploadFiles, uploadProgress, validationErrors, isUploading, clearProgress } = useDocumentUpload()
  const [rejectionErrors, setRejectionErrors] = useState<string[]>([])

  const handleFilesAccepted = (files: File[]) => {
    console.warn('[DocumentUpload] Files accepted', {
      fileCount: files.length,
      filenames: files.map((f) => f.name),
      timestamp: new Date().toISOString(),
    })

    setRejectionErrors([])
    uploadFiles(files)
  }

  const handleFilesRejected = (rejections: FileRejection[]) => {
    console.error('[DocumentUpload] Files rejected', {
      rejectionCount: rejections.length,
      timestamp: new Date().toISOString(),
    })

    const errors = rejections.flatMap((rejection) =>
      rejection.errors.map((error) => `${rejection.file.name}: ${error.message}`)
    )
    setRejectionErrors(errors)
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-secondary-900 mb-2">Upload Documents</h2>
        <p className="text-secondary-600">
          Upload your documents to get started. Supported formats: PDF, DOCX, TXT (max 10 MB)
        </p>
      </div>

      <FileDropzone
        onFilesAccepted={handleFilesAccepted}
        onFilesRejected={handleFilesRejected}
        disabled={isUploading}
      />

      {validationErrors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start">
            <svg
              className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5"
              fill="currentColor"
              viewBox="0 0 20 20"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-red-800">Validation Errors</h3>
              <ul className="mt-2 text-sm text-red-700 list-disc list-inside space-y-1">
                {validationErrors.map((error, index) => (
                  <li key={index}>{error.message}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {rejectionErrors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start">
            <svg
              className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5"
              fill="currentColor"
              viewBox="0 0 20 20"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-red-800">Upload Errors</h3>
              <ul className="mt-2 text-sm text-red-700 list-disc list-inside space-y-1">
                {rejectionErrors.map((error, index) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {uploadProgress.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-secondary-900">Upload Progress</h3>
          {uploadProgress.map((progress) => (
            <UploadProgress
              key={`${progress.filename}`}
              progress={progress}
              onCancel={
                progress.status === 'uploading'
                  ? () => {
                      console.warn('[DocumentUpload] Upload cancelled', {
                        filename: progress.filename,
                        timestamp: new Date().toISOString(),
                      })
                    }
                  : undefined
              }
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default DocumentUpload
