"""
Visa requirement definitions and validation rules.
Loads visa-specific requirements from JSON files and provides helpers.
"""

import json
import os
from typing import Optional


class RequirementService:
    """
    Service for loading and querying visa requirements.
    Requirements are stored as JSON files in the database/requirements/ directory.
    """

    def __init__(self, requirements_dir: Optional[str] = None):
        self.requirements_dir = requirements_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "database",
            "requirements",
        )
        self._cache: dict[str, dict] = {}

    def get_requirements(self, visa_type: str) -> dict:
        """Get requirements for a specific visa type."""
        if visa_type in self._cache:
            return self._cache[visa_type]

        file_path = os.path.join(self.requirements_dir, f"{visa_type}.json")
        if not os.path.exists(file_path):
            return self._default_requirements(visa_type)

        try:
            with open(file_path, "r") as f:
                requirements = json.load(f)
                self._cache[visa_type] = requirements
                return requirements
        except (json.JSONDecodeError, IOError):
            return self._default_requirements(visa_type)

    def check_document_requirements(
        self,
        visa_type: str,
        classified_docs: list[dict],
    ) -> dict:
        """
        Check which required documents are present vs missing.
        Returns a dict with present, missing, and optional docs.
        """
        requirements = self.get_requirements(visa_type)
        required_docs = [d.lower() for d in requirements.get("required_documents", [])]
        optional_docs = [d.lower() for d in requirements.get("optional_documents", [])]

        found_types = set()
        for doc in classified_docs:
            doc_type = doc.get("classified_as", "").lower()
            if doc_type:
                found_types.add(doc_type)

        present = []
        missing = []
        for req_doc in required_docs:
            if req_doc in found_types:
                present.append(req_doc)
            else:
                missing.append(req_doc)

        found_optional = [d for d in optional_docs if d in found_types]

        return {
            "visa_type": visa_type,
            "required": {
                "present": present,
                "missing": missing,
                "total": len(required_docs),
                "completed": len(present),
            },
            "optional": {
                "found": found_optional,
                "suggested": [d for d in optional_docs if d not in found_optional],
            },
        }

    def get_all_visa_types(self) -> list[str]:
        """Get all available visa types from requirements files."""
        if not os.path.isdir(self.requirements_dir):
            return []

        visa_types = []
        for filename in os.listdir(self.requirements_dir):
            if filename.endswith(".json"):
                visa_type = filename[:-5]  # Remove .json
                visa_types.append(visa_type)
        return sorted(visa_types)

    def _default_requirements(self, visa_type: str) -> dict:
        """Return sensible defaults for unknown visa types."""
        return {
            "visa_type": visa_type,
            "country": visa_type.split("_")[0].title() if "_" in visa_type else visa_type,
            "visa_category": visa_type.split("_")[1].title() if "_" in visa_type else "General",
            "required_documents": ["passport"],
            "optional_documents": [],
            "processing_time": "Varies",
            "notes": "Requirements loaded from default configuration.",
        }