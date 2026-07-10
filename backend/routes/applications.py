"""Application & Document CRUD routes."""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel

from backend.middleware.auth import get_current_user
from backend.services.application_service import (
    create_application,
    list_applications,
    get_application,
    get_application_with_documents,
    update_application,
    delete_application,
)
from backend.services.document_service import (
    create_document,
    list_documents,
    get_document,
    update_document,
    delete_document,
    get_document_with_classification,
    verify_document_ownership,
)

router = APIRouter(prefix='/api', tags=['applications'])


# ── Request / Response models ────────────────────────────────────────────────

class CreateAppRequest(BaseModel):
    visa_type: str
    applicant_name: str | None = None
    passport_number: str | None = None


class UpdateAppRequest(BaseModel):
    visa_type: str | None = None
    status: str | None = None
    applicant_name: str | None = None
    passport_number: str | None = None
    overall_score: int | None = None


class CreateDocRequest(BaseModel):
    file_name: str
    document_type: str | None = None


class UpdateDocRequest(BaseModel):
    status: str | None = None
    document_type: str | None = None
    File_contents: str | None = None


# ── Application endpoints ────────────────────────────────────────────────────

@router.post('/applications')
async def api_create_application(
    body: CreateAppRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a new visa application."""
    try:
        app = create_application(
            userid=current_user['id'],
            visa_type=body.visa_type,
            applicant_name=body.applicant_name,
            passport_number=body.passport_number,
        )
        return app
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/applications')
async def api_list_applications(
    current_user: dict = Depends(get_current_user),
):
    """List all applications for the current user."""
    apps = list_applications(current_user['id'])
    return {'applications': apps}


@router.get('/applications/{app_id}')
async def api_get_application(
    app_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a single application with its documents."""
    app = get_application_with_documents(app_id)
    if not app:
        raise HTTPException(status_code=404, detail='Application not found')
    if str(app.get('userid', '')) != str(current_user['id']):
        raise HTTPException(status_code=403, detail='Access denied')
    return app


@router.patch('/applications/{app_id}')
async def api_update_application(
    app_id: str,
    body: UpdateAppRequest,
    current_user: dict = Depends(get_current_user),
):
    """Update an application's fields."""
    app = get_application(app_id)
    if not app:
        raise HTTPException(status_code=404, detail='Application not found')
    if str(app.get('userid', '')) != str(current_user['id']):
        raise HTTPException(status_code=403, detail='Access denied')

    data = body.model_dump(exclude_none=True)
    try:
        updated = update_application(app_id, data)
        return updated
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put('/applications/{app_id}')
async def api_update_application_put(
    app_id: str,
    body: UpdateAppRequest,
    current_user: dict = Depends(get_current_user),
):
    """Alias for PATCH — update an application's fields."""
    app = get_application(app_id)
    if not app:
        raise HTTPException(status_code=404, detail='Application not found')
    if str(app.get('userid', '')) != str(current_user['id']):
        raise HTTPException(status_code=403, detail='Access denied')

    data = body.model_dump(exclude_none=True)
    try:
        updated = update_application(app_id, data)
        return updated
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete('/applications/{app_id}')
async def api_delete_application(
    app_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete an application and its documents."""
    app = get_application(app_id)
    if not app:
        raise HTTPException(status_code=404, detail='Application not found')
    if str(app.get('userid', '')) != str(current_user['id']):
        raise HTTPException(status_code=403, detail='Access denied')

    delete_application(app_id, current_user['id'])
    return {'message': 'Application deleted'}


# ── Document endpoints (scoped under an application) ────────────────────────

@router.post('/applications/{app_id}/documents')
async def api_create_document(
    app_id: str,
    body: CreateDocRequest,
    current_user: dict = Depends(get_current_user),
):
    """Add a document record to an application."""
    app = get_application(app_id)
    if not app:
        raise HTTPException(status_code=404, detail='Application not found')
    if str(app.get('userid', '')) != str(current_user['id']):
        raise HTTPException(status_code=403, detail='Access denied')

    try:
        doc = create_document(
            application_id=app_id,
            file_name=body.file_name,
            document_type=body.document_type,
        )
        return doc
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/applications/{app_id}/documents')
async def api_list_documents(
    app_id: str,
    current_user: dict = Depends(get_current_user),
):
    """List all documents for an application."""
    app = get_application(app_id)
    if not app:
        raise HTTPException(status_code=404, detail='Application not found')
    if str(app.get('userid', '')) != str(current_user['id']):
        raise HTTPException(status_code=403, detail='Access denied')

    docs = list_documents(app_id)
    return {'documents': docs}


@router.get('/documents/{doc_id}')
async def api_get_document(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a single document with its classification."""
    if not verify_document_ownership(doc_id, current_user['id']):
        raise HTTPException(status_code=404, detail='Document not found')

    doc = get_document_with_classification(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail='Document not found')
    return doc


@router.patch('/documents/{doc_id}')
async def api_update_document(
    doc_id: str,
    body: UpdateDocRequest,
    current_user: dict = Depends(get_current_user),
):
    """Update a document record."""
    if not verify_document_ownership(doc_id, current_user['id']):
        raise HTTPException(status_code=404, detail='Document not found')

    data = body.model_dump(exclude_none=True)
    try:
        updated = update_document(doc_id, data)
        return updated
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete('/documents/{doc_id}')
async def api_delete_document(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a document."""
    if not verify_document_ownership(doc_id, current_user['id']):
        raise HTTPException(status_code=404, detail='Document not found')

    delete_document(doc_id)
    return {'message': 'Document deleted'}