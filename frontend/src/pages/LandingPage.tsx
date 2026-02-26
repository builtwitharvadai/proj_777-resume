import { useEffect } from 'react'
import Hero from '../components/landing/Hero'
import Features from '../components/landing/Features'
import Testimonials from '../components/landing/Testimonials'
import Pricing from '../components/landing/Pricing'
import FAQ from '../components/landing/FAQ'

const LandingPage = () => {
  useEffect(() => {
    document.title = 'ResumeAI - AI-Powered Resume & Cover Letter Builder'

    const metaDescription = document.querySelector('meta[name="description"]')
    if (metaDescription) {
      metaDescription.setAttribute(
        'content',
        'Create professional resumes and cover letters with AI-powered suggestions. Upload documents, get instant feedback, and land your dream job faster.'
      )
    } else {
      const meta = document.createElement('meta')
      meta.name = 'description'
      meta.content = 'Create professional resumes and cover letters with AI-powered suggestions. Upload documents, get instant feedback, and land your dream job faster.'
      document.head.appendChild(meta)
    }

    const metaKeywords = document.querySelector('meta[name="keywords"]')
    if (metaKeywords) {
      metaKeywords.setAttribute(
        'content',
        'resume builder, cover letter generator, AI resume, job application, career, professional resume, ATS-friendly, resume templates'
      )
    } else {
      const meta = document.createElement('meta')
      meta.name = 'keywords'
      meta.content = 'resume builder, cover letter generator, AI resume, job application, career, professional resume, ATS-friendly, resume templates'
      document.head.appendChild(meta)
    }

    const structuredData = {
      '@context': 'https://schema.org',
      '@type': 'WebApplication',
      name: 'ResumeAI',
      description: 'AI-powered resume and cover letter builder that helps professionals create outstanding job applications',
      applicationCategory: 'BusinessApplication',
      operatingSystem: 'Web',
      offers: {
        '@type': 'Offer',
        price: '0',
        priceCurrency: 'USD',
        description: 'Free plan available'
      },
      aggregateRating: {
        '@type': 'AggregateRating',
        ratingValue: '4.9',
        ratingCount: '10000',
        bestRating: '5',
        worstRating: '1'
      },
      author: {
        '@type': 'Organization',
        name: 'ResumeAI',
        url: window.location.origin
      }
    }

    let scriptTag = document.querySelector('script[type="application/ld+json"]')
    if (!scriptTag) {
      scriptTag = document.createElement('script')
      scriptTag.type = 'application/ld+json'
      document.head.appendChild(scriptTag)
    }
    scriptTag.textContent = JSON.stringify(structuredData)

    const canonicalLink = document.querySelector('link[rel="canonical"]')
    if (canonicalLink) {
      canonicalLink.setAttribute('href', window.location.origin)
    } else {
      const link = document.createElement('link')
      link.rel = 'canonical'
      link.href = window.location.origin
      document.head.appendChild(link)
    }

    const ogTitle = document.querySelector('meta[property="og:title"]')
    if (ogTitle) {
      ogTitle.setAttribute('content', 'ResumeAI - AI-Powered Resume & Cover Letter Builder')
    } else {
      const meta = document.createElement('meta')
      meta.setAttribute('property', 'og:title')
      meta.content = 'ResumeAI - AI-Powered Resume & Cover Letter Builder'
      document.head.appendChild(meta)
    }

    const ogDescription = document.querySelector('meta[property="og:description"]')
    if (ogDescription) {
      ogDescription.setAttribute(
        'content',
        'Create professional resumes and cover letters with AI-powered suggestions. Get instant feedback and land your dream job faster.'
      )
    } else {
      const meta = document.createElement('meta')
      meta.setAttribute('property', 'og:description')
      meta.content = 'Create professional resumes and cover letters with AI-powered suggestions. Get instant feedback and land your dream job faster.'
      document.head.appendChild(meta)
    }

    const ogType = document.querySelector('meta[property="og:type"]')
    if (ogType) {
      ogType.setAttribute('content', 'website')
    } else {
      const meta = document.createElement('meta')
      meta.setAttribute('property', 'og:type')
      meta.content = 'website'
      document.head.appendChild(meta)
    }

    return () => {
      document.title = 'Resume Builder'
    }
  }, [])

  return (
    <main className="min-h-screen">
      <Hero />
      <Features />
      <Testimonials />
      <Pricing />
      <FAQ />
    </main>
  )
}

export default LandingPage
