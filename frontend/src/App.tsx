import { Routes, Route, Navigate } from 'react-router-dom'

function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <h1 className="text-5xl font-bold text-primary-900 mb-6">
          Welcome to Resume Builder
        </h1>
        <p className="text-xl text-secondary-700 mb-8">
          Create professional resumes powered by AI
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/dashboard"
            className="px-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors"
          >
            Get Started
          </a>
          <a
            href="/dashboard"
            className="px-6 py-3 bg-white text-primary-600 border-2 border-primary-600 rounded-lg font-semibold hover:bg-primary-50 transition-colors"
          >
            View Dashboard
          </a>
        </div>
      </div>
    </div>
  )
}

function DashboardPage() {
  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-secondary-900">Dashboard</h1>
          <p className="text-secondary-600 mt-2">Manage your resumes and documents</p>
        </header>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl shadow-md p-6 border border-secondary-200">
            <h3 className="text-lg font-semibold text-secondary-900 mb-2">My Resumes</h3>
            <p className="text-secondary-600">Create and manage your resumes</p>
          </div>
          <div className="bg-white rounded-xl shadow-md p-6 border border-secondary-200">
            <h3 className="text-lg font-semibold text-secondary-900 mb-2">Documents</h3>
            <p className="text-secondary-600">Upload and organize your documents</p>
          </div>
          <div className="bg-white rounded-xl shadow-md p-6 border border-secondary-200">
            <h3 className="text-lg font-semibold text-secondary-900 mb-2">Settings</h3>
            <p className="text-secondary-600">Configure your preferences</p>
          </div>
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
