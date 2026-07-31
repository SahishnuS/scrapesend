from sqlalchemy import String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
import uuid
from datetime import datetime

class Log(Base):
    __tablename__ = "logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    level: Mapped[str] = mapped_column(String(20)) # INFO, WARNING, ERROR
    module: Mapped[str] = mapped_column(String(100)) # e.g. crawler, ai_matcher
    message: Mapped[str] = mapped_column(Text)
    details: Mapped[dict | None] = mapped_column(JSONB)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
