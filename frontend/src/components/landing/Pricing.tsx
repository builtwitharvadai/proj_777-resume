import { Link } from 'react-router-dom'

const Pricing = () => {
  const tiers = [
    {
      id: 'free',
      name: 'Free',
      price: '$0',
      period: 'forever',
      description: 'Perfect for getting started with your first resume',
      features: [
        'Create 1 resume',
        'Basic templates',
        'Document upload',
        'PDF export',
        'Email support',
        '7-day history'
      ],
      limitations: [
        'No cover letter generation',
        'Limited AI suggestions',
        'No priority support'
      ],
      cta: 'Get Started Free',
      ctaLink: '/register',
      highlighted: false,
      popular: false
    },
    {
      id: 'premium',
      name: 'Premium',
      price: '$19',
      period: 'per month',
      description: 'Everything you need to accelerate your job search',
      features: [
        'Unlimited resumes & cover letters',
        'All premium templates',
        'Advanced AI suggestions',
        'Unlimited document uploads',
        'PDF, DOCX, TXT export',
        'Priority email support',
        'Unlimited history',
        'Q&A assistant access',
        'ATS optimization',
        'Interview prep tips',
        'Custom branding',
        'Analytics dashboard'
      ],
      limitations: [],
      cta: 'Start Premium Trial',
      ctaLink: '/register?plan=premium',
      highlighted: true,
      popular: true,
      badge: 'Most Popular'
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 'Custom',
      period: 'contact us',
      description: 'Advanced features for teams and organizations',
      features: [
        'Everything in Premium',
        'Team collaboration',
        'Admin dashboard',
        'Custom integrations',
        'Dedicated support',
        'SLA guarantee',
        'Custom templates',
        'White-label options',
        'API access',
        'Training sessions'
      ],
      limitations: [],
      cta: 'Contact Sales',
      ctaLink: '/contact',
      highlighted: false,
      popular: false
    }
  ]

  return (
    <section id="pricing" className="py-20 sm:py-24 lg:py-32 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16 sm:mb-20">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-secondary-900 mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-lg sm:text-xl text-secondary-600 max-w-3xl mx-auto">
            Choose the perfect plan for your career goals. All plans include our core features with no hidden fees.
          </p>
        </div>

        {/* Pricing cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-10">
          {tiers.map((tier) => (
            <div
              key={tier.id}
              className={`relative rounded-2xl p-8 transition-all duration-300 ${
                tier.highlighted
                  ? 'bg-gradient-to-br from-primary-600 to-primary-700 text-white shadow-2xl scale-105 border-4 border-primary-400'
                  : 'bg-white border-2 border-secondary-200 hover:border-primary-300 hover:shadow-xl'
              }`}
            >
              {/* Popular badge */}
              {tier.popular && (
                <div className="absolute -top-5 left-1/2 -translate-x-1/2">
                  <span className="inline-flex items-center px-4 py-1 rounded-full text-sm font-semibold bg-accent-500 text-white shadow-lg">
                    {tier.badge}
                  </span>
                </div>
              )}

              {/* Tier name */}
              <div className="mb-6">
                <h3
                  className={`text-2xl font-bold mb-2 ${
                    tier.highlighted ? 'text-white' : 'text-secondary-900'
                  }`}
                >
                  {tier.name}
                </h3>
                <p
                  className={`text-sm ${
                    tier.highlighted ? 'text-primary-100' : 'text-secondary-600'
                  }`}
                >
                  {tier.description}
                </p>
              </div>

              {/* Price */}
              <div className="mb-8">
                <div className="flex items-baseline gap-2">
                  <span
                    className={`text-5xl font-bold ${
                      tier.highlighted ? 'text-white' : 'text-secondary-900'
                    }`}
                  >
                    {tier.price}
                  </span>
                  <span
                    className={`text-lg ${
                      tier.highlighted ? 'text-primary-100' : 'text-secondary-600'
                    }`}
                  >
                    {tier.period}
                  </span>
                </div>
              </div>

              {/* Features list */}
              <ul className="space-y-4 mb-8">
                {tier.features.map((feature, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <svg
                      className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
                        tier.highlighted ? 'text-primary-200' : 'text-primary-600'
                      }`}
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
                    <span
                      className={`text-sm ${
                        tier.highlighted ? 'text-primary-50' : 'text-secondary-700'
                      }`}
                    >
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>

              {/* Limitations (only for free tier) */}
              {tier.limitations.length > 0 && (
                <ul className="space-y-3 mb-8 pt-6 border-t border-secondary-200">
                  {tier.limitations.map((limitation, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <svg
                        className="w-5 h-5 text-secondary-400 flex-shrink-0 mt-0.5"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                        aria-hidden="true"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                          clipRule="evenodd"
                        />
                      </svg>
                      <span className="text-sm text-secondary-600">{limitation}</span>
                    </li>
                  ))}
                </ul>
              )}

              {/* CTA button */}
              <Link
                to={tier.ctaLink}
                className={`block w-full text-center px-6 py-4 rounded-lg font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                  tier.highlighted
                    ? 'bg-white text-primary-600 hover:bg-primary-50 focus:ring-white shadow-lg hover:shadow-xl transform hover:scale-105'
                    : 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500 shadow-md hover:shadow-lg'
                }`}
                aria-label={`${tier.cta} - ${tier.name} plan`}
              >
                {tier.cta}
              </Link>
            </div>
          ))}
        </div>

        {/* Feature comparison note */}
        <div className="mt-16 text-center">
          <p className="text-secondary-600 mb-4">
            All plans include 30-day money-back guarantee
          </p>
          <div className="flex flex-wrap justify-center gap-6 text-sm text-secondary-600">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-primary-600" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>No credit card required for free plan</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-primary-600" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>Cancel anytime</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-primary-600" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>Secure payment processing</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Pricing
