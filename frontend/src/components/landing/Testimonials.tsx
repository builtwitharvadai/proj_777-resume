import { useState, useEffect } from 'react'

const Testimonials = () => {
  const [currentSlide, setCurrentSlide] = useState(0)

  const testimonials = [
    {
      id: 1,
      name: 'Sarah Johnson',
      role: 'Software Engineer',
      company: 'Tech Corp',
      image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&h=150&q=80',
      rating: 5,
      quote: 'This platform transformed how I approach job applications. The AI-powered suggestions helped me land multiple interviews within weeks. The resume templates are professional and the cover letter generator is brilliant!'
    },
    {
      id: 2,
      name: 'Michael Chen',
      role: 'Marketing Manager',
      company: 'Growth Inc',
      image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&h=150&q=80',
      rating: 5,
      quote: 'I was skeptical at first, but the quality of the output exceeded my expectations. The Q&A feature answered all my resume questions and the document upload feature saved me hours of manual data entry.'
    },
    {
      id: 3,
      name: 'Emily Rodriguez',
      role: 'Product Designer',
      company: 'Creative Studio',
      image: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=150&h=150&q=80',
      rating: 5,
      quote: 'The best investment in my career! The templates are modern and ATS-friendly. I received so many compliments on my resume presentation. Got my dream job within a month of using this service.'
    },
    {
      id: 4,
      name: 'David Thompson',
      role: 'Data Scientist',
      company: 'Analytics Pro',
      image: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&h=150&q=80',
      rating: 5,
      quote: 'Outstanding tool for professionals at any career stage. The AI understands industry-specific terminology and helped me highlight my technical skills effectively. Highly recommended for anyone serious about their career.'
    },
    {
      id: 5,
      name: 'Jessica Lee',
      role: 'HR Director',
      company: 'People First',
      image: 'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=150&h=150&q=80',
      rating: 5,
      quote: 'From an HR perspective, resumes created with this tool stand out immediately. They are well-structured, professional, and optimized for our applicant tracking systems. I recommend it to all job seekers.'
    },
    {
      id: 6,
      name: 'Robert Martinez',
      role: 'Sales Executive',
      company: 'Revenue Growth',
      image: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=150&h=150&q=80',
      rating: 5,
      quote: 'Game-changer for my job search! The cover letter feature helped me personalize each application effortlessly. My response rate tripled after switching to this platform. Worth every penny!'
    }
  ]

  const itemsPerSlide = 3
  const totalSlides = Math.ceil(testimonials.length / itemsPerSlide)

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % totalSlides)
    }, 5000)

    return () => clearInterval(timer)
  }, [totalSlides])

  const goToSlide = (index: number) => {
    setCurrentSlide(index)
  }

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % totalSlides)
  }

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + totalSlides) % totalSlides)
  }

  const getVisibleTestimonials = () => {
    const start = currentSlide * itemsPerSlide
    return testimonials.slice(start, start + itemsPerSlide)
  }

  const renderStars = (rating: number) => {
    return (
      <div className="flex gap-1" aria-label={`${rating} out of 5 stars`}>
        {[...Array(5)].map((_, index) => (
          <svg
            key={index}
            className={`w-5 h-5 ${
              index < rating ? 'text-yellow-400' : 'text-secondary-300'
            }`}
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
      </div>
    )
  }

  return (
    <section className="py-20 sm:py-24 lg:py-32 bg-gradient-to-br from-secondary-50 to-primary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16 sm:mb-20">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-secondary-900 mb-4">
            Loved by Professionals Worldwide
          </h2>
          <p className="text-lg sm:text-xl text-secondary-600 max-w-3xl mx-auto">
            Join thousands of successful job seekers who transformed their careers with our platform
          </p>
        </div>

        {/* Testimonials carousel */}
        <div className="relative">
          {/* Testimonials grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {getVisibleTestimonials().map((testimonial) => (
              <div
                key={testimonial.id}
                className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow duration-300 border border-secondary-100"
              >
                {/* Rating */}
                <div className="mb-4">
                  {renderStars(testimonial.rating)}
                </div>

                {/* Quote */}
                <blockquote className="text-secondary-700 leading-relaxed mb-6">
                  &ldquo;{testimonial.quote}&rdquo;
                </blockquote>

                {/* Author */}
                <div className="flex items-center gap-4 pt-4 border-t border-secondary-100">
                  <img
                    src={testimonial.image}
                    alt={`${testimonial.name}, ${testimonial.role}`}
                    className="w-12 h-12 rounded-full object-cover"
                    loading="lazy"
                  />
                  <div>
                    <div className="font-semibold text-secondary-900">
                      {testimonial.name}
                    </div>
                    <div className="text-sm text-secondary-600">
                      {testimonial.role} at {testimonial.company}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Navigation buttons */}
          <button
            onClick={prevSlide}
            className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 lg:-translate-x-12 bg-white p-3 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 hover:bg-primary-50"
            aria-label="Previous testimonials"
          >
            <svg className="w-6 h-6 text-secondary-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            onClick={nextSlide}
            className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 lg:translate-x-12 bg-white p-3 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 hover:bg-primary-50"
            aria-label="Next testimonials"
          >
            <svg className="w-6 h-6 text-secondary-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        {/* Pagination dots */}
        <div className="flex justify-center gap-2 mt-12">
          {[...Array(totalSlides)].map((_, index) => (
            <button
              key={index}
              onClick={() => goToSlide(index)}
              className={`w-3 h-3 rounded-full transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
                index === currentSlide
                  ? 'bg-primary-600 w-8'
                  : 'bg-secondary-300 hover:bg-secondary-400'
              }`}
              aria-label={`Go to testimonial slide ${index + 1}`}
              aria-current={index === currentSlide ? 'true' : 'false'}
            />
          ))}
        </div>

        {/* Stats section */}
        <div className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-4xl font-bold text-primary-600 mb-2">10K+</div>
            <div className="text-secondary-600">Happy Users</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-primary-600 mb-2">98%</div>
            <div className="text-secondary-600">Success Rate</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-primary-600 mb-2">4.9/5</div>
            <div className="text-secondary-600">Average Rating</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-primary-600 mb-2">50K+</div>
            <div className="text-secondary-600">Resumes Created</div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Testimonials
