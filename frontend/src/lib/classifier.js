import { DOCUMENT_LABELS, VISA_REQUIREMENTS } from './types'

// ========================
// File-name-based document classifier
// ========================

const FILE_PATTERNS = [
  { regex: /passport|travel\s*doc|identity/i, label: 'passport', keywords: ['passport', 'identity'] },
  { regex: /bank|statement|financial|account/i, label: 'bank_statement', keywords: ['bank', 'statement', 'financial'] },
  { regex: /photo|picture|image|photograph|passport\s*size/i, label: 'photograph', keywords: ['photo', 'picture', 'photograph'] },
  { regex: /itinerary|travel\s*plan|flight|booking/i, label: 'travel_itinerary', keywords: ['itinerary', 'travel plan', 'flight booking'] },
  { regex: /accommodation|hotel|stay|lodging|residence/i, label: 'accommodation_proof', keywords: ['accommodation', 'hotel', 'lodging'] },
  { regex: /acceptance|admission|offer\s*letter|enrollment|university|college|school/i, label: 'acceptance_letter', keywords: ['acceptance letter', 'admission', 'offer letter'] },
  { regex: /ielts|toefl|english|language\s*test/i, label: 'english_test', keywords: ['english test', 'ielts', 'toefl'] },
  { regex: /employment|contract|offer\s*of\s*employment|job\s*letter|appointment/i, label: 'employment_contract', keywords: ['employment', 'contract', 'job offer'] },
  { regex: /certificate|qualification|degree|diploma|transcript|academic/i, label: 'qualifications', keywords: ['certificate', 'degree', 'qualification', 'transcript'] },
  { regex: /invitation|invite|conference|event/i, label: 'invitation_letter', keywords: ['invitation', 'invite', 'conference'] },
  { regex: /company\s*doc|registration|certificate\s*of\s*incorporation|business\s*license/i, label: 'company_documents', keywords: ['company registration', 'business license', 'incorporation'] },
]

/**
 * Classify a single document based on its file name.
 * @param {{ id: string, file_name: string }} doc
 * @returns {{ classified_as: string, confidence: number, details: object }}
 */
export function classifyDocument(doc) {
  const name = doc.file_name || ''

  // Try to match against known patterns
  for (const pattern of FILE_PATTERNS) {
    if (pattern.regex.test(name)) {
      // Confidence based on how many keywords are present
      const matchCount = pattern.keywords.filter(kw =>
        new RegExp(kw, 'i').test(name)
      ).length

      // Extract extension
      const ext = name.split('.').pop()?.toLowerCase()
      const extBonus = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'].includes(ext) ? 0.05 : 0
      const confidence = Math.min(0.95, 0.65 + matchCount * 0.1 + extBonus)

      const issues = []
      if (confidence < 0.7) issues.push('Low confidence in document type classification — verify manually')
      if (confidence < 0.5) issues.push('File name does not clearly indicate document type')
      if (name.length < 10) issues.push('File name is too generic, consider renaming')

      return {
        classified_as: DOCUMENT_LABELS[pattern.label] || pattern.label,
        confidence: Math.round(confidence * 100) / 100,
        details: {
          analysis_date: new Date().toISOString(),
          quality: confidence >= 0.8 ? 'good' : confidence >= 0.5 ? 'acceptable' : 'low',
          matched_pattern: pattern.label,
          file_extension: ext || 'unknown',
        },
        issues: issues.length > 0 ? issues : [],
      }
    }
  }

  // Fallback: unknown document
  return {
    classified_as: 'Other Document',
    confidence: 0.35,
    details: {
      analysis_date: new Date().toISOString(),
      quality: 'low',
      matched_pattern: null,
      file_extension: name.split('.').pop()?.toLowerCase() || 'unknown',
      note: 'Could not determine document type from file name',
    },
    issues: [
      'Unable to classify this document — AI needs more information',
      'Ensure the file name clearly indicates its type (e.g., "Passport_JohnDoe.pdf")',
    ],
  }
}

/**
 * Classify all documents in an application.
 * @param {Array} documents
 * @returns {Array} documents with classification results
 */
export function classifyAllDocuments(documents) {
  return documents.map(doc => {
    const classification = classifyDocument(doc)
    const issues = classification.issues || []
    const status = issues.length > 0 ? 'needs_review' : 'verified'
    return {
      document_id: doc.id,
      document: doc,
      ...classification,
      status,
    }
  })
}

/**
 * Validate classified documents against visa requirements.
 * @param {Array} classifications - results from classifyAllDocuments
 * @param {string} visaType - e.g. 'canada_work', 'canada_student'
 * @returns {{ matched: Array, missing: Array, score: number, findings: Array }}
 */
export function validateAgainstRequirements(classifications, visaType) {
  const requirements = VISA_REQUIREMENTS[visaType]
  if (!requirements) {
    // Fallback to generic tourist requirements
    return validateAgainstRequirements(classifications, 'tourist')
  }

  const required = requirements.required
  const findings = []

  // Map classified documents to their type keys
  const classifiedTypes = classifications.map(c => {
    // Find which key matches the classified_as label
    for (const [key, label] of Object.entries(DOCUMENT_LABELS)) {
      if (label === c.classified_as) return key
    }
    return null
  }).filter(Boolean)

  // Check each requirement
  const matched = []
  const missing = []

  for (const req of required) {
    if (classifiedTypes.includes(req)) {
      const classification = classifications.find(c => {
        for (const [key, label] of Object.entries(DOCUMENT_LABELS)) {
          if (label === c.classified_as && key === req) return true
        }
        return false
      })
      matched.push({ type: req, confidence: classification?.confidence || 0, label: DOCUMENT_LABELS[req] })
      if (classification?.confidence < 0.6) {
        findings.push(`Low confidence for ${DOCUMENT_LABELS[req]} — check quality`)
      }
    } else {
      missing.push({ type: req, label: DOCUMENT_LABELS[req] })
      findings.push(`Missing required document: ${DOCUMENT_LABELS[req]}`)
    }
  }

  // Calculate readiness score
  const matchedWeight = matched.reduce((sum, m) => sum + m.confidence, 0)
  const maxScore = required.length
  const rawScore = (matchedWeight / maxScore) * 100

  // Deduct for issues
  const totalIssues = classifications.reduce((sum, c) => sum + (c.issues?.length || 0), 0)
  const score = Math.max(0, Math.round(rawScore - totalIssues * 5))

  return { matched, missing, score, findings }
}

/**
 * Run the full analysis pipeline for an application.
 * @param {Array} documents
 * @param {string} visaType
 * @returns {{ classifications: Array, validation: object, overall_score: number, status: string }}
 */
export function runFullAnalysis(documents, visaType) {
  const classifications = classifyAllDocuments(documents)
  const validation = validateAgainstRequirements(classifications, visaType)

  return {
    classifications,
    validation,
    overall_score: validation.score,
    status: validation.score >= 70 ? 'verified' : validation.score >= 40 ? 'needs_review' : 'rejected',
  }
}