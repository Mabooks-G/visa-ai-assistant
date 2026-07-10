"""
User queries routes — Q&A between applicants and admins on their application.

Endpoints:
  POST /api/queries                    — Create a new query on an application
  GET  /api/queries/{application_id}   — List queries for an application (user can see their own)
  PUT  /api/queries/{query_id}         — Admin replies to a query
"""

from datetime import datetime, timezone
import logging

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from backend.middleware.auth import get_current_user, admin_required
from backend.database.db import get_supabase
from backend.services.application_service import get_application

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["queries"])


# ── Models ────────────────────────────────────────────────────────────────────

class CreateQueryRequest(BaseModel):
    application_id: str
    message: str


class ReplyQueryRequest(BaseModel):
    reply: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/queries")
async def create_query(
    body: CreateQueryRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a new query on an application (by the applicant)."""
    app = get_application(body.application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Only the owner or an admin can create queries
    is_owner = str(app.get("userid", "")) == str(current_user["id"])
    is_admin = current_user.get("user_type") == "admin"
    if not is_owner and not is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    sb = get_supabase()
    result = sb.table("queries").insert({
        "application_id": body.application_id,
        "user_id": current_user["id"],
        "message": body.message,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create query")
    return result.data[0]


@router.get("/queries/{application_id}")
async def list_queries(
    application_id: str,
    current_user: dict = Depends(get_current_user),
):
    """List queries for an application."""
    app = get_application(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    is_owner = str(app.get("userid", "")) == str(current_user["id"])
    is_admin = current_user.get("user_type") == "admin"
    if not is_owner and not is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    sb = get_supabase()
    result = sb.table("queries") \
        .select("*") \
        .eq("application_id", application_id) \
        .order("created_at", asc=True) \
        .execute()

    return {"queries": result.data or []}


@router.put("/queries/{query_id}")
async def reply_to_query(
    query_id: str,
    body: ReplyQueryRequest,
    current_user: dict = Depends(admin_required),
):
    """Admin replies to a query."""
    sb = get_supabase()
    now = datetime.now(timezone.utc).isoformat()

    result = sb.table("queries") \
        .update({
            "reply": body.reply,
            "admin_id": current_user["id"],
            "replied_at": now,
        }) \
        .eq("id", query_id) \
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Query not found")
    return result.data[0]