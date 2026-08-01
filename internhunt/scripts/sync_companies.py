#!/usr/bin/env python3
"""
Sync data/career_portals.json into the companies table.

The registry file is the source of truth for which portals get crawled. This
script is idempotent and safe to run before every crawl:

  * new companies are inserted and marked active
  * a changed careers_url / ats_provider is written back
  * companies whose registry entry has a null careers_url (no crawlable portal)
    are deactivated rather than deleted, so their existing jobs stay intact
  * companies no longer in the registry at all are also deactivated

Usage:
    python scripts/sync_companies.py            # apply the sync
    python scripts/sync_companies.py --dry-run  # print the plan only
"""

import argparse
import asyncio
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

PORTALS_FILE = os.path.join(os.path.dirname(__file__), "../data/career_portals.json")


def load_registry() -> list[dict]:
    """Return every registry entry, crawlable or not."""
    with open(PORTALS_FILE) as f:
        return json.load(f)["companies"]


def plan_sync(registry: list[dict], existing: dict[str, dict]) -> dict[str, list]:
    """
    Work out what to do, without touching the database.

    `existing` maps company name -> {"careers_url", "ats_provider", "is_active"}.
    Returns lists of insert / update / deactivate actions.
    """
    crawlable = {c["name"]: c for c in registry if c["careers_url"]}
    inserts, updates, deactivates = [], [], []

    for name, entry in crawlable.items():
        current = existing.get(name)
        if current is None:
            inserts.append(
                {
                    "name": name,
                    "careers_url": entry["careers_url"],
                    "ats_provider": entry["ats_provider"],
                }
            )
            continue

        changes = {}
        if current["careers_url"] != entry["careers_url"]:
            changes["careers_url"] = entry["careers_url"]
        if current["ats_provider"] != entry["ats_provider"]:
            changes["ats_provider"] = entry["ats_provider"]
        if not current["is_active"]:
            changes["is_active"] = True
        if changes:
            updates.append({"name": name, "changes": changes})

    # Anything active in the DB that is not a crawlable registry entry any more.
    for name, current in existing.items():
        if current["is_active"] and name not in crawlable:
            deactivates.append(name)

    return {"insert": inserts, "update": updates, "deactivate": deactivates}


async def sync_companies(dry_run: bool = False) -> dict[str, int]:
    from sqlalchemy import select

    from app.db.session import AsyncSessionLocal
    from app.models.company import Company

    registry = load_registry()

    async with AsyncSessionLocal() as db:
        rows = (await db.execute(select(Company))).scalars().all()
        existing = {
            row.name: {
                "careers_url": row.careers_url,
                "ats_provider": row.ats_provider,
                "is_active": row.is_active,
            }
            for row in rows
        }

        plan = plan_sync(registry, existing)

        print(
            f"Registry: {len(registry)} entries "
            f"({sum(1 for c in registry if c['careers_url'])} crawlable). "
            f"Database: {len(existing)} companies."
        )
        print(
            f"Plan: +{len(plan['insert'])} insert, "
            f"~{len(plan['update'])} update, "
            f"-{len(plan['deactivate'])} deactivate"
        )

        if dry_run:
            for item in plan["insert"]:
                print(f"  + {item['name']}  {item['careers_url']}")
            for item in plan["update"]:
                print(f"  ~ {item['name']}  {item['changes']}")
            for name in plan["deactivate"]:
                print(f"  - {name}")
            return {k: len(v) for k, v in plan.items()}

        for item in plan["insert"]:
            db.add(Company(**item, is_active=True))

        by_name = {row.name: row for row in rows}
        for item in plan["update"]:
            row = by_name[item["name"]]
            for field, value in item["changes"].items():
                setattr(row, field, value)

        for name in plan["deactivate"]:
            by_name[name].is_active = False

        await db.commit()

    print("Sync complete.")
    return {k: len(v) for k, v in plan.items()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print the plan without writing")
    args = parser.parse_args()
    asyncio.run(sync_companies(dry_run=args.dry_run))
