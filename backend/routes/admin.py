"""
Admin routes — requirement overrides, queries management, demo data seeding.

Endpoints:
  GET    /admin/requirements           — List all requirement overrides
  PUT    /admin/requirements           — Upsert an override for a country+visa_type
  DELETE /admin/requirements/{id}      — Remove an override
  GET    /admin/queries                — List all user queries (optional ?status=open/answered)
  POST   /admin/seed-demo              — Seed demo admin + applicant data
  GET    /admin/demo-data              — Get demo credentials info
"""

import hashlib
import secrets
import logging

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from backend.middleware.auth import admin_required, store_token
from backend.database.db import get_supabase

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["admin"])


# ── Models ────────────────────────────────────────────────────────────────────

class UpsertRequirementRequest(BaseModel):
    country: str
    visa_type: str
    requirements: list  # list of requirement dicts


class QueryReplyRequest(BaseModel):
    reply: str


# ── Requirements Management ───────────────────────────────────────────────────

@router.get("/admin/requirements")
async def admin_list_overrides(current_user: dict = Depends(admin_required)):
    """List all requirement overrides."""
    sb = get_supabase()
    result = sb.table("requirement_overrides") \
        .select("*") \
        .order("country") \
        .execute()
    return {"overrides": result.data or []}


@router.put("/admin/requirements")
async def admin_upsert_override(
    body: UpsertRequirementRequest,
    current_user: dict = Depends(admin_required),
):
    """Create or update a requirement override for a country+visa_type."""
    sb = get_supabase()
    existing = sb.table("requirement_overrides") \
        .select("id") \
        .eq("country", body.country) \
        .eq("visa_type", body.visa_type) \
        .execute()

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()

    if existing.data:
        result = sb.table("requirement_overrides") \
            .update({
                "requirements": body.requirements,
                "updated_at": now,
            }) \
            .eq("id", existing.data[0]["id"]) \
            .execute()
    else:
        result = sb.table("requirement_overrides") \
            .insert({
                "country": body.country,
                "visa_type": body.visa_type,
                "requirements": body.requirements,
                "created_at": now,
                "updated_at": now,
            }) \
            .execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save override")
    return result.data[0]


@router.delete("/admin/requirements/{override_id}")
async def admin_delete_override(
    override_id: str,
    current_user: dict = Depends(admin_required),
):
    """Delete a requirement override."""
    sb = get_supabase()
    sb.table("requirement_overrides") \
        .delete() \
        .eq("id", override_id) \
        .execute()
    return {"message": "Override deleted"}


# ── Queries Management ────────────────────────────────────────────────────────

@router.get("/admin/queries")
async def admin_list_queries(
    status: str | None = None,
    current_user: dict = Depends(admin_required),
):
    """List all user queries, optionally filtered by status (open / answered)."""
    sb = get_supabase()
    query = sb.table("queries") \
        .select("*, users!queries_user_id_fkey(email), visa_applications!queries_application_id_fkey(applicant_name, visa_type)") \
        .order("created_at", desc=True)

    if status == "open":
        query = query.or_("reply.is.null,reply.eq.")
    elif status == "answered":
        query = query.neq("reply", "")

    result = query.execute()
    return {"queries": result.data or []}


# ── Demo Data Seeding ─────────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a random salt (matches auth_service)."""
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{h}"


@router.post("/admin/seed-demo")
async def admin_seed_demo(current_user: dict = Depends(admin_required)):
    """Seed demo data: ensures demo admin exists, returns credentials."""
    sb = get_supabase()

    # Check if demo admin exists
    existing = sb.table("users") \
        .select("id") \
        .eq("email", "admin@visa-ai.com") \
        .execute()

    if not existing.data:
        hashed = _hash_password("admin123")
        sb.table("users").insert({
            "email": "admin@visa-ai.com",
            "password": hashed,
            "user_type": "admin",
        }).execute()

    return {
        "message": "Demo data ready",
        "admin": {"email": "admin@visa-ai.com", "password": "admin123"},
    }


@router.get("/admin/demo-data")
async def admin_get_demo_data():
    """Return demo credentials (no auth required — only returns public demo info)."""
    return {
        "admin": {"email": "admin@visa-ai.com", "password": "admin123"},
    }