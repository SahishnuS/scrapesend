"""
Models package — imports all ORM models so Alembic autogenerate finds them.

Add every new model module import here when creating new tables.
"""

from app.models.category import Category  # noqa: F401
from app.models.company import Company  # noqa: F401
from app.models.job import Job  # noqa: F401
from app.models.resume import Resume  # noqa: F401
from app.models.application import Application  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.log import Log  # noqa: F401
