"""
Document validation service.
Validates document content, format, and extracted information.
"""

import re
from typing import Optional


class ValidationService:
    """
    Service for validating document content and extracted information.
    """

    def validate_document(self, document_text: str, document_type: str) -> dict:
        """
        Validate a document based on its type.
        Returns validation result with status and issues.
        """
        validators = {
            "passport": self._validate_passport,
            "bank_statement": self._validate_bank_statement,
            "employment_letter": self._validate_employment_letter,
            "academic_transcript": self._validate_academic_transcript,
            "acceptance_letter": self._validate_acceptance_letter,
            "health_insurance": self._validate_health_insurance,
            "id_card": self._validate_id_card,
            "proof_of_address": self._validate_proof_of_address,
        }

        validator = validators.get(document_type, self._validate_generic)
        result = validator(document_text)
        return result

    def _validate_passport(self, text: str) -> dict:
        """Validate passport document."""
        issues = []
        is_valid = True

        # Check for passport number
        has_passport_no = bool(
            re.search(r"(?:passport\s*(?:no|number|#)\s*[:\-]?\s*([A-Z0-9]{5,20}))", text, re.IGNORECASE)
        )
        if not has_passport_no:
            issues.append("Could not find passport number")
            is_valid = False

        # Check for name
        has_name = bool(re.search(r"(?:name|surname|given\s*name)[:\s]", text, re.IGNORECASE))
        if not has_name:
            issues.append("Could not find name on passport")

        # Check for expiry
        has_expiry = bool(re.search(r"(?:expir|date\s*of\s*expir|valid\s*until)", text, re.IGNORECASE))
        if not has_expiry:
            issues.append("Could not find expiry date")

        return {
            "is_valid": is_valid,
            "issues": issues,
            "warnings": [] if is_valid else ["Document validation flagged issues"],
        }

    def _validate_bank_statement(self, text: str) -> dict:
        """Validate bank statement document."""
        issues = []
        is_valid = True

        has_balance = bool(re.search(r"(?:balance|total|amount)", text, re.IGNORECASE))
        has_account = bool(re.search(r"(?:account\s*(?:no|number|#))", text, re.IGNORECASE))
        has_institution = bool(re.search(r"(?:bank|financial\s*institution)", text, re.IGNORECASE))

        if not has_balance:
            issues.append("Could not find balance information")
            is_valid = False
        if not has_account:
            issues.append("Could not find account number")
        if not has_institution:
            issues.append("Could not identify banking institution")

        return {
            "is_valid": is_valid,
            "issues": issues,
            "warnings": [],
        }

    def _validate_employment_letter(self, text: str) -> dict:
        """Validate employment letter."""
        issues = []
        is_valid = True

        has_employer = bool(re.search(r"(?:employer|company|organization)", text, re.IGNORECASE))
        has_position = bool(re.search(r"(?:position|role|title|designation)", text, re.IGNORECASE))
        has_dates = bool(re.search(r"(?:date|start|employed|joining)", text, re.IGNORECASE))

        if not has_employer:
            issues.append("Could not find employer/company name")
        if not has_position:
            issues.append("Could not find position/title")
        if not has_dates:
            issues.append("Could not find employment dates")

        return {
            "is_valid": is_valid,
            "issues": issues,
            "warnings": [],
        }

    def _validate_academic_transcript(self, text: str) -> dict:
        issues = []
        is_valid = True

        has_grades = bool(re.search(r"(?:grade|score|gpa|cgpa|mark)", text, re.IGNORECASE))
        has_institution = bool(re.search(r"(?:university|college|institution|school)", text, re.IGNORECASE))

        if not has_grades:
            issues.append("Could not find grade/score information")
        if not has_institution:
            issues.append("Could not identify educational institution")

        return {"is_valid": is_valid, "issues": issues, "warnings": []}

    def _validate_acceptance_letter(self, text: str) -> dict:
        issues = []
        is_valid = True

        has_program = bool(re.search(r"(?:program|course|degree|major)", text, re.IGNORECASE))
        has_institution = bool(re.search(r"(?:university|college|institution)", text, re.IGNORECASE))
        has_dates = bool(re.search(r"(?:semester|term|start|intake|fall|spring)", text, re.IGNORECASE))

        if not has_program:
            issues.append("Could not find program/course details")
        if not has_institution:
            issues.append("Could not identify institution")

        return {"is_valid": is_valid, "issues": issues, "warnings": []}

    def _validate_health_insurance(self, text: str) -> dict:
        issues = []
        is_valid = True

        has_policy = bool(re.search(r"(?:policy\s*(?:no|number|#))", text, re.IGNORECASE))
        has_provider = bool(re.search(r"(?:insurance|provider|company|assurance)", text, re.IGNORECASE))
        has_coverage = bool(re.search(r"(?:coverage|cover|benefit|valid)", text, re.IGNORECASE))

        if not has_policy:
            issues.append("Could not find policy number")
        if not has_provider:
            issues.append("Could not identify insurance provider")

        return {"is_valid": is_valid, "issues": issues, "warnings": []}

    def _validate_id_card(self, text: str) -> dict:
        issues = []
        is_valid = True

        has_id_no = bool(re.search(r"(?:id\s*(?:no|number|#))", text, re.IGNORECASE))
        has_name = bool(re.search(r"(?:name|full\s*name)", text, re.IGNORECASE))
        has_photo = bool("photo" in text.lower())

        if not has_id_no:
            issues.append("Could not find ID number")

        return {"is_valid": is_valid, "issues": issues, "warnings": []}

    def _validate_proof_of_address(self, text: str) -> dict:
        issues = []
        is_valid = True

        has_address = bool(re.search(r"(?:address|street|road|avenue|drive|lane)", text, re.IGNORECASE))
        has_date = bool(re.search(r"\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}", text))

        if not has_address:
            issues.append("Could not find address")
        if not has_date:
            issues.append("Could not find date on document")

        return {"is_valid": is_valid, "issues": issues, "warnings": []}

    def _validate_generic(self, text: str) -> dict:
        """Generic validation for unknown document types."""
        issues = []
        if len(text.strip()) < 20:
            issues.append("Document text is too short to validate")
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": [],
        }