"""Applications CRUD endpoints with ATS score tracking."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationRead

router = APIRouter()

VALID_STATUSES = {"matched", "applied", "interviewing", "offer", "rejected"}


@router.get("/", response_model=List[ApplicationRead], summary="List applications")
async def list_applications(
    status: Optional[str] = Query(None, description="Filter by status"),
    job_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Application).order_by(Application.created_at.desc()).offset(skip).limit(limit)
    if status:
        stmt = stmt.where(Application.status == status)
    if job_id:
        stmt = stmt.where(Application.job_id == job_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED, summary="Create an application record")
async def create_application(payload: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail=f"Invalid status. Choose from: {VALID_STATUSES}")
    application = Application(**payload.model_dump())
    db.add(application)
    await db.flush()
    await db.refresh(application)
    return application


@router.get("/{application_id}", response_model=ApplicationRead, summary="Get an application by ID")
async def get_application(application_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    application = await db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.patch("/{application_id}", response_model=ApplicationRead, summary="Update application status / ATS scores")
async def update_application(application_id: uuid.UUID, payload: ApplicationUpdate, db: AsyncSession = Depends(get_db)):
    application = await db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if payload.status and payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail=f"Invalid status. Choose from: {VALID_STATUSES}")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(application, field, value)
    await db.flush()
    await db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an application")
async def delete_application(application_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    application = await db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    await db.delete(application)
