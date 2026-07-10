"""
Report generation service.
Creates comprehensive visa readiness reports.
"""

import json
from datetime import datetime
from typing import Optional


class ReportService:
    """
    Service for generating visa readiness reports.
    Combines classification results, validation, and scoring into a report.
    """

    def generate_report(
        self,
        application: dict,
        classifications: list[dict],
        requirements_check: dict,
        readiness_scores: dict,
    ) -> dict:
        """Generate a full visa readiness report."""
        return {
            "report_id": self._generate_report_id(),
            "generated_at": datetime.utcnow().isoformat(),
            "application": self._format_application(application),
            "readiness_summary": readiness_scores,
            "documents_review": self._build_document_review(classifications),
            "requirements_check": requirements_check,
            "recommendations": self._generate_recommendations(
                classifications, readiness_scores, requirements_check
            ),
            "strengths": self._identify_strengths(readiness_scores),
            "weaknesses": self._identify_weaknesses(readiness_scores, requirements_check),
        }

    def _generate_report_id(self) -> str:
        """Generate a unique report ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"RPT-{timestamp}-{id(self) % 10000:04d}"

    def _format_application(self, application: dict) -> dict:
        """Format application details for the report."""
        return {
            "id": application.get("id"),
            "visa_type": application.get("visa_type", "unknown"),
            "applicant_name": application.get("applicant_name", "Not provided"),
            "status": application.get("status", "in_progress"),
            "created_at": application.get("created_at"),
        }

    def _build_document_review(self, classifications: list[dict]) -> list[dict]:
        """Build a detailed review of each classified document."""
        return [
            {
                "document_id": c.get("document_id", c.get("id")),
                "classified_as": c.get("classified_as", c.get("document_type", "unknown")),
                "confidence": c.get("confidence", 0),
                "confidence_label": self._confidence_label(c.get("confidence", 0)),
                "issues": c.get("issues", []),
                "details": c.get("details", c.get("extracted_fields", {})),
            }
            for c in classifications
        ]

    def _confidence_label(self, confidence: float) -> str:
        """Get a human-readable label for confidence score."""
        if confidence >= 0.9:
            return "Very High"
        elif confidence >= 0.7:
            return "High"
        elif confidence >= 0.5:
            return "Medium"
        elif confidence >= 0.3:
            return "Low"
        else:
            return "Very Low"

    def _generate_recommendations(
        self,
        classifications: list[dict],
        readiness_scores: dict,
        requirements_check: dict,
    ) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []
        score = readiness_scores.get("overall_readiness", 0)

        if score < 50:
            recommendations.append(
                "Your application needs significant improvement before submission."
            )

        # Check for missing required documents
        missing = requirements_check.get("required", {}).get("missing", [])
        if missing:
            docs_list = ", ".join(m.replace("_", " ").title() for m in missing)
            recommendations.append(f"Add missing required documents: {docs_list}")

        # Check for issues
        for c in classifications:
            issues = c.get("issues", [])
            if issues:
                doc_type = c.get("classified_as", c.get("document_type", "document"))
                recommendations.append(
                    f"Review {doc_type.replace('_', ' ').title()}: {issues[0]}"
                )

        if readiness_scores.get("financial_readiness", 0) < 50:
            recommendations.append(
                "Provide stronger financial documentation (bank statements, proof of funds)"
            )

        if len(classifications) < 3:
            recommendations.append("Submit more supporting documents to strengthen your application")

        if not recommendations:
            recommendations.append("Your application looks well-prepared! Ensure all details are accurate.")

        return recommendations

    def _identify_strengths(self, scores: dict) -> list[str]:
        """Identify strengths based on scores."""
        strengths = []
        if scores.get("documentation_completeness", 0) >= 70:
            strengths.append("Good document coverage")
        if scores.get("document_validity", 0) >= 70:
            strengths.append("Documents appear valid and well-formatted")
        if scores.get("financial_readiness", 0) >= 70:
            strengths.append("Strong financial documentation")
        if scores.get("information_consistency", 0) >= 70:
            strengths.append("Information is consistent across documents")
        if not strengths:
            strengths.append("Application submitted — review recommendations for improvement")
        return strengths

    def _identify_weaknesses(self, scores: dict, requirements_check: dict) -> list[str]:
        """Identify weaknesses based on scores and missing requirements."""
        weaknesses = []
        if scores.get("documentation_completeness", 0) < 50:
            weaknesses.append("Missing several required documents")
        if scores.get("financial_readiness", 0) < 50:
            weaknesses.append("Insufficient financial documentation")
        if scores.get("document_validity", 0) < 50:
            weaknesses.append("Document quality or validity concerns")
        if requirements_check.get("required", {}).get("missing"):
            weaknesses.append("Required documents not yet submitted")
        if not weaknesses:
            weaknesses.append("No significant weaknesses detected")
        return weaknesses

    def generate_summary(self, report: dict) -> str:
        """Generate a plain-text summary of the report."""
        score = report.get("readiness_summary", {}).get("overall_readiness", 0)
        visa = report.get("application", {}).get("visa_type", "Unknown")

        lines = [
            f"Visa Application Report — {visa.replace('_', ' ').title()}",
            f"Overall Readiness: {score}/100",
            "",
            "Strengths:",
        ]
        for s in report.get("strengths", []):
            lines.append(f"  ✓ {s}")

        lines.append("")
        lines.append("Recommendations:")
        for r in report.get("recommendations", []):
            lines.append(f"  → {r}")

        return "\n".join(lines)