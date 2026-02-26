const TypingIndicator = () => {
  return (
    <div className="flex justify-start mb-4 animate-fadeIn">
      <div className="flex flex-row max-w-[80%] md:max-w-[70%]">
        <div className="flex-shrink-0 mr-3">
          <div className="w-8 h-8 rounded-full flex items-center justify-center bg-secondary-200 text-secondary-700">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
              <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" />
            </svg>
          </div>
        </div>

        <div className="flex flex-col">
          <div className="px-4 py-3 rounded-2xl bg-secondary-100 text-secondary-900 rounded-tl-sm shadow-sm">
            <div className="flex items-center gap-1">
              <span className="text-sm text-secondary-600">AI is typing</span>
              <div className="flex gap-1 ml-2">
                <span className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 mt-1 px-2">
            <span className="text-xs text-secondary-500">Just now</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TypingIndicator
