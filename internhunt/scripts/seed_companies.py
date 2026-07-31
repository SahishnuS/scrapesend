import asyncio
import sys
import os

# Ensure the backend directory is in the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from app.db.session import AsyncSessionLocal
from app.models.company import Company

COMPANIES_TO_SEED = [
    {"name": "Ather Energy", "careers_url": "https://atherenergy.com/careers", "ats_provider": "other"},
    {"name": "GreyOrange", "careers_url": "https://www.greyorange.com/careers/", "ats_provider": "greenhouse"},
    {"name": "CynLr", "careers_url": "https://cynlr.com/careers/", "ats_provider": "other"},
    {"name": "Ati Motors", "careers_url": "https://www.atimotors.com/careers/", "ats_provider": "other"},
    {"name": "Planys Technologies", "careers_url": "https://www.planystech.com/careers/", "ats_provider": "other"},
    {"name": "Detect Technologies", "careers_url": "https://detecttechnologies.com/careers/", "ats_provider": "other"},
    {"name": "Ola Electric", "careers_url": "https://olaelectric.com/careers", "ats_provider": "other"},
    {"name": "Niqo Robotics", "careers_url": "https://niqorobotics.com/careers/", "ats_provider": "other"},
    {"name": "Unbox Robotics", "careers_url": "https://unboxrobotics.com/careers/", "ats_provider": "other"},
    {"name": "Locus", "careers_url": "https://locus.sh/careers/", "ats_provider": "lever"},
    {"name": "Wysa", "careers_url": "https://www.wysa.io/careers", "ats_provider": "other"},
    {"name": "Mad Street Den", "careers_url": "https://www.madstreetden.com/careers/", "ats_provider": "workable"},
    {"name": "AlphaICs", "careers_url": "https://alphaics.com/careers", "ats_provider": "other"},
    {"name": "Ideaforge", "careers_url": "https://www.ideaforge.co.in/careers/", "ats_provider": "other"},
]

async def seed_database():
    async with AsyncSessionLocal() as db:
        print("Seeding Indian Robotics & AI Companies...")
        for company_data in COMPANIES_TO_SEED:
            # Check if exists
            from sqlalchemy import select
            result = await db.execute(select(Company).where(Company.name == company_data["name"]))
            existing = result.scalar_one_or_none()
            
            if not existing:
                company = Company(**company_data)
                db.add(company)
                print(f"✅ Added {company.name}")
            else:
                print(f"⚡ Skipped {company_data['name']} (already exists)")
        
        await db.commit()
        print("Database seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_database())
