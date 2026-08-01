"""Pydantic schemas for Job."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobBase(BaseModel):
    company_id: uuid.UUID
    category_id: uuid.UUID | None = None
    title: str
    job_url: str
    location: str | None = None
    description: str | None = None
    job_hash: str
    status: str = "open"


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    title: str | None = None
    job_url: str | None = None
    location: str | None = None
    description: str | None = None
    status: str | None = None


class JobRead(JobBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    discovered_at: datetime
    created_at: datetime
    updated_at: datetime
