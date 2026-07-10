import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, Users, FileText, CheckCircle, AlertTriangle, Clock, Search, Filter, RefreshCw, ExternalLink } from 'lucide-react'
import { adminListApplications, updateApplication } from '/src/lib/api'

const statusConfig = {
  in_progress: { label: 'In Progress', class: 'bg-amber-100 text-amber-700' },
  verified: { label: 'Verified', class: 'bg-emerald-100 text-emerald-700' },
  rejected: { label: 'Rejected', class: 'bg-red-100 text-red-700' },
  needs_review: { label: 'Needs Review', class: 'bg-orange-100 text-orange-700' },
}

export default function AdminDashboard() {
  const navigate = useNavigate()
  const [applications, setApplications] = useState([])
  const [filtered, setFiltered] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [stats, setStats] = useState({
    total: 0, needsReview: 0, verified: 0, rejected: 0,
  })

  useEffect(() => {
    loadApplications()
  }, [])

  useEffect(() => {
    let result = applications
    if (search) {
      result = result.filter(a =>
        a.applicant_name?.toLowerCase().includes(search.toLowerCase()) ||
        a.visa_type?.toLowerCase().includes(search.toLowerCase())
      )
    }
    if (statusFilter !== 'all') {
      result = result.filter(a => a.status === statusFilter)
    }
    setFiltered(result)
  }, [search, statusFilter, applications])

  const loadApplications = async () => {
    const { data, error } = await adminListApplications()

    if (!error && data) {
      setApplications(data)
      setFiltered(data)
      setStats({
        total: data.length,
        needsReview: data.filter(a => a.status === 'needs_review').length,
        verified: data.filter(a => a.status === 'verified').length,
        rejected: data.filter(a => a.status === 'rejected').length,
      })
    }
    setLoading(false)
  }

  const updateStatus = async (id, newStatus) => {
    await updateApplication(id, { status: newStatus })
    loadApplications()
  }

  const getVisaLabel = (type) => {
    const labels = {
      canada_work: 'Canada Work',
      canada_student: 'Canada Student',
      germany_student: 'Germany Student',
      south_africa_work: 'SA Work',
    }
    return labels[type] || type
  }

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6">
        <h1 className="font-heading text-2xl font-bold text-foreground">Admin Dashboard</h1>
        <p className="text-secondary">Manage and review visa applications</p>
      </div>

      {/* Stats */}
      <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div className="rounded-xl border border-border bg-white p-4 shadow-sm">
          <p className="text-sm text-secondary">Total</p>
          <p className="font-heading text-2xl font-bold text-foreground">{stats.total}</p>
        </div>
        <div className="rounded-xl border border-border bg-white p-4 shadow-sm">
          <p className="flex items-center gap-1.5 text-sm text-amber-600">
            <AlertTriangle size={14} /> Needs Review
          </p>
          <p className="font-heading text-2xl font-bold text-foreground">{stats.needsReview}</p>
        </div>
        <div className="rounded-xl border border-border bg-white p-4 shadow-sm">
          <p className="flex items-center gap-1.5 text-sm text-emerald-600">
            <CheckCircle size={14} /> Verified
          </p>
          <p className="font-heading text-2xl font-bold text-foreground">{stats.verified}</p>
        </div>
        <div className="rounded-xl border border-border bg-white p-4 shadow-sm">
          <p className="flex items-center gap-1.5 text-sm text-red-600">
            <AlertTriangle size={14} /> Rejected
          </p>
          <p className="font-heading text-2xl font-bold text-foreground">{stats.rejected}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1 max-w-md">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name or visa type..."
            className="w-full rounded-lg border border-border bg-white py-2 pl-9 pr-3 text-sm focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter size={16} className="text-secondary" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border border-border bg-white px-3 py-2 text-sm focus:border-accent focus:outline-none cursor-pointer"
          >
            <option value="all">All Status</option>
            <option value="needs_review">Needs Review</option>
            <option value="in_progress">In Progress</option>
            <option value="verified">Verified</option>
            <option value="rejected">Rejected</option>
          </select>
          <button
            onClick={loadApplications}
            className="rounded-lg border border-border p-2 text-secondary hover:bg-muted transition-colors cursor-pointer"
            aria-label="Refresh"
          >
            <RefreshCw size={16} />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-border bg-white shadow-sm">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-muted/50">
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-secondary">Applicant</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-secondary">Visa Type</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-secondary">Score</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-secondary">Status</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-secondary">Date</th>
              <th className="px-4 py-3 text-right text-xs font-semibold uppercase text-secondary">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {loading ? (
              <tr>
                <td colSpan="6" className="px-4 py-12 text-center">
                  <div className="inline-block h-6 w-6 animate-spin rounded-full border-2 border-accent border-t-transparent" />
                </td>
              </tr>
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-4 py-12 text-center text-sm text-secondary">
                  No applications found
                </td>
              </tr>
            ) : (
              filtered.map((app) => (
                <tr key={app.id} className="hover:bg-muted/30 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/10 text-xs font-bold text-accent">
                        {app.applicant_name?.charAt(0) || '?'}
                      </div>
                      <span className="text-sm font-medium text-foreground">{app.applicant_name || 'Unnamed'}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-secondary">{getVisaLabel(app.visa_type)}</td>
                  <td className="px-4 py-3">
                    <span className={`font-heading text-sm font-bold ${
                      (app.overall_score || 0) >= 80 ? 'text-emerald-600' :
                      (app.overall_score || 0) >= 50 ? 'text-amber-600' :
                      'text-red-600'
                    }`}>
                      {app.overall_score || 0}%
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                      statusConfig[app.status]?.class || 'bg-gray-100 text-gray-700'
                    }`}>
                      {statusConfig[app.status]?.label || app.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-secondary">
                    {new Date(app.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        onClick={() => navigate(`/results/${app.id}`)}
                        className="rounded-lg px-3 py-1.5 text-xs font-medium text-accent hover:bg-accent/5 transition-colors cursor-pointer"
                      >
                        View
                      </button>
                      {app.status === 'needs_review' && (
                        <button
                          onClick={() => updateStatus(app.id, 'verified')}
                          className="rounded-lg px-3 py-1.5 text-xs font-medium text-emerald-600 hover:bg-emerald-50 transition-colors cursor-pointer"
                        >
                          Approve
                        </button>
                      )}
                      {app.status === 'in_progress' && (
                        <button
                          onClick={() => updateStatus(app.id, 'needs_review')}
                          className="rounded-lg px-3 py-1.5 text-xs font-medium text-amber-600 hover:bg-amber-50 transition-colors cursor-pointer"
                        >
                          Flag
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {filtered.length > 0 && (
        <p className="mt-3 text-xs text-secondary">
          Showing {filtered.length} of {applications.length} application{applications.length !== 1 ? 's' : ''}
        </p>
      )}
    </div>
  )
}