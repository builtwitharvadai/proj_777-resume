import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import RegisterForm from '../components/auth/RegisterForm'

const RegisterPage = () => {
  useEffect(() => {
    document.title = 'Create Account - ResumeAI'

    const metaDescription = document.querySelector('meta[name="description"]')
    if (metaDescription) {
      metaDescription.setAttribute(
        'content',
        'Create your free ResumeAI account and start building professional resumes with AI-powered assistance.'
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
          <p className="mt-2 text-secondary-600">Join thousands of professionals</p>
        </div>

        <RegisterForm />

        <div className="mt-8 text-center">
          <p className="text-xs text-secondary-500">
            By creating an account, you agree to our{' '}
            <a href="#" className="text-primary-600 hover:text-primary-700">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="#" className="text-primary-600 hover:text-primary-700">
              Privacy Policy
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
