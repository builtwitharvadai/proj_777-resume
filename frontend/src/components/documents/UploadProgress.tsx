import { UploadProgress as UploadProgressType } from '../../types/document'

interface UploadProgressProps {
  progress: UploadProgressType
  onCancel?: () => void
}

const UploadProgress = ({ progress, onCancel }: UploadProgressProps) => {
  const formatTime = (seconds: number): string => {
    if (seconds < 60) {
      return `${Math.round(seconds)}s`
    }
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.round(seconds % 60)
    return `${minutes}m ${remainingSeconds}s`
  }

  const getStatusColor = () => {
    switch (progress.status) {
      case 'completed':
        return 'bg-green-500'
      case 'error':
        return 'bg-red-500'
      case 'uploading':
        return 'bg-primary-500'
      default:
        return 'bg-secondary-300'
    }
  }

  const getStatusText = () => {
    switch (progress.status) {
      case 'completed':
        return 'Completed'
      case 'error':
        return 'Failed'
      case 'uploading':
        return 'Uploading...'
      default:
        return 'Idle'
    }
  }

  return (
    <div className="bg-white rounded-lg border border-secondary-200 p-4 shadow-sm">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-secondary-900 truncate">{progress.filename}</p>
          <div className="flex items-center mt-1 space-x-2">
            <p className="text-xs text-secondary-500">{getStatusText()}</p>
            {progress.status === 'uploading' && (
              <p className="text-xs text-secondary-500">{progress.progress}%</p>
            )}
            {progress.estimatedTimeRemaining !== undefined &&
              progress.status === 'uploading' &&
              progress.estimatedTimeRemaining > 0 && (
                <p className="text-xs text-secondary-500">
                  {formatTime(progress.estimatedTimeRemaining)} remaining
                </p>
              )}
          </div>
        </div>
        {onCancel && progress.status === 'uploading' && (
          <button
            onClick={onCancel}
            className="ml-2 text-secondary-400 hover:text-secondary-600 transition-colors"
            aria-label="Cancel upload"
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
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>

      <div className="w-full bg-secondary-200 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ease-out ${getStatusColor()}`}
          style={{ width: `${progress.progress}%` }}
          role="progressbar"
          aria-valuenow={progress.progress}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>

      {progress.error && (
        <div className="mt-2 flex items-start space-x-2">
          <svg
            className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5"
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
          <p className="text-xs text-red-600">{progress.error}</p>
        </div>
      )}
    </div>
  )
}

export default UploadProgress
