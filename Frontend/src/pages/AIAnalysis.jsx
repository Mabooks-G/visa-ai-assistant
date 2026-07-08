import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Brain, CheckCircle, AlertCircle, AlertTriangle, FileText, RefreshCw, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { supabase } from '/src/lib/supabase'

export default function AIAnalysis() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [application, setApplication] = useState(null)
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)

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

  const runAnalysis = async () => {
    setAnalyzing(true)
    // Simulate AI analysis
    await new Promise(r => setTimeout(r, 2000))

    for (const doc of documents) {
      const confidence = 0.7 + Math.random() * 0.3
      const issues = Math.random() > 0.6 ? ['Document quality could be improved', 'Check expiry date'] : []

      await supabase.from('document_classifications').upsert({
        document_id: doc.id,
        classified_as: doc.document_type || 'General Document',
        confidence: Math.round(confidence * 100) / 100,
        details: { analysis_date: new Date().toISOString(), quality: confidence > 0.8 ? 'good' : 'acceptable' },
        issues: issues,
      })

      await supabase.from('documents').update({
        status: issues.length > 0 ? 'needs_review' : 'verified',
      }).eq('id', doc.id)
    }

    const avgScore = Math.round(50 + Math.random() * 40)
    await supabase.from('visa_applications').update({
      overall_score: avgScore,
      status: avgScore >= 70 ? 'verified' : 'needs_review',
    }).eq('id', id)

    setAnalyzing(false)
    loadData()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-accent border-t-transparent" />
      </div>
    )
  }

  const hasClassification = documents.some(d => d.document_classifications?.length > 0)

  return (
    <div className="mx-auto max-w-4xl">
      <button
        onClick={() => navigate(`/results/${id}`)}
        className="mb-4 flex items-center gap-2 text-sm text-secondary hover:text-foreground transition-colors cursor-pointer"
      >
        <ArrowLeft size={16} />
        Back to Results
      </button>

      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-heading text-2xl font-bold text-foreground">AI Analysis</h1>
          <p className="text-secondary">AI-powered document validation and insights</p>
        </div>
        <button
          onClick={runAnalysis}
          disabled={analyzing}
          className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-semibold text-white transition-all hover:bg-accent/90 active:scale-[0.97] disabled:opacity-60 cursor-pointer"
        >
          {analyzing ? (
            <>
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Analyzing...
            </>
          ) : (
            <>
              <Brain size={18} />
              Run Analysis
            </>
          )}
        </button>
      </div>

      {!hasClassification && !analyzing && (
        <div className="flex flex-col items-center rounded-xl border border-border bg-white py-12 text-center shadow-sm">
          <Brain size={48} className="mb-3 text-secondary/50" />
          <h2 className="font-heading text-lg font-semibold text-foreground">No analysis yet</h2>
          <p className="mt-1 text-sm text-secondary">Click "Run Analysis" to start AI-powered document validation.</p>
        </div>
      )}

      {(analyzing || hasClassification) && (
        <div className="space-y-6">
          {/* Overall Assessment */}
          {application?.overall_score > 0 && (
            <div className="rounded-xl border border-border bg-white p-6 shadow-sm">
              <h2 className="mb-3 font-heading text-lg font-semibold text-foreground">Overall Assessment</h2>
              <div className="flex items-center gap-4">
                <div className={`flex h-20 w-20 items-center justify-center rounded-full text-2xl font-bold ${
                  application.overall_score >= 80 ? 'bg-emerald-100 text-emerald-600' :
                  application.overall_score >= 50 ? 'bg-amber-100 text-amber-600' :
                  'bg-red-100 text-red-600'
                }`}>
                  {application.overall_score}%
                </div>
                <div>
                  <p className="font-medium text-foreground">
                    {application.overall_score >= 80 ? 'Strong Application' :
                     application.overall_score >= 50 ? 'Needs Improvement' :
                     'Major Gaps Detected'}
                  </p>
                  <p className="text-sm text-secondary">
                    {application.overall_score >= 80 ? 'Your documents appear to meet the requirements. Consider a final review before submission.' :
                     application.overall_score >= 50 ? 'Some documents need attention. Review the recommendations below.' :
                     'Several critical requirements are not met. Please address the issues listed below.'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Document Classifications */}
          <div className="rounded-xl border border-border bg-white shadow-sm">
            <div className="border-b border-border px-6 py-4">
              <h2 className="font-heading text-lg font-semibold text-foreground">Document Analysis</h2>
            </div>
            <div className="divide-y divide-border">
              {documents.filter(d => d.document_classifications?.length > 0).map((doc) => {
                const cls = doc.document_classifications[0]
                return (
                  <div key={doc.id} className="px-6 py-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <FileText size={18} className="mt-0.5 text-accent" />
                        <div>
                          <p className="font-medium text-foreground">{doc.file_name}</p>
                          <p className="text-xs text-secondary">
                            Classified as: <strong>{cls.classified_as}</strong>
                          </p>
                          <div className="mt-1 flex items-center gap-2">
                            <span className="text-xs text-secondary">Confidence:</span>
                            <div className="flex items-center gap-1">
                              {cls.confidence >= 0.8 ? <TrendingUp size={14} className="text-emerald-500" /> :
                               cls.confidence >= 0.6 ? <Minus size={14} className="text-amber-500" /> :
                               <TrendingDown size={14} className="text-red-500" />}
                              <span className={`text-xs font-semibold ${
                                cls.confidence >= 0.8 ? 'text-emerald-600' :
                                cls.confidence >= 0.6 ? 'text-amber-600' :
                                'text-red-600'
                              }`}>
                                {Math.round(cls.confidence * 100)}%
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                        doc.status === 'verified' ? 'bg-emerald-100 text-emerald-700' :
                        doc.status === 'needs_review' ? 'bg-orange-100 text-orange-700' :
                        'bg-amber-100 text-amber-700'
                      }`}>
                        {doc.status === 'verified' ? <CheckCircle size={12} /> : <AlertTriangle size={12} />}
                        {doc.status?.replace(/_/g, ' ')}
                      </span>
                    </div>
                    {cls.issues?.length > 0 && (
                      <div className="mt-3 space-y-1.5 pl-9">
                        {cls.issues.map((issue, i) => (
                          <div key={i} className="flex items-start gap-2 text-xs text-amber-600">
                            <AlertTriangle size={12} className="mt-0.5 flex-shrink-0" />
                            <span>{issue}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}