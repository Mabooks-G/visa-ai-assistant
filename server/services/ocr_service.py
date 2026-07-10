"""
OCR (Optical Character Recognition) service.
Extracts text from images and scanned documents.
Uses Tesseract OCR or PaddleOCR for image-to-text conversion.
"""

import io
import logging
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)


class OCRService:
    """
    Service for extracting text from images and scanned PDFs.
    Uses Tesseract (pre-installed) with optional PaddleOCR for better accuracy.
    """

    def __init__(self, engine: str = "tesseract"):
        self.engine = engine
        self._tesseract_available = self._check_tesseract()
        self._paddle_available = False

        if engine == "paddle":
            try:
                from paddleocr import PaddleOCR
                self._paddle_ocr = PaddleOCR(use_angle_cls=True, lang="en")
                self._paddle_available = True
                logger.info("PaddleOCR initialized")
            except ImportError:
                logger.warning("PaddleOCR not installed, falling back to Tesseract")
                self.engine = "tesseract"

    def _check_tesseract(self) -> bool:
        """Check if Tesseract is available on the system."""
        try:
            import subprocess
            result = subprocess.run(
                ["tesseract", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("Tesseract not found on system")
            return False

    def extract_text(self, image_bytes: bytes, filename: str = "") -> str:
        """
        Extract text from image bytes.
        Returns extracted text or error message.
        """
        if not image_bytes:
            return ""

        try:
            from PIL import Image

            image = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB if needed
            if image.mode != "RGB":
                image = image.convert("RGB")

            if self.engine == "paddle" and self._paddle_available:
                return self._extract_paddle(image)
            elif self._tesseract_available:
                return self._extract_tesseract(image)
            else:
                logger.warning("No OCR engine available")
                return "[OCR not available — no Tesseract or PaddleOCR installed]"

        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return f"[OCR failed: {str(e)}]"

    def _extract_tesseract(self, image) -> str:
        """Extract text using Tesseract OCR."""
        try:
            import pytesseract
            text = pytesseract.image_to_string(image, lang="eng")
            return text.strip()
        except Exception as e:
            logger.error(f"Tesseract error: {e}")
            return ""

    def _extract_paddle(self, image) -> str:
        """Extract text using PaddleOCR (AMD GPU compatible)."""
        try:
            import numpy as np
            img_array = np.array(image)
            results = self._paddle_ocr.ocr(img_array)

            text_parts = []
            for line in results:
                if line:
                    for word_info in line:
                        text_parts.append(word_info[1][0])

            return "\n".join(text_parts)
        except Exception as e:
            logger.error(f"PaddleOCR error: {e}")
            return ""

    def is_available(self) -> bool:
        """Check if any OCR engine is available."""
        return self._tesseract_available or self._paddle_available