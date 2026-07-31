"""Pydantic schemas for Notification."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class NotificationBase(BaseModel):
    job_id: Optional[uuid.UUID] = None
    platform: str  # telegram, email
    message: str
    is_sent: bool = False
    sent_at: Optional[datetime] = None


class NotificationCreate(NotificationBase):
    pass


class NotificationRead(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
