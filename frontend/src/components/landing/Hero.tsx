import { Link } from 'react-router-dom'

const Hero = () => {
  return (
    <section className="relative bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 text-white overflow-hidden">
      {/* Background image overlay */}
      <div
        className="absolute inset-0 opacity-10 bg-cover bg-center"
        style={{
          backgroundImage: 'url(https://images.unsplash.com/photo-1586281380349-632531db7ed4?auto=format&fit=crop&w=2000&q=80)',
        }}
        aria-hidden="true"
      />

      {/* Decorative elements */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-primary-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob" aria-hidden="true" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-accent-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000" aria-hidden="true" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28 lg:py-36">
        <div className="text-center">
          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight mb-6 animate-fade-in">
            <span className="block">Craft Your Perfect</span>
            <span className="block text-accent-300">Resume & Cover Letter</span>
          </h1>

          {/* Subheadline */}
          <p className="mt-6 max-w-3xl mx-auto text-lg sm:text-xl md:text-2xl text-primary-100 leading-relaxed animate-fade-in animation-delay-100">
            AI-powered resume and cover letter creation that helps you stand out.
            Upload your documents, get instant feedback, and land your dream job faster.
          </p>

          {/* Key benefits */}
          <div className="mt-10 flex flex-wrap justify-center gap-6 text-sm sm:text-base text-primary-100 animate-fade-in animation-delay-200">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-accent-300" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>AI-Powered Writing</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-accent-300" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>Professional Templates</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-accent-300" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>Instant Feedback</span>
            </div>
          </div>

          {/* CTA Button */}
          <div className="mt-12 flex flex-col sm:flex-row gap-4 justify-center items-center animate-fade-in animation-delay-300">
            <Link
              to="/register"
              className="inline-flex items-center justify-center px-8 py-4 text-base sm:text-lg font-semibold rounded-lg bg-accent-500 text-white hover:bg-accent-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-accent-400 transform hover:scale-105 transition-all duration-200 shadow-xl hover:shadow-2xl min-w-[200px]"
              aria-label="Get started with free registration"
            >
              Get Started Free
              <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center justify-center px-8 py-4 text-base sm:text-lg font-semibold rounded-lg bg-white bg-opacity-10 backdrop-blur-sm text-white hover:bg-opacity-20 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white transform hover:scale-105 transition-all duration-200 border-2 border-white border-opacity-30 min-w-[200px]"
              aria-label="Sign in to your account"
            >
              Sign In
            </Link>
          </div>

          {/* Trust indicators */}
          <div className="mt-12 animate-fade-in animation-delay-400">
            <p className="text-sm text-primary-200 mb-4">Trusted by professionals worldwide</p>
            <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
              <div className="text-2xl font-bold">10K+</div>
              <div className="w-px h-6 bg-primary-300" aria-hidden="true" />
              <div className="text-sm">Resumes Created</div>
              <div className="w-px h-6 bg-primary-300" aria-hidden="true" />
              <div className="text-2xl font-bold">98%</div>
              <div className="w-px h-6 bg-primary-300" aria-hidden="true" />
              <div className="text-sm">Success Rate</div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom wave decoration */}
      <div className="absolute bottom-0 left-0 right-0" aria-hidden="true">
        <svg className="w-full h-16 sm:h-20 text-white" preserveAspectRatio="none" viewBox="0 0 1440 74" fill="currentColor">
          <path d="M0,32L80,37.3C160,43,320,53,480,53.3C640,53,800,43,960,42.7C1120,43,1280,53,1360,58.7L1440,64L1440,74L1360,74C1280,74,1120,74,960,74C800,74,640,74,480,74C320,74,160,74,80,74L0,74Z" />
        </svg>
      </div>
    </section>
  )
}

export default Hero
