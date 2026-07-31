"""Notifications endpoints."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationRead

router = APIRouter()


@router.get("/", response_model=List[NotificationRead], summary="List notifications")
async def list_notifications(
    is_sent: Optional[bool] = Query(None),
    platform: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Notification).order_by(Notification.created_at.desc()).offset(skip).limit(limit)
    if is_sent is not None:
        stmt = stmt.where(Notification.is_sent == is_sent)
    if platform:
        stmt = stmt.where(Notification.platform == platform)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=NotificationRead, status_code=201, summary="Create a notification record")
async def create_notification(payload: NotificationCreate, db: AsyncSession = Depends(get_db)):
    notification = Notification(**payload.model_dump())
    db.add(notification)
    await db.flush()
    await db.refresh(notification)
    return notification


@router.get("/{notification_id}", response_model=NotificationRead, summary="Get a notification by ID")
async def get_notification(notification_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    notification = await db.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.delete("/{notification_id}", status_code=204, summary="Delete a notification")
async def delete_notification(notification_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    notification = await db.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    await db.delete(notification)
