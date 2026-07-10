"""
Validation service — validates extracted document text against business rules.

Performs checks for:
  - Expiry dates
  - Name consistency across documents
  - Passport number formats
  - Minimum required fields presence
  - Document-specific validations
"""

import re
import logging
from datetime import datetime, date
from typing import Optional

logger = logging.getLogger(__name__)

# ── Helper regex patterns ──────────────────────────────────────────────────────

_DATE_PATTERNS = [
    (re.compile(r"(\d{4}[-/]\d{2}[-/]\d{2})"), "%Y-%m-%d"),
    (re.compile(r"(\d{2}[-/]\d{2}[-/]\d{4})"), "%d-%m-%Y"),
    (re.compile(r"(\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})"), "%d %b %Y"),
    (re.compile(r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2},?\s+\d{4})"), "%b %d %Y"),
]

_PASSPORT_PATTERNS = [
    re.compile(r"[A-Z]{1,2}\d{6,9}"),  # Generic passport number
    re.compile(r"P\d{7}"),             # Some country formats
]

_EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
_PHONE_PATTERN = re.compile(r"\+?\d{1,4}[\s.-]?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,4}")


# ── Date extraction ────────────────────────────────────────────────────────────

def extract_date(text: str) -> Optional[datetime]:
    """Extract the first valid date found in the text."""
    for pattern, fmt in _DATE_PATTERNS:
        match = pattern.search(text)
        if match:
            try:
                return datetime.strptime(match.group(1), fmt)
            except ValueError:
                continue
    return None


def extract_all_dates(text: str) -> list[datetime]:
    """Extract all valid dates from the text."""
    dates = []
    for pattern, fmt in _DATE_PATTERNS:
        for match in pattern.finditer(text):
            try:
                dates.append(datetime.strptime(match.group(1), fmt))
            except ValueError:
                continue
    return dates


# ── Validation functions ───────────────────────────────────────────────────────

def validate_expiry_date(expiry_date_str: str) -> list[dict]:
    """Check whether a document is expired or expiring soon."""
    issues = []
    expiry = extract_date(expiry_date_str)
    if expiry:
        today = datetime.now()
        if expiry < today:
            issues.append({
                "field": "expiry_date",
                "message": "Document is expired.",
                "severity": "critical",
            })
        elif (expiry - today).days < 90:
            issues.append({
                "field": "expiry_date",
                "message": "Document expires within 90 days.",
                "severity": "warning",
            })
    return issues


def validate_name_consistency(names: list[str]) -> list[dict]:
    """Check if names across documents are consistent."""
    issues = []
    if len(names) < 2:
        return issues

    normalized = [n.strip().lower() for n in names if n]
    if len(set(normalized)) > 1:
        issues.append({
            "field": "applicant_name",
            "message": f"Name inconsistency detected across documents: {set(names)}",
            "severity": "critical",
        })
    return issues


def validate_passport_format(passport_number: str) -> list[dict]:
    """Basic passport number format validation."""
    issues = []
    if not passport_number:
        return issues

    clean = passport_number.strip().upper()
    if not any(p.fullmatch(clean) for p in _PASSPORT_PATTERNS):
        issues.append({
            "field": "passport_number",
            "message": "Passport number format may be invalid.",
            "severity": "warning",
        })
    return issues


def validate_document_content(text: str, doc_type: str) -> list[dict]:
    """
    Run type-specific content checks on extracted document text.
    Returns a list of issues (each with field, message, severity).
    """
    issues = []
    text_lower = text.lower()

    if doc_type == "passport":
        if not _has_any(text_lower, ["passport", "pass no", "passport no", "nationality"]):
            issues.append({
                "field": "content",
                "message": "Does not appear to be a valid passport document.",
                "severity": "critical",
            })
        if not _PASSPORT_PATTERNS[0].search(text):
            issues.append({
                "field": "passport_number",
                "message": "Passport number not found in document.",
                "severity": "critical",
            })

    elif doc_type == "bank_statement":
        if not _has_any(text_lower, ["bank", "account", "statement", "balance", "transaction"]):
            issues.append({
                "field": "content",
                "message": "Does not appear to be a valid bank statement.",
                "severity": "critical",
            })
        dates = extract_all_dates(text)
        if len(dates) < 2:
            issues.append({
                "field": "date_range",
                "message": "Statement period not clearly identified.",
                "severity": "warning",
            })

    elif doc_type == "degree_certificate":
        if not _has_any(text_lower, ["degree", "certificate", "graduate", "bachelor", "master", "phd", "diploma"]):
            issues.append({
                "field": "content",
                "message": "Does not appear to be a valid degree certificate.",
                "severity": "critical",
            })

    elif doc_type == "english_test":
        if not _has_any(text_lower, ["ielts", "toefl", "score", "band", "pte", "english"]):
            issues.append({
                "field": "content",
                "message": "Does not appear to be a valid English language test result.",
                "severity": "critical",
            })

    elif doc_type == "medical_report":
        if not _has_any(text_lower, ["medical", "health", "examination", "doctor", "physician", "clinic"]):
            issues.append({
                "field": "content",
                "message": "Does not appear to be a valid medical report.",
                "severity": "warning",
            })

    elif doc_type == "police_clearance":
        if not _has_any(text_lower, ["police", "clearance", "criminal", "record", "good conduct"]):
            issues.append({
                "field": "content",
                "message": "Does not appear to be a valid police clearance certificate.",
                "severity": "critical",
            })
        # Check for an expiry date
        dates = extract_all_dates(text)
        if dates:
            latest = max(dates)
            if latest.year < 2020:
                issues.append({
                    "field": "issue_date",
                    "message": "Police clearance appears to be older than expected.",
                    "severity": "warning",
                })

    elif doc_type == "work_experience":
        if not _has_any(text_lower, ["employment", "employer", "position", "job", "worked", "experience"]):
            issues.append({
                "field": "content",
                "message": "Does not appear to be a valid work experience letter.",
                "severity": "warning",
            })

    return issues


def _has_any(text: str, keywords: list[str]) -> bool:
    """Check if any keyword appears in the text."""
    return any(kw in text for kw in keywords)


def validate_application(documents: list[dict], visa_type: str, country: str) -> dict:
    """
    Run all validations across an application's documents.

    Args:
        documents: List of classified document summaries
        visa_type: e.g. "student", "work"
        country: Destination country

    Returns:
        dict with:
          - all_issues: list of all issues found
          - critical_count: int
          - warning_count: int
          - passed: bool (true if zero critical issues)
    """
    all_issues = []
    names_found = []

    for doc in documents:
        text = doc.get("extracted_text", doc.get("text", ""))
        doc_type = doc.get("document_type", "unknown")

        # Document content validation
        content_issues = validate_document_content(text, doc_type)
        for issue in content_issues:
            issue["document_type"] = doc_type
            issue["document_id"] = doc.get("id", "")
            all_issues.append(issue)

        # Collect names for cross-document check
        if doc.get("applicant_name"):
            names_found.append(doc["applicant_name"])

    # Cross-document checks
    name_issues = validate_name_consistency(names_found)
    all_issues.extend(name_issues)

    critical_count = sum(1 for i in all_issues if i.get("severity") == "critical")
    warning_count = sum(1 for i in all_issues if i.get("severity") == "warning")

    return {
        "all_issues": all_issues,
        "critical_count": critical_count,
        "warning_count": warning_count,
        "passed": critical_count == 0,
    }


def health() -> dict:
    """Return validation service health."""
    return {"available": True}