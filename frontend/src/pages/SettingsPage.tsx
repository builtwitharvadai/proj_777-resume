import { useState } from 'react'
import DashboardLayout from '../components/dashboard/DashboardLayout'
import { useAuth } from '../contexts/AuthContext'

interface NotificationPreferences {
  emailNotifications: boolean
  productUpdates: boolean
  securityAlerts: boolean
}

interface PrivacySettings {
  profileVisibility: 'public' | 'private'
  dataSharing: boolean
}

const SettingsPage = () => {
  const { user } = useAuth()
  const [notificationPrefs, setNotificationPrefs] = useState<NotificationPreferences>({
    emailNotifications: true,
    productUpdates: false,
    securityAlerts: true,
  })
  const [privacySettings, setPrivacySettings] = useState<PrivacySettings>({
    profileVisibility: 'private',
    dataSharing: false,
  })
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  console.warn('[SettingsPage] Rendering settings page', {
    userId: user?.id,
    email: user?.email,
    timestamp: new Date().toISOString(),
  })

  const handleNotificationChange = (key: keyof NotificationPreferences) => {
    setNotificationPrefs((prev) => ({
      ...prev,
      [key]: !prev[key],
    }))
    if (success) setSuccess(false)
    if (error) setError(null)
  }

  const handlePrivacyChange = (key: keyof PrivacySettings, value: string | boolean) => {
    setPrivacySettings((prev) => ({
      ...prev,
      [key]: value,
    }))
    if (success) setSuccess(false)
    if (error) setError(null)
  }

  const handleSaveSettings = async () => {
    try {
      setLoading(true)
      setError(null)
      setSuccess(false)

      console.warn('[SettingsPage] Saving settings', {
        userId: user?.id,
        timestamp: new Date().toISOString(),
      })

      const response = await fetch('/api/users/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
        body: JSON.stringify({
          notification_preferences: notificationPrefs,
          privacy_settings: privacySettings,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || errorData.message || 'Failed to save settings')
      }

      console.warn('[SettingsPage] Settings saved successfully', {
        userId: user?.id,
        timestamp: new Date().toISOString(),
      })

      setSuccess(true)
    } catch (err) {
      console.error('[SettingsPage] Failed to save settings', {
        error: err,
        userId: user?.id,
        timestamp: new Date().toISOString(),
      })

      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Failed to save settings. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">Settings</h1>
          <p className="text-secondary-600">Manage your account preferences and settings</p>
        </div>

        {/* Notification Preferences */}
        <div className="bg-white rounded-xl shadow-md p-6 border border-secondary-200">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">
            Notification Preferences
          </h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-secondary-900">Email Notifications</p>
                <p className="text-sm text-secondary-600">
                  Receive email updates about your account activity
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationPrefs.emailNotifications}
                  onChange={() => handleNotificationChange('emailNotifications')}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-secondary-900">Product Updates</p>
                <p className="text-sm text-secondary-600">
                  Get notified about new features and improvements
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationPrefs.productUpdates}
                  onChange={() => handleNotificationChange('productUpdates')}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-secondary-900">Security Alerts</p>
                <p className="text-sm text-secondary-600">
                  Important notifications about your account security
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationPrefs.securityAlerts}
                  onChange={() => handleNotificationChange('securityAlerts')}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Privacy Settings */}
        <div className="bg-white rounded-xl shadow-md p-6 border border-secondary-200">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">Privacy Settings</h2>
          <div className="space-y-6">
            <div>
              <label
                htmlFor="profileVisibility"
                className="block font-medium text-secondary-900 mb-2"
              >
                Profile Visibility
              </label>
              <select
                id="profileVisibility"
                value={privacySettings.profileVisibility}
                onChange={(e) =>
                  handlePrivacyChange('profileVisibility', e.target.value as 'public' | 'private')
                }
                className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="private">Private - Only visible to you</option>
                <option value="public">Public - Visible to everyone</option>
              </select>
              <p className="mt-1 text-sm text-secondary-600">
                Control who can see your profile information
              </p>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-secondary-900">Data Sharing</p>
                <p className="text-sm text-secondary-600">
                  Allow us to use anonymized data to improve our services
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={privacySettings.dataSharing}
                  onChange={() => handlePrivacyChange('dataSharing', !privacySettings.dataSharing)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Placeholder Sections */}
        <div className="bg-white rounded-xl shadow-md p-6 border border-secondary-200">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">
            Language & Region
            <span className="ml-2 text-xs bg-secondary-100 text-secondary-600 px-2 py-1 rounded">
              Coming Soon
            </span>
          </h2>
          <p className="text-secondary-600">Set your preferred language and region settings</p>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6 border border-secondary-200">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">
            Integrations
            <span className="ml-2 text-xs bg-secondary-100 text-secondary-600 px-2 py-1 rounded">
              Coming Soon
            </span>
          </h2>
          <p className="text-secondary-600">
            Connect your account with third-party services and applications
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6 border border-secondary-200">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">
            Advanced Settings
            <span className="ml-2 text-xs bg-secondary-100 text-secondary-600 px-2 py-1 rounded">
              Coming Soon
            </span>
          </h2>
          <p className="text-secondary-600">
            Configure advanced options and developer settings
          </p>
        </div>

        {/* Messages */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg" role="alert">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {success && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg" role="status">
            <p className="text-sm text-green-800">Settings saved successfully!</p>
          </div>
        )}

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            type="button"
            onClick={handleSaveSettings}
            disabled={loading}
            className={`px-8 py-3 text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 ${
              loading ? 'bg-primary-400 cursor-not-allowed' : 'bg-primary-600 hover:bg-primary-700'
            }`}
          >
            {loading ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </DashboardLayout>
  )
}

export default SettingsPage
