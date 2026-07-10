"""
Quality check service for document verification and fraud detection.
Performs checks on document text and metadata for quality issues.
"""

import re
from typing import Optional


class QualityCheckService:
    """
    Service for quality checking documents.
    Detects potential fraud indicators, format issues, and data inconsistencies.
    """

    def check_document(self, document_text: str, document_type: str) -> dict:
        """
        Run quality checks on a single document.
        Returns check results with any warnings or flags.
        """
        flags = []
        warnings = []
        score = 100  # Start at 100, deduct for issues

        # Check for common fraud indicators
        fraud_flags = self._check_fraud_indicators(document_text)
        if fraud_flags:
            flags.extend(fraud_flags)
            score -= len(fraud_flags) * 15

        # Check for formatting issues
        format_issues = self._check_formatting(document_text)
        if format_issues:
            warnings.extend(format_issues)
            score -= len(format_issues) * 10

        # Check for data consistency
        consistency_issues = self._check_consistency(document_text, document_type)
        if consistency_issues:
            warnings.extend(consistency_issues)
            score -= len(consistency_issues) * 10

        return {
            "score": max(0, score),
            "passed": score >= 50,
            "flags": flags,
            "warnings": warnings,
        }

    def _check_fraud_indicators(self, text: str) -> list[str]:
        """Check for potential fraud indicators."""
        flags = []
        text_lower = text.lower()

        # Check for scanned copies marked as "certified true copy"
        if re.search(r"\bcertified\s+true\s+copy\b", text_lower):
            flags.append("Document is a certified copy — verify original")

        # Check for obvious template markers
        if re.search(r"\b\[.*?\]", text):
            flags.append("Document contains template placeholders [bracketed text]")

        # Check for inconsistent dates
        dates = re.findall(r"\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}", text)
        if len(dates) > 1:
            # Check if dates span unreasonable ranges
            pass  # Simplified — in production compare actual dates

        # Check for heavily redacted content
        redacted_patterns = len(re.findall(r"[\*#]{4,}", text))
        if redacted_patterns > 3:
            flags.append("Document contains heavy redactions")

        return flags

    def _check_formatting(self, text: str) -> list[str]:
        """Check for formatting issues."""
        warnings = []

        # Check for garbled text (non-ASCII or encoding issues)
        non_ascii_ratio = sum(1 for c in text if ord(c) > 127) / max(len(text), 1)
        if non_ascii_ratio > 0.2:
            warnings.append("Text contains unusual characters — possible encoding issue")

        # Check for very short content
        if len(text.strip()) < 100:
            warnings.append("Document content appears incomplete or very short")

        # Check for excessive whitespace
        if re.search(r"\n{5,}", text):
            warnings.append("Document has excessive blank lines — may be incomplete")

        # Check for mixed languages
        non_english_chars = len(re.findall(r"[À-üñçéèêëàâùûüôöîï]", text, re.IGNORECASE))
        if non_english_chars > 20 and non_english_chars < 100:
            warnings.append("Document contains significant non-English text")

        return warnings

    def _check_consistency(self, text: str, document_type: str) -> list[str]:
        """Check for data consistency issues specific to document type."""
        warnings = []

        if document_type == "passport":
            # Multiple passport numbers
            passport_nos = re.findall(r"[A-Z0-9]{6,12}", text)
            unique_nos = set(passport_nos)
            if len(unique_nos) > 2:
                warnings.append("Multiple potential passport/ID numbers found")

        if document_type == "bank_statement":
            # Check for multiple currencies
            currencies = re.findall(r"\b(USD|EUR|GBP|CAD|ZAR|INR|JPY|AUD)\b", text.upper())
            if len(set(currencies)) > 2:
                warnings.append("Multiple currencies detected in bank statement")
            # Check for negative balances
            if re.search(r"[-–]\s*\$?\d+", text):
                warnings.append("Negative balances or deductions detected")

        if document_type == "employment_letter":
            # Check for contradictory dates
            if re.search(r"(?:part.time|temporary|contract)", text, re.IGNORECASE):
                warnings.append("Employment may not be permanent")

        return warnings

    def cross_check_documents(self, documents: list[dict]) -> list[dict]:
        """
        Cross-check multiple documents for consistency.
        For example, verify names and dates match across documents.
        """
        inconsistencies = []

        # Check name consistency
        names = set()
        for doc in documents:
            text = doc.get("file_contents", "")
            extracted = doc.get("extracted_fields", {})

            # Try to extract name from text or classification
            doc_name = extracted.get("name", "")
            if doc_name and doc_name not in names:
                names.add(doc_name)

            # Also check from raw text
            name_match = re.search(r"(?:name[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+))", text)
            if name_match:
                found_name = name_match.group(1).strip()
                if found_name and found_name not in names:
                    names.add(found_name)

        if len(names) > 1:
            inconsistencies.append({
                "type": "name_mismatch",
                "detail": f"Different names found across documents: {', '.join(names)}",
                "severity": "high",
            })

        return inconsistencies