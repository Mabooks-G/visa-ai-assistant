import React, { useState, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileText, X, CheckCircle, AlertCircle, Globe, ArrowRight } from 'lucide-react'
import { createApplication, uploadDocument } from '/src/lib/api'

const visaOptions = [
  { value: 'canada_work', label: 'Canada Work Visa', countries: ['Canada'] },
  { value: 'canada_student', label: 'Canada Student Visa', countries: ['Canada'] },
  { value: 'germany_student', label: 'Germany Student Visa', countries: ['Germany'] },
  { value: 'south_africa_work', label: 'South Africa Work Visa', countries: ['South Africa'] },
]

const requiredDocuments = {
  canada_work: ['Passport', 'Employment Letter', 'Bank Statement', 'Educational Certificates'],
  canada_student: ['Passport', 'Acceptance Letter', 'Bank Statement', 'English Test Score'],
  germany_student: ['Passport', 'Acceptance Letter', 'Blocked Account Proof', 'Health Insurance'],
  south_africa_work: ['Passport', 'Employment Contract', 'Bank Statement', 'CV/Resume'],
}

export default function UploadDocuments() {
  const navigate = useNavigate()
  const fileInputRef = useRef(null)
  const [step, setStep] = useState(1)
  const [visaType, setVisaType] = useState('')
  const [applicantName, setApplicantName] = useState('')
  const [passportNumber, setPassportNumber] = useState('')
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [applicationId, setApplicationId] = useState(null)
  const [error, setError] = useState('')

  const onDrop = useCallback((e) => {
    e.preventDefault()
    const droppedFiles = Array.from(e.dataTransfer.files)
    addFiles(droppedFiles)
  }, [])

  const addFiles = (newFiles) => {
    const validFiles = newFiles.filter(f => 
      ['application/pdf', 'image/jpeg', 'image/png'].includes(f.type)
    )
    setFiles(prev => [...prev, ...validFiles.map(f => ({
      id: Math.random().toString(36).substr(2, 9),
      file: f,
      name: f.name,
      size: f.size,
      type: f.type,
      status: 'pending',
      documentType: '',
    }))])
  }

  const removeFile = (id) => {
    setFiles(prev => prev.filter(f => f.id !== id))
  }

  const handleFileSelect = (e) => {
    addFiles(Array.from(e.target.files))
    e.target.value = ''
  }

  const handleCreateApplication = async () => {
    if (!visaType || !applicantName) {
      setError('Please fill in all required fields')
      return
    }

    setError('')
    setUploading(true)

    try {
      const applicationData = await createApplication({
        visa_type: visaType,
        applicant_name: applicantName,
        passport_number: passportNumber || null,
        status: 'in_progress',
      })

      const appId = applicationData.id || applicationData.application_id

      // Upload each file
      for (const fileItem of files) {
        const formData = new FormData()
        formData.append('file', fileItem.file)
        formData.append('application_id', appId)
        formData.append('file_name', fileItem.file.name)

        try {
          await uploadDocument(formData)
        } catch (uploadErr) {
          console.error('Upload failed for', fileItem.name, uploadErr)
        }
      }

      setUploading(false)
      navigate(`/results/${appId}`)
    } catch (err) {
      setError(err.message || 'Failed to create application')
      setUploading(false)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-heading text-2xl font-bold text-foreground">New Application</h1>
      <p className="mb-6 text-secondary">Fill in your details and upload required documents</p>

      {error && (
        <div className="mb-4 flex items-start gap-3 rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
          <AlertCircle size={18} className="mt-0.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Stepper */}
      <div className="mb-8 flex items-center gap-2">
        {[1, 2, 3].map((s) => (
          <React.Fragment key={s}>
            <div className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold transition-colors ${
              step >= s ? 'bg-accent text-white' : 'bg-muted text-secondary'
            }`}>
              {step > s ? <CheckCircle size={16} /> : s}
            </div>
            {s < 3 && <div className={`flex-1 h-0.5 ${step > s ? 'bg-accent' : 'bg-border'}`} />}
          </React.Fragment>
        ))}
      </div>

      {step === 1 && (
        <div className="rounded-xl border border-border bg-white p-6 shadow-sm">
          <h2 className="font-heading text-lg font-semibold text-foreground">Visa Type & Personal Info</h2>
          <p className="mb-4 text-sm text-secondary">Select the visa type you're applying for</p>

          <div className="mb-4">
            <label className="mb-1.5 block text-sm font-medium text-foreground">Visa Type *</label>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {visaOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setVisaType(option.value)}
                  className={`flex items-start gap-3 rounded-lg border p-4 text-left transition-all cursor-pointer ${
                    visaType === option.value
                      ? 'border-accent bg-accent/5 ring-1 ring-accent'
                      : 'border-border hover:border-accent/50'
                  }`}
                >
                  <Globe size={20} className={visaType === option.value ? 'text-accent' : 'text-secondary'} />
                  <div>
                    <p className="font-medium text-foreground">{option.label}</p>
                    <p className="text-xs text-secondary">{option.countries.join(', ')}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <label className="mb-1.5 block text-sm font-medium text-foreground">Applicant Name *</label>
            <input
              type="text"
              value={applicantName}
              onChange={(e) => setApplicantName(e.target.value)}
              placeholder="Full name as on passport"
              className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20"
            />
          </div>

          <div className="mb-6">
            <label className="mb-1.5 block text-sm font-medium text-foreground">Passport Number</label>
            <input
              type="text"
              value={passportNumber}
              onChange={(e) => setPassportNumber(e.target.value)}
              placeholder="Optional"
              className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20"
            />
          </div>

          <button
            onClick={() => setStep(2)}
            disabled={!visaType || !applicantName}
            className="flex items-center gap-2 rounded-lg bg-accent px-6 py-2.5 text-sm font-semibold text-white transition-all duration-150 hover:bg-accent/90 active:scale-[0.97] disabled:opacity-50 cursor-pointer"
          >
            Next Step
            <ArrowRight size={16} />
          </button>
        </div>
      )}

      {step === 2 && (
        <div className="rounded-xl border border-border bg-white p-6 shadow-sm">
          <h2 className="font-heading text-lg font-semibold text-foreground">Upload Documents</h2>
          <p className="mb-4 text-sm text-secondary">
            Upload your documents (PDF, JPG, PNG). Required: {requiredDocuments[visaType]?.join(', ')}
          </p>

          {/* Drop zone */}
          <div
            onDrop={onDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => fileInputRef.current?.click()}
            className="mb-4 cursor-pointer rounded-xl border-2 border-dashed border-border bg-background p-8 text-center transition-colors hover:border-accent/50 hover:bg-accent/5"
          >
            <Upload size={32} className="mx-auto mb-2 text-secondary" />
            <p className="font-medium text-foreground">Drop files here or click to browse</p>
            <p className="text-xs text-secondary">PDF, JPG, PNG accepted. Max 10MB each.</p>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.jpg,.jpeg,.png"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {/* File list */}
          {files.length > 0 && (
            <div className="space-y-2">
              {files.map((fileItem) => (
                <div key={fileItem.id} className="flex items-center justify-between rounded-lg border border-border bg-background p-3">
                  <div className="flex items-center gap-3">
                    <FileText size={18} className="text-accent" />
                    <div>
                      <p className="text-sm font-medium text-foreground">{fileItem.name}</p>
                      <p className="text-xs text-secondary">{formatFileSize(fileItem.size)}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(fileItem.id)}
                    className="cursor-pointer rounded-lg p-1.5 text-secondary hover:bg-destructive/10 hover:text-destructive transition-colors"
                    aria-label={`Remove ${fileItem.name}`}
                  >
                    <X size={16} />
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="mt-6 flex gap-3">
            <button
              onClick={() => setStep(1)}
              className="rounded-lg border border-border px-6 py-2.5 text-sm font-medium text-secondary hover:bg-muted transition-all cursor-pointer"
            >
              Back
            </button>
            <button
              onClick={() => setStep(3)}
              className="flex items-center gap-2 rounded-lg bg-accent px-6 py-2.5 text-sm font-semibold text-white transition-all duration-150 hover:bg-accent/90 active:scale-[0.97] cursor-pointer"
            >
              Review & Submit
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="rounded-xl border border-border bg-white p-6 shadow-sm">
          <h2 className="font-heading text-lg font-semibold text-foreground">Review & Submit</h2>
          <p className="mb-4 text-sm text-secondary">Review your application before submitting</p>

          <div className="mb-4 rounded-lg bg-muted p-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-secondary">Visa Type</p>
                <p className="font-medium text-foreground">{visaOptions.find(o => o.value === visaType)?.label}</p>
              </div>
              <div>
                <p className="text-xs text-secondary">Applicant</p>
                <p className="font-medium text-foreground">{applicantName}</p>
              </div>
              {passportNumber && (
                <div>
                  <p className="text-xs text-secondary">Passport</p>
                  <p className="font-medium text-foreground">{passportNumber}</p>
                </div>
              )}
              <div>
                <p className="text-xs text-secondary">Documents</p>
                <p className="font-medium text-foreground">{files.length} file{files.length !== 1 ? 's' : ''}</p>
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep(2)}
              className="rounded-lg border border-border px-6 py-2.5 text-sm font-medium text-secondary hover:bg-muted transition-all cursor-pointer"
            >
              Back
            </button>
            <button
              onClick={handleCreateApplication}
              disabled={uploading}
              className="flex items-center gap-2 rounded-lg bg-accent px-6 py-2.5 text-sm font-semibold text-white transition-all duration-150 hover:bg-accent/90 active:scale-[0.97] disabled:opacity-60 cursor-pointer"
            >
              {uploading ? (
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
              ) : (
                <>
                  <CheckCircle size={16} />
                  Submit Application
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}