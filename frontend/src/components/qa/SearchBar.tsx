import { useState, useEffect, useCallback, useRef } from 'react'

interface SearchBarProps {
  onSearch: (query: string, filters: SearchFilters) => void
  onClear: () => void
  isLoading?: boolean
}

export interface SearchFilters {
  category?: string
  dateRange?: {
    from: string
    to: string
  }
}

const SearchBar = ({ onSearch, onClear, isLoading = false }: SearchBarProps) => {
  const [query, setQuery] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState<SearchFilters>({})
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1)

  const inputRef = useRef<HTMLInputElement>(null)
  const suggestionsRef = useRef<HTMLDivElement>(null)

  // Debounced search with 300ms delay
  useEffect(() => {
    if (!query.trim()) {
      setSuggestions([])
      return
    }

    const debounceTimer = setTimeout(() => {
      // Generate simple suggestions based on query
      const commonQueries = [
        'resume tips',
        'cover letter examples',
        'interview preparation',
        'career advice',
        'job search strategies',
        'salary negotiation',
      ]

      const filtered = commonQueries.filter((q) =>
        q.toLowerCase().includes(query.toLowerCase())
      )

      setSuggestions(filtered)
    }, 300)

    return () => clearTimeout(debounceTimer)
  }, [query])

  const handleSearch = useCallback(() => {
    if (query.trim()) {
      onSearch(query.trim(), filters)
      setShowSuggestions(false)
    }
  }, [query, filters, onSearch])

  const handleClear = useCallback(() => {
    setQuery('')
    setFilters({})
    setSuggestions([])
    setShowSuggestions(false)
    onClear()
  }, [onClear])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      if (selectedSuggestionIndex >= 0 && suggestions.length > 0) {
        setQuery(suggestions[selectedSuggestionIndex])
        setShowSuggestions(false)
        setSelectedSuggestionIndex(-1)
        setTimeout(() => handleSearch(), 0)
      } else {
        handleSearch()
      }
    } else if (e.key === 'Escape') {
      setShowSuggestions(false)
      setSelectedSuggestionIndex(-1)
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      if (suggestions.length > 0) {
        setShowSuggestions(true)
        setSelectedSuggestionIndex((prev) =>
          prev < suggestions.length - 1 ? prev + 1 : 0
        )
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      if (suggestions.length > 0) {
        setShowSuggestions(true)
        setSelectedSuggestionIndex((prev) =>
          prev > 0 ? prev - 1 : suggestions.length - 1
        )
      }
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion)
    setShowSuggestions(false)
    setSelectedSuggestionIndex(-1)
    setTimeout(() => {
      onSearch(suggestion, filters)
    }, 0)
  }

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        !inputRef.current?.contains(event.target as Node)
      ) {
        setShowSuggestions(false)
        setSelectedSuggestionIndex(-1)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-4">
        <div className="relative">
          <div className="flex items-center gap-2">
            <div className="flex-1 relative">
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value)
                  setShowSuggestions(true)
                  setSelectedSuggestionIndex(-1)
                }}
                onKeyDown={handleKeyDown}
                onFocus={() => {
                  if (suggestions.length > 0) {
                    setShowSuggestions(true)
                  }
                }}
                placeholder="Search conversations..."
                disabled={isLoading}
                className="w-full pl-10 pr-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-secondary-50 disabled:text-secondary-500"
                aria-label="Search conversations"
                aria-autocomplete="list"
                aria-controls="search-suggestions"
                aria-expanded={showSuggestions && suggestions.length > 0}
              />
              <svg
                className="w-5 h-5 text-secondary-400 absolute left-3 top-1/2 transform -translate-y-1/2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>

              {showSuggestions && suggestions.length > 0 && (
                <div
                  ref={suggestionsRef}
                  id="search-suggestions"
                  role="listbox"
                  className="absolute z-10 w-full mt-1 bg-white border border-secondary-200 rounded-lg shadow-lg max-h-48 overflow-y-auto"
                >
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      type="button"
                      role="option"
                      aria-selected={selectedSuggestionIndex === index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className={`w-full text-left px-4 py-2 hover:bg-secondary-50 transition-colors ${
                        selectedSuggestionIndex === index
                          ? 'bg-primary-50 text-primary-700'
                          : 'text-secondary-700'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <svg
                          className="w-4 h-4 text-secondary-400"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                          />
                        </svg>
                        <span>{suggestion}</span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            <button
              type="button"
              onClick={handleSearch}
              disabled={isLoading || !query.trim()}
              className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:bg-secondary-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              aria-label="Search"
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                  <span className="hidden sm:inline">Search</span>
                </>
              )}
            </button>

            {query && (
              <button
                type="button"
                onClick={handleClear}
                disabled={isLoading}
                className="px-3 py-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-lg transition-colors"
                aria-label="Clear search"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            )}

            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                showFilters
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100'
              }`}
              aria-label="Toggle filters"
              aria-expanded={showFilters}
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
                />
              </svg>
              <span className="hidden sm:inline">Filters</span>
            </button>
          </div>

          {showFilters && (
            <div className="mt-4 pt-4 border-t border-secondary-200">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label
                    htmlFor="category-filter"
                    className="block text-sm font-medium text-secondary-700 mb-1"
                  >
                    Category
                  </label>
                  <select
                    id="category-filter"
                    value={filters.category || ''}
                    onChange={(e) =>
                      setFilters((prev) => ({
                        ...prev,
                        category: e.target.value || undefined,
                      }))
                    }
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="">All categories</option>
                    <option value="resume_help">Resume Help</option>
                    <option value="career_advice">Career Advice</option>
                    <option value="interview_prep">Interview Prep</option>
                    <option value="job_search">Job Search</option>
                  </select>
                </div>

                <div>
                  <label
                    htmlFor="date-from"
                    className="block text-sm font-medium text-secondary-700 mb-1"
                  >
                    Date Range
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      id="date-from"
                      type="date"
                      value={filters.dateRange?.from || ''}
                      onChange={(e) =>
                        setFilters((prev) => ({
                          ...prev,
                          dateRange: {
                            from: e.target.value,
                            to: prev.dateRange?.to || '',
                          },
                        }))
                      }
                      className="flex-1 px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                    <span className="text-secondary-500">to</span>
                    <input
                      id="date-to"
                      type="date"
                      value={filters.dateRange?.to || ''}
                      onChange={(e) =>
                        setFilters((prev) => ({
                          ...prev,
                          dateRange: {
                            from: prev.dateRange?.from || '',
                            to: e.target.value,
                          },
                        }))
                      }
                      className="flex-1 px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    />
                  </div>
                </div>
              </div>

              {(filters.category || filters.dateRange?.from || filters.dateRange?.to) && (
                <button
                  type="button"
                  onClick={() => setFilters({})}
                  className="mt-3 text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  Clear filters
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default SearchBar
