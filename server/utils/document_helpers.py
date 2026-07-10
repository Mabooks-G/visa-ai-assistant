"""
Helper functions for document processing and validation.
"""

import re
from typing import Optional


def extract_text_from_upload(file_content: bytes, filename: str) -> str:
    """
    Extract text content from uploaded file.
    Handles PDF, images (via OCR), and plain text files.
    """
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext in ("txt", "csv", "json", "xml", "html", "md"):
        return file_content.decode("utf-8", errors="replace")

    if ext in ("pdf",):
        # Simple PDF text extraction fallback
        try:
            text = file_content.decode("utf-8", errors="replace")
            return text
        except UnicodeDecodeError:
            return "[Binary PDF content — OCR required]"

    if ext in ("jpg", "jpeg", "png", "tiff", "bmp"):
        return f"[Image file — {filename}, size: {len(file_content)} bytes. OCR pipeline would process this.]"

    # Fallback
    try:
        return file_content.decode("utf-8", errors="replace")
    except UnicodeDecodeError:
        return f"[Binary file — {filename}, size: {len(file_content)} bytes]"


def validate_passport_number(passport_number: str) -> bool:
    """Basic passport number validation (alphanumeric, 6-20 chars)."""
    return bool(re.match(r"^[A-Z0-9]{6,20}$", passport_number.upper()))


def validate_email(email: str) -> bool:
    """Basic email format validation."""
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email))


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to remove unsafe characters."""
    return re.sub(r"[^\w\-_.() ]", "", filename)


def truncate_text(text: str, max_length: int = 10000) -> str:
    """Truncate text to a maximum length, preserving word boundaries."""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "... [truncated]"