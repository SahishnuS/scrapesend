#!/usr/bin/env python3
"""
Master Pipeline Script for InternHunt.
Executes the entire monitoring pipeline sequentially:
0. Company sync (scripts/sync_companies.py) — registry JSON is the source of truth
1. Crawler (playwright/queue_manager.py)
2. AI Matcher (scripts/run_matcher.py)
3. Notifications (scripts/run_notifications.py)
"""

import sys
import os
import asyncio
import time
import structlog

# Ensure imports resolve properly from root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "backend"))
sys.path.insert(0, os.path.join(ROOT_DIR, "playwright"))

from queue_manager import run_crawler_queue
from run_matcher import run_matching_pipeline
from run_notifications import run_notification_pipeline
from sync_companies import sync_companies

log = structlog.get_logger(__name__)

async def run_full_pipeline():
    start_time = time.time()

    print("\n" + "="*50)
    print("🚀 STARTING InternHunt MONITORING PIPELINE")
    print("="*50 + "\n")

    # Step 0: Sync the career portal registry into the companies table.
    # Without this the crawler has nothing to crawl on a fresh database, and
    # portals fixed in the registry never reach production.
    print("\n--- [STEP 0/3] SYNCING COMPANY REGISTRY ---")
    try:
        summary = await sync_companies()
        print(
            f"✅ Sync complete: +{summary['insert']} new, "
            f"~{summary['update']} updated, -{summary['deactivate']} deactivated."
        )
    except Exception as e:
        log.error("Pipeline failed during SYNC phase", error=str(e))
        return

    # Steps 1 and 2 are best-effort. A crawl or matcher failure must NOT stop
    # the notification step: there is usually a backlog of already-discovered
    # jobs waiting to be emailed, and skipping alerts would delay them by
    # another two hours for no reason.

    # Step 1: Run Crawler
    print("\n--- [STEP 1/3] CRAWLING COMPANIES ---")
    try:
        crawl_summary = await run_crawler_queue()
        print(f"✅ Crawl complete: Found {crawl_summary.get('total_new_jobs', 0)} new jobs.")
    except Exception as e:
        log.error("Crawl phase failed; continuing to matching and alerts", error=str(e))

    # Step 2: Run AI Matcher
    print("\n--- [STEP 2/3] AI MATCHING ---")
    try:
        await run_matching_pipeline()
        print("✅ AI Matching complete.")
    except Exception as e:
        log.error("Matching phase failed; continuing to alerts", error=str(e))

    # Step 3: Run Notifications
    print("\n--- [STEP 3/3] NOTIFICATIONS ---")
    try:
        alerted = await run_notification_pipeline()
        print(f"✅ Notifications complete: {alerted} new posting(s) emailed this run.")
    except Exception as e:
        log.error("Pipeline failed during NOTIFICATIONS phase", error=str(e))
        return

    duration = round(time.time() - start_time, 2)
    print("\n" + "="*50)
    print(f"🎉 PIPELINE COMPLETED SUCCESSFULLY IN {duration} SECONDS")
    print("="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(run_full_pipeline())
