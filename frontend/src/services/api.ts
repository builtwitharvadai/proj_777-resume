import axios, { AxiosError, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

let isRefreshing = false
let refreshSubscribers: ((token: string) => void)[] = []

const subscribeTokenRefresh = (callback: (token: string) => void) => {
  refreshSubscribers.push(callback)
}

const onTokenRefreshed = (token: string) => {
  refreshSubscribers.forEach((callback) => callback(token))
  refreshSubscribers = []
}

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('accessToken')

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    const correlationId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    if (config.headers) {
      config.headers['X-Correlation-ID'] = correlationId
    }

    console.warn(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
      correlationId,
      timestamp: new Date().toISOString(),
    })

    return config
  },
  (error: AxiosError) => {
    console.error('[API Request Error]', {
      message: error.message,
      code: error.code,
      timestamp: new Date().toISOString(),
    })
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.warn(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
      status: response.status,
      timestamp: new Date().toISOString(),
    })
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }

    console.error('[API Response Error]', {
      url: originalRequest?.url,
      status: error.response?.status,
      message: error.message,
      timestamp: new Date().toISOString(),
    })

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve) => {
          subscribeTokenRefresh((token: string) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`
            }
            resolve(api(originalRequest))
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const refreshToken = localStorage.getItem('refreshToken')

        if (!refreshToken) {
          throw new Error('No refresh token available')
        }

        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        })

        const { access_token, refresh_token: newRefreshToken } = response.data

        localStorage.setItem('accessToken', access_token)
        if (newRefreshToken) {
          localStorage.setItem('refreshToken', newRefreshToken)
        }

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`
        }

        onTokenRefreshed(access_token)
        isRefreshing = false

        console.warn('[Token Refresh] Successfully refreshed access token', {
          timestamp: new Date().toISOString(),
        })

        return api(originalRequest)
      } catch (refreshError) {
        isRefreshing = false
        refreshSubscribers = []

        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')

        console.error('[Token Refresh] Failed to refresh token', {
          error: refreshError,
          timestamp: new Date().toISOString(),
        })

        window.location.href = '/login'

        return Promise.reject(refreshError)
      }
    }

    if (error.response?.status === 403) {
      console.error('[Authorization Error] Access forbidden', {
        url: originalRequest?.url,
        timestamp: new Date().toISOString(),
      })
    }

    if (error.response?.status === 404) {
      console.error('[Not Found] Resource not found', {
        url: originalRequest?.url,
        timestamp: new Date().toISOString(),
      })
    }

    if (error.response?.status && error.response.status >= 500) {
      console.error('[Server Error] Internal server error', {
        url: originalRequest?.url,
        status: error.response.status,
        timestamp: new Date().toISOString(),
      })
    }

    if (error.code === 'ECONNABORTED') {
      console.error('[Timeout Error] Request timeout', {
        url: originalRequest?.url,
        timestamp: new Date().toISOString(),
      })
    }

    if (!error.response) {
      console.error('[Network Error] No response received', {
        message: error.message,
        timestamp: new Date().toISOString(),
      })
    }

    return Promise.reject(error)
  }
)

export const setAuthToken = (token: string | null) => {
  if (token) {
    localStorage.setItem('accessToken', token)
    console.warn('[Auth] Access token set', {
      timestamp: new Date().toISOString(),
    })
  } else {
    localStorage.removeItem('accessToken')
    console.warn('[Auth] Access token removed', {
      timestamp: new Date().toISOString(),
    })
  }
}

export const setRefreshToken = (token: string | null) => {
  if (token) {
    localStorage.setItem('refreshToken', token)
    console.warn('[Auth] Refresh token set', {
      timestamp: new Date().toISOString(),
    })
  } else {
    localStorage.removeItem('refreshToken')
    console.warn('[Auth] Refresh token removed', {
      timestamp: new Date().toISOString(),
    })
  }
}

export const clearTokens = () => {
  localStorage.removeItem('accessToken')
  localStorage.removeItem('refreshToken')
  console.warn('[Auth] All tokens cleared', {
    timestamp: new Date().toISOString(),
  })
}

export default api
