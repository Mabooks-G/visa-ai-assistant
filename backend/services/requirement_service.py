"""
Requirement service — loads visa requirements from backend constants.
Supports admin overrides stored in the requirement_overrides Supabase table.
"""

import logging
from typing import Optional

from backend.database.db import get_supabase
from backend.config.constants import UNIVERSAL_REQUIREMENTS, VISA_TYPE_IDS

logger = logging.getLogger(__name__)


def get_requirements(visa_type: str, country: str) -> list[dict]:
    """
    Get requirements for a visa type + country, merging universal defaults
    with any admin overrides from the database.
    
    Args:
        visa_type: One of 'tourist', 'work', 'study', 'permanent_residence', 'asylum'
        country: Destination country name
    
    Returns:
        List of requirement dicts with: document_type, label, required, tags
    """
    base = _get_universal_requirements(visa_type)
    overrides = _get_overrides(visa_type, country)
    return _merge_overrides(base, overrides)


def _get_universal_requirements(visa_type: str) -> list[dict]:
    """Get the universal requirements for a visa type."""
    return UNIVERSAL_REQUIREMENTS.get(visa_type, [])


def _get_overrides(visa_type: str, country: str) -> list[dict]:
    """Fetch admin overrides from the requirement_overrides table."""
    try:
        sb = get_supabase()
        result = sb.table("requirement_overrides") \
            .select("*") \
            .or_(
                f"visa_type.eq.{visa_type},visa_type.eq.ALL"
            ) \
            .execute()
        overrides = result.data or []
        
        # Filter by country match
        applicable = []
        for ov in overrides:
            tags = ov.get("tags", [])
            if "ALL" in tags or country in tags:
                applicable.append(ov)
        return applicable
    except Exception as e:
        logger.warning(f"Could not fetch overrides: {e}")
        return []


def _merge_overrides(base: list[dict], overrides: list[dict]) -> list[dict]:
    """Merge admin overrides into base requirements.
    
    Overrides with action='add' are appended.
    Overrides with action='remove' remove matching document_types.
    Overrides with action='modify' update matching fields.
    """
    result = list(base)
    
    for ov in overrides:
        action = ov.get("action", "add")
        if action == "add":
            result.append({
                "document_type": ov.get("document_type", ""),
                "label": ov.get("label", ""),
                "required": ov.get("required", True),
                "tags": ov.get("tags", ["ALL"]),
            })
        elif action == "remove":
            doc_type = ov.get("document_type", "")
            result = [r for r in result if r.get("document_type") != doc_type]
        elif action == "modify":
            doc_type = ov.get("document_type", "")
            for r in result:
                if r.get("document_type") == doc_type:
                    if ov.get("label"):
                        r["label"] = ov["label"]
                    if ov.get("required") is not None:
                        r["required"] = ov["required"]
    
    return result


def check_document_completeness(
    visa_type: str, country: str, provided_documents: list[dict]
) -> dict:
    """
    Check which required documents are present and which are missing.
    
    Args:
        visa_type: Type of visa
        country: Destination country
        provided_documents: List of document dicts with 'document_type' field
    
    Returns:
        dict with required, provided, missing, optional_provided, completeness_pct
    """
    reqs = get_requirements(visa_type, country)
    if not reqs:
        return {
            "required": [],
            "provided": [],
            "missing": [],
            "optional_provided": [],
            "completeness_pct": 0,
        }
    
    required_types = [d.get("document_type", "") for d in reqs]
    provided_types = [d.get("document_type", "").lower() for d in provided_documents]
    
    provided_matched = []
    missing = []
    for req_dt in required_types:
        if req_dt.lower() in provided_types:
            provided_matched.append(req_dt)
        else:
            missing.append(req_dt)
    
    required_lower = [r.lower() for r in required_types]
    optional_provided = [
        d.get("document_type")
        for d in provided_documents
        if d.get("document_type", "").lower() not in required_lower
    ]
    
    completeness_pct = round(
        (len(provided_matched) / max(len(required_types), 1)) * 100, 1
    )
    
    return {
        "required": required_types,
        "provided": provided_matched,
        "missing": missing,
        "optional_provided": optional_provided,
        "completeness_pct": completeness_pct,
    }


def list_all_requirements() -> dict:
    """List all universal requirements grouped by visa type."""
    return UNIVERSAL_REQUIREMENTS


def health() -> dict:
    """Return requirement service health."""
    return {
        "available": True,
        "visa_types": len(VISA_TYPE_IDS),
        "universal_requirements": sum(len(v) for v in UNIVERSAL_REQUIREMENTS.values()),
    }