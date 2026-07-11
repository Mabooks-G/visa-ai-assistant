"""
Global visa system constants.
195 sovereign countries, 5 visa types, and universal requirement definitions.
Requirements use [ALL] tag for universal requirements or specific country tags.
"""

# ── All 195 Sovereign Countries ────────────────────────────────────────────

COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda",
    "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan",
    "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize",
    "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil",
    "Brunei", "Bulgaria", "Burkina Faso", "Burundi",
    "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic",
    "Chad", "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica",
    "Côte d'Ivoire", "Croatia", "Cuba", "Cyprus", "Czech Republic",
    "Denmark", "Djibouti", "Dominica", "Dominican Republic",
    "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia",
    "Eswatini", "Ethiopia",
    "Fiji", "Finland", "France",
    "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada",
    "Guatemala", "Guinea", "Guinea-Bissau", "Guyana",
    "Haiti", "Honduras", "Hungary",
    "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy",
    "Jamaica", "Japan", "Jordan",
    "Kazakhstan", "Kenya", "Kiribati", "South Korea", "Kosovo", "Kuwait", "Kyrgyzstan",
    "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein",
    "Lithuania", "Luxembourg",
    "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands",
    "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia",
    "Montenegro", "Morocco", "Mozambique", "Myanmar",
    "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger",
    "Nigeria", "North Korea", "North Macedonia", "Norway",
    "Oman",
    "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay",
    "Peru", "Philippines", "Poland", "Portugal",
    "Qatar",
    "Romania", "Russia", "Rwanda",
    "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines",
    "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal",
    "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia",
    "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain",
    "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria",
    "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo",
    "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu",
    "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom",
    "United States", "Uruguay", "Uzbekistan",
    "Vanuatu", "Vatican City", "Venezuela", "Vietnam",
    "Yemen",
    "Zambia", "Zimbabwe",
]

# ── Visa Types ────────────────────────────────────────────────────────────

VISA_TYPES = [
    {"id": "tourist", "label": "Tourist Visa"},
    {"id": "work", "label": "Work Visa"},
    {"id": "study", "label": "Study Visa"},
    {"id": "permanent_residence", "label": "Permanent Residence"},
    {"id": "asylum", "label": "Asylum Seeker"},
]

VISA_TYPE_IDS = [v["id"] for v in VISA_TYPES]

# ── Recognised Document Types ────────────────────────────────────────────

DOCUMENT_TYPES = [
    "passport",
    "photograph",
    "birth_certificate",
    "marriage_certificate",
    "police_clearance",
    "medical_certificate",
    "bank_statement",
    "employment_letter",
    "payslips",
    "tax_returns",
    "invitation_letter",
    "travel_itinerary",
    "accommodation_proof",
    "travel_insurance",
    "acceptance_letter",
    "english_test",
    "qualifications",
    "transcript",
    "cv_resume",
    "company_documents",
    "sponsorship_letter",
    "proof_of_funds",
    "blocked_account",
    "passport_photo_page",
    "visa_application_form",
    "previous_visas",
    "letter_of_intent",
    "proof_of_address",
    "no_objection",
    "medical_report",
    "other",
]

# ── Universal Requirements per Visa Type ──────────────────────────────────
# Structure: {visa_type_id: [{document_type, label, required, tags: [country or ALL]}]}

