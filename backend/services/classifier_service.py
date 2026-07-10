"""
Document classifier service — lightweight heuristic + Gemma AI fallback.

Pre-classifies documents using filename / metadata heuristics, then falls back
to the Gemma AI model when heuristics are insufficient.
"""

import re
import logging
from typing import Optional

from services.gemma_service import classify_document as gemma_classify

logger = logging.getLogger(__name__)

# Filename patterns for heuristic classification
_FILENAME_PATTERNS: list[tuple[re.Pattern, str, str]] = [
    (re.compile(r"passport", re.I), "passport", "Passport / travel document"),
    (re.compile(r"bank.?statement|bank.?letter", re.I), "bank_statement", "Bank statement or financial letter"),
    (re.compile(r"degree|diploma|certificate.*education|graduation", re.I), "degree_certificate", "Degree or education certificate"),
    (re.compile(r"transcript|academic.?record|marksheet|grade.*card", re.I), "transcript", "Academic transcript"),
    (re.compile(r"ielts|toefl|english.?test|language.?test", re.I), "english_test", "English language test score"),
    (re.compile(r"work.?exp|employ.?letter|cv|resume", re.I), "work_experience", "Employment / work experience document"),
    (re.compile(r"visa.?app|application.?form", re.I), "visa_application_form", "Visa application form"),
    (re.compile(r"photo|photograph|passport.?photo", re.I), "photograph", "Passport photograph"),
    (re.compile(r"marriage|wedding", re.I), "marriage_certificate", "Marriage certificate"),
    (re.compile(r"birth", re.I), "birth_certificate", "Birth certificate"),
    (re.compile(r"police|clearance|criminal", re.I), "police_clearance", "Police clearance certificate"),
    (re.compile(r"medical|health|doctor", re.I), "medical_report", "Medical examination report"),
    (re.compile(r"invitation|letter.*sponsor", re.I), "invitation_letter", "Invitation / sponsorship letter"),
    (re.compile(r"financial|funds|support|sponsor.?letter", re.I), "financial_support", "Financial support evidence"),
    (re.compile(r"travel.?insur|insurance", re.I), "travel_insurance", "Travel insurance policy"),
    (re.compile(r"itinerary|flight|booking|ticket", re.I), "itinerary", "Travel itinerary"),
    (re.compile(r"accommodation|hotel|housing|rental", re.I), "accommodation_proof", "Accommodation proof"),
    (re.compile(r"employment|job.?offer|contract", re.I), "employment_letter", "Employment offer / contract"),
    (re.compile(r"tax|return|assessment", re.I), "tax_return", "Tax return / assessment"),
]

_COUNTRY_KEYWORDS = {
    "canada": "Canada",
    "germany": "Germany",
    "south africa": "South Africa",
    "uk": "United Kingdom",
    "united kingdom": "United Kingdom",
    "usa": "United States",
    "united states": "United States",
    "india": "India",
    "china": "China",
    "australia": "Australia",
    "new zealand": "New Zealand",
    "france": "France",
    "spain": "Spain",
    "italy": "Italy",
    "netherlands": "Netherlands",
    "sweden": "Sweden",
    "norway": "Norway",
    "denmark": "Denmark",
    "switzerland": "Switzerland",
    "japan": "Japan",
    "south korea": "South Korea",
    "brazil": "Brazil",
    "mexico": "Mexico",
    "nigeria": "Nigeria",
    "kenya": "Kenya",
}


def classify_by_filename(filename: str) -> Optional[dict]:
    """Try to classify a document based on its filename alone."""
    for pattern, doc_type, desc in _FILENAME_PATTERNS:
        if pattern.search(filename):
            return {
                "document_type": doc_type,
                "summary": desc,
                "confidence": 0.6,
                "method": "heuristic_filename",
            }
    return None


def _guess_country(text: str) -> str:
    """Simple keyword-based country guess from the extracted text."""
    text_lower = text.lower()[:2000]
    for keyword, country in _COUNTRY_KEYWORDS.items():
        if keyword in text_lower:
            return country

    m = re.search(r"(?:issuing\s+(?:country|authority|state)|place\s+of\s+issue)\s*[:\-]?\s*(\w[\w\s]*)", text_lower)
    if m:
        return m.group(1).strip().title()

    return "unknown"


def classify_document(text: str, filename: str = "") -> dict:
    """
    Classify a document using heuristic first, then Gemma AI.

    Args:
        text: OCR-extracted text
        filename: Original filename (used for quick heuristic match)

    Returns:
        dict with document_type, issuing_country, confidence, summary
    """
    heuristic = classify_by_filename(filename)
    if heuristic and heuristic.get("confidence", 0) >= 0.6:
        logger.info(f"Heuristic classification: {filename} -> {heuristic['document_type']}")
        country = _guess_country(text)
        return {
            "document_type": heuristic["document_type"],
            "issuing_country": country,
            "confidence": heuristic["confidence"],
            "summary": heuristic["summary"],
        }

    logger.info(f"Falling back to Gemma for: {filename or 'unknown'}")
    try:
        result = gemma_classify(text)
        result.setdefault("issuing_country", "unknown")
        result.setdefault("confidence", 0.0)
        result.setdefault("summary", "")
        return result
    except Exception as exc:
        logger.error(f"Gemma classification failed: {exc}")
        return {
            "document_type": "other",
            "issuing_country": "unknown",
            "confidence": 0.0,
            "summary": "Classification unavailable due to AI model error.",
        }


def health() -> dict:
    """Return classifier service health."""
    return {"available": True}