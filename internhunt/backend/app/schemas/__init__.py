"""
Pydantic schemas for request/response serialisation.
Import all schemas from this package.
"""

from app.schemas.application import ApplicationCreate, ApplicationRead, ApplicationUpdate
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.schemas.job import JobCreate, JobRead, JobUpdate
from app.schemas.log import LogCreate, LogRead
from app.schemas.notification import NotificationCreate, NotificationRead
from app.schemas.resume import ResumeCreate, ResumeRead, ResumeUpdate

__all__ = [
    "ApplicationCreate",
    "ApplicationRead",
    "ApplicationUpdate",
    "CategoryCreate",
    "CategoryRead",
    "CategoryUpdate",
    "CompanyCreate",
    "CompanyRead",
    "CompanyUpdate",
    "JobCreate",
    "JobRead",
    "JobUpdate",
    "LogCreate",
    "LogRead",
    "NotificationCreate",
    "NotificationRead",
    "ResumeCreate",
    "ResumeRead",
    "ResumeUpdate",
]
