"""Pydantic schemas for Log."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class LogBase(BaseModel):
    level: str  # INFO, WARNING, ERROR
    module: str
    message: str
    details: Any | None = None


class LogCreate(LogBase):
    pass


class LogRead(LogBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    timestamp: datetime
