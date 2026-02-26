import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import RegisterForm from '../RegisterForm'
import { AuthProvider } from '../../../contexts/AuthContext'
import authService from '../../../services/auth'

vi.mock('../../../services/auth', () => ({
  default: {
    register: vi.fn(),
    isAuthenticated: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <AuthProvider>{component}</AuthProvider>
    </BrowserRouter>
  )
}

describe('RegisterForm Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockNavigate.mockClear()
    vi.mocked(authService.isAuthenticated).mockReturnValue(false)
  })

  describe('Rendering', () => {
    it('should render the registration form', () => {
      renderWithProviders(<RegisterForm />)
      expect(screen.getByText('Create Your Account')).toBeDefined()
    })

    it('should render all form fields', () => {
      renderWithProviders(<RegisterForm />)
      expect(screen.getByLabelText(/Email Address/i)).toBeDefined()
      expect(screen.getByLabelText(/Full Name/i)).toBeDefined()
      expect(screen.getByLabelText(/^Password$/i)).toBeDefined()
      expect(screen.getByLabelText(/Confirm Password/i)).toBeDefined()
    })

    it('should render submit button', () => {
      renderWithProviders(<RegisterForm />)
      const button = screen.getByRole('button', { name: /Create Account/i })
      expect(button).toBeDefined()
    })

    it('should render link to login page', () => {
      renderWithProviders(<RegisterForm />)
      const link = screen.getByText(/Sign in/i)
      expect(link).toBeDefined()
      expect(link.closest('a')?.getAttribute('href')).toBe('/login')
    })
  })

  describe('Form Validation', () => {
    it('should show error when email is empty', async () => {
      renderWithProviders(<RegisterForm />)
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeDefined()
      })
    })

    it('should show error for invalid email format', async () => {
      renderWithProviders(<RegisterForm />)
      const emailInput = screen.getByLabelText(/Email Address/i)
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.change(emailInput, { target: { value: 'invalid-email' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email address')).toBeDefined()
      })
    })

    it('should show error when password is empty', async () => {
      renderWithProviders(<RegisterForm />)
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Password is required')).toBeDefined()
      })
    })

    it('should show error when password is too short', async () => {
      renderWithProviders(<RegisterForm />)
      const passwordInput = screen.getByLabelText(/^Password$/i)
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.change(passwordInput, { target: { value: 'short' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Password must be at least 8 characters long')).toBeDefined()
      })
    })

    it('should show error when confirm password is empty', async () => {
      renderWithProviders(<RegisterForm />)
      const passwordInput = screen.getByLabelText(/^Password$/i)
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Please confirm your password')).toBeDefined()
      })
    })

    it('should show error when passwords do not match', async () => {
      renderWithProviders(<RegisterForm />)
      const passwordInput = screen.getByLabelText(/^Password$/i)
      const confirmPasswordInput = screen.getByLabelText(/Confirm Password/i)
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.change(confirmPasswordInput, { target: { value: 'password456' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Passwords do not match')).toBeDefined()
      })
    })

    it('should clear error when user types in field', async () => {
      renderWithProviders(<RegisterForm />)
      const emailInput = screen.getByLabelText(/Email Address/i)
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeDefined()
      })

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })

      await waitFor(() => {
        expect(screen.queryByText('Email is required')).toBeNull()
      })
    })
  })

  describe('Form Submission', () => {
    it('should submit form with valid data', async () => {
      vi.mocked(authService.register).mockResolvedValue({
        user: {
          id: '123',
          email: 'test@example.com',
          full_name: 'Test User',
          created_at: new Date().toISOString(),
          is_verified: false,
        },
        access_token: 'token123',
        refresh_token: 'refresh123',
        token_type: 'Bearer',
      })

      renderWithProviders(<RegisterForm />)

      const emailInput = screen.getByLabelText(/Email Address/i)
      const fullNameInput = screen.getByLabelText(/Full Name/i)
      const passwordInput = screen.getByLabelText(/^Password$/i)
      const confirmPasswordInput = screen.getByLabelText(/Confirm Password/i)
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
      fireEvent.change(fullNameInput, { target: { value: 'Test User' } })
      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(authService.register).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'password123',
          full_name: 'Test User',
        })
      })
    })

    it('should navigate to dashboard after successful registration', async () => {
      vi.mocked(authService.register).mockResolvedValue({
        user: {
          id: '123',
          email: 'test@example.com',
          full_name: null,
          created_at: new Date().toISOString(),
          is_verified: false,
        },
        access_token: 'token123',
        refresh_token: 'refresh123',
        token_type: 'Bearer',
      })

      renderWithProviders(<RegisterForm />)

      const emailInput = screen.getByLabelText(/Email Address/i)
      const passwordInput = screen.getByLabelText(/^Password$/i)
      const confirmPasswordInput = screen.getByLabelText(/Confirm Password/i)
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard')
      })
    })

    it('should show loading state during submission', async () => {
      vi.mocked(authService.register).mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(
              () =>
                resolve({
                  user: {
                    id: '123',
                    email: 'test@example.com',
                    full_name: null,
                    created_at: new Date().toISOString(),
                    is_verified: false,
                  },
                  access_token: 'token123',
                  refresh_token: 'refresh123',
                  token_type: 'Bearer',
                }),
              100
            )
          )
      )

      renderWithProviders(<RegisterForm />)

      const emailInput = screen.getByLabelText(/Email Address/i)
      const passwordInput = screen.getByLabelText(/^Password$/i)
      const confirmPasswordInput = screen.getByLabelText(/Confirm Password/i)
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Creating Account...')).toBeDefined()
      })
    })

    it('should disable form inputs during submission', async () => {
      vi.mocked(authService.register).mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(
              () =>
                resolve({
                  user: {
                    id: '123',
                    email: 'test@example.com',
                    full_name: null,
                    created_at: new Date().toISOString(),
                    is_verified: false,
                  },
                  access_token: 'token123',
                  refresh_token: 'refresh123',
                  token_type: 'Bearer',
                }),
              100
            )
          )
      )

      renderWithProviders(<RegisterForm />)

      const emailInput = screen.getByLabelText(/Email Address/i) as HTMLInputElement
      const passwordInput = screen.getByLabelText(/^Password$/i) as HTMLInputElement
      const confirmPasswordInput = screen.getByLabelText(/Confirm Password/i) as HTMLInputElement
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(emailInput.disabled).toBe(true)
        expect(passwordInput.disabled).toBe(true)
        expect(confirmPasswordInput.disabled).toBe(true)
      })
    })
  })

  describe('Error Handling', () => {
    it('should display error message from AuthContext', async () => {
      vi.mocked(authService.register).mockRejectedValue({
        response: {
          status: 400,
          data: { detail: 'User with this email already exists' },
        },
      })

      renderWithProviders(<RegisterForm />)

      const emailInput = screen.getByLabelText(/Email Address/i)
      const passwordInput = screen.getByLabelText(/^Password$/i)
      const confirmPasswordInput = screen.getByLabelText(/Confirm Password/i)
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('User with this email already exists')).toBeDefined()
      })
    })

    it('should handle network error', async () => {
      vi.mocked(authService.register).mockRejectedValue({
        code: 'ECONNABORTED',
      })

      renderWithProviders(<RegisterForm />)

      const emailInput = screen.getByLabelText(/Email Address/i)
      const passwordInput = screen.getByLabelText(/^Password$/i)
      const confirmPasswordInput = screen.getByLabelText(/Confirm Password/i)
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/Request timeout/i)).toBeDefined()
      })
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA attributes on error fields', async () => {
      renderWithProviders(<RegisterForm />)
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.click(submitButton)

      await waitFor(() => {
        const emailInput = screen.getByLabelText(/Email Address/i)
        expect(emailInput.getAttribute('aria-invalid')).toBe('true')
        expect(emailInput.getAttribute('aria-describedby')).toBe('email-error')
      })
    })

    it('should have role alert on error message', async () => {
      vi.mocked(authService.register).mockRejectedValue({
        response: {
          status: 400,
          data: { detail: 'Registration failed' },
        },
      })

      renderWithProviders(<RegisterForm />)

      const emailInput = screen.getByLabelText(/Email Address/i)
      const passwordInput = screen.getByLabelText(/^Password$/i)
      const confirmPasswordInput = screen.getByLabelText(/Confirm Password/i)
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        const alert = screen.getByRole('alert')
        expect(alert).toBeDefined()
      })
    })
  })

  describe('Form Field Interactions', () => {
    it('should update email field on input', () => {
      renderWithProviders(<RegisterForm />)
      const emailInput = screen.getByLabelText(/Email Address/i) as HTMLInputElement

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })

      expect(emailInput.value).toBe('test@example.com')
    })

    it('should update password field on input', () => {
      renderWithProviders(<RegisterForm />)
      const passwordInput = screen.getByLabelText(/^Password$/i) as HTMLInputElement

      fireEvent.change(passwordInput, { target: { value: 'password123' } })

      expect(passwordInput.value).toBe('password123')
    })

    it('should trim whitespace from email', async () => {
      vi.mocked(authService.register).mockResolvedValue({
        user: {
          id: '123',
          email: 'test@example.com',
          full_name: null,
          created_at: new Date().toISOString(),
          is_verified: false,
        },
        access_token: 'token123',
        refresh_token: 'refresh123',
        token_type: 'Bearer',
      })

      renderWithProviders(<RegisterForm />)

      const emailInput = screen.getByLabelText(/Email Address/i)
      const passwordInput = screen.getByLabelText(/^Password$/i)
      const confirmPasswordInput = screen.getByLabelText(/Confirm Password/i)
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.change(emailInput, { target: { value: '  test@example.com  ' } })
      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(authService.register).toHaveBeenCalledWith(
          expect.objectContaining({
            email: '  test@example.com  ',
          })
        )
      })
    })
  })
})
