/**
 * Constants for the Visa AI Assistant.
 * Global-minded: countries, visa types, document types, and requirements.
 * Requirements use [ALL] tag for universal requirements or specific countries.
 */

// ── All Sovereign Countries ────────────────────────────────────────────────
// Based on UN member states + a few widely recognised territories

export const COUNTRIES = [
  'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda',
  'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan',
  'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize',
  'Benin', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil',
  'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi',
  'Cabo Verde', 'Cambodia', 'Cameroon', 'Canada', 'Central African Republic',
  'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 'Costa Rica',
  "Côte d'Ivoire", 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic',
  'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic',
  'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia',
  'Eswatini', 'Ethiopia',
  'Fiji', 'Finland', 'France',
  'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada',
  'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana',
  'Haiti', 'Honduras', 'Hungary',
  'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy',
  'Jamaica', 'Japan', 'Jordan',
  'Kazakhstan', 'Kenya', 'Kiribati', 'South Korea', 'Kosovo', 'Kuwait', 'Kyrgyzstan',
  'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein',
  'Lithuania', 'Luxembourg',
  'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands',
  'Mauritania', 'Mauritius', 'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia',
  'Montenegro', 'Morocco', 'Mozambique', 'Myanmar',
  'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger',
  'Nigeria', 'North Korea', 'North Macedonia', 'Norway',
  'Oman',
  'Pakistan', 'Palau', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay',
  'Peru', 'Philippines', 'Poland', 'Portugal',
  'Qatar',
  'Romania', 'Russia', 'Rwanda',
  'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines',
  'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal',
  'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia',
  'Solomon Islands', 'Somalia', 'South Africa', 'South Sudan', 'Spain',
  'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria',
  'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste', 'Togo',
  'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu',
  'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom',
  'United States', 'Uruguay', 'Uzbekistan',
  'Vanuatu', 'Vatican City', 'Venezuela', 'Vietnam',
  'Yemen',
  'Zambia', 'Zimbabwe',
]

// ── Visa Types ────────────────────────────────────────────────────────────

export const VISA_TYPES = [
  { id: 'tourist', label: 'Tourist / Visitor Visa' },
  { id: 'work', label: 'Work / Employment Visa' },
  { id: 'student', label: 'Student Visa' },
  { id: 'business', label: 'Business / Investment Visa' },
  { id: 'permanent_residence', label: 'Permanent Residence / Immigrant Visa' },
  { id: 'transit', label: 'Transit / Airport Transit Visa' },
  { id: 'medical', label: 'Medical Treatment Visa' },
  { id: 'diplomatic', label: 'Diplomatic / Official Visa' },
  { id: 'family_reunion', label: 'Family Reunion / Spousal Visa' },
  { id: 'working_holiday', label: 'Working Holiday Visa' },
  { id: 'digital_nomad', label: 'Digital Nomad Visa' },
  { id: 'asylum', label: 'Asylum / Refugee Application' },
]

// ── Document Types ──────────────────────────────────────────────────────

export const DOCUMENT_TYPES = {
  passport: 'Valid Passport',
  photograph: 'Passport-Sized Photographs',
  birth_certificate: 'Birth Certificate',
  marriage_certificate: 'Marriage Certificate',
  police_clearance: 'Police Clearance Certificate',
  medical_certificate: 'Medical Examination Certificate',
  bank_statement: 'Bank Statements (last 3-6 months)',
  employment_letter: 'Employment Letter / Offer Letter',
  payslips: 'Recent Payslips',
  tax_returns: 'Tax Returns / ITR',
  invitation_letter: 'Invitation Letter',
  travel_itinerary: 'Travel Itinerary / Flight Booking',
  accommodation_proof: 'Accommodation Proof / Hotel Booking',
  travel_insurance: 'Travel / Health Insurance',
  acceptance_letter: 'Acceptance Letter from Institution',
  english_test: 'English Language Test (IELTS/TOEFL)',
  qualifications: 'Educational Degrees / Diplomas',
  transcript: 'Academic Transcripts',
  cv_resume: 'CV / Resume',
  company_documents: 'Company Registration / Business Documents',
  sponsorship_letter: 'Sponsorship Letter',
  proof_of_funds: 'Proof of Sufficient Funds',
  blocked_account: 'Blocked Account Confirmation',
  passport_photo_page: 'Passport Bio-Page Copy',
  visa_application_form: 'Completed Visa Application Form',
  previous_visas: 'Copies of Previous Visas',
  letter_of_intent: 'Letter of Intent / Statement of Purpose',
  proof_of_address: 'Proof of Residence / Utility Bill',
  no_objection: 'No Objection Certificate (NOC)',
}

