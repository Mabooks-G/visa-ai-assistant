"""
Document classification service.
Handles classifying uploaded documents into types using AI.
"""

import json
import random
import re
from typing import Optional

# In production, this imports from gemma_service
# from server.services.gemma_service import GemmaService


class ClassifierService:
    """AI-powered document classification service."""

    # Document type patterns (keywords that hint at document type)
    TYPE_PATTERNS = {
        "passport": [
            r"\bpassport\b", r"\bpasse?port\b", r"\btravel\s*document\b",
            r"\bnationality\b", r"\bpassport\s*no\b", r"\bpassport\s*number\b",
        ],
        "bank_statement": [
            r"\bbank\s*statement\b", r"\bbank\s*account\b", r"\baccount\s*number\b",
            r"\btransaction\b", r"\bbalance\b", r"\bdeposit\b", r"\bwithdrawal\b",
            r"\bbank\b.*\bstatement\b",
        ],
        "employment_letter": [
            r"\bemployment\s*letter\b", r"\boffer\s*letter\b", r"\bjob\s*offer\b",
            r"\bemployer\b", r"\bemployment\b", r"\bwork\s*contract\b",
            r"\bhire\b", r"\bposition\b",
        ],
        "academic_transcript": [
            r"\btranscript\b", r"\bacademic\s*record\b", r"\bgrades?\b",
            r"\bmarksheet\b", r"\buniversity\b", r"\bcourse\b.*\bgrade\b",
            r"\bsemester\b",
        ],
        "acceptance_letter": [
            r"\bacceptance\b", r"\badmission\b", r"\boffer\s*of\s*admission\b",
            r"\bwelcome\s*to\b.*\buniversity\b",
        ],
        "invitation_letter": [
            r"\binvitation\b", r"\binvite\b", r"\bconference\b",
        ],
        "id_card": [
            r"\bid\s*card\b", r"\bidentity\b", r"\bdriver\s*license\b",
            r"\bnational\s*id\b",
        ],
        "health_insurance": [
            r"\binsurance\b", r"\bhealth\s*cover\b", r"\bmedical\s*insurance\b",
            r"\bpolicy\s*number\b",
        ],
        "proof_of_address": [
            r"\baddress\b", r"\butility\s*bill\b", r"\bresidence\b",
            r"\brent\b", r"\blease\b",
        ],
    }

    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        # In production with GPU:
        # self.gemma = GemmaService(model_path=os.environ.get("GEMMA_MODEL_PATH"))

    def classify(self, document_text: str, document_name: str = "") -> dict:
        """
        Classify a document based on its text content.
        Returns classification result with type, confidence, extracted fields, and issues.
        """
        text_lower = document_text.lower()

        # Score each document type based on keyword matches
        scores = {}
        for doc_type, patterns in self.TYPE_PATTERNS.items():
            score = 0
            matched_patterns = []
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    score += len(matches) * 10
                    matched_patterns.append(pattern)
            if score > 0:
                scores[doc_type] = {
                    "score": score,
                    "matches": len(matched_patterns),
                }

        # If no patterns matched, use filename as hint
        if not scores and document_name:
            name_lower = document_name.lower()
            for doc_type, patterns in self.TYPE_PATTERNS.items():
                for keyword in doc_type.replace("_", " ").split():
                    if keyword in name_lower:
                        scores[doc_type] = {"score": 30, "matches": 1}
                        break

        # Determine best match
        if scores:
            best_type = max(scores, key=lambda k: scores[k]["score"])
            best_score = scores[best_type]["score"]
            # Normalize confidence to 0-1
            confidence = min(0.95, 0.3 + (best_score / 100))
        else:
            best_type = "other"
            confidence = 0.2

        # Extract fields based on document type
        extracted_fields = self._extract_fields(document_text, best_type)

        # Check for issues
        issues = self._check_issues(document_text, extracted_fields)

        return {
            "document_type": best_type,
            "confidence": round(confidence, 2),
            "extracted_fields": extracted_fields,
            "issues": issues,
        }

    def classify_batch(self, documents: list[dict]) -> list[dict]:
        """Classify multiple documents at once."""
        return [
            {
                "document_id": doc.get("id", ""),
                **self.classify(doc.get("file_contents", ""), doc.get("file_name", "")),
            }
            for doc in documents
        ]

    def _extract_fields(self, text: str, doc_type: str) -> dict:
        """Extract relevant fields from document text based on type."""
        fields = {}

        if doc_type == "passport":
            # Try to extract passport number
            match = re.search(r"(?:passport\s*(?:no|number|#)\s*[:\-]?\s*([A-Z0-9]{5,20}))", text, re.IGNORECASE)
            if match:
                fields["passport_number"] = match.group(1)

            # Try to extract name
            match = re.search(r"(?:name[:\s]+([A-Za-z\s]+))", text)
            if match:
                fields["name"] = match.group(1).strip()

            # Try to extract nationality
            match = re.search(r"(?:nationality[:\s]+([A-Za-z\s]+))", text)
            if match:
                fields["nationality"] = match.group(1).strip()

        elif doc_type == "bank_statement":
            match = re.search(r"(?:account\s*(?:no|number|#)\s*[:\-]?\s*([A-Z0-9\-]+))", text, re.IGNORECASE)
            if match:
                fields["account_number"] = match.group(1)

            match = re.search(r"(?:balance[:\s]*\$?([0-9,]+\.?\d*))", text)
            if match:
                fields["balance"] = match.group(1)

        elif doc_type == "employment_letter":
            match = re.search(r"(?:position[:\s]+([A-Za-z\s]+))", text)
            if match:
                fields["position"] = match.group(1).strip()

            match = re.search(r"(?:salary[:\s]*\$?([0-9,]+))", text, re.IGNORECASE)
            if match:
                fields["salary"] = match.group(1)

        return fields

    def _check_issues(self, text: str, fields: dict) -> list[str]:
        """Check for potential issues in the document."""
        issues = []

        # Check for expired dates
        if re.search(r"(?:expir(?:y|ed|es?)\s*(?:date)?[:\s]*\d{4})", text, re.IGNORECASE):
            # This is a simplified check - in production you'd compare dates
            issues.append("Document may be expired — verify date")

        # Check for poor quality indicators
        if len(text.strip()) < 50:
            issues.append("Document text is very short — may be low quality")

        if re.search(r"(?:sample|example|template|draft)", text, re.IGNORECASE):
            issues.append("Document appears to be a sample or template")

        return issues