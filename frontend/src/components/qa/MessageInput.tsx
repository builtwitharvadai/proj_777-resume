import { useState, useRef, KeyboardEvent } from 'react'
import TextareaAutosize from 'react-textarea-autosize'
import EmojiPicker, { EmojiClickData } from 'emoji-picker-react'

interface MessageInputProps {
  onSend: (message: string) => void
  disabled?: boolean
  placeholder?: string
  maxLength?: number
}

const MessageInput = ({ onSend, disabled = false, placeholder = 'Type your message...', maxLength = 2000 }: MessageInputProps) => {
  const [message, setMessage] = useState('')
  const [showEmojiPicker, setShowEmojiPicker] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    const trimmedMessage = message.trim()

    if (!trimmedMessage || disabled) {
      return
    }

    if (trimmedMessage.length > maxLength) {
      console.error('[MessageInput] Message exceeds max length', {
        length: trimmedMessage.length,
        maxLength,
        timestamp: new Date().toISOString(),
      })
      return
    }

    console.warn('[MessageInput] Sending message', {
      length: trimmedMessage.length,
      timestamp: new Date().toISOString(),
    })

    onSend(trimmedMessage)
    setMessage('')
    setShowEmojiPicker(false)

    setTimeout(() => {
      textareaRef.current?.focus()
    }, 0)
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleEmojiClick = (emojiData: EmojiClickData) => {
    const emoji = emojiData.emoji
    const textarea = textareaRef.current

    if (!textarea) {
      setMessage((prev) => prev + emoji)
      return
    }

    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const newMessage = message.slice(0, start) + emoji + message.slice(end)

    setMessage(newMessage)

    setTimeout(() => {
      const newCursorPos = start + emoji.length
      textarea.setSelectionRange(newCursorPos, newCursorPos)
      textarea.focus()
    }, 0)
  }

  const remainingChars = maxLength - message.length
  const isNearLimit = remainingChars < 100
  const isOverLimit = remainingChars < 0

  return (
    <div className="border-t border-secondary-200 bg-white p-4">
      <div className="max-w-4xl mx-auto">
        <div className="relative">
          {showEmojiPicker && (
            <div className="absolute bottom-full mb-2 right-0 z-50">
              <div className="bg-white rounded-lg shadow-xl border border-secondary-200">
                <div className="flex justify-between items-center p-2 border-b border-secondary-200">
                  <span className="text-sm font-medium text-secondary-700">Pick an emoji</span>
                  <button
                    type="button"
                    onClick={() => setShowEmojiPicker(false)}
                    className="text-secondary-500 hover:text-secondary-700 transition-colors"
                    aria-label="Close emoji picker"
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <EmojiPicker onEmojiClick={handleEmojiClick} width={320} height={400} />
              </div>
            </div>
          )}

          <div className="flex items-end gap-2">
            <div className="flex-1 relative">
              <TextareaAutosize
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={placeholder}
                disabled={disabled}
                minRows={1}
                maxRows={6}
                className={`w-full px-4 py-3 pr-12 border rounded-lg resize-none focus:outline-none focus:ring-2 transition-colors ${
                  isOverLimit
                    ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
                    : disabled
                    ? 'border-secondary-200 bg-secondary-50 text-secondary-500 cursor-not-allowed'
                    : 'border-secondary-300 focus:ring-primary-500 focus:border-primary-500'
                }`}
                aria-label="Message input"
              />

              <button
                type="button"
                onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                disabled={disabled}
                className="absolute right-3 bottom-3 text-secondary-400 hover:text-secondary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Toggle emoji picker"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 100-2 1 1 0 000 2zm7-1a1 1 0 11-2 0 1 1 0 012 0zm-.464 5.535a1 1 0 10-1.415-1.414 3 3 0 01-4.242 0 1 1 0 00-1.415 1.414 5 5 0 007.072 0z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>

            <button
              type="button"
              onClick={handleSend}
              disabled={disabled || !message.trim() || isOverLimit}
              className="px-5 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 flex items-center gap-2"
              aria-label="Send message"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              <span className="hidden sm:inline">Send</span>
            </button>
          </div>

          {isNearLimit && (
            <div className="mt-2 flex justify-between items-center">
              <div className="text-xs text-secondary-500">
                <kbd className="px-2 py-1 bg-secondary-100 rounded text-secondary-600 font-mono text-xs">Enter</kbd> to send,{' '}
                <kbd className="px-2 py-1 bg-secondary-100 rounded text-secondary-600 font-mono text-xs">Shift + Enter</kbd> for new line
              </div>
              <div className={`text-xs font-medium ${isOverLimit ? 'text-red-600' : 'text-secondary-500'}`}>
                {remainingChars} / {maxLength}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MessageInput
