"""
Gemma AI service — document classification & readiness scoring via HuggingFace Transformers.

Uses Google's Gemma 2B Instruct model on the available device (ROCm / CUDA / CPU).
Model weights are downloaded on first use and cached in the HuggingFace cache directory.
"""

import os
import re
import json
import logging
from typing import Optional

import torch

logger = logging.getLogger(__name__)

MODEL_NAME = os.getenv("GEMMA_MODEL", "google/gemma-2-2b-it")
MAX_INPUT_TOKENS = int(os.getenv("GEMMA_MAX_INPUT_TOKENS", "2048"))
MAX_OUTPUT_TOKENS = int(os.getenv("GEMMA_MAX_OUTPUT_TOKENS", "512"))
DEVICE = os.getenv("GEMMA_DEVICE", "auto")

_model = None
_tokenizer = None


def _resolve_device() -> str:
    """Pick the best available device."""
    if DEVICE != "auto":
        return DEVICE
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def load_model():
    """Load (or reload) the Gemma model and tokenizer into memory."""
    global _model, _tokenizer

    if _model is not None and _tokenizer is not None:
        return  # Already loaded

    device = _resolve_device()
    logger.info(f"Loading Gemma model '{MODEL_NAME}' on device={device}")

    from transformers import AutoTokenizer, AutoModelForCausalLM

    _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    _model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16 if device in ("cuda",) else torch.float32,
        device_map="auto" if device == "cuda" else None,
        low_cpu_mem_usage=True,
    )

    if device == "cpu":
        _model = _model.to("cpu")

    _model.eval()
    logger.info("Gemma model loaded successfully")


def unload_model():
    """Free GPU memory by deleting the model reference."""
    global _model, _tokenizer
    _model = None
    _tokenizer = None
    torch.cuda.empty_cache()


def _generate(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Run a prompt through Gemma and return the generated text."""
    load_model()

    messages = []
    if system_prompt:
        messages.append({"role": "user", "content": system_prompt + "\n\n" + prompt})
    else:
        messages.append({"role": "user", "content": prompt})

    formatted = _tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    inputs = _tokenizer(
        formatted,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_INPUT_TOKENS,
    ).to(_model.device)

    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=MAX_OUTPUT_TOKENS,
            temperature=0.1,
            top_p=0.95,
            do_sample=True,
            pad_token_id=_tokenizer.eos_token_id,
        )

    response = _tokenizer.decode(outputs[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True)
    return response.strip()


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

    raw = _generate(prompt)
    try:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(raw)
    except (json.JSONDecodeError, AttributeError):
        logger.warning(f"Failed to parse classification JSON from: {raw[:200]}")
        result = {
            "document_type": "other",
            "issuing_country": "unknown",
            "confidence": 0.0,
            "summary": "Classification failed — could not parse model output.",
        }

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

    raw = _generate(prompt)
    try:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(raw)
    except (json.JSONDecodeError, AttributeError):
        logger.warning(f"Failed to parse readiness JSON from: {raw[:200]}")
        result = {
            "overall_score": 50,
            "category_scores": {"documents": 50, "completeness": 50, "validity": 50},
            "missing_documents": [],
            "recommendations": ["Could not generate recommendations — model output was unparseable."],
            "critical_issues": [],
        }

    result.setdefault("overall_score", 50)
    result.setdefault("category_scores", {"documents": 50, "completeness": 50, "validity": 50})
    result.setdefault("missing_documents", [])
    result.setdefault("recommendations", [])
    result.setdefault("critical_issues", [])

    return result


def health() -> dict:
    """Return the status of the Gemma service."""
    try:
        load_model()
        device = str(_model.device) if _model else "not_loaded"
        return {"available": _model is not None, "model": MODEL_NAME, "device": device}
    except Exception as exc:
        return {"available": False, "error": str(exc)}