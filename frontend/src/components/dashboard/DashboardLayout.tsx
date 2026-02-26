import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import Sidebar from './Sidebar'

interface DashboardLayoutProps {
  children: React.ReactNode
}

const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  console.warn('[DashboardLayout] Rendering dashboard layout', {
    userId: user?.id,
    email: user?.email,
    sidebarOpen,
    timestamp: new Date().toISOString(),
  })

  const handleLogout = async () => {
    try {
      console.warn('[DashboardLayout] Logout initiated', {
        userId: user?.id,
        timestamp: new Date().toISOString(),
      })

      await logout()

      console.warn('[DashboardLayout] Logout successful, redirecting to login', {
        timestamp: new Date().toISOString(),
      })

      navigate('/login')
    } catch (error) {
      console.error('[DashboardLayout] Logout failed', {
        error,
        userId: user?.id,
        timestamp: new Date().toISOString(),
      })

      navigate('/login')
    }
  }

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen)
    console.warn('[DashboardLayout] Sidebar toggled', {
      newState: !sidebarOpen,
      timestamp: new Date().toISOString(),
    })
  }

  return (
    <div className="min-h-screen bg-secondary-50 flex">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Header */}
        <header className="bg-white border-b border-secondary-200 sticky top-0 z-20">
          <div className="px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
            {/* Left side - Toggle button for desktop */}
            <button
              type="button"
              onClick={toggleSidebar}
              className="hidden lg:block p-2 rounded-md hover:bg-secondary-100 transition-colors"
              aria-label="Toggle sidebar"
              aria-expanded={sidebarOpen}
            >
              <span className="text-xl">{sidebarOpen ? '☰' : '☰'}</span>
            </button>

            {/* Mobile spacer */}
            <div className="lg:hidden w-12"></div>

            {/* Right side - User info and logout */}
            <div className="flex items-center space-x-4">
              {user && (
                <div className="flex items-center space-x-3">
                  {/* User info */}
                  <div className="text-right hidden sm:block">
                    <p className="text-sm font-medium text-secondary-900">
                      {user.full_name || 'User'}
                    </p>
                    <p className="text-xs text-secondary-500">{user.email}</p>
                  </div>

                  {/* Avatar */}
                  <div
                    className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center"
                    aria-label={`${user.full_name || user.email} avatar`}
                  >
                    <span className="text-primary-700 font-semibold text-lg">
                      {(user.full_name || user.email).charAt(0).toUpperCase()}
                    </span>
                  </div>

                  {/* Logout button */}
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    aria-label="Logout"
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="px-4 sm:px-6 lg:px-8 py-8">{children}</div>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-secondary-200 py-4">
          <div className="px-4 sm:px-6 lg:px-8">
            <p className="text-center text-sm text-secondary-500">
              &copy; 2024 Resume Builder. All rights reserved.
            </p>
          </div>
        </footer>
      </div>
    </div>
  )
}

export default DashboardLayout
