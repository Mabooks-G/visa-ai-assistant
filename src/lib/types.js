// ========================
// Type definitions for Visa AI Assistant
// ========================

/**
 * @typedef {Object} VisaApplication
 * @property {string} id - UUID
 * @property {string} created_at - ISO timestamp
 * @property {string} visa_type - e.g. 'canada_work', 'canada_student', 'germany_student', 'south_africa_work'
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
 * @property {string|null} document_type - e.g. 'passport', 'bank_statement', 'employment_letter'
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

/**
 * @typedef {Object} DashboardStats
 * @property {number} total - Total applications
 * @property {number} inProgress - In progress count
 * @property {number} verified - Verified count
 * @property {number} rejected - Rejected count
 * @property {number} avgScore - Average readiness score
 */

export {}