export const DOCUMENT_LABELS = DOCUMENT_TYPES

// ── Requirements: Global Minded ──────────────────────────────────────────
// Each requirement specifies which countries and visa types it applies to.
// `tags` contains country names or ['ALL'] for universal requirements.
// The admin can modify these via the requirement_overrides table.

export const REQUIREMENTS = [
  // ── Universal Requirements (ALL countries, ALL visa types) ──────────
  {
    id: 'passport',
    documentType: 'passport',
    tags: ['ALL'],
    visaTypes: ['ALL'],
    description: 'Valid passport with at least 6 months validity beyond intended stay',
    notes: 'Must have at least 2 blank pages',
  },
  {
    id: 'photograph',
    documentType: 'photograph',
    tags: ['ALL'],
    visaTypes: ['ALL'],
    description: 'Recent passport-sized photographs meeting ICAO standards',
    notes: 'Usually 2-4 photos, white background',
  },
  {
    id: 'visa_application_form',
    documentType: 'visa_application_form',
    tags: ['ALL'],
    visaTypes: ['ALL'],
    description: 'Completed and signed visa application form',
    notes: 'May need to be completed online or printed',
  },
  {
    id: 'passport_photo_page',
    documentType: 'passport_photo_page',
    tags: ['ALL'],
    visaTypes: ['ALL'],
    description: 'Copy of passport bio-data page',
    notes: 'Clear color copy',
  },

  // ── Financial / Economic Requirements ──────────────────────────────
  {
    id: 'bank_statement',
    documentType: 'bank_statement',
    tags: ['ALL'],
    visaTypes: ['tourist', 'student', 'work', 'business', 'permanent_residence', 'family_reunion', 'digital_nomad'],
    description: 'Recent bank statements showing sufficient funds',
    notes: 'Usually last 3-6 months',
  },
  {
    id: 'proof_of_funds',
    documentType: 'proof_of_funds',
    tags: ['ALL'],
    visaTypes: ['tourist', 'student', 'permanent_residence'],
    description: 'Proof of sufficient funds for the duration of stay',
    notes: 'May include bank statements, sponsorship letters, or financial guarantees',
  },
  {
    id: 'travel_insurance',
    documentType: 'travel_insurance',
    tags: ['ALL'],
    visaTypes: ['tourist', 'transit'],
    description: 'Travel health insurance covering the entire stay',
    notes: 'Minimum coverage of €30,000 for Schengen area',
  },

  // ── Travel / Itinerary ─────────────────────────────────────────────
  {
    id: 'travel_itinerary',
    documentType: 'travel_itinerary',
    tags: ['ALL'],
    visaTypes: ['tourist', 'business'],
    description: 'Detailed travel itinerary and flight bookings',
    notes: 'Round-trip or onward travel proof recommended',
  },
  {
    id: 'accommodation_proof',
    documentType: 'accommodation_proof',
    tags: ['ALL'],
    visaTypes: ['tourist', 'business'],
    description: 'Hotel reservations or accommodation proof',
    notes: 'For the entire duration of stay',
  },

  // ── Employment / Work ──────────────────────────────────────────────
  {
    id: 'employment_letter',
    documentType: 'employment_letter',
    tags: ['ALL'],
    visaTypes: ['work', 'working_holiday'],
    description: 'Employment contract or job offer letter',
    notes: 'Should include salary, position, and duration',
  },
  {
    id: 'cv_resume',
    documentType: 'cv_resume',
    tags: ['ALL'],
    visaTypes: ['work', 'student', 'permanent_residence', 'digital_nomad'],
    description: 'Updated CV or resume',
    notes: 'Should match employment/education history',
  },
  {
    id: 'payslips',
    documentType: 'payslips',
    tags: ['ALL'],
    visaTypes: ['work', 'permanent_residence'],
    description: 'Recent pay slips (last 3-6 months)',
    notes: '',
  },
  {
    id: 'tax_returns',
    documentType: 'tax_returns',
    tags: ['ALL'],
    visaTypes: ['work', 'business', 'permanent_residence'],
    description: 'Tax returns or ITR for recent years',
    notes: 'Usually last 2-3 years',
  },
  {
    id: 'company_documents',
    documentType: 'company_documents',
    tags: ['ALL'],
    visaTypes: ['business'],
    description: 'Company registration documents or business license',
    notes: 'May need MOA, AOA, tax registration',
  },

  // ── Education / Study ──────────────────────────────────────────────
  {
    id: 'acceptance_letter',
    documentType: 'acceptance_letter',
    tags: ['ALL'],
    visaTypes: ['student'],
    description: 'Letter of acceptance from the educational institution',
    notes: 'Must be from a recognized institution',
  },
  {
    id: 'english_test',
    documentType: 'english_test',
    tags: ['ALL'],
    visaTypes: ['student', 'work', 'permanent_residence'],
    description: 'English language proficiency test scores (IELTS/TOEFL/PTE)',
    notes: 'Minimum scores vary by country and institution',
  },
  {
    id: 'qualifications',
    documentType: 'qualifications',
    tags: ['ALL'],
    visaTypes: ['student', 'work', 'permanent_residence'],
    description: 'Educational degrees, diplomas, and certificates',
    notes: 'May need notarized translations',
  },
  {
    id: 'transcript',
    documentType: 'transcript',
    tags: ['ALL'],
    visaTypes: ['student'],
    description: 'Academic transcripts from previous institutions',
    notes: 'Original or certified copies',
  },
  {
    id: 'letter_of_intent',
    documentType: 'letter_of_intent',
    tags: ['ALL'],
    visaTypes: ['student'],
    description: 'Statement of Purpose / Letter of Intent',
    notes: 'Explain why you chose the program and institution',
  },

  // ── Family / Personal Status ───────────────────────────────────────
  {
    id: 'birth_certificate',
    documentType: 'birth_certificate',
    tags: ['ALL'],
    visaTypes: ['family_reunion', 'permanent_residence'],
    description: 'Birth certificate',
    notes: 'May need apostille or notarized translation',
  },
  {
    id: 'marriage_certificate',
    documentType: 'marriage_certificate',
    tags: ['ALL'],
    visaTypes: ['family_reunion', 'permanent_residence'],
    description: 'Marriage certificate (if applicable)',
    notes: 'May need apostille or notarized translation',
  },
  {
    id: 'sponsorship_letter',
    documentType: 'sponsorship_letter',
    tags: ['ALL'],
    visaTypes: ['tourist', 'family_reunion', 'student'],
    description: 'Sponsorship letter from host or family member',
    notes: 'Include sponsor\'s financial documents and proof of relationship',
  },

  // ── Security / Clearance ───────────────────────────────────────────
  {
    id: 'police_clearance',
    documentType: 'police_clearance',
    tags: ['ALL'],
    visaTypes: ['work', 'permanent_residence', 'student', 'family_reunion'],
    description: 'Police clearance certificate from country of residence',
    notes: 'Usually valid for 6-12 months',
  },
  {
    id: 'medical_certificate',
    documentType: 'medical_certificate',
    tags: ['ALL'],
    visaTypes: ['work', 'permanent_residence', 'student'],
    description: 'Medical examination certificate from approved panel physician',
    notes: 'Includes chest X-ray and blood tests for some countries',
  },
  {
    id: 'no_objection',
    documentType: 'no_objection',
    tags: ['ALL'],
    visaTypes: ['work', 'student'],
    description: 'No Objection Certificate (NOC) from current employer',
    notes: 'Required in some countries for work/study release',
  },

  // ── Country-Specific Requirements ──────────────────────────────────

  // Canada
  {
    id: 'canada_biometrics',
    documentType: 'police_clearance',
    tags: ['Canada'],
    visaTypes: ['work', 'student', 'permanent_residence'],
    description: 'Biometrics (fingerprints and photograph) at VAC',
    notes: 'Valid for 10 years',
  },
  {
    id: 'canada_proof_of_funds_student',
    documentType: 'blocked_account',
    tags: ['Canada'],
    visaTypes: ['student'],
    description: 'Proof of tuition payment + living expenses (CAD $20,635/year)',
    notes: 'Guaranteed Investment Certificate (GIC) option available',
  },
  {
    id: 'canada_lmia',
    documentType: 'employment_letter',
    tags: ['Canada'],
    visaTypes: ['work'],
    description: 'Labour Market Impact Assessment (LMIA) or LMIA-exempt offer',
    notes: 'Employer must obtain positive or neutral LMIA',
  },
  {
    id: 'canada_caq',
    documentType: 'acceptance_letter',
    tags: ['Canada'],
    visaTypes: ['student'],
    description: 'Certificat d\'Acceptation du Québec (CAQ) for Quebec institutions',
    notes: 'Required in addition to study permit for Quebec',
  },

  // United States
  {
    id: 'us_ds160',
    documentType: 'visa_application_form',
    tags: ['United States'],
    visaTypes: ['ALL'],
    description: 'DS-160 Online Visa Application confirmation page',
    notes: 'Must be completed online before interview',
  },
  {
    id: 'us_sevis',
    documentType: 'acceptance_letter',
    tags: ['United States'],
    visaTypes: ['student'],
    description: 'SEVIS I-20 form from the US institution',
    notes: 'Pay SEVIS I-901 fee before visa interview',
  },
  {
    id: 'us_interview',
    documentType: 'passport',
    tags: ['United States'],
    visaTypes: ['ALL'],
    description: 'In-person visa interview at US Embassy/Consulate',
    notes: 'Most applicants aged 14-79 must appear in person',
  },
  {
    id: 'us_work_certification',
    documentType: 'employment_letter',
    tags: ['United States'],
    visaTypes: ['work'],
    description: 'USCIS petition approval (Form I-129 or I-140)',
    notes: 'Employer must file petition before you apply for visa',
  },

  // United Kingdom
  {
    id: 'uk_cas',
    documentType: 'acceptance_letter',
    tags: ['United Kingdom'],
    visaTypes: ['student'],
    description: 'Confirmation of Acceptance for Studies (CAS) number',
    notes: 'Issued by the educational institution',
  },
  {
    id: 'uk_cos',
    documentType: 'employment_letter',
    tags: ['United Kingdom'],
    visaTypes: ['work'],
    description: 'Certificate of Sponsorship (CoS) from employer',
    notes: 'Employer must be a licensed sponsor',
  },
  {
    id: 'uk_health_surcharge',
    documentType: 'travel_insurance',
    tags: ['United Kingdom'],
    visaTypes: ['ALL'],
    description: 'Immigration Health Surcharge (IHS) payment receipt',
    notes: '£624-£1,035 per year depending on visa type',
  },
  {
    id: 'uk_english_test',
    documentType: 'english_test',
    tags: ['United Kingdom'],
    visaTypes: ['student', 'work'],
    description: 'SELT (Secure English Language Test) from approved provider',
    notes: 'Specific tests: IELTS for UKVI, PTE Academic UKVI, etc.',
  },

  // Germany / Schengen
  {
    id: 'germany_blocked_account',
    documentType: 'blocked_account',
    tags: ['Germany'],
    visaTypes: ['student'],
    description: 'Blocked bank account (Sperrkonto) with €11,904 for first year',
    notes: 'Must be opened before applying',
  },
  {
    id: 'germany_health_insurance',
    documentType: 'travel_insurance',
    tags: ['Germany'],
    visaTypes: ['ALL'],
    description: 'Health insurance covering the entire stay',
    notes: 'Public or private insurance accepted; Schengen travel insurance for short stays',
  },
  {
    id: 'germany_aps',
    documentType: 'qualifications',
    tags: ['Germany'],
    visaTypes: ['student'],
    description: 'APS certificate for applicants from China, Vietnam, Mongolia',
    notes: 'Academic evaluation required',
  },
  {
    id: 'germany_work_approval',
    documentType: 'employment_letter',
    tags: ['Germany'],
    visaTypes: ['work'],
    description: 'Federal Employment Agency (Bundesagentur für Arbeit) approval',
    notes: 'Check if job is on the shortage occupation list',
  },

  // Australia
  {
    id: 'australia_genuine_temporary',
    documentType: 'letter_of_intent',
    tags: ['Australia'],
    visaTypes: ['student', 'work', 'tourist'],
    description: 'Genuine Temporary Entrant (GTE) or Genuine Student (GS) statement',
    notes: 'Required for most temporary visas',
  },
  {
    id: 'australia_health_insurance_oshc',
    documentType: 'travel_insurance',
    tags: ['Australia'],
    visaTypes: ['student'],
    description: 'Overseas Student Health Cover (OSHC)',
    notes: 'Must be held for duration of student visa',
  },
  {
    id: 'australia_skills_assessment',
    documentType: 'qualifications',
    tags: ['Australia'],
    visaTypes: ['work', 'permanent_residence'],
    description: 'Skills assessment from relevant assessing authority',
    notes: 'Required for skilled migration visas',
  },
  {
    id: 'australia_expression_interest',
    documentType: 'visa_application_form',
    tags: ['Australia'],
    visaTypes: ['work', 'permanent_residence'],
    description: 'Expression of Interest (EOI) via SkillSelect (SkillSelect/ImmiAccount)',
    notes: 'Points-based system for skilled migration',
  },

  // UAE
  {
    id: 'uae_employment_offer',
    documentType: 'employment_letter',
    tags: ['United Arab Emirates'],
    visaTypes: ['work'],
    description: 'Employment contract attested by Ministry of Human Resources',
    notes: 'Employer usually sponsors the visa',
  },
  {
    id: 'uae_medical_fitness',
    documentType: 'medical_certificate',
    tags: ['United Arab Emirates'],
    visaTypes: ['work', 'permanent_residence'],
    description: 'Medical fitness test (including HIV, Hepatitis B/C, TB)',
    notes: 'Done at approved government health centers in UAE',
  },
  {
    id: 'uae_id_application',
    documentType: 'passport_photo_page',
    tags: ['United Arab Emirates'],
    visaTypes: ['work', 'permanent_residence'],
    description: 'Emirates ID application',
    notes: 'Required for residency visa holders',
  },

  // Japan
  {
    id: 'japan_certificate_eligibility',
    documentType: 'employment_letter',
    tags: ['Japan'],
    visaTypes: ['work'],
    description: 'Certificate of Eligibility (COE) from Japanese Immigration',
    notes: 'Employer or sponsor applies on your behalf',
  },
  {
    id: 'japan_guarantor',
    documentType: 'sponsorship_letter',
    tags: ['Japan'],
    visaTypes: ['ALL'],
    description: 'Guarantor letter from a resident in Japan',
    notes: 'The guarantor vouches for your stay and conduct',
  },

  // China
  {
    id: 'china_invitation',
    documentType: 'invitation_letter',
    tags: ['China'],
    visaTypes: ['tourist', 'business'],
    description: 'Invitation letter from a Chinese organization or individual',
    notes: 'For business visas: from a registered Chinese company',
  },
  {
    id: 'china_travel_schedule',
    documentType: 'travel_itinerary',
    tags: ['China'],
    visaTypes: ['tourist'],
    description: 'Round-trip flight and hotel bookings',
    notes: 'Detailed itinerary including cities and dates',
  },

  // South Africa
  {
    id: 'south_africa_yellow_fever',
    documentType: 'medical_certificate',
    tags: ['South Africa'],
    visaTypes: ['ALL'],
    description: 'Yellow fever vaccination certificate (if from endemic country)',
    notes: 'Required if traveling from or through yellow fever endemic zones',
  },
  {
    id: 'south_africa_spousal_consent',
    documentType: 'marriage_certificate',
    tags: ['South Africa'],
    visaTypes: ['ALL'],
    description: 'Spousal consent for minors traveling with one parent',
    notes: 'Affidavit from non-traveling parent',
  },

  // India
  {
    id: 'india_evisa_photo',
    documentType: 'photograph',
    tags: ['India'],
    visaTypes: ['tourist', 'business', 'medical'],
    description: 'Digital photo for e-Visa application (square format, white background)',
    notes: 'e-Visa available for citizens of many countries',
  },
]

