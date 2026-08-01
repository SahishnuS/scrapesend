#!/usr/bin/env python3
"""
Career portal verifier.

Loads data/career_portals.json and, for every company, opens the career portal
in headless Chromium to confirm that:
  1. the URL responds with an HTTP status below 400,
  2. the rendered page actually looks like a careers page, and
  3. the GenericHandler used by the crawler can extract job links from it.

The primary `careers_url` is tried first, then each entry in `fallback_urls`,
for at most MAX_ATTEMPTS URLs per company. If none of them work the company is
skipped rather than failing the run. Results are written to
data/career_portals_report.json.

Usage:
    python scripts/verify_portals.py --new      # only companies not yet in the report
    python scripts/verify_portals.py            # re-verify every company
    python scripts/verify_portals.py CynLr Ati  # verify matching companies only

`--new` merges its results into the existing report instead of replacing it, so
adding companies to the registry costs one short run rather than a full sweep.
"""

import argparse
import asyncio
import contextlib
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "playwright"))

from ats.filters import filter_listings  # noqa: E402
from ats.generic import GenericHandler  # noqa: E402
from playwright.async_api import async_playwright  # noqa: E402

PORTALS_FILE = ROOT_DIR / "data" / "career_portals.json"
REPORT_FILE = ROOT_DIR / "data" / "career_portals_report.json"

# Give up on a company after this many candidate URLs and move on.
MAX_ATTEMPTS = 3

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Words that a genuine careers page is expected to contain somewhere in its text.
CAREER_SIGNALS = (
    "career",
    "job",
    "opening",
    "vacanc",
    "we're hiring",
    "we are hiring",
    "join us",
    "join our team",
    "open position",
    "apply now",
    "internship",
)

HANDLER = GenericHandler()


async def check_url(context, url: str) -> dict:
    """Load a single URL and report whether it works as a career portal."""
    page = await context.new_page()
    result: dict = {"url": url, "ok": False}
    try:
        response = await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        result["status"] = response.status if response else None
        result["final_url"] = page.url

        if response is None or response.status >= 400:
            result["error"] = f"HTTP {result['status']}"
            return result

        # Give client-rendered job boards (Freshteam, Zoho, Wix, Framer) time to paint.
        with contextlib.suppress(Exception):
            await page.wait_for_load_state("networkidle", timeout=15000)

        html = await page.content()
        text = (await page.inner_text("body")).lower()

        listings = HANDLER.extract(html, base_url=url)
        result["career_signals"] = sorted({s for s in CAREER_SIGNALS if s in text})
        result["job_links"] = len(listings)
        result["intern_links"] = len(filter_listings(listings))
        result["sample_titles"] = [listing.title for listing in listings[:5]]

        if not result["career_signals"]:
            result["error"] = "page has no careers/jobs wording"
        elif len(text.strip()) < 100:
            result["error"] = "page rendered almost empty"
        else:
            result["ok"] = True
        return result
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result
    finally:
        await page.close()


async def verify_company(browser, company: dict, sem: asyncio.Semaphore) -> dict:
    """Try the primary URL then each fallback until one works."""
    if not company["careers_url"]:
        print(f"[{'SKIPPED':<12}] {company['name']:<32} {company.get('note', 'no careers_url')}")
        return {
            "name": company["name"],
            "status": "skipped",
            "configured_url": None,
            "working_url": None,
            "job_links": 0,
            "intern_links": 0,
            "sample_titles": [],
            "attempts": [],
        }

    async with sem:
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
            locale="en-US",
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )
        # Hide the headless fingerprint that Cloudflare-fronted sites reject.
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        try:
            attempts = []
            candidates = [company["careers_url"], *company.get("fallback_urls", [])]
            for url in candidates[:MAX_ATTEMPTS]:
                attempt = await check_url(context, url)
                attempts.append(attempt)
                if attempt["ok"]:
                    break
        finally:
            await context.close()

    working = next((a for a in attempts if a["ok"]), None)
    if not working:
        status = "unreachable"
    elif working["url"] != company["careers_url"]:
        status = "use_fallback"
    else:
        status = "ok"

    detail = (
        f"{working['url']}  ({working['job_links']} job links)"
        if working
        else f"gave up after {len(attempts)} attempt(s): {attempts[-1].get('error')}"
    )
    print(f"[{status.upper():<12}] {company['name']:<32} {detail}")

    return {
        "name": company["name"],
        "status": status,
        "configured_url": company["careers_url"],
        "working_url": working["url"] if working else None,
        "job_links": working["job_links"] if working else 0,
        "intern_links": working["intern_links"] if working else 0,
        "sample_titles": working["sample_titles"] if working else [],
        "attempts": attempts,
    }


def load_previous_report() -> dict[str, dict]:
    """Previous results keyed by company name, empty if there is no report yet."""
    if not REPORT_FILE.exists():
        return {}
    return {r["name"]: r for r in json.loads(REPORT_FILE.read_text())}


async def main(name_filters: list[str], only_new: bool) -> int:
    data = json.loads(PORTALS_FILE.read_text())
    companies = data["companies"]
    if name_filters:
        lowered = [f.lower() for f in name_filters]
        companies = [c for c in companies if any(f in c["name"].lower() for f in lowered)]

    previous = load_previous_report()
    if only_new:
        settled = {name for name, r in previous.items() if r["status"] in ("ok", "skipped")}
        total = len(companies)
        companies = [c for c in companies if c["name"] not in settled]
        print(f"--new: {total - len(companies)} already verified, {len(companies)} to check.")

    if not companies:
        print("Nothing to verify - every company in the registry is already verified.")
        return 0

    print(f"Verifying {len(companies)} career portals...\n")

    sem = asyncio.Semaphore(6)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        try:
            results = await asyncio.gather(
                *(verify_company(browser, company, sem) for company in companies)
            )
        finally:
            await browser.close()

    unreachable = [r for r in results if r["status"] == "unreachable"]
    fallbacks = [r for r in results if r["status"] == "use_fallback"]
    skipped = [r for r in results if r["status"] == "skipped"]

    # A partial run merges into the existing report so earlier results survive.
    merged = {**previous, **{r["name"]: r for r in results}}
    REPORT_FILE.write_text(json.dumps(list(merged.values()), indent=2) + "\n")

    print(f"\n{'=' * 60}")
    print(f"  ok:           {len(results) - len(unreachable) - len(fallbacks) - len(skipped)}")
    print(f"  fallback:     {len(fallbacks)}")
    print(f"  unreachable:  {len(unreachable)} (skipped after {MAX_ATTEMPTS} attempts)")
    print(f"  skipped:      {len(skipped)} (no careers_url configured)")
    print(f"  report:       {REPORT_FILE.relative_to(ROOT_DIR)}")
    print(f"{'=' * 60}")

    for r in fallbacks:
        print(f"  ↪ {r['name']}: replace careers_url with {r['working_url']}")
    for r in unreachable:
        print(f"  ✗ {r['name']}: {r['attempts'][-1].get('error')}")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names", nargs="*", help="Only verify companies matching these substrings")
    parser.add_argument(
        "--new",
        action="store_true",
        help="Only verify companies that are not already ok/skipped in the report",
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(main(args.names, args.new)))
