import api, { setAuthToken, setRefreshToken, clearTokens } from './api'

export interface RegisterRequest {
  email: string
  password: string
  full_name?: string
}

export interface RegisterResponse {
  user: {
    id: string
    email: string
    full_name: string | null
    created_at: string
    is_verified: boolean
  }
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  user: {
    id: string
    email: string
    full_name: string | null
    is_verified: boolean
  }
  access_token: string
  refresh_token: string
  token_type: string
}

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface RefreshTokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface VerifyEmailRequest {
  token: string
}

export interface VerifyEmailResponse {
  message: string
  user: {
    id: string
    email: string
    is_verified: boolean
  }
}

export interface User {
  id: string
  email: string
  full_name: string | null
  is_verified: boolean
  created_at?: string
}

export const authService = {
  async register(data: RegisterRequest): Promise<RegisterResponse> {
    try {
      console.warn('[Auth Service] Register request initiated', {
        email: data.email,
        timestamp: new Date().toISOString(),
      })

      const response = await api.post<RegisterResponse>('/auth/register', {
        email: data.email.trim().toLowerCase(),
        password: data.password,
        full_name: data.full_name?.trim() || null,
      })

      if (response.data.access_token && response.data.refresh_token) {
        setAuthToken(response.data.access_token)
        setRefreshToken(response.data.refresh_token)

        console.warn('[Auth Service] Registration successful', {
          userId: response.data.user.id,
          email: response.data.user.email,
          timestamp: new Date().toISOString(),
        })
      }

      return response.data
    } catch (error) {
      console.error('[Auth Service] Registration failed', {
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  async login(data: LoginRequest): Promise<LoginResponse> {
    try {
      console.warn('[Auth Service] Login request initiated', {
        email: data.email,
        timestamp: new Date().toISOString(),
      })

      const response = await api.post<LoginResponse>('/auth/login', {
        email: data.email.trim().toLowerCase(),
        password: data.password,
      })

      if (response.data.access_token && response.data.refresh_token) {
        setAuthToken(response.data.access_token)
        setRefreshToken(response.data.refresh_token)

        console.warn('[Auth Service] Login successful', {
          userId: response.data.user.id,
          email: response.data.user.email,
          timestamp: new Date().toISOString(),
        })
      }

      return response.data
    } catch (error) {
      console.error('[Auth Service] Login failed', {
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  async logout(): Promise<void> {
    try {
      console.warn('[Auth Service] Logout request initiated', {
        timestamp: new Date().toISOString(),
      })

      const refreshToken = localStorage.getItem('refreshToken')

      if (refreshToken) {
        await api.post('/auth/logout', {
          refresh_token: refreshToken,
        })
      }

      clearTokens()

      console.warn('[Auth Service] Logout successful', {
        timestamp: new Date().toISOString(),
      })
    } catch (error) {
      console.error('[Auth Service] Logout failed', {
        error,
        timestamp: new Date().toISOString(),
      })

      clearTokens()

      throw error
    }
  },

  async refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
    try {
      console.warn('[Auth Service] Token refresh request initiated', {
        timestamp: new Date().toISOString(),
      })

      const response = await api.post<RefreshTokenResponse>('/auth/refresh', {
        refresh_token: refreshToken,
      })

      if (response.data.access_token && response.data.refresh_token) {
        setAuthToken(response.data.access_token)
        setRefreshToken(response.data.refresh_token)

        console.warn('[Auth Service] Token refresh successful', {
          timestamp: new Date().toISOString(),
        })
      }

      return response.data
    } catch (error) {
      console.error('[Auth Service] Token refresh failed', {
        error,
        timestamp: new Date().toISOString(),
      })

      clearTokens()

      throw error
    }
  },

  async verifyEmail(token: string): Promise<VerifyEmailResponse> {
    try {
      console.warn('[Auth Service] Email verification request initiated', {
        timestamp: new Date().toISOString(),
      })

      const response = await api.post<VerifyEmailResponse>('/auth/verify-email', {
        token,
      })

      console.warn('[Auth Service] Email verification successful', {
        userId: response.data.user.id,
        email: response.data.user.email,
        timestamp: new Date().toISOString(),
      })

      return response.data
    } catch (error) {
      console.error('[Auth Service] Email verification failed', {
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  async getCurrentUser(): Promise<User> {
    try {
      console.warn('[Auth Service] Get current user request initiated', {
        timestamp: new Date().toISOString(),
      })

      const response = await api.get<User>('/auth/me')

      console.warn('[Auth Service] Get current user successful', {
        userId: response.data.id,
        email: response.data.email,
        timestamp: new Date().toISOString(),
      })

      return response.data
    } catch (error) {
      console.error('[Auth Service] Get current user failed', {
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  isAuthenticated(): boolean {
    const token = localStorage.getItem('accessToken')
    return !!token
  },

  getAccessToken(): string | null {
    return localStorage.getItem('accessToken')
  },

  getRefreshToken(): string | null {
    return localStorage.getItem('refreshToken')
  },
}

export default authService
