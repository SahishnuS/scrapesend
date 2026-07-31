"""Pydantic schemas for Application."""

import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class ApplicationBase(BaseModel):
    job_id: uuid.UUID
    resume_id: uuid.UUID
    status: str = "matched"
    match_score: Optional[float] = None
    ats_score: Optional[float] = None
    ats_keywords_matched: Optional[Any] = None
    applied_at: Optional[datetime] = None
    notes: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    match_score: Optional[float] = None
    ats_score: Optional[float] = None
    ats_keywords_matched: Optional[Any] = None
    applied_at: Optional[datetime] = None
    notes: Optional[str] = None


class ApplicationRead(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
