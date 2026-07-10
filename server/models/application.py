from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ApplicationCreate(BaseModel):
    visa_type: str
    applicant_name: Optional[str] = None
    passport_number: Optional[str] = None
    userid: Optional[str] = None


class ApplicationUpdate(BaseModel):
    visa_type: Optional[str] = None
    status: Optional[str] = None
    applicant_name: Optional[str] = None
    passport_number: Optional[str] = None
    overall_score: Optional[int] = None


class ApplicationResponse(BaseModel):
    id: str
    created_at: Optional[datetime] = None
    visa_type: str
    status: str = "in_progress"
    applicant_name: Optional[str] = None
    passport_number: Optional[str] = None
    overall_score: Optional[int] = 0
    userid: Optional[str] = None