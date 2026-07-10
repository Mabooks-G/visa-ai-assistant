"""
Report service — compiles comprehensive visa readiness reports from all analysis sources.

Combines OCR output, classification data, validation results, requirement checks,
and Gemma AI scoring into a single structured readiness report.
"""

import logging
from datetime import datetime
from typing import Optional

from services import (
    ocr_service,
    classifier_service,
    validation_service,
    requirement_service,
    gemma_service,
)

logger = logging.getLogger(__name__)


def generate_report(
    application: dict,
    documents: list[dict],
    visa_country: str,
    visa_type: str,
) -> dict:
    """
    Generate a full readiness report for a visa application.

    Args:
        application: Application dict (id, applicant_name, etc.)
        documents: List of document dicts with 'extracted_text', 'file_name', etc.
        visa_country: Target country
        visa_type: Visa category (student, work, etc.)

    Returns:
        Comprehensive report dict with all analysis sections.
    """
    report = {
        "report_id": f"RPT-{application.get('id', '')[:8]}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "application": {
            "id": application.get("id", ""),
            "applicant_name": application.get("applicant_name", ""),
            "visa_type": visa_type,
            "country": visa_country,
            "status": application.get("status", "draft"),
        },
        "document_analysis": [],
        "document_completeness": {},
        "validation_results": {},
        "ai_readiness_score": {},
        "summary": {},
    }

    # ── Step 1: Classify each document ──────────────────────────────────────
    classified_docs = []
    for doc in documents:
        text = doc.get("extracted_text", doc.get("text", "")) or ""
        filename = doc.get("file_name", "") or ""

        classification = classifier_service.classify_document(text, filename)

        # Run validation on the document content
        validation_issues = validation_service.validate_document_content(
            text, classification.get("document_type", "unknown")
        )

        entry = {
            "document_id": doc.get("id", ""),
            "file_name": filename,
            "document_type": classification.get("document_type", "unknown"),
            "confidence": classification.get("confidence", 0),
            "issuing_country": classification.get("issuing_country", "unknown"),
            "summary": classification.get("summary", ""),
            "validation_issues": validation_issues,
            "critical_issues": [i for i in validation_issues if i.get("severity") == "critical"],
            "warning_issues": [i for i in validation_issues if i.get("severity") == "warning"],
        }

        report["document_analysis"].append(entry)
        classified_docs.append(classification)

    # ── Step 2: Check document completeness against requirements ────────────
    completeness = requirement_service.check_document_completeness(
        visa_country, visa_type, classified_docs
    )
    report["document_completeness"] = completeness

    # ── Step 3: Cross-document validation ───────────────────────────────────
    validation_result = validation_service.validate_application(
        [{"extracted_text": d.get("extracted_text", ""), "document_type": c.get("document_type")}
         for d, c in zip(documents, classified_docs)],
        visa_type,
        visa_country,
    )
    report["validation_results"] = validation_result

    # ── Step 4: AI readiness scoring via Gemma ──────────────────────────────
    try:
        ai_score = gemma_service.score_application(classified_docs, visa_type, visa_country)
        report["ai_readiness_score"] = ai_score
    except Exception as exc:
        logger.error(f"Gemma scoring failed: {exc}")
        report["ai_readiness_score"] = {
            "overall_score": completeness.get("completeness_pct", 0) if not validation_result.get("critical_count") else max(0, completeness.get("completeness_pct", 0) - 20),
            "category_scores": {"documents": completeness.get("completeness_pct", 0)},
            "missing_documents": completeness.get("missing", []),
            "recommendations": ["AI scoring is temporarily unavailable — score is based on document completeness only."],
            "critical_issues": validation_result.get("all_issues", []),
        }

    # ── Step 5: Executive summary ───────────────────────────────────────────
    doc_total = len(documents)
    doc_valid = sum(
        1 for d in report["document_analysis"] if not d.get("critical_issues")
    )
    overall_score = report["ai_readiness_score"].get("overall_score", 0)

    report["summary"] = {
        "total_documents": doc_total,
        "valid_documents": doc_valid,
        "issues_found": validation_result.get("critical_count", 0) + validation_result.get("warning_count", 0),
        "completeness_pct": completeness.get("completeness_pct", 0),
        "overall_score": overall_score,
        "verdict": _get_verdict(overall_score, validation_result.get("critical_count", 0)),
    }

    return report


def _get_verdict(score: float, critical_issues: int) -> str:
    """Produce a plain-text verdict from the readiness data."""
    if critical_issues > 0:
        return "Application has critical issues that must be resolved before submission."
    if score >= 80:
        return "Application appears well-prepared. Ready for submission."
    if score >= 60:
        return "Application is mostly complete. Address the warnings before submission."
    return "Application needs significant improvement. See recommendations for details."


def health() -> dict:
    """Return report service health."""
    return {"available": True}