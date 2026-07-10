"""
Analysis routes — document classification, readiness scoring, and reporting.
This is the core AI pipeline that runs on AMD Cloud GPUs.
"""

import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from server.database import db
from server.services.classifier_service import ClassifierService
from server.services.gemma_service import GemmaService
from server.services.requirement_service import RequirementService
from server.services.validation_service import ValidationService
from server.services.quality_check_service import QualityCheckService
from server.services.report_service import ReportService
from server.utils.readiness_score import calculate_readiness_score, get_visa_type_label
from server.utils.document_helpers import extract_text_from_upload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

# Service instances (singletons)
classifier = ClassifierService(use_gpu=True)
gemma = GemmaService()
requirements = RequirementService()
validator = ValidationService()
quality = QualityCheckService()
reporter = ReportService()


# ── Request / Response Models ──────────────────────────────────

class ClassifyRequest(BaseModel):
    document_text: str
    document_name: Optional[str] = ""


class BatchClassifyRequest(BaseModel):
    application_id: str


class AnalysisResult(BaseModel):
    document_id: str
    classification: dict
    validation: dict
    quality_check: dict


# ── Endpoints ──────────────────────────────────────────────────

@router.post("/classify")
def classify_document(payload: ClassifyRequest):
    """Classify a single document by text content."""
    try:
        result = classifier.classify(payload.document_text, payload.document_name)
        return result
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@router.post("/upload")
async def upload_and_classify(
    file: UploadFile = File(...),
    application_id: str = Form(...),
    visa_type: str = Form("canada_work"),
):
    """
    Upload a document, store in Supabase, classify it,
    validate it, and run quality checks — all in one call.
    """
    try:
        # Read file content
        file_content = await file.read()
        text = extract_text_from_upload(file_content, file.filename)

        # Store document in Supabase
        doc_data = {
            "application_id": application_id,
            "file_name": file.filename,
            "File_contents": text,
            "status": "processing",
        }
        document = db.create_document(doc_data)
        doc_id = document["id"]

        # Classify
        classification = classifier.classify(text, file.filename)
        doc_type = classification["document_type"]

        # Validate
        validation = validator.validate_document(text, doc_type)

        # Quality check
        quality_check = quality.check_document(text, doc_type)

        # Store classification in Supabase
        class_data = {
            "document_id": doc_id,
            "classified_as": doc_type,
            "confidence": classification["confidence"],
            "details": classification.get("extracted_fields", {}),
            "issues": classification.get("issues", []) + validation.get("issues", []),
        }
        db.create_classification(class_data)

        # Update document status
        db.update_document(doc_id, {"status": "classified"})

        return {
            "document_id": doc_id,
            "classification": classification,
            "validation": validation,
            "quality_check": quality_check,
        }

    except Exception as e:
        logger.error(f"Upload & classify error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch/{application_id}")
def classify_application(application_id: str):
    """Classify all unclassified documents for an application."""
    documents = db.get_documents(application_id)

    results = []
    for doc in documents:
        if doc.get("status") == "classified":
            continue

        text = doc.get("File_contents", "")
        if not text:
            continue

        classification = classifier.classify(text, doc.get("file_name", ""))
        doc_type = classification["document_type"]

        # Validate
        validation = validator.validate_document(text, doc_type)
        quality_check = quality.check_document(text, doc_type)

        # Store classification
        class_data = {
            "document_id": doc["id"],
            "classified_as": doc_type,
            "confidence": classification["confidence"],
            "details": classification.get("extracted_fields", {}),
            "issues": classification.get("issues", []) + validation.get("issues", []),
        }
        db.create_classification(class_data)
        db.update_document(doc["id"], {"status": "classified"})

        results.append({
            "document_id": doc["id"],
            "classification": classification,
            "validation": validation,
            "quality_check": quality_check,
        })

    return {"results": results, "count": len(results)}


@router.get("/readiness/{application_id}")
def get_readiness(application_id: str):
    """Calculate readiness score for an application."""
    application = db.get_application(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    classifications = db.get_application_classifications(application_id)
    visa_type = application.get("visa_type", "canada_work")

    # Check requirements
    requirement_check = requirements.check_document_requirements(visa_type, classifications)

    # Calculate scores
    scores = calculate_readiness_score(classifications, visa_type)

    # Update application with score
    db.update_application(application_id, {
        "overall_score": scores["overall_readiness"],
        "status": "verified" if scores["overall_readiness"] >= 70 else "needs_review",
    })

    return {
        "application_id": application_id,
        "visa_type": visa_type,
        "visa_type_label": get_visa_type_label(visa_type),
        "scores": scores,
        "requirements": requirement_check,
        "documents_classified": len(classifications),
    }


@router.get("/report/{application_id}")
def get_report(application_id: str):
    """Generate a comprehensive readiness report."""
    application = db.get_application(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    classifications = db.get_application_classifications(application_id)
    visa_type = application.get("visa_type", "canada_work")

    requirement_check = requirements.check_document_requirements(visa_type, classifications)
    scores = calculate_readiness_score(classifications, visa_type)

    report = reporter.generate_report(
        application=application,
        classifications=classifications,
        requirements_check=requirement_check,
        readiness_scores=scores,
    )

    return report


@router.get("/report/{application_id}/summary")
def get_report_summary(application_id: str):
    """Get a plain-text summary of the readiness report."""
    application = db.get_application(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    classifications = db.get_application_classifications(application_id)
    visa_type = application.get("visa_type", "canada_work")

    requirement_check = requirements.check_document_requirements(visa_type, classifications)
    scores = calculate_readiness_score(classifications, visa_type)

    report = reporter.generate_report(
        application=application,
        classifications=classifications,
        requirements_check=requirement_check,
        readiness_scores=scores,
    )

    return {"summary": reporter.generate_summary(report)}


@router.get("/dashboard-stats")
def get_dashboard_stats():
    """Get overall dashboard statistics."""
    stats = db.get_dashboard_stats()
    return stats