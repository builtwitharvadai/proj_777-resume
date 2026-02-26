import { useState } from 'react'

const FAQ = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(0)

  const categories = [
    {
      name: 'Resume Writing',
      faqs: [
        {
          question: 'How does the AI-powered resume writing work?',
          answer: 'Our AI analyzes your work experience, skills, and the job description to generate tailored content suggestions. It uses natural language processing to understand industry-specific terminology and creates compelling bullet points that highlight your achievements. The AI also optimizes your resume for Applicant Tracking Systems (ATS) to increase your chances of getting past initial screenings.'
        },
        {
          question: 'Can I use my own resume template?',
          answer: 'Yes! You can upload your existing resume and our platform will parse the information while maintaining your preferred style. Alternatively, you can choose from our extensive library of professional, ATS-friendly templates that are designed by career experts and regularly updated to match current hiring trends.'
        },
        {
          question: 'What file formats are supported for resumes?',
          answer: 'We support all major file formats including PDF, DOCX (Microsoft Word), and TXT. You can export your finished resume in PDF or DOCX format. PDF is recommended for final submissions, while DOCX allows for easy editing if employers request an editable version.'
        }
      ]
    },
    {
      name: 'Cover Letters',
      faqs: [
        {
          question: 'How personalized are the generated cover letters?',
          answer: 'Our AI generates highly personalized cover letters by analyzing your resume, the job description, and company information. It crafts a unique narrative that connects your experience to the specific role, includes relevant keywords, and maintains a professional yet authentic tone. You can further customize the output to match your personal writing style.'
        },
        {
          question: 'Can I save multiple cover letter templates?',
          answer: 'Absolutely! Premium users can save unlimited cover letter templates and versions. This is perfect for targeting different industries, roles, or companies. You can organize them by job type, company, or any custom category, making it easy to quickly customize and send tailored applications.'
        }
      ]
    },
    {
      name: 'Pricing & Accounts',
      faqs: [
        {
          question: 'Is there really a free plan?',
          answer: 'Yes! Our free plan gives you everything needed to create your first professional resume. You can create one complete resume, use basic templates, upload documents, and export to PDF. No credit card required. Upgrade to Premium anytime for unlimited resumes, advanced features, and AI-powered cover letters.'
        },
        {
          question: 'Can I cancel my Premium subscription anytime?',
          answer: 'Yes, you can cancel your subscription at any time with no penalties or hidden fees. Your Premium features will remain active until the end of your current billing period. We also offer a 30-day money-back guarantee if you are not completely satisfied with Premium features.'
        },
        {
          question: 'Do you offer student or bulk discounts?',
          answer: 'Yes! We offer special discounts for students (50% off Premium), recent graduates, military personnel, and non-profit organizations. For teams of 5 or more, we provide volume discounts through our Enterprise plan. Contact our sales team for custom pricing tailored to your organization needs.'
        }
      ]
    },
    {
      name: 'Features & Usage',
      faqs: [
        {
          question: 'What is the Q&A assistant feature?',
          answer: 'The Q&A assistant is your personal career advisor available 24/7. Ask questions about resume formatting, career advice, interview preparation, or how to highlight specific skills. It provides instant, personalized answers based on your profile and industry best practices. Premium users get unlimited access with priority responses.'
        },
        {
          question: 'How secure is my personal information?',
          answer: 'We take security very seriously. All data is encrypted in transit and at rest using industry-standard AES-256 encryption. We never sell or share your personal information with third parties. Your resumes and documents are stored securely in the cloud with regular backups. We are fully GDPR compliant and you can delete your data at any time.'
        },
        {
          question: 'Can I collaborate with others on my resume?',
          answer: 'Yes, Premium and Enterprise users can share their resumes with career advisors, mentors, or colleagues for feedback. Enterprise plans include full collaboration features with real-time editing, comments, and version control. You control who can view or edit your documents, and you can revoke access at any time.'
        },
        {
          question: 'Do you provide job search assistance?',
          answer: 'While our primary focus is resume and cover letter creation, Premium users get access to interview preparation tips, salary negotiation guidance, and career development resources. Our Q&A assistant can help with job search strategies, networking advice, and answer specific questions about your career path.'
        }
      ]
    }
  ]

  const toggleFaq = (index: number) => {
    setOpenIndex(openIndex === index ? null : index)
  }

  let globalIndex = 0

  return (
    <section id="faq" className="py-20 sm:py-24 lg:py-32 bg-gradient-to-br from-white to-secondary-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16 sm:mb-20">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-secondary-900 mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-lg sm:text-xl text-secondary-600 max-w-2xl mx-auto">
            Find answers to common questions about our platform, features, and pricing
          </p>
        </div>

        {/* FAQ categories */}
        <div className="space-y-12">
          {categories.map((category, categoryIndex) => (
            <div key={categoryIndex}>
              {/* Category title */}
              <h3 className="text-2xl font-bold text-secondary-900 mb-6 pb-3 border-b-2 border-primary-200">
                {category.name}
              </h3>

              {/* FAQs in category */}
              <div className="space-y-4">
                {category.faqs.map((faq) => {
                  const currentIndex = globalIndex++
                  const isOpen = openIndex === currentIndex

                  return (
                    <div
                      key={currentIndex}
                      className="bg-white rounded-xl border-2 border-secondary-100 hover:border-primary-200 transition-all duration-200 overflow-hidden shadow-sm hover:shadow-md"
                    >
                      {/* Question button */}
                      <button
                        onClick={() => toggleFaq(currentIndex)}
                        className="w-full text-left px-6 py-5 flex items-center justify-between gap-4 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-inset"
                        aria-expanded={isOpen}
                        aria-controls={`faq-answer-${currentIndex}`}
                      >
                        <span className="text-lg font-semibold text-secondary-900 pr-4">
                          {faq.question}
                        </span>
                        <svg
                          className={`w-6 h-6 text-primary-600 flex-shrink-0 transition-transform duration-200 ${
                            isOpen ? 'transform rotate-180' : ''
                          }`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                          aria-hidden="true"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 9l-7 7-7-7"
                          />
                        </svg>
                      </button>

                      {/* Answer */}
                      <div
                        id={`faq-answer-${currentIndex}`}
                        className={`transition-all duration-200 ease-in-out ${
                          isOpen
                            ? 'max-h-96 opacity-100'
                            : 'max-h-0 opacity-0 overflow-hidden'
                        }`}
                      >
                        <div className="px-6 pb-5 text-secondary-700 leading-relaxed">
                          {faq.answer}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 sm:mt-20 text-center bg-gradient-to-br from-primary-600 to-primary-700 rounded-2xl p-8 sm:p-12 shadow-xl">
          <h3 className="text-2xl sm:text-3xl font-bold text-white mb-4">
            Still Have Questions?
          </h3>
          <p className="text-primary-100 text-lg mb-8 max-w-2xl mx-auto">
            Our support team is here to help. Reach out and we'll get back to you within 24 hours.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/contact"
              className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold rounded-lg bg-white text-primary-600 hover:bg-primary-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white transform hover:scale-105 transition-all duration-200 shadow-lg"
              aria-label="Contact our support team"
            >
              Contact Support
            </a>
            <a
              href="/register"
              className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold rounded-lg bg-accent-500 text-white hover:bg-accent-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-accent-400 transform hover:scale-105 transition-all duration-200 shadow-lg"
              aria-label="Start using the platform for free"
            >
              Get Started Free
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}

export default FAQ