// ── Helper Functions ──────────────────────────────────────────────────────

/**
 * Get requirements applicable to a specific country and visa type.
 * Merges [ALL]-tagged requirements with country-specific ones.
 */
export function getRequirementsForCountry(country, visaType) {
  if (!country || !visaType) return []

  return REQUIREMENTS.filter((req) => {
    // Must match visa type
    const matchesVisa = req.visaTypes.includes('ALL') || req.visaTypes.includes(visaType)
    if (!matchesVisa) return false

    // Must match tag
    const matchesTag = req.tags.includes('ALL') || req.tags.includes(country)
    return matchesTag
  })
}

/**
 * Get available visa types for a country (those with defined requirements).
 */
export function getVisaTypesForCountry(country) {
  if (!country) return []

  const types = new Set()
  for (const req of REQUIREMENTS) {
    if (req.tags.includes('ALL') || req.tags.includes(country)) {
      for (const vt of req.visaTypes) {
        if (vt !== 'ALL') types.add(vt)
      }
    }
  }

  return VISA_TYPES.filter((vt) => types.has(vt.id))
}

/**
 * Get default visa types when no specific requirements exist.
 */
export function getDefaultVisaTypes() {
  return VISA_TYPES.slice(0, 5) // tourist, work, student, business, permanent_residence
}

/**
 * Format the visa type ID to a readable label.
 */
export function getVisaLabel(visaTypeId) {
  const found = VISA_TYPES.find((vt) => vt.id === visaTypeId)
  return found?.label || visaTypeId
}

/**
 * Get document type label.
 */
export function getDocTypeLabel(docTypeId) {
  return DOCUMENT_TYPES[docTypeId] || docTypeId || 'Unknown Document'
}

/**
 * Get list of document type IDs that a requirement expects.
 */
export function getRequiredDocTypeIds(country, visaType) {
  const reqs = getRequirementsForCountry(country, visaType)
  return [...new Set(reqs.map((r) => r.documentType))]
}