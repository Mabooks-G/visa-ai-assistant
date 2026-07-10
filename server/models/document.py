from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class DocumentResponse(BaseModel):
    id: str
    application_id: Optional[str] = None
    created_at: Optional[datetime] = None
    file_name: str
    file_url: Optional[str] = None
    status: str = "pending"
    document_type: Optional[str] = None
    file_contents: Optional[str] = None


class ClassificationResponse(BaseModel):
    id: str
    document_id: Optional[str] = None
    created_at: Optional[datetime] = None
    classified_as: str
    confidence: float
    details: Optional[Any] = None
    issues: Optional[list[str]] = None