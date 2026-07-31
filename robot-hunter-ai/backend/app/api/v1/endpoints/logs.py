"""Logs endpoints — read-only (writes happen internally)."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.log import Log
from app.schemas.log import LogCreate, LogRead

router = APIRouter()


@router.get("/", response_model=List[LogRead], summary="List system logs")
async def list_logs(
    level: Optional[str] = Query(None, description="Filter by level: INFO, WARNING, ERROR"),
    module: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Log).order_by(Log.timestamp.desc()).offset(skip).limit(limit)
    if level:
        stmt = stmt.where(Log.level == level.upper())
    if module:
        stmt = stmt.where(Log.module == module)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=LogRead, status_code=201, summary="Write a log entry")
async def create_log(payload: LogCreate, db: AsyncSession = Depends(get_db)):
    log = Log(**payload.model_dump())
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


@router.get("/{log_id}", response_model=LogRead, summary="Get a log entry by ID")
async def get_log(log_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from fastapi import HTTPException
    log = await db.get(Log, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log
