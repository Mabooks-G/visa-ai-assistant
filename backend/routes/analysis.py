"""
Analysis routes — orchestrates OCR, classification, validation, and scoring.

Endpoints:
  - POST /api/analyze/{application_id}  — Run full analysis on an application
  - GET /api/analyze/{application_id}   — Get the latest analysis report
  - POST /api/analyze/{doc_id}/ocr      — Run OCR on a single document
  - GET /api/analyze/requirements       — List available requirement configs
"""

import logging
from fastapi import APIRouter, HTTPException, Depends

from backend.middleware.auth import get_current_user, admin_required
from backend.services.application_service import get_application_with_documents
from backend.services.document_service import get_document
from backend.services.ocr_service import extract_text_from_bytes
from backend.services.classifier_service import classify_document as classifier_classify
from backend.services.report_service import generate_report
from backend.services.gemma_service import health as gemma_health
from backend.services.requirement_service import (
    list_available_requirements,
    get_required_documents,
)
from backend.database.db import get_supabase

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["analysis"])


# ── Health ─────────────────────────────────────────────────────────────────────

@router.get("/analyze/health")
async def analysis_health():
    """Check availability of all analysis services."""
    return {
        "ocr": {"available": True},
        "classifier": {"available": True},
        "validation": {"available": True},
        "requirement": {"available": True},
        "report": {"available": True},
        "gemma": gemma_health(),
    }


# ── Requirements ───────────────────────────────────────────────────────────────

@router.get("/analyze/requirements")
async def list_requirements(current_user: dict = Depends(get_current_user)):
    """List all available visa requirement configurations."""
    return {"requirements": list_available_requirements()}


@router.get("/analyze/requirements/{country}/{visa_type}")
async def get_requirements_for(
    country: str,
    visa_type: str,
    current_user: dict = Depends(get_current_user),
):
    """Get required documents for a specific country and visa type."""
    reqs = get_required_documents(country, visa_type)
    return {"country": country, "visa_type": visa_type, "required_documents": reqs}


# ── OCR on a single document ──────────────────────────────────────────────────

@router.post("/analyze/{doc_id}/ocr")
async def run_ocr(doc_id: str, current_user: dict = Depends(get_current_user)):
    """Run OCR text extraction on a single document by its ID."""
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    file_url = doc.get("file_url") or doc.get("file_path", "")
    if not file_url:
        raise HTTPException(status_code=400, detail="No file associated with this document")

    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(file_url)
            response.raise_for_status()
            file_bytes = response.content

        result = extract_text_from_bytes(file_bytes, doc.get("file_name", "document"))
        text = result.get("text", "")

        return {"text": text, "method": "paddle_ocr", "confidence": result.get("confidence", 0.0)}
    except Exception as exc:
        logger.error(f"OCR failed for document {doc_id}: {exc}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(exc)}")


# ── Full analysis ─────────────────────────────────────────────────────────────

@router.post("/analyze/{application_id}")
async def run_full_analysis(
    application_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Run full analysis — OCR, classification, validation, and scoring.

    Returns a comprehensive readiness report.
    """
    app = get_application_with_documents(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Ownership check
    if current_user.get("user_type") != "admin":
        if str(app.get("userid", "")) != str(current_user["id"]):
            raise HTTPException(status_code=403, detail="Access denied")

    visa_type = app.get("visa_type", "student")
    visa_country = app.get("country", "Canada")
    documents = app.get("documents", [])

    if not documents:
        raise HTTPException(status_code=400, detail="No documents found for this application")

    # Step 1: Run OCR on any document without extracted text
    import httpx
    logger.info(f"Running OCR on {len(documents)} documents for application {application_id}")
    async with httpx.AsyncClient(timeout=60) as client:
        for doc in documents:
            text = doc.get("extracted_text", "")
            if not text:
                file_url = doc.get("file_url") or doc.get("file_path", "")
                if file_url:
                    try:
                        resp = await client.get(file_url)
                        resp.raise_for_status()
                        ocr_result = extract_text_from_bytes(resp.content, doc.get("file_name", "document"))
                        doc["extracted_text"] = ocr_result.get("text", "")
                    except Exception as exc:
                        logger.warning(f"OCR skipped for {doc.get('file_name', 'doc')}: {exc}")
                        doc["extracted_text"] = ""

    # Step 2: Generate full report
    report = generate_report(app, documents, visa_country, visa_type)

    # Step 3: Persist results
    try:
        sb = get_supabase()
        sb.table("visa_applications").update({
            "overall_score": report["summary"]["overall_score"],
            "status": "analyzed",
        }).eq("id", application_id).execute()

        for entry in report["document_analysis"]:
            doc_id = entry["document_id"]
            if doc_id:
                classification_data = {
                    "document_id": doc_id,
                    "classified_as": entry.get("document_type", entry.get("classified_as", "unknown")),
                    "confidence": entry["confidence"],
                    "summary": entry.get("summary", ""),
                    "issues": entry.get("issues", []),
                    "issuing_country": entry.get("issuing_country", "unknown"),
                }
                existing = sb.table("document_classifications").select("id").eq("document_id", doc_id).execute()
                if existing.data:
                    sb.table("document_classifications").update(classification_data).eq("document_id", doc_id).execute()
                else:
                    sb.table("document_classifications").insert(classification_data).execute()
    except Exception as exc:
        logger.error(f"Failed to persist analysis: {exc}")

    return report


@router.get("/analyze/{application_id}")
async def get_analysis_report(
    application_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get the analysis report for an application (re-built from existing data)."""
    app = get_application_with_documents(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if current_user.get("user_type") != "admin":
        if str(app.get("userid", "")) != str(current_user["id"]):
            raise HTTPException(status_code=403, detail="Access denied")

    visa_type = app.get("visa_type", "student")
    visa_country = app.get("country", "Canada")
    documents = app.get("documents", [])

    report = generate_report(app, documents, visa_country, visa_type)
    return report


# ── Admin endpoints ────────────────────────────────────────────────────────────

@router.get("/admin/analyze/applications")
async def admin_list_all_analyses(current_user: dict = Depends(admin_required)):
    """Admin: list all applications with analysis status."""
    from backend.services.application_service import list_applications
    all_apps = list_applications()
    results = [{
        "id": a.get("id"),
        "applicant_name": a.get("applicant_name"),
        "visa_type": a.get("visa_type"),
        "status": a.get("status"),
        "overall_score": a.get("overall_score"),
        "created_at": a.get("created_at"),
    } for a in all_apps]
    return {"applications": results}


@router.post("/admin/analyze/{application_id}/reanalyze")
async def admin_reanalyze(
    application_id: str,
    current_user: dict = Depends(admin_required),
):
    """Admin: force re-analysis of an application."""
    return await run_full_analysis(application_id, current_user)