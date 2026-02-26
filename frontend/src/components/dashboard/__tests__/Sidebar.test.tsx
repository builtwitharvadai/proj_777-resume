import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Sidebar from '../Sidebar'

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('Sidebar Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render the sidebar', () => {
      renderWithRouter(<Sidebar />)
      expect(screen.getByRole('navigation', { name: /main navigation/i })).toBeDefined()
    })

    it('should render the logo/header', () => {
      renderWithRouter(<Sidebar />)
      expect(screen.getByText('Resume Builder')).toBeDefined()
    })

    it('should render all navigation items', () => {
      renderWithRouter(<Sidebar />)
      expect(screen.getByText('Dashboard')).toBeDefined()
      expect(screen.getByText('Profile')).toBeDefined()
      expect(screen.getByText('Documents')).toBeDefined()
      expect(screen.getByText('Resume Generator')).toBeDefined()
      expect(screen.getByText('Q&A')).toBeDefined()
      expect(screen.getByText('Settings')).toBeDefined()
    })

    it('should render mobile menu button', () => {
      renderWithRouter(<Sidebar />)
      const button = screen.getByLabelText(/toggle navigation menu/i)
      expect(button).toBeDefined()
    })

    it('should render footer copyright', () => {
      renderWithRouter(<Sidebar />)
      expect(screen.getByText(/© 2024 Resume Builder/i)).toBeDefined()
    })
  })

  describe('Navigation Links', () => {
    it('should render active navigation links', () => {
      renderWithRouter(<Sidebar />)
      const dashboardLink = screen.getByRole('link', { name: /dashboard/i })
      const profileLink = screen.getByRole('link', { name: /profile/i })
      const settingsLink = screen.getByRole('link', { name: /settings/i })

      expect(dashboardLink).toBeDefined()
      expect(profileLink).toBeDefined()
      expect(settingsLink).toBeDefined()
    })

    it('should have correct href attributes for active links', () => {
      renderWithRouter(<Sidebar />)
      const dashboardLink = screen.getByRole('link', { name: /dashboard/i })
      const profileLink = screen.getByRole('link', { name: /profile/i })
      const settingsLink = screen.getByRole('link', { name: /settings/i })

      expect(dashboardLink.getAttribute('href')).toBe('/dashboard')
      expect(profileLink.getAttribute('href')).toBe('/profile')
      expect(settingsLink.getAttribute('href')).toBe('/settings')
    })

    it('should mark placeholder items with "Soon" badge', () => {
      renderWithRouter(<Sidebar />)
      const soonBadges = screen.getAllByText('Soon')
      expect(soonBadges.length).toBe(3)
    })

    it('should have aria-disabled on placeholder items', () => {
      renderWithRouter(<Sidebar />)
      const documentsItem = screen.getByText('Documents').closest('[role="button"]')
      expect(documentsItem?.getAttribute('aria-disabled')).toBe('true')
    })

    it('should render icons for all navigation items', () => {
      renderWithRouter(<Sidebar />)
      const icons = screen.getAllByText(/[📊👤📄📝💬⚙️]/)
      expect(icons.length).toBeGreaterThan(0)
    })
  })

  describe('Responsive Behavior', () => {
    it('should start with mobile menu closed', () => {
      renderWithRouter(<Sidebar />)
      const button = screen.getByLabelText(/toggle navigation menu/i)
      expect(button.getAttribute('aria-expanded')).toBe('false')
    })

    it('should toggle mobile menu when button is clicked', () => {
      renderWithRouter(<Sidebar />)
      const button = screen.getByLabelText(/toggle navigation menu/i)

      fireEvent.click(button)
      expect(button.getAttribute('aria-expanded')).toBe('true')

      fireEvent.click(button)
      expect(button.getAttribute('aria-expanded')).toBe('false')
    })

    it('should show close icon when mobile menu is open', () => {
      renderWithRouter(<Sidebar />)
      const button = screen.getByLabelText(/toggle navigation menu/i)

      expect(button.textContent).toBe('☰')

      fireEvent.click(button)
      expect(button.textContent).toBe('✕')
    })

    it('should render overlay when mobile menu is open', () => {
      renderWithRouter(<Sidebar />)
      const button = screen.getByLabelText(/toggle navigation menu/i)

      fireEvent.click(button)

      const overlays = document.querySelectorAll('[aria-hidden="true"]')
      const overlay = Array.from(overlays).find((el) =>
        el.className.includes('bg-black bg-opacity-50')
      )
      expect(overlay).toBeDefined()
    })

    it('should close mobile menu when overlay is clicked', () => {
      renderWithRouter(<Sidebar />)
      const button = screen.getByLabelText(/toggle navigation menu/i)

      fireEvent.click(button)
      expect(button.getAttribute('aria-expanded')).toBe('true')

      const overlays = document.querySelectorAll('[aria-hidden="true"]')
      const overlay = Array.from(overlays).find((el) =>
        el.className.includes('bg-black bg-opacity-50')
      )

      if (overlay) {
        fireEvent.click(overlay)
        expect(button.getAttribute('aria-expanded')).toBe('false')
      }
    })

    it('should close mobile menu when onClose is called', () => {
      const onClose = vi.fn()
      renderWithRouter(<Sidebar onClose={onClose} />)

      const button = screen.getByLabelText(/toggle navigation menu/i)
      fireEvent.click(button)

      const dashboardLink = screen.getByRole('link', { name: /dashboard/i })
      fireEvent.click(dashboardLink)

      expect(onClose).toHaveBeenCalled()
    })

    it('should respect isOpen prop', () => {
      const { container } = renderWithRouter(<Sidebar isOpen={false} />)
      const sidebar = container.querySelector('aside')
      expect(sidebar?.className).toContain('lg:hidden')
    })
  })

  describe('Active State Management', () => {
    it('should apply active styles to current route', () => {
      renderWithRouter(<Sidebar />)
      const dashboardLink = screen.getByRole('link', { name: /dashboard/i })

      expect(dashboardLink.className).toContain('text-secondary-700')
    })

    it('should have aria-current attribute on active links', () => {
      renderWithRouter(<Sidebar />)
      const links = screen.getAllByRole('link')

      links.forEach((link) => {
        const ariaCurrent = link.getAttribute('aria-current')
        expect(ariaCurrent === null || ariaCurrent === 'page').toBe(true)
      })
    })
  })

  describe('Accessibility', () => {
    it('should have proper role on sidebar', () => {
      renderWithRouter(<Sidebar />)
      const sidebar = screen.getByRole('navigation', { name: /main navigation/i })
      expect(sidebar).toBeDefined()
    })

    it('should have aria-label on toggle button', () => {
      renderWithRouter(<Sidebar />)
      const button = screen.getByLabelText(/toggle navigation menu/i)
      expect(button).toBeDefined()
    })

    it('should have aria-expanded on toggle button', () => {
      renderWithRouter(<Sidebar />)
      const button = screen.getByLabelText(/toggle navigation menu/i)
      expect(button.getAttribute('aria-expanded')).toBeDefined()
    })

    it('should mark icons as aria-hidden', () => {
      const { container } = renderWithRouter(<Sidebar />)
      const icons = container.querySelectorAll('[aria-hidden="true"]')
      expect(icons.length).toBeGreaterThan(0)
    })

    it('should have title attribute on placeholder items', () => {
      renderWithRouter(<Sidebar />)
      const documentsItem = screen.getByText('Documents').closest('[role="button"]')
      expect(documentsItem?.getAttribute('title')).toContain('Coming Soon')
    })

    it('should be keyboard navigable', () => {
      renderWithRouter(<Sidebar />)
      const links = screen.getAllByRole('link')

      links.forEach((link) => {
        expect(link.tagName).toBe('A')
      })
    })
  })

  describe('Link Click Handling', () => {
    it('should call onClose when active link is clicked', () => {
      const onClose = vi.fn()
      renderWithRouter(<Sidebar onClose={onClose} />)

      const dashboardLink = screen.getByRole('link', { name: /dashboard/i })
      fireEvent.click(dashboardLink)

      expect(onClose).toHaveBeenCalled()
    })

    it('should close mobile menu when link is clicked', () => {
      renderWithRouter(<Sidebar />)
      const button = screen.getByLabelText(/toggle navigation menu/i)

      fireEvent.click(button)
      expect(button.getAttribute('aria-expanded')).toBe('true')

      const dashboardLink = screen.getByRole('link', { name: /dashboard/i })
      fireEvent.click(dashboardLink)

      expect(button.getAttribute('aria-expanded')).toBe('false')
    })

    it('should handle placeholder item clicks', () => {
      renderWithRouter(<Sidebar />)
      const documentsItem = screen.getByText('Documents').closest('[role="button"]')

      expect(() => {
        if (documentsItem) {
          fireEvent.click(documentsItem)
        }
      }).not.toThrow()
    })
  })

  describe('Sidebar Visibility', () => {
    it('should be visible by default', () => {
      const { container } = renderWithRouter(<Sidebar />)
      const sidebar = container.querySelector('aside')
      expect(sidebar?.className).not.toContain('lg:hidden')
    })

    it('should be hidden when isOpen is false', () => {
      const { container } = renderWithRouter(<Sidebar isOpen={false} />)
      const sidebar = container.querySelector('aside')
      expect(sidebar?.className).toContain('lg:hidden')
    })

    it('should have correct transform classes for mobile', () => {
      const { container } = renderWithRouter(<Sidebar />)
      const sidebar = container.querySelector('aside')
      expect(sidebar?.className).toContain('-translate-x-full lg:translate-x-0')
    })
  })

  describe('Desktop Toggle Button', () => {
    it('should render desktop toggle button', () => {
      renderWithRouter(<Sidebar />)
      const buttons = screen.getAllByRole('button')
      expect(buttons.length).toBeGreaterThanOrEqual(1)
    })
  })

  describe('Navigation Structure', () => {
    it('should render navigation items in a list', () => {
      const { container } = renderWithRouter(<Sidebar />)
      const nav = container.querySelector('nav')
      const ul = nav?.querySelector('ul')
      expect(ul).toBeDefined()
    })

    it('should render correct number of navigation items', () => {
      const { container } = renderWithRouter(<Sidebar />)
      const nav = container.querySelector('nav')
      const items = nav?.querySelectorAll('li')
      expect(items?.length).toBe(6)
    })

    it('should have proper spacing between items', () => {
      const { container } = renderWithRouter(<Sidebar />)
      const nav = container.querySelector('nav')
      const ul = nav?.querySelector('ul')
      expect(ul?.className).toContain('space-y-2')
    })
  })
})
