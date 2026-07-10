"""
Gemma AI service — document classification & readiness scoring via Google AI API.

Uses Google's Generative AI API (Gemma models) instead of loading model weights locally.
Supports gemma-2-2b-it, gemma-4, and other Google AI models via API key.
"""

import os
import re
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
MODEL_NAME = os.getenv("GOOGLE_MODEL", "gemma-4")
MAX_OUTPUT_TOKENS = int(os.getenv("GEMMA_MAX_OUTPUT_TOKENS", "512"))

_client = None


def _get_client():
    """Lazy-init the Google AI client."""
    global _client
    if _client is None:
        try:
            from google import genai
            _client = genai.Client(api_key=GOOGLE_API_KEY)
        except Exception as exc:
            logger.error(f"Failed to initialise Google AI client: {exc}")
            raise
    return _client


def _generate(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Send a prompt to the Google AI API and return the generated text."""
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. "
            "Get a free key at https://aistudio.google.com/apikey"
        )

    client = _get_client()

    config = {
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "temperature": 0.1,
        "top_p": 0.95,
    }

    full_prompt = prompt
    if system_prompt:
        full_prompt = f"{system_prompt}\n\n{prompt}"

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=full_prompt,
        config=config,
    )
    return response.text.strip()


def classify_document(text: str) -> dict:
    """
    Classify an extracted document by type, country, and purpose.

    Returns a dict with:
      - document_type: str (e.g. "passport", "bank_statement", "degree_certificate")
      - issuing_country: str
      - confidence: float (0-1)
      - summary: str
    """
    prompt = f"""Analyse the following document text and classify it.

Return ONLY valid JSON with these fields:
  - "document_type": one of ["passport", "bank_statement", "degree_certificate", "transcript", "english_test", "work_experience", "visa_application_form", "photograph", "marriage_certificate", "birth_certificate", "police_clearance", "medical_report", "invitation_letter", "financial_support", "travel_insurance", "itinerary", "accommodation_proof", "employment_letter", "tax_return", "other"]
  - "issuing_country": the country that issued this document, or "unknown"
  - "confidence": a float between 0.0 and 1.0
  - "summary": a one-sentence summary of what the document contains

Document text:
{text[:3000]}"""

    try:
        raw = _generate(prompt)
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(raw)
    except Exception as exc:
        logger.warning(f"Gemma classification API call failed: {exc}")
        result = {
            "document_type": "other",
            "issuing_country": "unknown",
            "confidence": 0.0,
            "summary": "Classification unavailable — AI model error.",
        }

    result.setdefault("document_type", "other")
    result.setdefault("issuing_country", "unknown")
    result.setdefault("confidence", 0.0)
    result.setdefault("summary", "")
    return result


def score_application(documents: list[dict], visa_category: str, country: str) -> dict:
    """
    Score the overall readiness of a visa application.

    Args:
        documents: List of dicts with fields: document_type, issuing_country,
                   confidence (from classify_document), and extracted_text preview.
        visa_category: e.g. "student", "work", "tourist", "family"
        country: Target country, e.g. "Canada", "Germany", "South Africa"

    Returns:
        Dict with:
          - overall_score: float 0-100
          - category_scores: dict of sub-scores
          - missing_documents: list
          - recommendations: list[str]
          - critical_issues: list[str]
    """
    doc_summary = "\n".join(
        f"- {d.get('document_type', 'unknown')} (conf: {d.get('confidence', 0):.2f})"
        for d in documents
    )

    prompt = f"""You are a visa application assessor. Evaluate the readiness of this application.

Target visa: {visa_category} visa for {country}

Documents provided:
{doc_summary}

Return ONLY valid JSON with these fields:
  - "overall_score": integer 0-100 (how complete/ready the application is)
  - "category_scores": {{"documents": int, "completeness": int, "validity": int}}
  - "missing_documents": list of required document types that are not provided
  - "recommendations": list of suggested actions to improve the application
  - "critical_issues": list of issues that would cause rejection

Be strict — an incomplete application should score low.
"""

    try:
        raw = _generate(prompt)
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(raw)
    except Exception as exc:
        logger.warning(f"Gemma scoring API call failed: {exc}")
        result = {
            "overall_score": 50,
            "category_scores": {"documents": 50, "completeness": 50, "validity": 50},
            "missing_documents": [],
            "recommendations": ["AI scoring is temporarily unavailable."],
            "critical_issues": [],
        }

    result.setdefault("overall_score", 50)
    result.setdefault("category_scores", {"documents": 50, "completeness": 50, "validity": 50})
    result.setdefault("missing_documents", [])
    result.setdefault("recommendations", [])
    result.setdefault("critical_issues", [])
    return result


def health() -> dict:
    """Return the status of the Gemma AI service."""
    if not GOOGLE_API_KEY:
        return {
            "available": False,
            "error": "GOOGLE_API_KEY is not set. Get a key at https://aistudio.google.com/apikey",
        }
    try:
        client = _get_client()
        # Lightweight check — try to list models or do a simple generation
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents="Respond with just the word: OK",
            config={"max_output_tokens": 10},
        )
        return {
            "available": True,
            "model": MODEL_NAME,
            "api": "google_ai",
        }
    except Exception as exc:
        return {"available": False, "error": str(exc)}