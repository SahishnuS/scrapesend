"""Companies CRUD endpoints."""

import csv
import io
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate

router = APIRouter()


@router.get("/", response_model=list[CompanyRead], summary="List all companies")
async def list_companies(
    is_active: bool | None = Query(None, description="Filter by active status"),
    ats_provider: str | None = Query(None, description="Filter by ATS provider"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Company).order_by(Company.name)
    if is_active is not None:
        stmt = stmt.where(Company.is_active == is_active)
    if ats_provider:
        stmt = stmt.where(Company.ats_provider == ats_provider)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=CompanyRead, status_code=status.HTTP_201_CREATED, summary="Create a company")
async def create_company(payload: CompanyCreate, db: AsyncSession = Depends(get_db)):
    company = Company(**payload.model_dump())
    db.add(company)
    await db.flush()
    await db.refresh(company)
    return company


@router.get("/{company_id}", response_model=CompanyRead, summary="Get a company by ID")
async def get_company(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.patch("/{company_id}", response_model=CompanyRead, summary="Update a company")
async def update_company(company_id: uuid.UUID, payload: CompanyUpdate, db: AsyncSession = Depends(get_db)):
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    await db.flush()
    await db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a company")
async def delete_company(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    await db.delete(company)


@router.get("/template/csv", summary="Download CSV upload template")
async def download_csv_template():
    """Returns a CSV file with the correct headers for bulk company upload."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name", "careers_url", "ats_provider"])
    writer.writerow(["Ather Energy", "https://atherenergy.com/careers", "other"])
    writer.writerow(["GreyOrange", "https://www.greyorange.com/careers/", "greenhouse"])
    writer.writerow(["Locus", "https://locus.sh/careers/", "lever"])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=companies_template.csv"},
    )


@router.post("/bulk-upload", summary="Bulk upload companies from a CSV file")
async def bulk_upload_companies(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a CSV file with columns: name, careers_url, ats_provider.
    - 'name' is required.
    - 'careers_url' and 'ats_provider' are optional.
    - Duplicate company names are skipped.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted.")

    content = await file.read()
    try:
        text = content.decode("utf-8-sig")  # utf-8-sig handles BOM from Excel exports
    except UnicodeDecodeError as e:
        raise HTTPException(status_code=400, detail="File encoding must be UTF-8.") from e

    reader = csv.DictReader(io.StringIO(text))

    if not reader.fieldnames or "name" not in reader.fieldnames:
        raise HTTPException(
            status_code=400,
            detail="CSV must contain a 'name' column. Download the template for the correct format.",
        )

    added = []
    skipped = []
    errors = []

    for i, row in enumerate(reader, start=2):  # Row 1 is the header
        name = (row.get("name") or "").strip()
        if not name:
            errors.append(f"Row {i}: 'name' is empty, skipping.")
            continue

        # Check if already exists
        existing = await db.scalar(select(Company).where(Company.name == name))
        if existing:
            skipped.append(name)
            continue

        careers_url = (row.get("careers_url") or "").strip() or None
        ats_provider = (row.get("ats_provider") or "").strip().lower() or None

        company = Company(
            name=name,
            careers_url=careers_url,
            ats_provider=ats_provider,
            is_active=True,
        )
        db.add(company)
        added.append(name)

    await db.flush()

    return {
        "added": len(added),
        "skipped_duplicates": len(skipped),
        "errors": errors,
        "added_companies": added,
        "skipped_companies": skipped,
    }
