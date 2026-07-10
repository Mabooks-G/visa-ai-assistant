import os
import sys

# Ensure the backend directory is on sys.path so relative imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config.settings import CORS_ORIGINS, PORT

app = FastAPI(
    title='Visa AI Assistant API',
    version='1.0.0',
    docs_url='/api/docs',
    redoc_url='/api/redoc',
)

# ── CORS ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# ── Startup ────────────────────────────────────────────────────────────────
@app.on_event('startup')
async def startup():
    print(f'Visa AI Assistant API starting on port {PORT}')
    from backend.database.db import get_supabase
    try:
        sb = get_supabase()
        # Quick health check
        sb.table('users').select('id').limit(1).execute()
        print('✓ Supabase connection validated')
    except Exception as e:
        print(f'⚠  Supabase connection failed: {e}')


# ── Health endpoint ────────────────────────────────────────────────────────
@app.get('/api/health')
async def health_check():
    return {'status': 'ok', 'version': '1.0.0'}


# ── Route registration ──────────────────────────────────────────────────────
from backend.routes import users as user_routes
from backend.routes import applications as app_routes
from backend.routes import analysis as analysis_routes

app.include_router(user_routes.router)
app.include_router(app_routes.router)
app.include_router(analysis_routes.router)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend.app:app', host='0.0.0.0', port=PORT, reload=True)