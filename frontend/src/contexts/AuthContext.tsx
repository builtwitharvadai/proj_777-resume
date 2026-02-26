import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import authService, { User, LoginRequest, RegisterRequest } from '../services/auth'
import { AxiosError } from 'axios'

interface AuthContextType {
  user: User | null
  loading: boolean
  error: string | null
  isAuthenticated: boolean
  login: (credentials: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => Promise<void>
  clearError: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const clearError = () => {
    setError(null)
  }

  const loadUser = async () => {
    try {
      if (!authService.isAuthenticated()) {
        setUser(null)
        setLoading(false)
        return
      }

      console.warn('[AuthContext] Loading user', {
        timestamp: new Date().toISOString(),
      })

      const currentUser = await authService.getCurrentUser()
      setUser(currentUser)

      console.warn('[AuthContext] User loaded successfully', {
        userId: currentUser.id,
        email: currentUser.email,
        timestamp: new Date().toISOString(),
      })
    } catch (err) {
      console.error('[AuthContext] Failed to load user', {
        error: err,
        timestamp: new Date().toISOString(),
      })

      setUser(null)
      authService.getAccessToken() && authService.logout().catch(() => {
        // Silent logout on token validation failure
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUser()

    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'accessToken') {
        if (!e.newValue) {
          setUser(null)
          console.warn('[AuthContext] User logged out due to token removal', {
            timestamp: new Date().toISOString(),
          })
        } else if (!user) {
          loadUser()
        }
      }
    }

    window.addEventListener('storage', handleStorageChange)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
    }
  }, [])

  const login = async (credentials: LoginRequest) => {
    try {
      setLoading(true)
      setError(null)

      console.warn('[AuthContext] Login attempt', {
        email: credentials.email,
        timestamp: new Date().toISOString(),
      })

      const response = await authService.login(credentials)
      setUser(response.user)

      console.warn('[AuthContext] Login successful', {
        userId: response.user.id,
        email: response.user.email,
        timestamp: new Date().toISOString(),
      })
    } catch (err) {
      console.error('[AuthContext] Login failed', {
        error: err,
        timestamp: new Date().toISOString(),
      })

      const axiosError = err as AxiosError<{ detail?: string; message?: string }>

      if (axiosError.response?.status === 401) {
        setError('Invalid email or password')
      } else if (axiosError.response?.status === 422) {
        setError('Please provide valid email and password')
      } else if (axiosError.response?.status === 429) {
        setError('Too many login attempts. Please try again later')
      } else if (axiosError.response?.data?.detail) {
        setError(axiosError.response.data.detail)
      } else if (axiosError.response?.data?.message) {
        setError(axiosError.response.data.message)
      } else if (axiosError.code === 'ECONNABORTED') {
        setError('Request timeout. Please check your internet connection')
      } else if (!axiosError.response) {
        setError('Unable to connect to server. Please check your internet connection')
      } else {
        setError('Login failed. Please try again')
      }

      throw err
    } finally {
      setLoading(false)
    }
  }

  const register = async (data: RegisterRequest) => {
    try {
      setLoading(true)
      setError(null)

      console.warn('[AuthContext] Registration attempt', {
        email: data.email,
        timestamp: new Date().toISOString(),
      })

      const response = await authService.register(data)
      setUser(response.user)

      console.warn('[AuthContext] Registration successful', {
        userId: response.user.id,
        email: response.user.email,
        timestamp: new Date().toISOString(),
      })
    } catch (err) {
      console.error('[AuthContext] Registration failed', {
        error: err,
        timestamp: new Date().toISOString(),
      })

      const axiosError = err as AxiosError<{ detail?: string; message?: string }>

      if (axiosError.response?.status === 400) {
        setError('User with this email already exists')
      } else if (axiosError.response?.status === 422) {
        setError('Please provide valid registration information')
      } else if (axiosError.response?.data?.detail) {
        setError(axiosError.response.data.detail)
      } else if (axiosError.response?.data?.message) {
        setError(axiosError.response.data.message)
      } else if (axiosError.code === 'ECONNABORTED') {
        setError('Request timeout. Please check your internet connection')
      } else if (!axiosError.response) {
        setError('Unable to connect to server. Please check your internet connection')
      } else {
        setError('Registration failed. Please try again')
      }

      throw err
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    try {
      setLoading(true)
      setError(null)

      console.warn('[AuthContext] Logout attempt', {
        userId: user?.id,
        timestamp: new Date().toISOString(),
      })

      await authService.logout()
      setUser(null)

      console.warn('[AuthContext] Logout successful', {
        timestamp: new Date().toISOString(),
      })
    } catch (err) {
      console.error('[AuthContext] Logout failed', {
        error: err,
        timestamp: new Date().toISOString(),
      })

      setUser(null)

      setError('Logout failed')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const refreshUser = async () => {
    try {
      console.warn('[AuthContext] Refreshing user data', {
        userId: user?.id,
        timestamp: new Date().toISOString(),
      })

      const currentUser = await authService.getCurrentUser()
      setUser(currentUser)

      console.warn('[AuthContext] User data refreshed', {
        userId: currentUser.id,
        timestamp: new Date().toISOString(),
      })
    } catch (err) {
      console.error('[AuthContext] Failed to refresh user data', {
        error: err,
        timestamp: new Date().toISOString(),
      })
      throw err
    }
  }

  const value: AuthContextType = {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    clearError,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export default AuthContext
