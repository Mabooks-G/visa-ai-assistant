"""
Quality check service — automated quality checks on uploaded documents.

Performs checks for:
  - Image resolution / DPI (for scanned documents)
  - Blur detection (via Laplacian variance)
  - File type validation
  - File size limits
  - Page count for multi-page documents
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Allowed file types
ALLOWED_MIME_TYPES = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MIN_DPI = 150


def check_file_type(filename: str) -> dict:
    """Check if the file extension is supported."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_MIME_TYPES:
        return {
            "passed": False,
            "message": f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_MIME_TYPES)}",
            "severity": "critical",
        }
    return {"passed": True, "message": f"File type '{ext}' is supported.", "severity": "info"}


def check_file_size(file_size: int) -> dict:
    """Check if the file size is within the allowed limit."""
    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        limit_mb = MAX_FILE_SIZE / (1024 * 1024)
        return {
            "passed": False,
            "message": f"File size ({size_mb:.1f} MB) exceeds the {limit_mb:.0f} MB limit.",
            "severity": "critical",
        }
    return {"passed": True, "message": "File size is within limits.", "severity": "info"}


def check_image_quality(file_path: str) -> dict:
    """
    Basic image quality check — resolution and blur detection.

    Requires OpenCV (cv2). If not installed, returns a warning.
    """
    try:
        import cv2
    except ImportError:
        return {
            "passed": None,
            "message": "Image quality check requires OpenCV (cv2) — skipping.",
            "severity": "info",
        }

    if not os.path.exists(file_path):
        return {"passed": False, "message": "File not found.", "severity": "critical"}

    # Try to read as image
    img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        # Might be a PDF — skip image checks
        return {
            "passed": None,
            "message": "Could not read as image (may be a PDF).",
            "severity": "info",
        }

    h, w = img.shape
    dpi_estimate = max(h, w) / 8.5  # Rough DPI estimate for letter-size document

    issues = []
    if dpi_estimate < MIN_DPI:
        issues.append(f"Estimated DPI ({dpi_estimate:.0f}) is below minimum ({MIN_DPI}).")

    # Blur detection: Laplacian variance
    laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
    if laplacian_var < 50:
        issues.append("Image appears blurry (low Laplacian variance).")

    if issues:
        return {
            "passed": False,
            "message": "; ".join(issues),
            "severity": "warning",
            "details": {
                "width_px": w,
                "height_px": h,
                "estimated_dpi": round(dpi_estimate, 1),
                "laplacian_var": round(laplacian_var, 2),
            },
        }

    return {
        "passed": True,
        "message": "Image quality is acceptable.",
        "severity": "info",
        "details": {
            "width_px": w,
            "height_px": h,
            "estimated_dpi": round(dpi_estimate, 1),
            "laplacian_var": round(laplacian_var, 2),
        },
    }


def check_pdf_page_count(file_path: str) -> dict:
    """Check the number of pages in a PDF document."""
    try:
        import PyPDF2
    except ImportError:
        return {
            "passed": None,
            "message": "Page count check requires PyPDF2 — skipping.",
            "severity": "info",
        }

    if not os.path.exists(file_path):
        return {"passed": False, "message": "File not found.", "severity": "critical"}

    if not file_path.lower().endswith(".pdf"):
        return {"passed": None, "message": "Not a PDF — skipping page count.", "severity": "info"}

    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            page_count = len(reader.pages)

        if page_count > 20:
            return {
                "passed": False,
                "message": f"Document has {page_count} pages — may be too large for processing.",
                "severity": "warning",
            }
        return {
            "passed": True,
            "message": f"Document has {page_count} page(s).",
            "severity": "info",
        }
    except Exception as exc:
        return {
            "passed": False,
            "message": f"Could not read PDF: {exc}",
            "severity": "warning",
        }


def run_all_checks(file_path: str, filename: str, file_size: int) -> dict:
    """
    Run all quality checks on a document and return a consolidated result.

    Args:
        file_path: Path to the uploaded file
        filename: Original filename
        file_size: File size in bytes

    Returns:
        dict with:
          - passed: bool (true if no critical or warning issues)
          - checks: list of individual check results
          - score: int 0-100 quality score
    """
    checks = []

    checks.append(check_file_type(filename))
    checks.append(check_file_size(file_size))
    checks.append(check_image_quality(file_path))
    checks.append(check_pdf_page_count(file_path))

    # Calculate a quality score
    total = len(checks)
    critical_issues = sum(1 for c in checks if c.get("severity") == "critical" and c.get("passed") is False)
    warnings = sum(1 for c in checks if c.get("severity") == "warning" and c.get("passed") is False)

    score = max(0, 100 - (critical_issues * 40 + warnings * 15))

    return {
        "passed": critical_issues == 0 and warnings == 0,
        "checks": checks,
        "score": score,
    }


def health() -> dict:
    """Return quality check service health."""
    return {"available": True}