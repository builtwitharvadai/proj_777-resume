import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

const RegisterForm = () => {
  const navigate = useNavigate()
  const { register, loading, error, clearError } = useAuth()

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
  })

  const [formErrors, setFormErrors] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
  })

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const validatePassword = (password: string): boolean => {
    return password.length >= 8
  }

  const validateForm = (): boolean => {
    const errors = {
      email: '',
      password: '',
      confirmPassword: '',
      fullName: '',
    }

    let isValid = true

    if (!formData.email.trim()) {
      errors.email = 'Email is required'
      isValid = false
    } else if (!validateEmail(formData.email)) {
      errors.email = 'Please enter a valid email address'
      isValid = false
    }

    if (!formData.password) {
      errors.password = 'Password is required'
      isValid = false
    } else if (!validatePassword(formData.password)) {
      errors.password = 'Password must be at least 8 characters long'
      isValid = false
    }

    if (!formData.confirmPassword) {
      errors.confirmPassword = 'Please confirm your password'
      isValid = false
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match'
      isValid = false
    }

    setFormErrors(errors)
    return isValid
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))

    setFormErrors((prev) => ({
      ...prev,
      [name]: '',
    }))

    if (error) {
      clearError()
    }
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    try {
      await register({
        email: formData.email,
        password: formData.password,
        full_name: formData.fullName.trim() || undefined,
      })

      navigate('/dashboard')
    } catch (err) {
      console.error('Registration error:', err)
    }
  }

  return (
    <div className="w-full max-w-md">
      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-lg p-8 border border-secondary-200">
        <h2 className="text-2xl font-bold text-secondary-900 mb-6 text-center">Create Your Account</h2>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg" role="alert">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <div className="space-y-5">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-secondary-700 mb-2">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={`w-full px-4 py-3 rounded-lg border ${
                formErrors.email ? 'border-red-500' : 'border-secondary-300'
              } focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors`}
              placeholder="you@example.com"
              disabled={loading}
              aria-invalid={!!formErrors.email}
              aria-describedby={formErrors.email ? 'email-error' : undefined}
            />
            {formErrors.email && (
              <p id="email-error" className="mt-1 text-sm text-red-600">
                {formErrors.email}
              </p>
            )}
          </div>

          <div>
            <label htmlFor="fullName" className="block text-sm font-medium text-secondary-700 mb-2">
              Full Name (Optional)
            </label>
            <input
              type="text"
              id="fullName"
              name="fullName"
              value={formData.fullName}
              onChange={handleChange}
              className="w-full px-4 py-3 rounded-lg border border-secondary-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
              placeholder="John Doe"
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-secondary-700 mb-2">
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={`w-full px-4 py-3 rounded-lg border ${
                formErrors.password ? 'border-red-500' : 'border-secondary-300'
              } focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors`}
              placeholder="••••••••"
              disabled={loading}
              aria-invalid={!!formErrors.password}
              aria-describedby={formErrors.password ? 'password-error' : undefined}
            />
            {formErrors.password && (
              <p id="password-error" className="mt-1 text-sm text-red-600">
                {formErrors.password}
              </p>
            )}
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-secondary-700 mb-2">
              Confirm Password
            </label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              className={`w-full px-4 py-3 rounded-lg border ${
                formErrors.confirmPassword ? 'border-red-500' : 'border-secondary-300'
              } focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors`}
              placeholder="••••••••"
              disabled={loading}
              aria-invalid={!!formErrors.confirmPassword}
              aria-describedby={formErrors.confirmPassword ? 'confirmPassword-error' : undefined}
            />
            {formErrors.confirmPassword && (
              <p id="confirmPassword-error" className="mt-1 text-sm text-red-600">
                {formErrors.confirmPassword}
              </p>
            )}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full mt-6 px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105"
        >
          {loading ? 'Creating Account...' : 'Create Account'}
        </button>

        <div className="mt-6 text-center">
          <p className="text-sm text-secondary-600">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-primary-600 hover:text-primary-700 transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </form>
    </div>
  )
}

export default RegisterForm
