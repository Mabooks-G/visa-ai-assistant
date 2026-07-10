"""Application CRUD service — manages visa application records."""

from datetime import datetime, timezone

from backend.database.db import get_supabase


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_application(
    userid: str,
    visa_type: str,
    applicant_name: str | None = None,
    passport_number: str | None = None,
) -> dict:
    """Create a new visa application for a user."""
    sb = get_supabase()
    result = sb.table('visa_applications').insert({
        'userid': userid,
        'visa_type': visa_type,
        'status': 'in_progress',
        'applicant_name': applicant_name or '',
        'passport_number': passport_number or '',
        'overall_score': 0,
    }).execute()

    if not result.data or len(result.data) == 0:
        raise RuntimeError('Failed to create application')

    return result.data[0]


def list_applications(userid: str) -> list[dict]:
    """Return all applications for a given user, newest first."""
    sb = get_supabase()
    result = sb.table('visa_applications') \
        .select('*') \
        .eq('userid', userid) \
        .order('created_at', desc=True) \
        .execute()
    return result.data or []


def get_application(app_id: str) -> dict | None:
    """Fetch a single application by its ID."""
    sb = get_supabase()
    result = sb.table('visa_applications') \
        .select('*') \
        .eq('id', app_id) \
        .execute()
    if result.data and len(result.data) > 0:
        return result.data[0]
    return None


def update_application(app_id: str, data: dict) -> dict:
    """Update fields on an application."""
    allowed = {'visa_type', 'status', 'applicant_name', 'passport_number', 'overall_score'}
    payload = {k: v for k, v in data.items() if k in allowed}

    if not payload:
        raise ValueError('No valid fields to update')

    sb = get_supabase()
    result = sb.table('visa_applications') \
        .update(payload) \
        .eq('id', app_id) \
        .execute()

    if not result.data or len(result.data) == 0:
        raise RuntimeError('Application not found')
    return result.data[0]


def delete_application(app_id: str, userid: str) -> None:
    """Delete an application and its documents."""
    sb = get_supabase()

    # Delete associated documents first
    sb.table('documents') \
      .delete() \
      .eq('application_id', app_id) \
      .execute()

    # Delete the application
    sb.table('visa_applications') \
      .delete() \
      .eq('id', app_id) \
      .eq('userid', userid) \
      .execute()


def get_application_with_documents(app_id: str) -> dict:
    """Return an application together with its documents and classifications."""
    sb = get_supabase()
    app = get_application(app_id)
    if not app:
        raise ValueError('Application not found')

    docs_result = sb.table('documents') \
        .select('*') \
        .eq('application_id', app_id) \
        .order('created_at', desc=True) \
        .execute()
    docs = docs_result.data or []

    # Attach classifications to each document
    for doc in docs:
        class_result = sb.table('document_classifications') \
            .select('*') \
            .eq('document_id', doc['id']) \
            .limit(1) \
            .execute()
        doc['classification'] = class_result.data[0] if class_result.data else None

    app['documents'] = docs
    return app


def count_applications(status_filter: str | None = None) -> int:
    """Count applications, optionally filtered by status."""
    sb = get_supabase()
    query = sb.table('visa_applications').select('id', count='exact')
    if status_filter:
        query = query.eq('status', status_filter)
    result = query.execute()
    return result.count or 0


def list_all_applications(limit: int = 50, offset: int = 0) -> tuple[list[dict], int]:
    """Admin: list all applications with pagination."""
    sb = get_supabase()
    count_result = sb.table('visa_applications') \
        .select('id', count='exact') \
        .execute()
    total = count_result.count or 0

    result = sb.table('visa_applications') \
        .select('*') \
        .order('created_at', desc=True) \
        .range(offset, offset + limit - 1) \
        .execute()

    return result.data or [], total