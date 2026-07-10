import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, FileText, CheckCircle, Clock, AlertTriangle, TrendingUp, ExternalLink } from 'lucide-react'
import { getApplications } from '/src/lib/api'

const statusConfig = {
  in_progress: { label: 'In Progress', icon: Clock, class: 'bg-amber-100 text-amber-700' },
  verified: { label: 'Verified', icon: CheckCircle, class: 'bg-emerald-100 text-emerald-700' },
  rejected: { label: 'Rejected', icon: AlertTriangle, class: 'bg-red-100 text-red-700' },
  needs_review: { label: 'Needs Review', icon: AlertTriangle, class: 'bg-orange-100 text-orange-700' },
}

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="rounded-xl border border-border bg-white p-4 shadow-sm transition-all duration-150 hover:shadow-md">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-secondary">{label}</p>
          <p className="mt-1 font-heading text-2xl font-bold text-foreground">{value}</p>
        </div>
        <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${color}`}>
          <Icon size={20} />
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({ total: 0, inProgress: 0, verified: 0, rejected: 0 })

  useEffect(() => {
    loadApplications()
  }, [])

  const loadApplications = async () => {
    try {
      const data = await getApplications()
      if (data) {
        setApplications(data)
        setStats({
          total: data.length,
          inProgress: data.filter(a => a.status === 'in_progress').length,
          verified: data.filter(a => a.status === 'verified').length,
          rejected: data.filter(a => a.status === 'rejected').length,
        })
      }
    } catch (err) {
      console.error('Failed to load applications:', err)
    }
    setLoading(false)
  }

  const getVisaLabel = (type) => {
    const labels = {
      canada_work: 'Canada Work Visa',
      canada_student: 'Canada Student Visa',
      germany_student: 'Germany Student Visa',
      south_africa_work: 'South Africa Work Visa',
    }
    return labels[type] || type
  }

  return (
    <div className="mx-auto max-w-6xl">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-heading text-2xl font-bold text-foreground">Dashboard</h1>
          <p className="text-secondary">Track and manage your visa applications</p>
        </div>
        <button
          onClick={() => navigate('/upload')}
          className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-semibold text-white transition-all duration-150 hover:bg-accent/90 active:scale-[0.97] cursor-pointer"
        >
          <Plus size={18} />
          New Application
        </button>
      </div>

      {/* Stats */}
      <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard icon={FileText} label="Total Applications" value={stats.total} color="bg-blue-100 text-blue-600" />
        <StatCard icon={Clock} label="In Progress" value={stats.inProgress} color="bg-amber-100 text-amber-600" />
        <StatCard icon={CheckCircle} label="Verified" value={stats.verified} color="bg-emerald-100 text-emerald-600" />
        <StatCard icon={TrendingUp} label="Avg Score" value={`${stats.total > 0 ? Math.round(stats.verified / stats.total * 100) : 0}%`} color="bg-indigo-100 text-indigo-600" />
      </div>

      {/* Applications List */}
      <div className="rounded-xl border border-border bg-white shadow-sm">
        <div className="border-b border-border px-6 py-4">
          <h2 className="font-heading text-lg font-semibold text-foreground">Your Applications</h2>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-accent border-t-transparent" />
          </div>
        ) : applications.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <FileText size={48} className="mb-3 text-secondary/50" />
            <h3 className="font-heading text-lg font-semibold text-foreground">No applications yet</h3>
            <p className="mt-1 text-sm text-secondary">Create your first visa application to get started.</p>
            <button
              onClick={() => navigate('/upload')}
              className="mt-4 flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white transition-all duration-150 hover:bg-accent/90 active:scale-[0.97] cursor-pointer"
            >
              <Plus size={16} />
              New Application
            </button>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {applications.map((app) => {
              const StatusIcon = statusConfig[app.status]?.icon || Clock
              return (
                <div
                  key={app.id}
                  className="flex cursor-pointer items-center justify-between px-6 py-4 transition-colors hover:bg-muted/50"
                  onClick={() => navigate(`/results/${app.id}`)}
                >
                  <div className="flex items-center gap-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/10 text-accent">
                      <FileText size={20} />
                    </div>
                    <div>
                      <p className="font-medium text-foreground">{getVisaLabel(app.visa_type)}</p>
                      <p className="text-xs text-secondary">
                        {new Date(app.created_at).toLocaleDateString()} • {app.applicant_name || 'No name'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${statusConfig[app.status]?.class || 'bg-gray-100 text-gray-700'}`}>
                      <StatusIcon size={14} />
                      {statusConfig[app.status]?.label || app.status}
                    </span>
                    <span className="font-heading text-lg font-bold text-primary">
                      {app.overall_score || 0}%
                    </span>
                    <ExternalLink size={16} className="text-secondary" />
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}