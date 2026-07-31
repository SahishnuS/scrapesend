"""Pydantic schemas for Job."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class JobBase(BaseModel):
    company_id: uuid.UUID
    category_id: Optional[uuid.UUID] = None
    title: str
    job_url: str
    location: Optional[str] = None
    description: Optional[str] = None
    job_hash: str
    status: str = "open"


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    category_id: Optional[uuid.UUID] = None
    title: Optional[str] = None
    job_url: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class JobRead(JobBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    discovered_at: datetime
    created_at: datetime
    updated_at: datetime
