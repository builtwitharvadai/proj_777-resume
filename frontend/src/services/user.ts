import api from './api'

export interface UserProfile {
  id: string
  email: string
  full_name: string | null
  bio?: string | null
  is_verified: boolean
  created_at?: string
  updated_at?: string
}

export interface UpdateProfileRequest {
  full_name?: string
  bio?: string | null
}

export interface UpdatePasswordRequest {
  current_password: string
  new_password: string
}

export interface UserSettings {
  notification_preferences: {
    emailNotifications: boolean
    productUpdates: boolean
    securityAlerts: boolean
  }
  privacy_settings: {
    profileVisibility: 'public' | 'private'
    dataSharing: boolean
  }
}

export const userService = {
  async getProfile(): Promise<UserProfile> {
    try {
      console.warn('[User Service] Get profile request initiated', {
        timestamp: new Date().toISOString(),
      })

      const response = await api.get<UserProfile>('/users/profile')

      console.warn('[User Service] Get profile successful', {
        userId: response.data.id,
        email: response.data.email,
        timestamp: new Date().toISOString(),
      })

      return response.data
    } catch (error) {
      console.error('[User Service] Get profile failed', {
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  async updateProfile(data: UpdateProfileRequest): Promise<UserProfile> {
    try {
      console.warn('[User Service] Update profile request initiated', {
        timestamp: new Date().toISOString(),
      })

      const response = await api.put<UserProfile>('/users/profile', {
        full_name: data.full_name?.trim() || null,
        bio: data.bio?.trim() || null,
      })

      console.warn('[User Service] Update profile successful', {
        userId: response.data.id,
        timestamp: new Date().toISOString(),
      })

      return response.data
    } catch (error) {
      console.error('[User Service] Update profile failed', {
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  async updatePassword(data: UpdatePasswordRequest): Promise<void> {
    try {
      console.warn('[User Service] Update password request initiated', {
        timestamp: new Date().toISOString(),
      })

      await api.put('/users/password', {
        current_password: data.current_password,
        new_password: data.new_password,
      })

      console.warn('[User Service] Update password successful', {
        timestamp: new Date().toISOString(),
      })
    } catch (error) {
      console.error('[User Service] Update password failed', {
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  async deleteAccount(): Promise<void> {
    try {
      console.warn('[User Service] Delete account request initiated', {
        timestamp: new Date().toISOString(),
      })

      await api.delete('/users/account')

      console.warn('[User Service] Delete account successful', {
        timestamp: new Date().toISOString(),
      })
    } catch (error) {
      console.error('[User Service] Delete account failed', {
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  async getSettings(): Promise<UserSettings> {
    try {
      console.warn('[User Service] Get settings request initiated', {
        timestamp: new Date().toISOString(),
      })

      const response = await api.get<UserSettings>('/users/settings')

      console.warn('[User Service] Get settings successful', {
        timestamp: new Date().toISOString(),
      })

      return response.data
    } catch (error) {
      console.error('[User Service] Get settings failed', {
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },

  async updateSettings(data: UserSettings): Promise<UserSettings> {
    try {
      console.warn('[User Service] Update settings request initiated', {
        timestamp: new Date().toISOString(),
      })

      const response = await api.put<UserSettings>('/users/settings', data)

      console.warn('[User Service] Update settings successful', {
        timestamp: new Date().toISOString(),
      })

      return response.data
    } catch (error) {
      console.error('[User Service] Update settings failed', {
        error,
        timestamp: new Date().toISOString(),
      })
      throw error
    }
  },
}

export default userService