UNIVERSAL_REQUIREMENTS = {
    "tourist": [
        {"document_type": "passport", "label": "Valid Passport", "required": True, "tags": ["ALL"]},
        {"document_type": "visa_application_form", "label": "Completed Visa Application Form", "required": True, "tags": ["ALL"]},
        {"document_type": "photograph", "label": "Recent Passport-sized Photograph", "required": True, "tags": ["ALL"]},
        {"document_type": "proof_of_funds", "label": "Proof of Sufficient Financial Means", "required": True, "tags": ["ALL"]},
        {"document_type": "travel_itinerary", "label": "Travel Itinerary", "required": True, "tags": ["ALL"]},
        {"document_type": "accommodation_proof", "label": "Round-trip Flight Reservation", "required": False, "tags": ["ALL"]},
        {"document_type": "accommodation_proof", "label": "Proof of Accommodation", "required": True, "tags": ["ALL"]},
        {"document_type": "travel_insurance", "label": "Travel Medical Insurance", "required": True, "tags": ["ALL"]},
        {"document_type": "bank_statement", "label": "Visa Application Fee Payment Receipt", "required": True, "tags": ["ALL"]},
        {"document_type": "letter_of_intent", "label": "Cover Letter (Purpose of Visit)", "required": True, "tags": ["ALL"]},
    ],
    "work": [
        {"document_type": "passport", "label": "Valid Passport", "required": True, "tags": ["ALL"]},
        {"document_type": "visa_application_form", "label": "Completed Visa Application Form", "required": True, "tags": ["ALL"]},
        {"document_type": "photograph", "label": "Recent Passport-sized Photograph", "required": True, "tags": ["ALL"]},
        {"document_type": "employment_letter", "label": "Employment Offer or Employment Contract", "required": True, "tags": ["ALL"]},
        {"document_type": "sponsorship_letter", "label": "Employer Sponsorship Letter (if applicable)", "required": False, "tags": ["ALL"]},
        {"document_type": "qualifications", "label": "Proof of Qualifications or Professional Certificates", "required": True, "tags": ["ALL"]},
        {"document_type": "cv_resume", "label": "Curriculum Vitae (CV)", "required": True, "tags": ["ALL"]},
        {"document_type": "police_clearance", "label": "Police Clearance Certificate", "required": True, "tags": ["ALL"]},
        {"document_type": "medical_certificate", "label": "Medical Examination Report", "required": True, "tags": ["ALL"]},
        {"document_type": "proof_of_funds", "label": "Proof of Sufficient Financial Means (if required)", "required": False, "tags": ["ALL"]},
        {"document_type": "bank_statement", "label": "Visa Application Fee Payment Receipt", "required": True, "tags": ["ALL"]},
    ],
    "study": [
        {"document_type": "passport", "label": "Valid Passport", "required": True, "tags": ["ALL"]},
        {"document_type": "visa_application_form", "label": "Completed Visa Application Form", "required": True, "tags": ["ALL"]},
        {"document_type": "photograph", "label": "Recent Passport-sized Photograph", "required": True, "tags": ["ALL"]},
        {"document_type": "acceptance_letter", "label": "Letter of Acceptance from Educational Institution", "required": True, "tags": ["ALL"]},
        {"document_type": "proof_of_funds", "label": "Proof of Tuition Payment or Scholarship", "required": True, "tags": ["ALL"]},
        {"document_type": "proof_of_funds", "label": "Proof of Sufficient Financial Means", "required": True, "tags": ["ALL"]},
        {"document_type": "transcript", "label": "Academic Transcripts and Certificates", "required": True, "tags": ["ALL"]},
        {"document_type": "medical_certificate", "label": "Medical Examination Report", "required": True, "tags": ["ALL"]},
        {"document_type": "police_clearance", "label": "Police Clearance Certificate", "required": True, "tags": ["ALL"]},
        {"document_type": "travel_insurance", "label": "Health Insurance", "required": True, "tags": ["ALL"]},
        {"document_type": "bank_statement", "label": "Visa Application Fee Payment Receipt", "required": True, "tags": ["ALL"]},
    ],
    "permanent_residence": [
        {"document_type": "passport", "label": "Valid Passport", "required": True, "tags": ["ALL"]},
        {"document_type": "visa_application_form", "label": "Completed Permanent Residence Application Form", "required": True, "tags": ["ALL"]},
        {"document_type": "photograph", "label": "Recent Passport-sized Photograph", "required": True, "tags": ["ALL"]},
        {"document_type": "birth_certificate", "label": "Birth Certificate", "required": True, "tags": ["ALL"]},
        {"document_type": "marriage_certificate", "label": "Marriage Certificate (if applicable)", "required": False, "tags": ["ALL"]},
        {"document_type": "police_clearance", "label": "Police Clearance Certificate", "required": True, "tags": ["ALL"]},
        {"document_type": "medical_certificate", "label": "Medical Examination Report", "required": True, "tags": ["ALL"]},
        {"document_type": "proof_of_funds", "label": "Proof of Financial Stability", "required": True, "tags": ["ALL"]},
        {"document_type": "employment_letter", "label": "Employment History or Proof of Income", "required": True, "tags": ["ALL"]},
        {"document_type": "proof_of_address", "label": "Proof of Residence", "required": True, "tags": ["ALL"]},
        {"document_type": "english_test", "label": "Language Proficiency Certificate (if required)", "required": False, "tags": ["ALL"]},
        {"document_type": "bank_statement", "label": "Visa Application Fee Payment Receipt", "required": True, "tags": ["ALL"]},
    ],
    "asylum": [
        {"document_type": "passport", "label": "Valid Passport or Identity Document (if available)", "required": False, "tags": ["ALL"]},
        {"document_type": "visa_application_form", "label": "Completed Asylum Application Form", "required": True, "tags": ["ALL"]},
        {"document_type": "photograph", "label": "Recent Passport-sized Photograph", "required": True, "tags": ["ALL"]},
        {"document_type": "letter_of_intent", "label": "Statement Explaining the Need for Asylum", "required": True, "tags": ["ALL"]},
        {"document_type": "invitation_letter", "label": "Evidence Supporting the Asylum Claim (if available)", "required": False, "tags": ["ALL"]},
        {"document_type": "passport_photo_page", "label": "Proof of Identity", "required": True, "tags": ["ALL"]},
        {"document_type": "travel_itinerary", "label": "Travel History", "required": True, "tags": ["Nigeria", "Somalia"]},
        {"document_type": "police_clearance", "label": "Police Report or Supporting Legal Documents (if applicable)", "required": False, "tags": ["ALL"]},
        {"document_type": "medical_report", "label": "Medical Records (if relevant)", "required": False, "tags": ["ALL"]},
        {"document_type": "letter_of_intent", "label": "Interpreter Request (if required)", "required": False, "tags": ["ALL"]},
    ],
}

# Status enums
STATUS_APPLICATION = ["in_progress", "analyzed", "under_review", "approved", "rejected", "needs_info"]
STATUS_DOCUMENT = ["pending", "processing", "verified", "rejected"]