"""
Resumes endpoints — upload, list, activate, delete.
File upload is handled via multipart form; text extraction uses pdfplumber.
"""

import uuid
from typing import List

import pdfplumber
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.resume import Resume
from app.schemas.resume import ResumeRead, ResumeUpdate

router = APIRouter()


def _extract_text(file_bytes: bytes) -> str:
    """Extract plain text from a PDF byte stream using pdfplumber."""
    import io
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
    return "\n".join(text_parts)


@router.get("/", response_model=List[ResumeRead], summary="List all resumes")
async def list_resumes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).order_by(Resume.created_at.desc()))
    return result.scalars().all()


@router.post(
    "/upload",
    response_model=ResumeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a resume PDF",
)
async def upload_resume(
    file: UploadFile = File(..., description="PDF resume file"),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ("application/pdf",):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await file.read()
    extracted_text = _extract_text(file_bytes)

    # Store path as a placeholder — actual Supabase Storage upload is Phase 5
    file_path = f"resumes/{uuid.uuid4()}_{file.filename}"

    resume = Resume(
        filename=file.filename,
        file_path=file_path,
        extracted_text=extracted_text,
        is_active=False,
    )
    db.add(resume)
    await db.flush()
    await db.refresh(resume)
    return resume


@router.get("/{resume_id}", response_model=ResumeRead, summary="Get a resume by ID")
async def get_resume(resume_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.post("/{resume_id}/activate", response_model=ResumeRead, summary="Set a resume as active")
async def activate_resume(resume_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Deactivate all resumes, then activate the selected one."""
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    # Deactivate all
    await db.execute(update(Resume).values(is_active=False))
    # Activate selected
    resume.is_active = True
    await db.flush()
    await db.refresh(resume)
    return resume


@router.patch("/{resume_id}", response_model=ResumeRead, summary="Update resume metadata")
async def update_resume(resume_id: uuid.UUID, payload: ResumeUpdate, db: AsyncSession = Depends(get_db)):
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(resume, field, value)
    await db.flush()
    await db.refresh(resume)
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a resume")
async def delete_resume(resume_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    await db.delete(resume)
