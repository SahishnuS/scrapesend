"""
Central API v1 router.

Each feature module registers its own router here.
Keep this file minimal — business logic belongs in services.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    applications,
    categories,
    companies,
    health,
    jobs,
    logs,
    notifications,
    resumes,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
api_router.include_router(
    applications.router, prefix="/applications", tags=["Applications"]
)
api_router.include_router(
    notifications.router, prefix="/notifications", tags=["Notifications"]
)
api_router.include_router(logs.router, prefix="/logs", tags=["Logs"])
