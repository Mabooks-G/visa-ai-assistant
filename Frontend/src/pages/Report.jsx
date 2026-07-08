import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Download, Printer, FileText, CheckCircle, AlertCircle, Clock, Shield, User, Globe } from 'lucide-react'
import { supabase } from '/src/lib/supabase'

export default function Report() {
  const { id } = useParams()
  const navigate = useNavigate()
  const reportRef = useRef(null)
  const [application, setApplication] = useState(null)
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [id])

  const loadData = async () => {
    const { data: app } = await supabase
      .from('visa_applications')
      .select('*')
      .eq('id', id)
      .single()

    const { data: docs } = await supabase
      .from('documents')
      .select('*, document_classifications(*)')
      .eq('application_id', id)

    if (app) setApplication(app)
    if (docs) setDocuments(docs)
    setLoading(false)
  }

  const handlePrint = () => {
    window.print()
  }

  const handleDownload = () => {
    const element = reportRef.current
    if (!element) return

    const content = element.innerHTML
    const style = Array.from(document.styleSheets)
      .map(sheet => {
        try {
          return Array.from(sheet.cssRules || []).map(rule => rule.cssText).join('\n')
        } catch { return '' }
      })
      .join('\n')

    const html = `
      <!DOCTYPE html>
      <html><head>
        <title>Visa Report - ${application?.applicant_name || 'Application'}</title>
        <style>${style}</style>
        <style>
          @page { margin: 20mm; }
          body { font-family: 'Lato', sans-serif; color: #020617; background: #fff; }
          .no-print { display: none !important; }
        </style>
      </head><body>${content}</body></html>
    `

    const blob = new Blob([html], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `visa-report-${application?.id || id}.html`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-accent border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-4xl">
      {/* Actions */}
      <div className="mb-4 flex items-center justify-between no-print">
        <button
          onClick={() => navigate(`/results/${id}`)}
          className="flex items-center gap-2 text-sm text-secondary hover:text-foreground transition-colors cursor-pointer"
        >
          <ArrowLeft size={16} />
          Back
        </button>
        <div className="flex gap-2">
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm font-medium text-secondary hover:bg-muted transition-all cursor-pointer"
          >
            <Download size={16} />
            Download
          </button>
          <button
            onClick={handlePrint}
            className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm font-medium text-secondary hover:bg-muted transition-all cursor-pointer"
          >
            <Printer size={16} />
            Print
          </button>
        </div>
      </div>

      {/* Report Content */}
      <div ref={reportRef} className="rounded-xl border border-border bg-white shadow-sm">
        {/* Header */}
        <div className="border-b border-border bg-primary/5 px-8 py-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-on-primary">
              <Shield size={22} />
            </div>
            <div>
              <h1 className="font-heading text-2xl font-bold text-foreground">Visa Readiness Report</h1>
              <p className="text-sm text-secondary">AI-Powered Document Validation Summary</p>
            </div>
          </div>
        </div>

        <div className="px-8 py-6">
          {/* Application Details */}
          <div className="mb-6">
            <h2 className="mb-3 font-heading text-lg font-semibold text-foreground">Application Details</h2>
            <div className="grid grid-cols-2 gap-4 rounded-lg bg-muted p-4">
              <div className="flex items-center gap-2">
                <User size={16} className="text-secondary" />
                <div>
                  <p className="text-xs text-secondary">Applicant</p>
                  <p className="font-medium text-foreground">{application?.applicant_name || 'N/A'}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Globe size={16} className="text-secondary" />
                <div>
                  <p className="text-xs text-secondary">Visa Type</p>
                  <p className="font-medium text-foreground">{application?.visa_type?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <FileText size={16} className="text-secondary" />
                <div>
                  <p className="text-xs text-secondary">Passport</p>
                  <p className="font-medium text-foreground">{application?.passport_number || 'N/A'}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Clock size={16} className="text-secondary" />
                <div>
                  <p className="text-xs text-secondary">Created</p>
                  <p className="font-medium text-foreground">{new Date(application?.created_at).toLocaleDateString()}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Score */}
          <div className="mb-6">
            <h2 className="mb-3 font-heading text-lg font-semibold text-foreground">Readiness Score</h2>
            <div className="flex items-center gap-4 rounded-lg border border-border p-4">
              <div className={`flex h-16 w-16 items-center justify-center rounded-full text-xl font-bold ${
                (application?.overall_score || 0) >= 80 ? 'bg-emerald-100 text-emerald-600' :
                (application?.overall_score || 0) >= 50 ? 'bg-amber-100 text-amber-600' :
                'bg-red-100 text-red-600'
              }`}>
                {application?.overall_score || 0}%
              </div>
              <div>
                <p className="font-medium text-foreground">
                  {(application?.overall_score || 0) >= 80 ? 'Ready for Submission' :
                   (application?.overall_score || 0) >= 50 ? 'Needs Attention' :
                   'Not Ready'}
                </p>
                <p className="text-sm text-secondary">
                  Status: <strong>{application?.status?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</strong>
                </p>
              </div>
            </div>
          </div>

          {/* Documents Summary */}
          <div className="mb-6">
            <h2 className="mb-3 font-heading text-lg font-semibold text-foreground">Document Summary</h2>
            <div className="space-y-2">
              {documents.length === 0 ? (
                <p className="text-sm text-secondary">No documents uploaded.</p>
              ) : (
                documents.map((doc) => {
                  const cls = doc.document_classifications?.[0]
                  return (
                    <div key={doc.id} className="flex items-center justify-between rounded-lg border border-border p-3">
                      <div className="flex items-center gap-3">
                        {doc.status === 'verified' ? (
                          <CheckCircle size={18} className="text-emerald-500" />
                        ) : doc.status === 'rejected' ? (
                          <AlertCircle size={18} className="text-red-500" />
                        ) : (
                          <Clock size={18} className="text-amber-500" />
                        )}
                        <div>
                          <p className="text-sm font-medium text-foreground">{doc.file_name}</p>
                          <p className="text-xs text-secondary">
                            {cls ? `Classified as: ${cls.classified_as} (${Math.round(cls.confidence * 100)}% confidence)` : 'Pending classification'}
                          </p>
                        </div>
                      </div>
                      <span className={`text-xs font-semibold ${
                        doc.status === 'verified' ? 'text-emerald-600' :
                        doc.status === 'rejected' ? 'text-red-600' :
                        'text-amber-600'
                      }`}>
                        {doc.status?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                      </span>
                    </div>
                  )
                })
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="border-t border-border pt-4 text-center text-xs text-secondary">
            <p>Generated by Visa AI Assistant on {new Date().toLocaleString()}</p>
            <p className="mt-1">This is an AI-assisted analysis. Always verify with official immigration authorities.</p>
          </div>
        </div>
      </div>
    </div>
  )
}