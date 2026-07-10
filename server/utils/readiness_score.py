"""
Readiness score calculation and assessment logic.
"""

from typing import Optional


def calculate_readiness_score(
    classifications: list[dict],
    visa_type: str,
) -> dict:
    """
    Calculate readiness score based on document classifications.
    Returns a dict with individual category scores and overall score.
    """
    required_docs = get_required_document_types(visa_type)
    submitted_types = set(
        c.get("classified_as", "").lower()
        for c in classifications
        if c.get("classified_as")
    )

    # Documentation completeness
    docs_found = sum(1 for d in required_docs if d.lower() in submitted_types)
    documentation_completeness = round((docs_found / len(required_docs)) * 100) if required_docs else 50

    # Confidence average
    confidences = [c.get("confidence", 0) for c in classifications if c.get("confidence") is not None]
    avg_confidence = round((sum(confidences) / len(confidences)) * 100) if confidences else 0

    # Issues count penalties
    total_issues = sum(len(c.get("issues", [])) for c in classifications if c.get("issues"))
    issue_penalty = min(total_issues * 10, 50)

    # Information consistency (higher avg confidence = more consistent)
    information_consistency = max(0, min(100, avg_confidence - issue_penalty))

    # Financial readiness (check for bank statements)
    has_financial_docs = "bank_statement" in submitted_types
    financial_readiness = 80 if has_financial_docs else 20

    # Overall score
    overall_readiness = round(
        (documentation_completeness * 0.35)
        + (information_consistency * 0.30)
        + (financial_readiness * 0.20)
        + (avg_confidence * 0.15)
    )

    return {
        "documentation_completeness": documentation_completeness,
        "document_validity": avg_confidence,
        "information_consistency": information_consistency,
        "financial_readiness": financial_readiness,
        "overall_readiness": min(100, overall_readiness),
    }


def get_required_document_types(visa_type: str) -> list[str]:
    """Get the required document types for a given visa type."""
    requirements = {
        "canada_work": [
            "passport",
            "employment_letter",
            "bank_statement",
            "work_permit_application",
        ],
        "canada_student": [
            "passport",
            "academic_transcript",
            "bank_statement",
            "acceptance_letter",
        ],
        "germany_student": [
            "passport",
            "academic_transcript",
            "bank_statement",
            "health_insurance",
            "acceptance_letter",
        ],
        "south_africa_work": [
            "passport",
            "employment_letter",
            "qualification_certificate",
            "medical_report",
        ],
    }
    return requirements.get(visa_type, ["passport"])


def get_visa_type_label(visa_type: str) -> str:
    """Get a human-readable label for a visa type code."""
    labels = {
        "canada_work": "Canada Work Visa",
        "canada_student": "Canada Student Visa",
        "germany_student": "Germany Student Visa",
        "south_africa_work": "South Africa Work Visa",
    }
    return labels.get(visa_type, visa_type.replace("_", " ").title())