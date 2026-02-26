import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { AuthProvider } from './contexts/AuthContext'
import Header from './components/common/Header'
import Footer from './components/common/Footer'
import LandingPage from './pages/LandingPage'
import RegisterPage from './pages/RegisterPage'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import ProfilePage from './pages/ProfilePage'
import SettingsPage from './pages/SettingsPage'
import DocumentsPage from './pages/DocumentsPage'
import ProtectedRoute from './components/auth/ProtectedRoute'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
})

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
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AppLayout>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/documents"
              element={
                <ProtectedRoute>
                  <DocumentsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <SettingsPage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AppLayout>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
