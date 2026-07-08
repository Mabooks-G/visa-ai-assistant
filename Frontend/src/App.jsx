import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import UploadDocuments from './pages/UploadDocuments'
import AIAnalysis from './pages/AIAnalysis'
import Results from './pages/Results'
import Report from './pages/Report'
import AdminDashboard from './pages/AdminDashboard'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* All routes use the sidebar layout */}
        <Route element={<Layout />}>
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
