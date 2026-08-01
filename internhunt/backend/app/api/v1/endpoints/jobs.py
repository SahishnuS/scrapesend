"""Jobs CRUD endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.company import Company
from app.models.job import Job
from app.schemas.job import JobCreate, JobRead, JobUpdate

router = APIRouter()


@router.get("/", response_model=list[JobRead], summary="List jobs")
async def list_jobs(
    status: str | None = Query(None, description="Filter by status (open/closed)"),
    company_id: uuid.UUID | None = Query(None),
    category_id: uuid.UUID | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Job, Company.name.label("company_name"))
        .join(Company, Job.company_id == Company.id, isouter=True)
        .order_by(Job.discovered_at.desc())
        .offset(skip)
        .limit(limit)
    )
    if status:
        stmt = stmt.where(Job.status == status)
    if company_id:
        stmt = stmt.where(Job.company_id == company_id)
    if category_id:
        stmt = stmt.where(Job.category_id == category_id)
    result = await db.execute(stmt)
    rows = result.all()
    jobs_out = []
    for job, company_name in rows:
        job_data = JobRead.model_validate(job)
        job_data.company_name = company_name
        jobs_out.append(job_data)
    return jobs_out


@router.post("/", response_model=JobRead, status_code=201, summary="Create a job")
async def create_job(payload: JobCreate, db: AsyncSession = Depends(get_db)):
    job = Job(**payload.model_dump())
    db.add(job)
    await db.flush()
    await db.refresh(job)
    return job


@router.get("/{job_id}", response_model=JobRead, summary="Get a job by ID")
async def get_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/{job_id}", response_model=JobRead, summary="Update a job")
async def update_job(job_id: uuid.UUID, payload: JobUpdate, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    await db.flush()
    await db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=204, summary="Delete a job")
async def delete_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await db.delete(job)
