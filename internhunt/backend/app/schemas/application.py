"""Pydantic schemas for Application."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ApplicationBase(BaseModel):
    job_id: uuid.UUID
    resume_id: uuid.UUID
    status: str = "matched"
    match_score: float | None = None
    ats_score: float | None = None
    ats_keywords_matched: Any | None = None
    applied_at: datetime | None = None
    notes: str | None = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: str | None = None
    match_score: float | None = None
    ats_score: float | None = None
    ats_keywords_matched: Any | None = None
    applied_at: datetime | None = None
    notes: str | None = None


class ApplicationRead(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
