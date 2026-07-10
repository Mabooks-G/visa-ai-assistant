# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Ensure local binaries are in PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Default environment variables
ENV PORT=8000
ENV USE_GPU=true
ENV LOG_LEVEL=INFO

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT} --log-level ${LOG_LEVEL}"]