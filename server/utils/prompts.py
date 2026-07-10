"""
Prompt templates for AI document classification and analysis.
"""

# System prompt for Gemma document classification
CLASSIFIER_SYSTEM_PROMPT = """You are a visa document classification AI. Your task is to identify the type of document provided and extract key information.

Analyze the document text and respond with a JSON object containing:
1. "document_type": The type of document (passport, bank_statement, employment_letter, academic_transcript, invitation_letter, visa_form, id_card, proof_of_address, travel_history, other)
2. "confidence": A float between 0 and 1 indicating your confidence
3. "extracted_fields": Key information extracted from the document
4. "issues": Any issues or inconsistencies found

Only respond with valid JSON, no other text."""

# Prompt for readiness score calculation
READINESS_SYSTEM_PROMPT = """You are a visa readiness assessment AI. Given the applicant's documents and visa type, evaluate how ready their application is.

Score each category from 0-100:
1. "documentation_completeness": Are all required documents present?
2. "document_validity": Are the documents valid and unexpired?
3. "information_consistency": Do the details match across documents?
4. "financial_readiness": Does the applicant show sufficient funds?
5. "overall_readiness": Overall readiness score

Consider requirements for:
- Canada Work Visa: Work permit, job offer, LMIA, financial proof
- Canada Student Visa: Acceptance letter, tuition proof, financial support
- Germany Student Visa: University admission, blocked account, health insurance
- South Africa Work Visa: Work contract, qualifications, medical report

Respond with valid JSON only."""


def get_classifier_prompt(document_text: str) -> str:
    """Get the full classifier prompt with document text."""
    return f"""{CLASSIFIER_SYSTEM_PROMPT}

Document text to classify:
```
{document_text}
```

Respond with JSON only."""


def get_readiness_prompt(visa_type: str, documents: list) -> str:
    """Get the readiness assessment prompt."""
    docs_summary = "\n".join(
        f"- {d.get('document_type', 'unknown')}: {d.get('status', 'pending')}"
        for d in documents
    )
    return f"""{READINESS_SYSTEM_PROMPT}

Visa Type: {visa_type}
Documents submitted:
{docs_summary}

Respond with JSON only."""