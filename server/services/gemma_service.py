"""
Gemma AI model service for GPU-accelerated document classification.
This service loads and runs Google's Gemma model on AMD GPUs via ROCm.

Prerequisites on AMD Cloud:
  - ROCm drivers installed
  - transformers Python library (added to requirements.txt)
  - Gemma model weights downloaded to GEMMA_MODEL_PATH
"""

import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class GemmaService:
    """
    Service wrapping the Gemma model for visa document analysis.
    Designed to run on AMD GPUs via ROCm.
    """

    def __init__(self, model_path: Optional[str] = None, use_gpu: bool = True):
        self.model_path = model_path or os.environ.get(
            "GEMMA_MODEL_PATH", "/models/gemma-2b-it"
        )
        self.use_gpu = use_gpu and os.environ.get("USE_GPU", "true").lower() == "true"
        self.model = None
        self.tokenizer = None
        self._loaded = False

    def load_model(self):
        """Load the Gemma model into memory/GPU."""
        if self._loaded:
            return True

        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM

            logger.info(f"Loading Gemma model from {self.model_path}")

            device = "cuda" if self.use_gpu and torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None,
            )

            if device == "cpu":
                self.model.to("cpu")

            self._loaded = True
            logger.info("Gemma model loaded successfully")
            return True

        except ImportError:
            logger.warning(
                "transformers/torch not installed. "
                "Install with: pip install transformers torch torchvision"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to load Gemma model: {e}")
            return False

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.1,
    ) -> str:
        """
        Generate text using the Gemma model.
        Falls back to mock response if model is not available.
        """
        if not self._loaded:
            loaded = self.load_model()
            if not loaded:
                logger.warning("Gemma not available, using fallback")
                return self._fallback_response(prompt)

        try:
            import torch

            inputs = self.tokenizer(prompt, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=temperature > 0,
                    pad_token_id=self.tokenizer.eos_token_id,
                )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Strip the input prompt from the response
            if prompt in response:
                response = response[len(prompt):].strip()

            return response

        except Exception as e:
            logger.error(f"Gemma generation error: {e}")
            return self._fallback_response(prompt)

    def classify_document(self, document_text: str) -> dict:
        """
        Classify a document using the Gemma model.
        Returns structured JSON with document type, confidence, and fields.
        """
        from server.utils.prompts import get_classifier_prompt

        prompt = get_classifier_prompt(document_text)
        response = self.generate(prompt, max_new_tokens=300)

        # Try to parse JSON from response
        try:
            # Find JSON block in response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass

        # Fallback to regex-based classifier
        from server.services.classifier_service import ClassifierService
        fallback = ClassifierService(use_gpu=False)
        return fallback.classify(document_text)

    def assess_readiness(self, visa_type: str, documents: list) -> dict:
        """
        Assess visa readiness using the Gemma model.
        """
        from server.utils.prompts import get_readiness_prompt

        prompt = get_readiness_prompt(visa_type, documents)
        response = self.generate(prompt, max_new_tokens=400)

        # Try to parse JSON
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except (json.JSONDecodeError, ValueError):
            pass

        # Fallback
        from server.utils.readiness_score import calculate_readiness_score

        return calculate_readiness_score(documents, visa_type)

    def _fallback_response(self, prompt: str) -> str:
        """Return a mock response when Gemma is not available."""
        return json.dumps({
            "document_type": "other",
            "confidence": 0.5,
            "extracted_fields": {},
            "issues": ["AI model not available — using fallback classification"],
            "note": "Gemma model not loaded. Install with GPU for full AI analysis.",
        })