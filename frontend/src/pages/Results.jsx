import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, FileText, CheckCircle, AlertCircle, Clock, RefreshCw, BarChart3, Download } from 'lucide-react'
import { getApplication, getDocuments } from '/src/lib/api'

export default function Results() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [application, setApplication] = useState(null)
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [id])

  const loadData = async () => {
    try {
      const [app, docs] = await Promise.all([
        getApplication(id),
        getDocuments(id),
      ])
      if (app) setApplication(app)
      if (docs) setDocuments(docs)
    } catch (err) {
      console.error('Failed to load results:', err)
    }
    setLoading(false)
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-emerald-500'
    if (score >= 50) return 'text-amber-500'
    return 'text-red-500'
  }

  const getScoreRingColor = (score) => {
    if (score >= 80) return 'stroke-emerald-500'
    if (score >= 50) return 'stroke-amber-500'
    return 'stroke-red-500'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-accent border-t-transparent" />
      </div>
    )
  }

  if (!application) {
    return (
      <div className="text-center py-20">
        <AlertCircle size={48} className="mx-auto mb-3 text-secondary/50" />
        <h2 className="font-heading text-xl font-bold text-foreground">Application not found</h2>
        <button onClick={() => navigate('/dashboard')} className="mt-4 text-accent hover:underline cursor-pointer">
          Back to Dashboard
        </button>
      </div>
    )
  }

  const score = application.overall_score || 0
  const circumference = 2 * Math.PI * 54
  const offset = circumference - (score / 100) * circumference

  return (
    <div className="mx-auto max-w-4xl">
      <button
        onClick={() => navigate('/dashboard')}
        className="mb-4 flex items-center gap-2 text-sm text-secondary hover:text-foreground transition-colors cursor-pointer"
      >
        <ArrowLeft size={16} />
        Back to Dashboard
      </button>

      {/* Score + Status */}
      <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Score Circle */}
        <div className="flex flex-col items-center justify-center rounded-xl border border-border bg-white p-6 shadow-sm">
          <div className="relative mb-3">
            <svg width="120" height="120" className="transform -rotate-90">
              <circle cx="60" cy="60" r="54" fill="none" stroke="currentColor" strokeWidth="8" className="text-muted" />
              <circle
                cx="60" cy="60" r="54"
                fill="none"
                strokeWidth="8"
                strokeDasharray={circumference}
                strokeDashoffset={offset}
                strokeLinecap="round"
                className={getScoreRingColor(score) + ' transition-all duration-700'}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className={`font-heading text-3xl font-bold ${getScoreColor(score)}`}>{score}%</span>
            </div>
          </div>
          <p className="font-medium text-foreground">Readiness Score</p>
          <p className="text-xs text-secondary">
            {score >= 80 ? 'Ready to submit!' : score >= 50 ? 'Needs improvement' : 'Major gaps found'}
          </p>
        </div>

        {/* App Info */}
        <div className="col-span-2 rounded-xl border border-border bg-white p-6 shadow-sm">
          <h2 className="font-heading text-lg font-semibold text-foreground">{application.applicant_name || 'Untitled Application'}</h2>
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-secondary">Visa Type</p>
              <p className="font-medium text-foreground">{application.visa_type?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</p>
            </div>
            <div>
              <p className="text-xs text-secondary">Status</p>
              <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                application.status === 'verified' ? 'bg-emerald-100 text-emerald-700' :
                application.status === 'rejected' ? 'bg-red-100 text-red-700' :
                'bg-amber-100 text-amber-700'
              }`}>
                {application.status?.replace(/_/g, ' ')}
              </span>
            </div>
            <div>
              <p className="text-xs text-secondary">Passport</p>
              <p className="font-medium text-foreground">{application.passport_number || 'Not provided'}</p>
            </div>
            <div>
              <p className="text-xs text-secondary">Created</p>
              <p className="font-medium text-foreground">{new Date(application.created_at).toLocaleDateString()}</p>
            </div>
          </div>

          <div className="mt-4 flex gap-3">
            <button
              onClick={() => navigate(`/analysis/${id}`)}
              className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white transition-all hover:bg-accent/90 active:scale-[0.97] cursor-pointer"
            >
              <BarChart3 size={16} />
              AI Analysis
            </button>
            <button
              onClick={() => navigate(`/report/${id}`)}
              className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm font-medium text-secondary hover:bg-muted transition-all cursor-pointer"
            >
              <Download size={16} />
              Report
            </button>
          </div>
        </div>
      </div>

      {/* Documents */}
      <div className="rounded-xl border border-border bg-white shadow-sm">
        <div className="border-b border-border px-6 py-4">
          <h2 className="font-heading text-lg font-semibold text-foreground">Documents ({documents.length})</h2>
        </div>

        {documents.length === 0 ? (
          <div className="flex flex-col items-center py-8 text-center">
            <FileText size={36} className="mb-2 text-secondary/50" />
            <p className="text-sm text-secondary">No documents uploaded yet</p>
            <button
              onClick={() => navigate('/upload')}
              className="mt-2 text-sm font-medium text-accent hover:underline cursor-pointer"
            >
              Upload documents
            </button>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {documents.map((doc) => {
              const classification = doc.document_classifications?.[0]
              const isVerified = doc.status === 'verified'
              const isRejected = doc.status === 'rejected'

              return (
                <div key={doc.id} className="flex items-center justify-between px-6 py-4">
                  <div className="flex items-center gap-3">
                    <FileText size={18} className="text-accent" />
                    <div>
                      <p className="text-sm font-medium text-foreground">{doc.file_name}</p>
                      <div className="flex items-center gap-2 text-xs text-secondary">
                        <span>{doc.document_type || 'Unclassified'}</span>
                        {classification && (
                          <span>• AI: {classification.classified_as} ({Math.round(classification.confidence * 100)}%)</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {isVerified && <CheckCircle size={16} className="text-emerald-500" />}
                    {isRejected && <AlertCircle size={16} className="text-red-500" />}
                    {doc.status === 'pending' && <Clock size={16} className="text-amber-500" />}
                    <span className={`text-xs font-semibold ${
                      isVerified ? 'text-emerald-600' :
                      isRejected ? 'text-red-600' :
                      'text-amber-600'
                    }`}>
                      {doc.status}
                    </span>
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