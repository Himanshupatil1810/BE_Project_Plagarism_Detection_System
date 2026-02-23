import { useState } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'
import { ThemeProvider }         from './context/ThemeContext.jsx'
import Sidebar      from './components/Sidebar.jsx'
import Topbar       from './components/Topbar.jsx'
import Login        from './pages/Login.jsx'
import Dashboard    from './pages/Dashboard.jsx'
import ReportDetails from './pages/ReportDetails.jsx'
import History      from './pages/History.jsx'
import Verify       from './pages/Verify.jsx'

function ProtectedLayout() {
  const { user } = useAuth()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  if (!user) return <Navigate to="/login" state={{ from: location }} replace />

  return (
    <div className="flex min-h-screen" style={{ background: 'var(--bg)' }}>
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="main-content flex-1 flex flex-col">
        <Topbar
          onMenuClick={() => setSidebarOpen((o) => !o)}
          pathname={location.pathname}
        />
        <main className="flex-1">
          <Routes>
            <Route path="/"        element={<Dashboard />} />
            <Route path="/results" element={<ReportDetails />} />
            <Route path="/history" element={<History />} />
            <Route path="/verify"  element={<Verify />} />
            <Route path="*"        element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

function AuthLayout() {
  const { user } = useAuth()
  if (user) return <Navigate to="/" replace />
  return <Login />
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<AuthLayout />} />
          <Route path="/*"     element={<ProtectedLayout />} />
        </Routes>
      </AuthProvider>
    </ThemeProvider>
  )
}
