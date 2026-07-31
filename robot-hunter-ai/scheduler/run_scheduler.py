"""
RoboHunter AI — Main Scheduler Entry Point

Orchestrates the full pipeline:
  1. Fetch enabled companies from DB
  2. Run crawlers concurrently
  3. Deduplicate new jobs
  4. Run AI matching against active resume
  5. Send Telegram + Email notifications
  6. Log results

This script is invoked by GitHub Actions hourly.
"""

import asyncio
import os
import sys
import logging

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

log = logging.getLogger(__name__)


async def run_pipeline() -> None:
    """Main pipeline coroutine — implemented fully in Phase 7 (Crawler)."""
    log.info("RoboHunter scheduler starting...")

    # TODO Phase 7: Load enabled companies from DB
    # TODO Phase 7: Run ATS-aware crawlers concurrently
    # TODO Phase 9: AI matching
    # TODO Phase 10: Telegram + Gmail notifications

    log.info("Scheduler complete (stub — modules not yet implemented)")


def main() -> None:
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    if dry_run:
        log.info("DRY RUN mode — notifications will be suppressed")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    asyncio.run(run_pipeline())


if __name__ == "__main__":
    main()
