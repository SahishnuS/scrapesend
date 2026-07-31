#!/usr/bin/env python3
"""
Master Pipeline Script for RoboHunter AI.
Executes the entire monitoring pipeline sequentially:
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

log = structlog.get_logger(__name__)

async def run_full_pipeline():
    start_time = time.time()
    
    print("\n" + "="*50)
    print("🚀 STARTING ROBOHUNTER AI MONITORING PIPELINE")
    print("="*50 + "\n")

    # Step 1: Run Crawler
    print("\n--- [STEP 1/3] CRAWLING COMPANIES ---")
    try:
        crawl_summary = await run_crawler_queue()
        print(f"✅ Crawl complete: Found {crawl_summary.get('total_new_jobs', 0)} new jobs.")
    except Exception as e:
        log.error("Pipeline failed during CRAWL phase", error=str(e))
        return

    # Step 2: Run AI Matcher
    print("\n--- [STEP 2/3] AI MATCHING ---")
    try:
        await run_matching_pipeline()
        print(f"✅ AI Matching complete.")
    except Exception as e:
        log.error("Pipeline failed during MATCHING phase", error=str(e))
        return

    # Step 3: Run Notifications
    print("\n--- [STEP 3/3] NOTIFICATIONS ---")
    try:
        await run_notification_pipeline()
        print(f"✅ Notifications complete.")
    except Exception as e:
        log.error("Pipeline failed during NOTIFICATIONS phase", error=str(e))
        return

    duration = round(time.time() - start_time, 2)
    print("\n" + "="*50)
    print(f"🎉 PIPELINE COMPLETED SUCCESSFULLY IN {duration} SECONDS")
    print("="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(run_full_pipeline())
