// ========================
// Type definitions for Visa AI Assistant
// ========================

/**
 * @typedef {Object} VisaApplication
 * @property {string} id - UUID
 * @property {string} created_at - ISO timestamp
 * @property {string} visa_type - e.g. 'canada_work', 'canada_student', etc.
 * @property {string} status - 'in_progress' | 'verified' | 'rejected' | 'needs_review'
 * @property {string|null} applicant_name
 * @property {string|null} passport_number
 * @property {number} overall_score - 0-100 readiness score
 */

/**
 * @typedef {Object} Document
 * @property {string} id - UUID
 * @property {string} application_id - FK to visa_applications
 * @property {string} created_at - ISO timestamp
 * @property {string} file_name
 * @property {string|null} file_url
 * @property {string} status - 'pending' | 'processing' | 'verified' | 'rejected'
 * @property {string|null} document_type
 */

/**
 * @typedef {Object} DocumentClassification
 * @property {string} id - UUID
 * @property {string} document_id - FK to documents
 * @property {string} created_at - ISO timestamp
 * @property {string} classified_as - Document type identified by AI
 * @property {number} confidence - 0-1 confidence score
 * @property {Object|null} details - JSON with additional classification details
 * @property {string[]|null} issues - Array of validation issues found
 */

// ========================
// Document Labels
// ========================

export const DOCUMENT_LABELS = {
  passport: 'Passport',
  bank_statement: 'Bank Statement',
  photograph: 'Passport Photograph',
  travel_itinerary: 'Travel Itinerary',
  accommodation_proof: 'Accommodation Proof',
  acceptance_letter: 'Acceptance Letter',
  english_test: 'English Test Score',
  employment_contract: 'Employment Contract',
  qualifications: 'Educational / Professional Qualifications',
  invitation_letter: 'Invitation Letter',
  company_documents: 'Company Documents',
  other: 'Other Document',
}

// ========================
// Visa Requirements
// ========================

export const VISA_REQUIREMENTS = {
  tourist: {
    label: 'Tourist Visa',
    required: ['passport', 'photograph', 'bank_statement', 'travel_itinerary', 'accommodation_proof'],
  },
  student: {
    label: 'Student Visa',
    required: ['passport', 'photograph', 'bank_statement', 'acceptance_letter', 'english_test'],
  },
  work: {
    label: 'Work Visa',
    required: ['passport', 'photograph', 'bank_statement', 'employment_contract', 'qualifications'],
  },
  business: {
    label: 'Business Visa',
    required: ['passport', 'photograph', 'bank_statement', 'invitation_letter', 'company_documents'],
  },
  canada_work: {
    label: 'Canada Work Visa',
    required: ['passport', 'photograph', 'bank_statement', 'employment_contract', 'qualifications'],
    requiredLabels: ['Passport', 'Employment Letter', 'Bank Statement', 'Educational Certificates'],
  },
  canada_student: {
    label: 'Canada Student Visa',
    required: ['passport', 'photograph', 'bank_statement', 'acceptance_letter', 'english_test'],
    requiredLabels: ['Passport', 'Acceptance Letter', 'Bank Statement', 'English Test Score'],
  },
  germany_student: {
    label: 'Germany Student Visa',
    required: ['passport', 'photograph', 'bank_statement', 'acceptance_letter', 'english_test'],
    requiredLabels: ['Passport', 'Acceptance Letter', 'Blocked Account Proof', 'Health Insurance'],
  },
  south_africa_work: {
    label: 'South Africa Work Visa',
    required: ['passport', 'photograph', 'bank_statement', 'employment_contract', 'qualifications'],
    requiredLabels: ['Passport', 'Employment Contract', 'Bank Statement', 'CV/Resume'],
  },
}

// ========================
// Default Visa Types
// ========================

export const DEFAULT_VISA_OPTIONS = [
  { value: 'canada_work', label: 'Canada Work Visa', countries: ['Canada'] },
  { value: 'canada_student', label: 'Canada Student Visa', countries: ['Canada'] },
  { value: 'germany_student', label: 'Germany Student Visa', countries: ['Germany'] },
  { value: 'south_africa_work', label: 'South Africa Work Visa', countries: ['South Africa'] },
]