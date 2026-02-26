const Features = () => {
  const features = [
    {
      id: 'resume-writing',
      icon: (
        <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      title: 'AI-Powered Resume Writing',
      description: 'Create professional resumes with intelligent suggestions and industry-standard templates. Our AI analyzes your experience and optimizes every section for maximum impact.',
      benefits: [
        'Smart content suggestions',
        'ATS-friendly formatting',
        'Multiple professional templates',
        'Real-time optimization tips'
      ]
    },
    {
      id: 'cover-letter',
      icon: (
        <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
      title: 'Cover Letter Generation',
      description: 'Generate compelling cover letters tailored to each job application. Our AI crafts personalized narratives that highlight your unique qualifications and enthusiasm.',
      benefits: [
        'Job-specific customization',
        'Professional tone and structure',
        'Keyword optimization',
        'Multiple style options'
      ]
    },
    {
      id: 'document-upload',
      icon: (
        <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      ),
      title: 'Smart Document Upload',
      description: 'Upload your existing documents and let our AI extract and organize your information. Supports multiple formats including PDF, DOCX, and TXT.',
      benefits: [
        'Multi-format support',
        'Intelligent data extraction',
        'Secure cloud storage',
        'Instant parsing and analysis'
      ]
    },
    {
      id: 'qa-assistant',
      icon: (
        <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      ),
      title: 'Interactive Q&A Assistant',
      description: 'Get instant answers to your resume and career questions. Our AI assistant provides personalized guidance, suggestions, and best practices based on your specific situation.',
      benefits: [
        '24/7 expert guidance',
        'Personalized recommendations',
        'Industry-specific advice',
        'Interview preparation tips'
      ]
    }
  ]

  return (
    <section id="features" className="py-20 sm:py-24 lg:py-32 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16 sm:mb-20">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-secondary-900 mb-4">
            Everything You Need to Succeed
          </h2>
          <p className="text-lg sm:text-xl text-secondary-600 max-w-3xl mx-auto">
            Powerful features designed to help you create outstanding resumes and cover letters that get noticed by employers
          </p>
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-12">
          {features.map((feature, index) => (
            <div
              key={feature.id}
              className="group relative bg-gradient-to-br from-white to-primary-50 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border border-primary-100"
              style={{
                animationDelay: `${index * 100}ms`
              }}
            >
              {/* Icon */}
              <div className="flex items-center justify-center w-16 h-16 rounded-xl bg-primary-600 text-white mb-6 group-hover:scale-110 transition-transform duration-300 shadow-md">
                {feature.icon}
              </div>

              {/* Title */}
              <h3 className="text-2xl font-bold text-secondary-900 mb-4">
                {feature.title}
              </h3>

              {/* Description */}
              <p className="text-secondary-700 leading-relaxed mb-6">
                {feature.description}
              </p>

              {/* Benefits list */}
              <ul className="space-y-3">
                {feature.benefits.map((benefit, benefitIndex) => (
                  <li key={benefitIndex} className="flex items-start gap-3">
                    <svg
                      className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                      aria-hidden="true"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <span className="text-secondary-700 text-sm sm:text-base">{benefit}</span>
                  </li>
                ))}
              </ul>

              {/* Decorative gradient overlay */}
              <div
                className="absolute inset-0 bg-gradient-to-br from-primary-600 to-accent-600 rounded-2xl opacity-0 group-hover:opacity-5 transition-opacity duration-300 pointer-events-none"
                aria-hidden="true"
              />
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 sm:mt-20 text-center">
          <p className="text-lg text-secondary-700 mb-6">
            Ready to experience these powerful features?
          </p>
          <a
            href="/register"
            className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold rounded-lg bg-primary-600 text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
            aria-label="Start creating your resume for free"
          >
            Start Creating for Free
            <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </a>
        </div>
      </div>
    </section>
  )
}

export default Features
