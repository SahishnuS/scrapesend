"""
Queue Manager for the InternHunt crawler.

Orchestrates the full crawl pipeline:
  1. Fetch all active companies from the database.
  2. For each company, use the appropriate ATS handler to extract job listings.
  3. Deduplicate jobs using a SHA-256 hash of (company_id + job_url).
  4. Persist new jobs to the database and update last_crawled_at.
"""

import asyncio
import hashlib
import sys
import os
from datetime import datetime, timezone

# Allow imports from the backend package and the playwright directory itself
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend"))
sys.path.insert(0, os.path.dirname(__file__))  # For crawler_base

import structlog
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.company import Company
from app.models.job import Job
from crawler_base import BaseCrawler
from ats.greenhouse import GreenhouseHandler
from ats.lever import LeverHandler
from ats.generic import GenericHandler
from ats.filters import is_relevant_internship, looks_like_early_career

log = structlog.get_logger(__name__)

# Map ats_provider values to their handler classes
ATS_HANDLER_MAP = {
    "greenhouse": GreenhouseHandler(),
    "lever": LeverHandler(),
}
GENERIC_HANDLER = GenericHandler()

# Upper bound on job-detail pages fetched per company. Career pages routinely
# list 30-70 roles; without a cap one company could dominate the crawl window.
MAX_DETAIL_FETCHES = 15


def _make_job_hash(company_id: str, job_url: str) -> str:
    """
    Generate a stable, unique hash for a job to use as deduplication key.
    Uses the company ID + canonical job URL.
    """
    raw = f"{company_id}::{job_url.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _get_handler(ats_provider: str | None):
    """Return the appropriate ATS handler, defaulting to the generic one."""
    if ats_provider and ats_provider.lower() in ATS_HANDLER_MAP:
        return ATS_HANDLER_MAP[ats_provider.lower()]
    return GENERIC_HANDLER


async def resolve_internships(
    crawler: BaseCrawler, listings: list, company_name: str
) -> list:
    """
    Decide which extracted listings are relevant internships.

    Two stages, because a careers page usually gives us nothing but the link
    text:
      1. Listings that already prove themselves from the title alone are kept
         without any extra network cost.
      2. Listings that look like an internship but don't name a domain (cards
         reading just "Intern" or "Graduate Trainee") get their job-detail page
         fetched so the filter can judge them on the real description.

    Everything else is dropped without a fetch.
    """
    confirmed = [listing for listing in listings if is_relevant_internship(listing)]
    confirmed_urls = {listing.job_url for listing in confirmed}

    candidates = [
        listing
        for listing in listings
        if listing.job_url not in confirmed_urls and looks_like_early_career(listing)
    ]

    if not candidates:
        return confirmed

    budget = candidates[:MAX_DETAIL_FETCHES]
    if len(candidates) > MAX_DETAIL_FETCHES:
        log.info(
            "Capping job-detail fetches",
            company=company_name,
            candidates=len(candidates),
            fetching=MAX_DETAIL_FETCHES,
        )

    enriched = 0
    for listing in budget:
        detail = await crawler.fetch_detail_text(listing.job_url)
        if not detail:
            continue
        listing.description = detail
        if is_relevant_internship(listing):
            confirmed.append(listing)
            enriched += 1

    log.info(
        "Job-detail enrichment complete",
        company=company_name,
        fetched=len(budget),
        newly_confirmed=enriched,
    )
    return confirmed


async def crawl_company(crawler: BaseCrawler, company: Company) -> int:
    """
    Crawl a single company and persist any new jobs found.
    Returns the count of newly discovered jobs.
    """
    log.info("Crawling company", company=company.name, url=company.careers_url)

    html = await crawler.fetch_html(company.careers_url)
    if not html:
        log.warning("Empty HTML returned, skipping", company=company.name)
        return 0

    handler = _get_handler(company.ats_provider)
    raw_listings = handler.extract(html, base_url=company.careers_url)
    listings = await resolve_internships(crawler, raw_listings, company.name)
    log.info(
        "Listings after relevance filter",
        company=company.name,
        raw=len(raw_listings),
        filtered=len(listings),
    )

    new_count = 0
    async with AsyncSessionLocal() as db:
        for listing in listings:
            if not listing.title or not listing.job_url:
                continue

            job_hash = _make_job_hash(str(company.id), listing.job_url)

            # Skip if already in database
            existing = await db.scalar(
                select(Job).where(Job.job_hash == job_hash)
            )
            if existing:
                continue

            job = Job(
                company_id=company.id,
                title=listing.title,
                job_url=listing.job_url,
                location=listing.location,
                description=listing.description,
                job_hash=job_hash,
                status="open",
            )
            db.add(job)
            new_count += 1
            log.info("New job discovered", title=listing.title, company=company.name)

        # Update last_crawled_at on the company
        company_record = await db.get(Company, company.id)
        if company_record:
            company_record.last_crawled_at = datetime.now(tz=timezone.utc)

        await db.commit()

    return new_count


async def get_active_companies() -> list[Company]:
    """Fetch all active companies that have a careers URL configured."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Company)
            .where(Company.is_active == True)
            .where(Company.careers_url.isnot(None))
            .order_by(Company.name)
        )
        return list(result.scalars().all())


async def run_crawler_queue(politeness_delay: float = 3.0) -> dict:
    """
    Main entrypoint for the Phase 7/8 crawling pipeline.

    Args:
        politeness_delay: Seconds to wait between company crawls (avoids hammering servers).

    Returns:
        Summary dict with total_companies, total_new_jobs, errors.
    """
    from app.core.config import settings

    companies = await get_active_companies()

    if not companies:
        log.info("No active companies with a careers_url found. Queue is empty.")
        return {"total_companies": 0, "total_new_jobs": 0, "errors": 0}

    log.info(f"Starting crawl queue", total_companies=len(companies))

    crawler = BaseCrawler(headless=True)
    await crawler.start()

    total_new = 0
    errors = 0
    completed = 0

    concurrency = getattr(settings, "CRAWLER_CONCURRENCY", 5)
    sem = asyncio.Semaphore(concurrency)

    async def _crawl_worker(company):
        nonlocal total_new, errors, completed
        async with sem:
            try:
                new_jobs = await crawl_company(crawler, company)
                total_new += new_jobs
                completed += 1
                log.info(
                    f"[{completed}/{len(companies)}] Done",
                    company=company.name,
                    new_jobs=new_jobs,
                )
            except Exception as exc:
                errors += 1
                completed += 1
                log.error("Error crawling company", company=company.name, error=str(exc))
            
            # Politeness delay holding the semaphore limits overall throughput slightly,
            # which helps avoid sudden CPU spikes or triggering mass bot protections.
            await asyncio.sleep(politeness_delay)

    try:
        tasks = [_crawl_worker(company) for company in companies]
        await asyncio.gather(*tasks)
    finally:
        await crawler.stop()

    summary = {
        "total_companies": len(companies),
        "total_new_jobs": total_new,
        "errors": errors,
    }
    log.info("Crawl queue complete", **summary)
    return summary


if __name__ == "__main__":
    result = asyncio.run(run_crawler_queue())
    print(f"\n✅ Crawl complete: {result}")
