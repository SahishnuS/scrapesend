"""
SQLAlchemy declarative base for all ORM models.

All models import Base from this module to ensure a single metadata registry,
which Alembic uses to auto-generate migration scripts.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass
