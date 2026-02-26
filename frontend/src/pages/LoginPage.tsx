import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import LoginForm from '../components/auth/LoginForm'

const LoginPage = () => {
  useEffect(() => {
    document.title = 'Sign In - ResumeAI'

    const metaDescription = document.querySelector('meta[name="description"]')
    if (metaDescription) {
      metaDescription.setAttribute(
        'content',
        'Sign in to your ResumeAI account to access your resumes and continue building your professional profile.'
      )
    }
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-secondary-50 to-accent-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="absolute inset-0 overflow-hidden" aria-hidden="true">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-accent-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-secondary-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-block">
            <h1 className="text-3xl font-bold text-secondary-900">
              Resume<span className="text-primary-600">AI</span>
            </h1>
          </Link>
          <p className="mt-2 text-secondary-600">Sign in to your account</p>
        </div>

        <LoginForm />

        <div className="mt-8 text-center">
          <p className="text-sm text-secondary-500">
            Need help?{' '}
            <a href="#" className="text-primary-600 hover:text-primary-700">
              Contact Support
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
