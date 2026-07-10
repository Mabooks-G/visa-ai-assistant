"""
Supabase database connection and helper functions.
Uses the service_role key for backend-to-database operations.
"""

import os
from typing import Optional
from supabase import create_client, Client

# Lazy-loaded client
_supabase: Optional[Client] = None


def get_db() -> Client:
    """Get or create the Supabase client (singleton pattern)."""
    global _supabase
    if _supabase is None:
        url = os.environ.get("SUPABASE_URL")
        service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not service_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set"
            )
        _supabase = create_client(url, service_key)
    return _supabase


# ── Visa Applications ──────────────────────────────────────────

def create_application(data: dict) -> dict:
    db = get_db()
    result = db.table("visa_applications").insert(data).execute()
    return result.data[0] if result.data else None


def get_applications(status: Optional[str] = None) -> list:
    db = get_db()
    query = db.table("visa_applications").select("*").order("created_at", desc=True)
    if status:
        query = query.eq("status", status)
    result = query.execute()
    return result.data or []


def get_application(application_id: str) -> Optional[dict]:
    db = get_db()
    result = (
        db.table("visa_applications")
        .select("*")
        .eq("id", application_id)
        .execute()
    )
    return result.data[0] if result.data else None


def update_application(application_id: str, updates: dict) -> Optional[dict]:
    db = get_db()
    result = (
        db.table("visa_applications")
        .update(updates)
        .eq("id", application_id)
        .execute()
    )
    return result.data[0] if result.data else None


# ── Documents ──────────────────────────────────────────────────

def create_document(data: dict) -> dict:
    db = get_db()
    result = db.table("documents").insert(data).execute()
    return result.data[0] if result.data else None


def get_documents(application_id: str) -> list:
    db = get_db()
    result = (
        db.table("documents")
        .select("*")
        .eq("application_id", application_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


def get_document(document_id: str) -> Optional[dict]:
    db = get_db()
    result = (
        db.table("documents")
        .select("*, document_classifications(*)")
        .eq("id", document_id)
        .execute()
    )
    return result.data[0] if result.data else None


def update_document(document_id: str, updates: dict) -> Optional[dict]:
    db = get_db()
    result = (
        db.table("documents")
        .update(updates)
        .eq("id", document_id)
        .execute()
    )
    return result.data[0] if result.data else None


# ── Document Classifications ───────────────────────────────────

def create_classification(data: dict) -> dict:
    db = get_db()
    result = db.table("document_classifications").insert(data).execute()
    return result.data[0] if result.data else None


def get_classification(document_id: str) -> Optional[dict]:
    db = get_db()
    result = (
        db.table("document_classifications")
        .select("*")
        .eq("document_id", document_id)
        .execute()
    )
    return result.data[0] if result.data else None


def get_application_classifications(application_id: str) -> list:
    db = get_db()
    result = (
        db.table("document_classifications")
        .select("*, document:documents!inner(*)")
        .eq("document.application_id", application_id)
        .execute()
    )
    return result.data or []


# ── Users ──────────────────────────────────────────────────────

def create_user(data: dict) -> dict:
    db = get_db()
    result = db.table("users").insert(data).execute()
    return result.data[0] if result.data else None


def get_user_by_email(email: str) -> Optional[dict]:
    db = get_db()
    result = (
        db.table("users")
        .select("*")
        .eq("email", email)
        .execute()
    )
    return result.data[0] if result.data else None


def get_user(user_id: str) -> Optional[dict]:
    db = get_db()
    result = (
        db.table("users")
        .select("*")
        .eq("id", user_id)
        .execute()
    )
    return result.data[0] if result.data else None


# ── Dashboard Stats ────────────────────────────────────────────

def get_dashboard_stats() -> dict:
    db = get_db()
    result = db.table("visa_applications").select("*").execute()
    applications = result.data or []

    total = len(applications)
    in_progress = sum(1 for a in applications if a.get("status") == "in_progress")
    verified = sum(1 for a in applications if a.get("status") == "verified")
    rejected = sum(1 for a in applications if a.get("status") == "rejected")

    scores = [a.get("overall_score", 0) for a in applications if a.get("overall_score") is not None]
    avg_score = round(sum(scores) / len(scores)) if scores else 0

    return {
        "total": total,
        "inProgress": in_progress,
        "verified": verified,
        "rejected": rejected,
        "avgScore": avg_score,
    }