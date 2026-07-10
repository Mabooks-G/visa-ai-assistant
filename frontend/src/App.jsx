import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import UploadDocuments from './pages/UploadDocuments'
import AIAnalysis from './pages/AIAnalysis'
import Results from './pages/Results'
import Report from './pages/Report'
import AdminDashboard from './pages/AdminDashboard'
import { getCurrentUser } from '/src/lib/api'

function ProtectedRoute({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const location = useLocation()

  useEffect(() => {
    getCurrentUser()
      .then((data) => setUser(data.user || data))
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-accent border-t-transparent" />
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return children
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes — no sidebar */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected routes with sidebar layout */}
        <Route
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<UploadDocuments />} />
          <Route path="/analysis/:id" element={<AIAnalysis />} />
          <Route path="/results/:id" element={<Results />} />
          <Route path="/report/:id" element={<Report />} />
          <Route path="/admin" element={<AdminDashboard />} />
        </Route>

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App