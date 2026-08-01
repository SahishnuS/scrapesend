"""Pydantic schemas for Resume."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeBase(BaseModel):
    filename: str
    file_path: str
    extracted_text: str | None = None
    is_active: bool = False


class ResumeCreate(ResumeBase):
    pass


class ResumeUpdate(BaseModel):
    filename: str | None = None
    extracted_text: str | None = None
    is_active: bool | None = None


class ResumeRead(ResumeBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
