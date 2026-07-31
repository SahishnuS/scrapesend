"""Pydantic schemas for Company."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, HttpUrl


class CompanyBase(BaseModel):
    name: str
    careers_url: Optional[str] = None
    ats_provider: Optional[str] = None
    is_active: bool = True


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    careers_url: Optional[str] = None
    ats_provider: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyRead(CompanyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    last_crawled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
