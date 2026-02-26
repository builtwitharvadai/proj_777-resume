import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import DashboardLayout from '../components/dashboard/DashboardLayout'
import ProfileForm from '../components/profile/ProfileForm'
import { useAuth } from '../contexts/AuthContext'

const ProfilePage = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [showPasswordSection, setShowPasswordSection] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  })
  const [passwordError, setPasswordError] = useState<string | null>(null)
  const [passwordSuccess, setPasswordSuccess] = useState(false)
  const [passwordLoading, setPasswordLoading] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)

  console.warn('[ProfilePage] Rendering profile page', {
    userId: user?.id,
    email: user?.email,
    timestamp: new Date().toISOString(),
  })

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setPasswordData((prev) => ({ ...prev, [name]: value }))
    if (passwordError) {
      setPasswordError(null)
    }
    if (passwordSuccess) {
      setPasswordSuccess(false)
    }
  }

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setPasswordError(null)
    setPasswordSuccess(false)

    if (!passwordData.currentPassword) {
      setPasswordError('Current password is required')
      return
    }

    if (!passwordData.newPassword) {
      setPasswordError('New password is required')
      return
    }

    if (passwordData.newPassword.length < 8) {
      setPasswordError('New password must be at least 8 characters long')
      return
    }

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setPasswordError('New passwords do not match')
      return
    }

    try {
      setPasswordLoading(true)

      console.warn('[ProfilePage] Password change initiated', {
        userId: user?.id,
        timestamp: new Date().toISOString(),
      })

      const response = await fetch('/api/users/password', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
        body: JSON.stringify({
          current_password: passwordData.currentPassword,
          new_password: passwordData.newPassword,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || errorData.message || 'Failed to change password')
      }

      console.warn('[ProfilePage] Password changed successfully', {
        userId: user?.id,
        timestamp: new Date().toISOString(),
      })

      setPasswordSuccess(true)
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' })
      setShowPasswordSection(false)
    } catch (err) {
      console.error('[ProfilePage] Password change failed', {
        error: err,
        userId: user?.id,
        timestamp: new Date().toISOString(),
      })

      if (err instanceof Error) {
        setPasswordError(err.message)
      } else {
        setPasswordError('Failed to change password. Please try again.')
      }
    } finally {
      setPasswordLoading(false)
    }
  }

  const handleDeleteAccount = async () => {
    try {
      setDeleteLoading(true)

      console.warn('[ProfilePage] Account deletion initiated', {
        userId: user?.id,
        timestamp: new Date().toISOString(),
      })

      const response = await fetch('/api/users/account', {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || errorData.message || 'Failed to delete account')
      }

      console.warn('[ProfilePage] Account deleted successfully', {
        userId: user?.id,
        timestamp: new Date().toISOString(),
      })

      await logout()
      navigate('/login')
    } catch (err) {
      console.error('[ProfilePage] Account deletion failed', {
        error: err,
        userId: user?.id,
        timestamp: new Date().toISOString(),
      })

      alert('Failed to delete account. Please try again.')
    } finally {
      setDeleteLoading(false)
      setShowDeleteDialog(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">Profile Settings</h1>
          <p className="text-secondary-600">Manage your account information and preferences</p>
        </div>

        {/* Profile Information Section */}
        <div className="bg-white rounded-xl shadow-md p-6 border border-secondary-200">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">Profile Information</h2>
          <ProfileForm />
        </div>

        {/* Password Change Section */}
        <div className="bg-white rounded-xl shadow-md p-6 border border-secondary-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-secondary-900">Change Password</h2>
            {!showPasswordSection && (
              <button
                type="button"
                onClick={() => setShowPasswordSection(true)}
                className="px-4 py-2 text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors"
              >
                Change Password
              </button>
            )}
          </div>

          {showPasswordSection && (
            <form onSubmit={handlePasswordSubmit} className="space-y-4">
              <div>
                <label
                  htmlFor="currentPassword"
                  className="block text-sm font-medium text-secondary-700 mb-2"
                >
                  Current Password
                </label>
                <input
                  type="password"
                  id="currentPassword"
                  name="currentPassword"
                  value={passwordData.currentPassword}
                  onChange={handlePasswordChange}
                  disabled={passwordLoading}
                  className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  required
                />
              </div>

              <div>
                <label
                  htmlFor="newPassword"
                  className="block text-sm font-medium text-secondary-700 mb-2"
                >
                  New Password
                </label>
                <input
                  type="password"
                  id="newPassword"
                  name="newPassword"
                  value={passwordData.newPassword}
                  onChange={handlePasswordChange}
                  disabled={passwordLoading}
                  className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  required
                />
              </div>

              <div>
                <label
                  htmlFor="confirmPassword"
                  className="block text-sm font-medium text-secondary-700 mb-2"
                >
                  Confirm New Password
                </label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={passwordData.confirmPassword}
                  onChange={handlePasswordChange}
                  disabled={passwordLoading}
                  className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  required
                />
              </div>

              {passwordError && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg" role="alert">
                  <p className="text-sm text-red-800">{passwordError}</p>
                </div>
              )}

              {passwordSuccess && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg" role="status">
                  <p className="text-sm text-green-800">Password changed successfully!</p>
                </div>
              )}

              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={passwordLoading}
                  className={`flex-1 px-6 py-3 text-white font-medium rounded-lg transition-colors ${
                    passwordLoading
                      ? 'bg-primary-400 cursor-not-allowed'
                      : 'bg-primary-600 hover:bg-primary-700'
                  }`}
                >
                  {passwordLoading ? 'Updating...' : 'Update Password'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowPasswordSection(false)
                    setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' })
                    setPasswordError(null)
                    setPasswordSuccess(false)
                  }}
                  disabled={passwordLoading}
                  className="px-6 py-3 text-secondary-700 font-medium border border-secondary-300 rounded-lg hover:bg-secondary-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          {!showPasswordSection && (
            <p className="text-sm text-secondary-600">
              Keep your account secure by using a strong password
            </p>
          )}
        </div>

        {/* Danger Zone - Account Deletion */}
        <div className="bg-white rounded-xl shadow-md p-6 border border-red-200">
          <h2 className="text-xl font-semibold text-red-700 mb-2">Danger Zone</h2>
          <p className="text-secondary-600 mb-4">
            Once you delete your account, there is no going back. Please be certain.
          </p>
          <button
            type="button"
            onClick={() => setShowDeleteDialog(true)}
            className="px-6 py-3 text-white font-medium bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
          >
            Delete Account
          </button>
        </div>

        {/* Delete Confirmation Dialog */}
        {showDeleteDialog && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-dialog-title"
          >
            <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
              <h3 id="delete-dialog-title" className="text-xl font-semibold text-secondary-900 mb-4">
                Delete Account
              </h3>
              <p className="text-secondary-600 mb-6">
                Are you sure you want to delete your account? This action cannot be undone and all
                your data will be permanently deleted.
              </p>
              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={handleDeleteAccount}
                  disabled={deleteLoading}
                  className={`flex-1 px-6 py-3 text-white font-medium rounded-lg transition-colors ${
                    deleteLoading
                      ? 'bg-red-400 cursor-not-allowed'
                      : 'bg-red-600 hover:bg-red-700'
                  }`}
                >
                  {deleteLoading ? 'Deleting...' : 'Yes, Delete My Account'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowDeleteDialog(false)}
                  disabled={deleteLoading}
                  className="flex-1 px-6 py-3 text-secondary-700 font-medium border border-secondary-300 rounded-lg hover:bg-secondary-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}

export default ProfilePage
