# Supported countries
COUNTRIES = {
    'canada': 'Canada',
    'germany': 'Germany',
    'south_africa': 'South Africa',
}

# Visa type definitions
VISA_TYPES = {
    'canada_work': {'country': 'canada', 'label': 'Canada Work Visa'},
    'canada_student': {'country': 'canada', 'label': 'Canada Student Visa'},
    'germany_student': {'country': 'germany', 'label': 'Germany Student Visa'},
    'south_africa_work': {'country': 'south_africa', 'label': 'South Africa Work Visa'},
}

# Recognised document types for classification
DOCUMENT_TYPES = [
    'passport',
    'bank_statement',
    'photograph',
    'travel_itinerary',
    'accommodation_proof',
    'acceptance_letter',
    'english_test',
    'employment_contract',
    'qualifications',
    'invitation_letter',
    'company_documents',
    'other',
]

# Default requirements per visa type (used when no DB override exists)
DEFAULT_REQUIREMENTS = {
    'canada_work': [
        {'type': 'passport', 'label': 'Passport', 'required': True},
        {'type': 'employment_contract', 'label': 'Employment Letter', 'required': True},
        {'type': 'bank_statement', 'label': 'Bank Statement', 'required': True},
        {'type': 'qualifications', 'label': 'Educational Certificates', 'required': True},
        {'type': 'photograph', 'label': 'Passport Photograph', 'required': True},
    ],
    'canada_student': [
        {'type': 'passport', 'label': 'Passport', 'required': True},
        {'type': 'acceptance_letter', 'label': 'Acceptance Letter', 'required': True},
        {'type': 'bank_statement', 'label': 'Bank Statement', 'required': True},
        {'type': 'english_test', 'label': 'English Test Score', 'required': True},
        {'type': 'photograph', 'label': 'Passport Photograph', 'required': True},
    ],
    'germany_student': [
        {'type': 'passport', 'label': 'Passport', 'required': True},
        {'type': 'acceptance_letter', 'label': 'Acceptance Letter', 'required': True},
        {'type': 'bank_statement', 'label': 'Blocked Account Proof', 'required': True},
        {'type': 'english_test', 'label': 'English Test Score', 'required': True},
        {'type': 'photograph', 'label': 'Passport Photograph', 'required': True},
        {'type': 'accommodation_proof', 'label': 'Health Insurance', 'required': True},
    ],
    'south_africa_work': [
        {'type': 'passport', 'label': 'Passport', 'required': True},
        {'type': 'employment_contract', 'label': 'Employment Contract', 'required': True},
        {'type': 'bank_statement', 'label': 'Bank Statement', 'required': True},
        {'type': 'qualifications', 'label': 'CV/Resume', 'required': True},
        {'type': 'photograph', 'label': 'Passport Photograph', 'required': True},
    ],
}

# Status enums
STATUS_APPLICATION = ['in_progress', 'verified', 'rejected', 'needs_review']
STATUS_DOCUMENT = ['pending', 'processing', 'verified', 'rejected']