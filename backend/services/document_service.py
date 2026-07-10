"""Document CRUD service — manages uploaded document records."""

from datetime import datetime, timezone
from backend.database.db import get_supabase


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_document(
    application_id: str,
    file_name: str,
    document_type: str | None = None,
) -> dict:
    """Create a document record linked to an application."""
    sb = get_supabase()
    result = sb.table('documents').insert({
        'application_id': application_id,
        'file_name': file_name,
        'document_type': document_type or '',
        'status': 'pending',
    }).execute()

    if not result.data or len(result.data) == 0:
        raise RuntimeError('Failed to create document record')
    return result.data[0]


def list_documents(application_id: str) -> list[dict]:
    """Return all documents for an application, newest first."""
    sb = get_supabase()
    result = sb.table('documents') \
        .select('*') \
        .eq('application_id', application_id) \
        .order('created_at', desc=True) \
        .execute()
    return result.data or []


def get_document(doc_id: str) -> dict | None:
    """Fetch a single document by its ID."""
    sb = get_supabase()
    result = sb.table('documents') \
        .select('*') \
        .eq('id', doc_id) \
        .execute()
    if result.data and len(result.data) > 0:
        return result.data[0]
    return None


def update_document(doc_id: str, data: dict) -> dict:
    """Update fields on a document record."""
    allowed = {'status', 'document_type', 'File_contents'}
    payload = {k: v for k, v in data.items() if k in allowed}
    if not payload:
        raise ValueError('No valid fields to update')

    sb = get_supabase()
    result = sb.table('documents') \
        .update(payload) \
        .eq('id', doc_id) \
        .execute()

    if not result.data or len(result.data) == 0:
        raise RuntimeError('Document not found')
    return result.data[0]


def delete_document(doc_id: str) -> None:
    """Delete a document and its classifications."""
    sb = get_supabase()

    # Remove classifications first
    sb.table('document_classifications') \
      .delete() \
      .eq('document_id', doc_id) \
      .execute()

    # Remove the document record
    sb.table('documents') \
      .delete() \
      .eq('id', doc_id) \
      .execute()


def get_document_with_classification(doc_id: str) -> dict | None:
    """Return a document together with its latest classification."""
    doc = get_document(doc_id)
    if not doc:
        return None

    sb = get_supabase()
    class_result = sb.table('document_classifications') \
        .select('*') \
        .eq('document_id', doc_id) \
        .limit(1) \
        .execute()

    doc['classification'] = class_result.data[0] if class_result.data else None
    return doc


def verify_document_ownership(doc_id: str, userid: str) -> bool:
    """Check whether a document belongs to an application owned by the given user."""
    doc = get_document(doc_id)
    if not doc:
        return False
    app_id = doc.get('application_id')
    if not app_id:
        return False

    from backend.services.application_service import get_application
    app = get_application(app_id)
    if not app:
        return False
    return str(app.get('userid', '')) == str(userid)