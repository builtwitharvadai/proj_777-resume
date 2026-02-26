import { useCallback } from 'react'
import { useDropzone, FileRejection } from 'react-dropzone'

const MAX_FILE_SIZE = 10 * 1024 * 1024
const ACCEPTED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'text/plain': ['.txt'],
}

interface FileDropzoneProps {
  onFilesAccepted: (files: File[]) => void
  onFilesRejected?: (rejections: FileRejection[]) => void
  disabled?: boolean
}

const FileDropzone = ({ onFilesAccepted, onFilesRejected, disabled = false }: FileDropzoneProps) => {
  const onDrop = useCallback(
    (acceptedFiles: File[], fileRejections: FileRejection[]) => {
      console.warn('[FileDropzone] Files dropped', {
        acceptedCount: acceptedFiles.length,
        rejectedCount: fileRejections.length,
        timestamp: new Date().toISOString(),
      })

      if (acceptedFiles.length > 0) {
        onFilesAccepted(acceptedFiles)
      }

      if (fileRejections.length > 0) {
        console.error('[FileDropzone] Files rejected', {
          rejections: fileRejections.map((r) => ({
            filename: r.file.name,
            errors: r.errors.map((e) => e.message),
          })),
          timestamp: new Date().toISOString(),
        })

        if (onFilesRejected) {
          onFilesRejected(fileRejections)
        }
      }
    },
    [onFilesAccepted, onFilesRejected]
  )

  const { getRootProps, getInputProps, isDragActive, isDragAccept, isDragReject } = useDropzone({
    onDrop,
    accept: ACCEPTED_FILE_TYPES,
    maxSize: MAX_FILE_SIZE,
    multiple: true,
    disabled,
  })

  const getBorderColor = () => {
    if (isDragAccept) return 'border-primary-500 bg-primary-50'
    if (isDragReject) return 'border-red-500 bg-red-50'
    if (isDragActive) return 'border-primary-400 bg-primary-25'
    return 'border-secondary-300'
  }

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
        transition-all duration-200 ease-in-out
        ${getBorderColor()}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-primary-400 hover:bg-secondary-50'}
      `}
      aria-label="File upload dropzone"
      role="button"
      tabIndex={0}
    >
      <input {...getInputProps()} aria-label="File upload input" />

      <div className="flex flex-col items-center space-y-4">
        <svg
          className={`w-12 h-12 ${isDragActive ? 'text-primary-500' : 'text-secondary-400'}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>

        {isDragActive ? (
          <div>
            <p className="text-lg font-medium text-primary-600">Drop files here</p>
            <p className="text-sm text-secondary-500">Release to upload</p>
          </div>
        ) : (
          <div>
            <p className="text-lg font-medium text-secondary-700">
              Drag and drop files here, or click to select
            </p>
            <p className="text-sm text-secondary-500 mt-2">
              Supported formats: PDF, DOCX, TXT
            </p>
            <p className="text-sm text-secondary-500">Maximum file size: 10 MB</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default FileDropzone
