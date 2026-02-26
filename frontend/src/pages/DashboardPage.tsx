import DashboardLayout from '../components/dashboard/DashboardLayout'
import { useAuth } from '../contexts/AuthContext'
import { Link } from 'react-router-dom'

const DashboardPage = () => {
  const { user } = useAuth()

  console.warn('[DashboardPage] Rendering dashboard', {
    userId: user?.id,
    email: user?.email,
    timestamp: new Date().toISOString(),
  })

  const quickActions = [
    {
      title: 'Edit Profile',
      description: 'Update your personal information',
      path: '/profile',
      icon: '👤',
      available: true,
    },
    {
      title: 'Upload Document',
      description: 'Add your resume or CV',
      path: '/documents',
      icon: '📄',
      available: false,
    },
    {
      title: 'Generate Resume',
      description: 'Create a professional resume',
      path: '/resume',
      icon: '📝',
      available: false,
    },
    {
      title: 'Settings',
      description: 'Manage your account preferences',
      path: '/settings',
      icon: '⚙️',
      available: true,
    },
  ]

  const statsCards = [
    {
      title: 'Documents',
      value: '0',
      description: 'Uploaded documents',
      icon: '📄',
      color: 'bg-blue-50 text-blue-700',
    },
    {
      title: 'Resumes',
      value: '0',
      description: 'Generated resumes',
      icon: '📝',
      color: 'bg-green-50 text-green-700',
    },
    {
      title: 'Q&A Sessions',
      value: '0',
      description: 'Interview preparations',
      icon: '💬',
      color: 'bg-purple-50 text-purple-700',
    },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Welcome Section */}
        <div className="bg-white rounded-xl shadow-md p-6 border border-secondary-200">
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">
            Welcome back, {user?.full_name || 'User'}!
          </h1>
          <p className="text-secondary-600">
            Here's what's happening with your resume building journey today.
          </p>
        </div>

        {/* Statistics Cards */}
        <div>
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">Your Statistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {statsCards.map((stat) => (
              <div
                key={stat.title}
                className="bg-white rounded-xl shadow-md p-6 border border-secondary-200"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-secondary-600 mb-1">{stat.title}</p>
                    <p className="text-3xl font-bold text-secondary-900 mb-2">{stat.value}</p>
                    <p className="text-xs text-secondary-500">{stat.description}</p>
                  </div>
                  <div className={`p-3 rounded-lg ${stat.color}`}>
                    <span className="text-2xl" aria-hidden="true">
                      {stat.icon}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div>
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {quickActions.map((action) => (
              <div key={action.title}>
                {action.available ? (
                  <Link
                    to={action.path}
                    className="block bg-white rounded-xl shadow-md p-6 border border-secondary-200 hover:border-primary-300 hover:shadow-lg transition-all group"
                  >
                    <div className="text-center">
                      <div className="text-4xl mb-3 group-hover:scale-110 transition-transform">
                        {action.icon}
                      </div>
                      <h3 className="text-lg font-semibold text-secondary-900 mb-2 group-hover:text-primary-700 transition-colors">
                        {action.title}
                      </h3>
                      <p className="text-sm text-secondary-600">{action.description}</p>
                    </div>
                  </Link>
                ) : (
                  <div className="block bg-white rounded-xl shadow-md p-6 border border-secondary-200 opacity-60 cursor-not-allowed">
                    <div className="text-center">
                      <div className="text-4xl mb-3">{action.icon}</div>
                      <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                        {action.title}
                      </h3>
                      <p className="text-sm text-secondary-600 mb-2">{action.description}</p>
                      <span className="inline-block text-xs bg-secondary-100 text-secondary-600 px-2 py-1 rounded">
                        Coming Soon
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity Placeholder */}
        <div className="bg-white rounded-xl shadow-md p-6 border border-secondary-200">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">Recent Activity</h2>
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📊</div>
            <p className="text-secondary-600 mb-2">No recent activity yet</p>
            <p className="text-sm text-secondary-500">
              Your recent actions and updates will appear here
            </p>
          </div>
        </div>

        {/* Getting Started Section */}
        <div className="bg-gradient-to-r from-primary-50 to-blue-50 rounded-xl shadow-md p-6 border border-primary-200">
          <h2 className="text-xl font-semibold text-secondary-900 mb-3">Getting Started</h2>
          <ul className="space-y-2 text-secondary-700">
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span>Account created successfully</span>
            </li>
            <li className="flex items-start">
              <span className="text-secondary-400 mr-2">○</span>
              <span className="text-secondary-600">
                Complete your profile information (
                <Link to="/profile" className="text-primary-600 hover:text-primary-700 underline">
                  Go to Profile
                </Link>
                )
              </span>
            </li>
            <li className="flex items-start">
              <span className="text-secondary-400 mr-2">○</span>
              <span className="text-secondary-600">Upload your first document (Coming Soon)</span>
            </li>
            <li className="flex items-start">
              <span className="text-secondary-400 mr-2">○</span>
              <span className="text-secondary-600">Generate your first resume (Coming Soon)</span>
            </li>
          </ul>
        </div>
      </div>
    </DashboardLayout>
  )
}

export default DashboardPage
