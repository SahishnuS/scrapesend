import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    resume_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resumes.id", ondelete="RESTRICT"), index=True)

    status: Mapped[str] = mapped_column(String(50), default="matched") # matched, applied, interviewing, rejected, offer

    # ATS Tracking Fields
    match_score: Mapped[float | None] = mapped_column(Float)
    ats_score: Mapped[float | None] = mapped_column(Float) # Specific ATS evaluated score
    ats_keywords_matched: Mapped[dict | None] = mapped_column(JSONB) # Store list/dict of keywords matched for ATS

    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
