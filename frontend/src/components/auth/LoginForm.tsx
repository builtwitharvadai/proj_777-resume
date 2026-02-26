import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

const LoginForm = () => {
  const navigate = useNavigate()
  const { login, loading, error, clearError } = useAuth()

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false,
  })

  const [formErrors, setFormErrors] = useState({
    email: '',
    password: '',
  })

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const validateForm = (): boolean => {
    const errors = {
      email: '',
      password: '',
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
    }

    setFormErrors(errors)
    return isValid
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))

    if (name !== 'rememberMe') {
      setFormErrors((prev) => ({
        ...prev,
        [name]: '',
      }))
    }

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
      await login({
        email: formData.email,
        password: formData.password,
      })

      if (formData.rememberMe) {
        localStorage.setItem('rememberMe', 'true')
      } else {
        localStorage.removeItem('rememberMe')
      }

      navigate('/dashboard')
    } catch (err) {
      console.error('Login error:', err)
    }
  }

  return (
    <div className="w-full max-w-md">
      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-lg p-8 border border-secondary-200">
        <h2 className="text-2xl font-bold text-secondary-900 mb-6 text-center">Welcome Back</h2>

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

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="rememberMe"
                name="rememberMe"
                checked={formData.rememberMe}
                onChange={handleChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-secondary-300 rounded transition-colors"
                disabled={loading}
              />
              <label htmlFor="rememberMe" className="ml-2 block text-sm text-secondary-700">
                Remember me
              </label>
            </div>

            <div className="text-sm">
              <a
                href="#"
                className="font-medium text-primary-600 hover:text-primary-700 transition-colors"
                onClick={(e) => {
                  e.preventDefault()
                  console.warn('Password reset link clicked')
                }}
              >
                Forgot password?
              </a>
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full mt-6 px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105"
        >
          {loading ? 'Signing In...' : 'Sign In'}
        </button>

        <div className="mt-6 text-center">
          <p className="text-sm text-secondary-600">
            Don&apos;t have an account?{' '}
            <Link to="/register" className="font-medium text-primary-600 hover:text-primary-700 transition-colors">
              Sign up
            </Link>
          </p>
        </div>
      </form>
    </div>
  )
}

export default LoginForm
