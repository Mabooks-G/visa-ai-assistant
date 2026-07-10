import os
from dotenv import load_dotenv

load_dotenv()

# Debug: check which .env was loaded
import sys
print(f"[debug] CWD for load_dotenv: {os.getcwd()}", file=sys.stderr)

# Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://yuzcgqgojznjrimggfbo.supabase.co')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')
print(f"[debug] SUPABASE_SERVICE_KEY loaded: len={len(SUPABASE_SERVICE_KEY)}, starts_with={SUPABASE_SERVICE_KEY[:10] if SUPABASE_SERVICE_KEY else 'EMPTY'}", file=sys.stderr)
SUPABASE_ANON_KEY = os.getenv(
    'SUPABASE_ANON_KEY',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl1emNncWdvanpuanJpbWdnZmJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM1MDM2NjgsImV4cCI6MjA5OTA3OTY2OH0.fVTlR0s80Zq4s4JmY8pjNsMmp3swzjLiIV46jrVHb88'
)

# App
DATABASE_URL = os.getenv('DATABASE_URL', '')
SECRET_KEY = os.getenv('SECRET_KEY', 'visa-ai-secret-dev-key-change-in-production')
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
PORT = int(os.getenv('PORT', '8000'))

# Google AI / Gemma API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
GOOGLE_MODEL = os.getenv('GOOGLE_MODEL', 'gemma-4')

# Upload limits
UPLOAD_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
UPLOAD_DIR = os.getenv('UPLOAD_DIR', '/tmp/uploads')