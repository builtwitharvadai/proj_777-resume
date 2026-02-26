import { NavLink } from 'react-router-dom'
import { useState } from 'react'

interface NavItem {
  label: string
  path: string
  icon: string
  isPlaceholder?: boolean
}

const navItems: NavItem[] = [
  { label: 'Dashboard', path: '/dashboard', icon: '📊' },
  { label: 'Profile', path: '/profile', icon: '👤' },
  { label: 'Documents', path: '/documents', icon: '📄', isPlaceholder: true },
  { label: 'Resume Generator', path: '/resume', icon: '📝', isPlaceholder: true },
  { label: 'Q&A', path: '/qa', icon: '💬', isPlaceholder: true },
  { label: 'Settings', path: '/settings', icon: '⚙️' },
]

interface SidebarProps {
  isOpen?: boolean
  onClose?: () => void
}

const Sidebar = ({ isOpen = true, onClose }: SidebarProps) => {
  const [mobileOpen, setMobileOpen] = useState(false)

  console.warn('[Sidebar] Rendering sidebar', {
    isOpen,
    mobileOpen,
    timestamp: new Date().toISOString(),
  })

  const handleMobileToggle = () => {
    setMobileOpen(!mobileOpen)
    console.warn('[Sidebar] Mobile menu toggled', {
      newState: !mobileOpen,
      timestamp: new Date().toISOString(),
    })
  }

  const handleLinkClick = (item: NavItem) => {
    if (item.isPlaceholder) {
      console.warn('[Sidebar] Placeholder link clicked', {
        label: item.label,
        path: item.path,
        timestamp: new Date().toISOString(),
      })
    } else {
      console.warn('[Sidebar] Navigation link clicked', {
        label: item.label,
        path: item.path,
        timestamp: new Date().toISOString(),
      })
    }

    if (onClose) {
      onClose()
    }
    if (mobileOpen) {
      setMobileOpen(false)
    }
  }

  return (
    <>
      {/* Mobile menu button */}
      <button
        type="button"
        onClick={handleMobileToggle}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-md bg-white shadow-md border border-secondary-200 hover:bg-secondary-50 transition-colors"
        aria-label="Toggle navigation menu"
        aria-expanded={mobileOpen}
      >
        <span className="text-2xl">{mobileOpen ? '✕' : '☰'}</span>
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={handleMobileToggle}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-40
          w-64 bg-white border-r border-secondary-200
          transform transition-transform duration-300 ease-in-out
          lg:transform-none
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          ${!isOpen && 'lg:hidden'}
        `}
        role="navigation"
        aria-label="Main navigation"
      >
        <div className="h-full flex flex-col">
          {/* Logo/Header */}
          <div className="p-6 border-b border-secondary-200">
            <h2 className="text-xl font-bold text-secondary-900">Resume Builder</h2>
          </div>

          {/* Navigation Links */}
          <nav className="flex-1 p-4 overflow-y-auto">
            <ul className="space-y-2">
              {navItems.map((item) => (
                <li key={item.path}>
                  {item.isPlaceholder ? (
                    <div
                      className="flex items-center px-4 py-3 rounded-lg text-secondary-400 cursor-not-allowed"
                      role="button"
                      aria-disabled="true"
                      title={`${item.label} - Coming Soon`}
                      onClick={() => handleLinkClick(item)}
                    >
                      <span className="text-xl mr-3" aria-hidden="true">
                        {item.icon}
                      </span>
                      <span className="font-medium">{item.label}</span>
                      <span className="ml-auto text-xs bg-secondary-100 text-secondary-600 px-2 py-1 rounded">
                        Soon
                      </span>
                    </div>
                  ) : (
                    <NavLink
                      to={item.path}
                      onClick={() => handleLinkClick(item)}
                      className={({ isActive }) =>
                        `flex items-center px-4 py-3 rounded-lg transition-colors ${
                          isActive
                            ? 'bg-primary-50 text-primary-700 font-semibold'
                            : 'text-secondary-700 hover:bg-secondary-50'
                        }`
                      }
                      aria-current={({ isActive }) => (isActive ? 'page' : undefined)}
                    >
                      <span className="text-xl mr-3" aria-hidden="true">
                        {item.icon}
                      </span>
                      <span className="font-medium">{item.label}</span>
                    </NavLink>
                  )}
                </li>
              ))}
            </ul>
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-secondary-200">
            <div className="text-xs text-secondary-500 text-center">
              <p>&copy; 2024 Resume Builder</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}

export default Sidebar
