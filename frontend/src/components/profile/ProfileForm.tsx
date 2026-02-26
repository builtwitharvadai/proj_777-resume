import { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'

interface ProfileFormData {
  full_name: string
  email: string
  bio: string
}

interface ProfileFormProps {
  onSuccess?: () => void
}

const ProfileForm = ({ onSuccess }: ProfileFormProps) => {
  const { user, refreshUser } = useAuth()
  const [formData, setFormData] = useState<ProfileFormData>({
    full_name: '',
    email: '',
    bio: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [fieldErrors, setFieldErrors] = useState<Partial<Record<keyof ProfileFormData, string>>>({})

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        email: user.email,
        bio: '',
      })

      console.warn('[ProfileForm] User data loaded', {
        userId: user.id,
        timestamp: new Date().toISOString(),
      })
    }
  }, [user])

  const validateField = (name: keyof ProfileFormData, value: string): string | null => {
    switch (name) {
      case 'full_name':
        if (!value.trim()) {
          return 'Name is required'
        }
        if (value.trim().length < 2) {
          return 'Name must be at least 2 characters long'
        }
        return null

      case 'bio':
        if (value.length > 500) {
          return 'Bio must be 500 characters or less'
        }
        return null

      default:
        return null
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))

    const fieldError = validateField(name as keyof ProfileFormData, value)
    setFieldErrors((prev) => ({ ...prev, [name]: fieldError || undefined }))

    if (error) {
      setError(null)
    }
    if (success) {
      setSuccess(false)
    }
  }

  const validateForm = (): boolean => {
    const errors: Partial<Record<keyof ProfileFormData, string>> = {}

    const nameError = validateField('full_name', formData.full_name)
    if (nameError) {
      errors.full_name = nameError
    }

    const bioError = validateField('bio', formData.bio)
    if (bioError) {
      errors.bio = bioError
    }

    setFieldErrors(errors)

    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(false)

    if (!validateForm()) {
      console.warn('[ProfileForm] Form validation failed', {
        timestamp: new Date().toISOString(),
      })
      return
    }

    try {
      setLoading(true)

      console.warn('[ProfileForm] Profile update initiated', {
        userId: user?.id,
        timestamp: new Date().toISOString(),
      })

      const response = await fetch('/api/users/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
        },
        body: JSON.stringify({
          full_name: formData.full_name.trim(),
          bio: formData.bio.trim() || null,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || errorData.message || 'Failed to update profile')
      }

      console.warn('[ProfileForm] Profile updated successfully', {
        userId: user?.id,
        timestamp: new Date().toISOString(),
      })

      await refreshUser()

      setSuccess(true)
      setError(null)

      if (onSuccess) {
        onSuccess()
      }
    } catch (err) {
      console.error('[ProfileForm] Profile update failed', {
        error: err,
        userId: user?.id,
        timestamp: new Date().toISOString(),
      })

      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Failed to update profile. Please try again.')
      }
      setSuccess(false)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6" noValidate>
      {/* Email (read-only) */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-secondary-700 mb-2">
          Email Address
        </label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          disabled
          readOnly
          className="w-full px-4 py-2 bg-secondary-100 border border-secondary-300 rounded-lg text-secondary-700 cursor-not-allowed"
          aria-readonly="true"
        />
        <p className="mt-1 text-xs text-secondary-500">Email cannot be changed</p>
      </div>

      {/* Full Name */}
      <div>
        <label htmlFor="full_name" className="block text-sm font-medium text-secondary-700 mb-2">
          Full Name <span className="text-red-500" aria-label="required">*</span>
        </label>
        <input
          type="text"
          id="full_name"
          name="full_name"
          value={formData.full_name}
          onChange={handleChange}
          disabled={loading}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors ${
            fieldErrors.full_name
              ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
              : 'border-secondary-300'
          } ${loading ? 'bg-secondary-50 cursor-not-allowed' : 'bg-white'}`}
          aria-invalid={!!fieldErrors.full_name}
          aria-describedby={fieldErrors.full_name ? 'full_name-error' : undefined}
          required
        />
        {fieldErrors.full_name && (
          <p id="full_name-error" className="mt-1 text-sm text-red-600" role="alert">
            {fieldErrors.full_name}
          </p>
        )}
      </div>

      {/* Bio */}
      <div>
        <label htmlFor="bio" className="block text-sm font-medium text-secondary-700 mb-2">
          Bio
        </label>
        <textarea
          id="bio"
          name="bio"
          value={formData.bio}
          onChange={handleChange}
          disabled={loading}
          rows={4}
          maxLength={500}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors resize-none ${
            fieldErrors.bio
              ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
              : 'border-secondary-300'
          } ${loading ? 'bg-secondary-50 cursor-not-allowed' : 'bg-white'}`}
          placeholder="Tell us about yourself..."
          aria-invalid={!!fieldErrors.bio}
          aria-describedby={fieldErrors.bio ? 'bio-error bio-hint' : 'bio-hint'}
        />
        <div className="mt-1 flex justify-between items-center">
          <div>
            {fieldErrors.bio && (
              <p id="bio-error" className="text-sm text-red-600" role="alert">
                {fieldErrors.bio}
              </p>
            )}
          </div>
          <p id="bio-hint" className="text-xs text-secondary-500">
            {formData.bio.length}/500 characters
          </p>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg" role="alert">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg" role="status">
          <p className="text-sm text-green-800">Profile updated successfully!</p>
        </div>
      )}

      {/* Submit Button */}
      <div>
        <button
          type="submit"
          disabled={loading}
          className={`w-full px-6 py-3 text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 ${
            loading
              ? 'bg-primary-400 cursor-not-allowed'
              : 'bg-primary-600 hover:bg-primary-700'
          }`}
          aria-busy={loading}
        >
          {loading ? 'Updating Profile...' : 'Update Profile'}
        </button>
      </div>
    </form>
  )
}

export default ProfileForm
