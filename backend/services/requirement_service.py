"""
Requirement service — loads visa requirements from JSON and checks document completeness.

Requirements are stored in backend/database/requirements/*.json and loaded on demand.
"""

import json
import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_REQUIREMENTS_DIR = Path(__file__).resolve().parent.parent / "database" / "requirements"
_REQUIREMENTS_CACHE: dict[str, dict] = {}


def _country_key(country: str, visa_type: str) -> str:
    return f"{country.lower()}_{visa_type.lower()}"


def _load_requirements(country: str, visa_type: str) -> Optional[dict]:
    """Load requirements for a given country and visa type from JSON."""
    key = _country_key(country, visa_type)
    if key in _REQUIREMENTS_CACHE:
        return _REQUIREMENTS_CACHE[key]

    filename = f"{key.replace(' ', '_')}.json"
    filepath = _REQUIREMENTS_DIR / filename

    if not filepath.exists():
        logger.warning(f"Requirements file not found: {filepath}")
        return None

    try:
        with open(filepath) as f:
            data = json.load(f)
        _REQUIREMENTS_CACHE[key] = data
        return data
    except (json.JSONDecodeError, IOError) as exc:
        logger.error(f"Failed to load requirements {filepath}: {exc}")
        return None


def list_available_requirements() -> list[dict]:
    """List all available requirement configurations."""
    results = []
    if not _REQUIREMENTS_DIR.exists():
        return results

    for filepath in sorted(_REQUIREMENTS_DIR.glob("*.json")):
        name = filepath.stem.replace("_", " ").title()
        try:
            with open(filepath) as f:
                data = json.load(f)
            results.append({
                "file": filepath.name,
                "name": name,
                "country": data.get("country", ""),
                "visa_type": data.get("visa_type", ""),
                "document_count": len(data.get("required_documents", [])),
            })
        except (json.JSONDecodeError, IOError):
            continue

    return results


def get_requirements(country: str, visa_type: str) -> Optional[dict]:
    """Get the full requirements dict for a country + visa type."""
    return _load_requirements(country, visa_type)


def get_required_documents(country: str, visa_type: str) -> list[dict]:
    """Get the list of required document types for a given visa category."""
    reqs = _load_requirements(country, visa_type)
    if not reqs:
        return []
    return reqs.get("required_documents", [])


def check_document_completeness(
    country: str, visa_type: str, provided_documents: list[dict]
) -> dict:
    """
    Check which required documents are present and which are missing.

    Args:
        country: Destination country
        visa_type: Type of visa
        provided_documents: List of classified document dicts with 'document_type' field

    Returns:
        dict with:
          - required: list of all required document types
          - provided: list of document types that were matched
          - missing: list of required document types not found
          - optional_provided: list of documents provided that aren't strictly required
          - completeness_pct: float 0-100
    """
    req_docs = get_required_documents(country, visa_type)
    if not req_docs:
        return {
            "required": [],
            "provided": [],
            "missing": [],
            "optional_provided": [],
            "completeness_pct": 0,
        }

    required_types = [d.get("document_type", "") for d in req_docs]
    provided_types = [d.get("document_type", "").lower() for d in provided_documents]

    provided_matched = []
    missing = []
    for req_type in required_types:
        if req_type.lower() in provided_types:
            provided_matched.append(req_type)
        else:
            missing.append(req_type)

    # Optional documents — ones provided but not strictly required
    required_lower = [r.lower() for r in required_types]
    optional_provided = [
        d.get("document_type")
        for d in provided_documents
        if d.get("document_type", "").lower() not in required_lower
    ]

    completeness_pct = round((len(provided_matched) / max(len(required_types), 1)) * 100, 1)

    return {
        "required": required_types,
        "provided": provided_matched,
        "missing": missing,
        "optional_provided": optional_provided,
        "completeness_pct": completeness_pct,
    }


def health() -> dict:
    """Return requirement service health."""
    return {
        "available": _REQUIREMENTS_DIR.exists(),
        "requirements_count": len(list(_REQUIREMENTS_DIR.glob("*.json"))),
    }