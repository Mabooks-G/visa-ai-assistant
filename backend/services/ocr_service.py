"""
PaddleOCR service — GPU/ROCm accelerated text extraction with CPU fallback.

Detects whether ROCm (AMD GPU) or CUDA (NVIDIA GPU) is available and configures
PaddleOCR accordingly.  Falls back to CPU if no GPU is detected.
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy initialisation — the module import will work even if paddle is not installed
_ocr = None


def _detect_device() -> str:
    """Return 'gpu' if a usable GPU is found, otherwise 'cpu'."""
    try:
        import torch

        if torch.cuda.is_available():
            logger.info("CUDA device detected — using GPU")
            return "gpu"
        # ROCm exposes hip via torch
        if hasattr(torch, "hip") and torch.hip.is_available():
            logger.info("ROCm device detected — using GPU")
            return "gpu"
    except ImportError:
        pass

    try:
        import paddle

        if paddle.is_compiled_with_cuda():
            logger.info("Paddle compiled with CUDA — using GPU")
            return "gpu"
        if paddle.is_compiled_with_rocm():
            logger.info("Paddle compiled with ROCm — using GPU")
            return "gpu"
    except ImportError:
        pass

    logger.info("No GPU detected — falling back to CPU")
    return "cpu"


def _get_ocr(device: Optional[str] = None):
    """Return (or create) a singleton PaddleOCR instance."""
    global _ocr
    if _ocr is not None:
        return _ocr

    try:
        from paddleocr import PaddleOCR
    except ImportError:
        logger.warning("paddleocr is not installed — OCR will return empty results")
        return None

    if device is None:
        device = _detect_device()

    use_gpu = device == "gpu"
    logger.info(f"Initialising PaddleOCR (use_gpu={use_gpu})")

    _ocr = PaddleOCR(
        use_angle_cls=True,
        lang="en",
        use_gpu=use_gpu,
        show_log=False,
        # Lower memory usage for GPU
        gpu_mem=4000 if use_gpu else None,
    )
    return _ocr


def extract_text(file_path: str, device: Optional[str] = None) -> str:
    """
    Run OCR on a document image/PDF and return the extracted plain text.

    Args:
        file_path: Absolute or relative path to the document file.
        device: 'gpu' or 'cpu'.  Auto-detected when None.

    Returns:
        Concatenated text from all detected text regions.

    Raises:
        FileNotFoundError: if the file does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    ocr = _get_ocr(device)
    if ocr is None:
        logger.warning("PaddleOCR unavailable — returning empty text")
        return ""

    try:
        result = ocr.ocr(str(path), cls=True)
    except Exception as exc:
        logger.error(f"OCR processing failed: {exc}")
        # Retry once on CPU in case GPU OOM
        if device != "cpu":
            logger.info("Retrying OCR on CPU")
            # Force re-init on CPU
            global _ocr
            _ocr = None
            ocr = _get_ocr(device="cpu")
            result = ocr.ocr(str(path), cls=True)
        else:
            raise

    # PaddleOCR returns list[list[list[box, (text, confidence)]]]
    # For a single image, result is [[box_info, ...]]
    lines = []
    for page in result or []:
        for region in page or []:
            if len(region) >= 2:
                text, confidence = region[1]
                if confidence and confidence > 0.2:  # Filter low-confidence noise
                    lines.append(text.strip())

    return "\n".join(lines)


def extract_text_from_bytes(
    data: bytes, filename: str, device: Optional[str] = None
) -> str:
    """
    Convenience: write bytes to a temporary file, run OCR, return text.
    The temp file is cleaned up after extraction.
    """
    import tempfile

    suffix = Path(filename).suffix or ".png"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        return extract_text(tmp_path, device=device)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def health() -> dict:
    """Return the status of the OCR service."""
    device = _detect_device()
    return {
        "available": _get_ocr(device) is not None,
        "device": device,
    }