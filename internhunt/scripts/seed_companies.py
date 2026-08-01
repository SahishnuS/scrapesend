import asyncio
import json
import os
import sys

# Ensure the backend directory is in the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from app.db.session import AsyncSessionLocal
from app.models.company import Company

PORTALS_FILE = os.path.join(os.path.dirname(__file__), "../data/career_portals.json")


def load_companies() -> list[dict]:
    """
    Read the verified career portal registry.
    Entries with a null careers_url have no reachable public careers page
    (see the `note` field) and are not seeded.
    """
    with open(PORTALS_FILE) as f:
        registry = json.load(f)

    return [
        {
            "name": c["name"],
            "careers_url": c["careers_url"],
            "ats_provider": c["ats_provider"],
        }
        for c in registry["companies"]
        if c["careers_url"]
    ]


async def seed_database():
    companies_to_seed = load_companies()
    async with AsyncSessionLocal() as db:
        print(f"Seeding {len(companies_to_seed)} companies from career_portals.json...")
        for company_data in companies_to_seed:
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
