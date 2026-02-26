import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Hero from '../Hero'

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('Hero Component', () => {
  describe('Rendering', () => {
    it('should render the hero section', () => {
      renderWithRouter(<Hero />)
      const section = screen.getByRole('region', { hidden: true })
      expect(section).toBeDefined()
    })

    it('should render the main headline', () => {
      renderWithRouter(<Hero />)
      const headline = screen.getByText(/Craft Your Perfect/i)
      expect(headline).toBeDefined()
      expect(headline.textContent).toContain('Craft Your Perfect')
    })

    it('should render the secondary headline', () => {
      renderWithRouter(<Hero />)
      const secondaryHeadline = screen.getByText(/Resume & Cover Letter/i)
      expect(secondaryHeadline).toBeDefined()
    })

    it('should render the subheadline with benefits', () => {
      renderWithRouter(<Hero />)
      const subheadline = screen.getByText(/AI-powered resume and cover letter creation/i)
      expect(subheadline).toBeDefined()
      expect(subheadline.textContent).toContain('Upload your documents')
      expect(subheadline.textContent).toContain('get instant feedback')
    })

    it('should render key benefits', () => {
      renderWithRouter(<Hero />)
      expect(screen.getByText('AI-Powered Writing')).toBeDefined()
      expect(screen.getByText('Professional Templates')).toBeDefined()
      expect(screen.getByText('Instant Feedback')).toBeDefined()
    })

    it('should render trust indicators', () => {
      renderWithRouter(<Hero />)
      expect(screen.getByText('10K+')).toBeDefined()
      expect(screen.getByText('Resumes Created')).toBeDefined()
      expect(screen.getByText('98%')).toBeDefined()
      expect(screen.getByText('Success Rate')).toBeDefined()
    })
  })

  describe('CTA Buttons', () => {
    it('should render the primary CTA button', () => {
      renderWithRouter(<Hero />)
      const ctaButton = screen.getByRole('link', { name: /Get started with free registration/i })
      expect(ctaButton).toBeDefined()
      expect(ctaButton.textContent).toContain('Get Started Free')
    })

    it('should render the secondary CTA button', () => {
      renderWithRouter(<Hero />)
      const signInButton = screen.getByRole('link', { name: /Sign in to your account/i })
      expect(signInButton).toBeDefined()
      expect(signInButton.textContent).toContain('Sign In')
    })

    it('should link primary CTA to registration page', () => {
      renderWithRouter(<Hero />)
      const ctaButton = screen.getByRole('link', { name: /Get started with free registration/i })
      expect(ctaButton.getAttribute('href')).toBe('/register')
    })

    it('should link secondary CTA to login page', () => {
      renderWithRouter(<Hero />)
      const signInButton = screen.getByRole('link', { name: /Sign in to your account/i })
      expect(signInButton.getAttribute('href')).toBe('/login')
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA labels on CTA buttons', () => {
      renderWithRouter(<Hero />)
      const primaryCta = screen.getByRole('link', { name: /Get started with free registration/i })
      const secondaryCta = screen.getByRole('link', { name: /Sign in to your account/i })

      expect(primaryCta.getAttribute('aria-label')).toBe('Get started with free registration')
      expect(secondaryCta.getAttribute('aria-label')).toBe('Sign in to your account')
    })

    it('should have decorative elements marked with aria-hidden', () => {
      renderWithRouter(<Hero />)
      const container = screen.getByRole('region', { hidden: true }).parentElement
      expect(container).toBeDefined()

      const svgElements = container?.querySelectorAll('svg[aria-hidden="true"]')
      expect(svgElements && svgElements.length > 0).toBe(true)
    })

    it('should have proper heading hierarchy', () => {
      renderWithRouter(<Hero />)
      const headings = screen.getAllByRole('heading', { hidden: true })
      expect(headings.length).toBeGreaterThan(0)

      const mainHeading = headings.find(h => h.textContent?.includes('Craft Your Perfect'))
      expect(mainHeading).toBeDefined()
      expect(mainHeading?.tagName).toBe('H1')
    })
  })

  describe('Responsive Design', () => {
    it('should have responsive classes on main container', () => {
      renderWithRouter(<Hero />)
      const section = screen.getByRole('region', { hidden: true }).parentElement
      const container = section?.querySelector('.max-w-7xl')
      expect(container).toBeDefined()
      expect(container?.className).toContain('px-4')
      expect(container?.className).toContain('sm:px-6')
      expect(container?.className).toContain('lg:px-8')
    })

    it('should have responsive typography classes', () => {
      renderWithRouter(<Hero />)
      const headline = screen.getByText(/Craft Your Perfect/i)
      expect(headline.className).toContain('text-4xl')
      expect(headline.className).toContain('sm:text-5xl')
      expect(headline.className).toContain('md:text-6xl')
      expect(headline.className).toContain('lg:text-7xl')
    })

    it('should have responsive button layout', () => {
      renderWithRouter(<Hero />)
      const buttonContainer = screen.getByRole('link', { name: /Get started with free registration/i }).parentElement
      expect(buttonContainer?.className).toContain('flex-col')
      expect(buttonContainer?.className).toContain('sm:flex-row')
    })
  })

  describe('Visual Elements', () => {
    it('should render background image with proper attributes', () => {
      const { container } = renderWithRouter(<Hero />)
      const bgImage = container.querySelector('[style*="backgroundImage"]')
      expect(bgImage).toBeDefined()
      expect(bgImage?.getAttribute('style')).toContain('unsplash.com')
    })

    it('should render decorative gradient blobs', () => {
      const { container } = renderWithRouter(<Hero />)
      const blobs = container.querySelectorAll('[aria-hidden="true"]')
      expect(blobs.length).toBeGreaterThan(0)
    })

    it('should render wave decoration at bottom', () => {
      const { container } = renderWithRouter(<Hero />)
      const wave = container.querySelector('svg')
      expect(wave).toBeDefined()
    })
  })

  describe('Content Quality', () => {
    it('should have compelling value proposition', () => {
      renderWithRouter(<Hero />)
      const valueProposition = screen.getByText(/AI-powered resume and cover letter creation that helps you stand out/i)
      expect(valueProposition).toBeDefined()
    })

    it('should highlight multiple benefits', () => {
      renderWithRouter(<Hero />)
      expect(screen.getByText('AI-Powered Writing')).toBeDefined()
      expect(screen.getByText('Professional Templates')).toBeDefined()
      expect(screen.getByText('Instant Feedback')).toBeDefined()
    })

    it('should include social proof', () => {
      renderWithRouter(<Hero />)
      expect(screen.getByText(/Trusted by professionals worldwide/i)).toBeDefined()
    })
  })

  describe('Button Behavior', () => {
    it('should have hover styles on primary CTA', () => {
      renderWithRouter(<Hero />)
      const button = screen.getByRole('link', { name: /Get started with free registration/i })
      expect(button.className).toContain('hover:bg-accent-600')
      expect(button.className).toContain('hover:scale-105')
    })

    it('should have focus styles for keyboard navigation', () => {
      renderWithRouter(<Hero />)
      const button = screen.getByRole('link', { name: /Get started with free registration/i })
      expect(button.className).toContain('focus:outline-none')
      expect(button.className).toContain('focus:ring-2')
    })

    it('should have minimum width for consistent sizing', () => {
      renderWithRouter(<Hero />)
      const primaryButton = screen.getByRole('link', { name: /Get started with free registration/i })
      const secondaryButton = screen.getByRole('link', { name: /Sign in to your account/i })

      expect(primaryButton.className).toContain('min-w-[200px]')
      expect(secondaryButton.className).toContain('min-w-[200px]')
    })
  })

  describe('Animation Classes', () => {
    it('should have animation classes on main elements', () => {
      renderWithRouter(<Hero />)
      const headline = screen.getByText(/Craft Your Perfect/i)
      expect(headline.className).toContain('animate-fade-in')
    })

    it('should have staggered animations on key benefits', () => {
      const { container } = renderWithRouter(<Hero />)
      const benefitsSection = container.querySelector('.animate-fade-in.animation-delay-200')
      expect(benefitsSection).toBeDefined()
    })
  })

  describe('Icon Rendering', () => {
    it('should render checkmark icons for benefits', () => {
      const { container } = renderWithRouter(<Hero />)
      const checkmarks = container.querySelectorAll('svg path[fill-rule="evenodd"]')
      expect(checkmarks.length).toBeGreaterThan(0)
    })

    it('should render arrow icon on primary CTA', () => {
      const { container } = renderWithRouter(<Hero />)
      const primaryButton = screen.getByRole('link', { name: /Get started with free registration/i })
      const svg = primaryButton.querySelector('svg')
      expect(svg).toBeDefined()
    })
  })
})
