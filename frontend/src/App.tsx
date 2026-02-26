import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Header from './components/common/Header'
import Footer from './components/common/Footer'
import LandingPage from './pages/LandingPage'

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

function AppLayout({ children }: { children: React.ReactNode }) {
  const location = useLocation()
  const showHeaderFooter = location.pathname === '/'

  return (
    <div className="min-h-screen flex flex-col">
      {showHeaderFooter && <Header />}
      <div className="flex-1">{children}</div>
      {showHeaderFooter && <Footer />}
    </div>
  )
}

function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppLayout>
  )
}

export default App
