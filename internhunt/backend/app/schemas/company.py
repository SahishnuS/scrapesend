"""Pydantic schemas for Company."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CompanyBase(BaseModel):
    name: str
    careers_url: str | None = None
    ats_provider: str | None = None
    is_active: bool = True


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = None
    careers_url: str | None = None
    ats_provider: str | None = None
    is_active: bool | None = None


class CompanyRead(CompanyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    last_crawled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
