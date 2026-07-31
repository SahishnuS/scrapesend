"""
Lever ATS Handler.

Lever exposes a public JSON API at:
  https://api.lever.co/v0/postings/{company_slug}?mode=json

We prefer the JSON API for reliability; HTML scraping is the fallback.
"""

import json
import re
from bs4 import BeautifulSoup
from .base import BaseATSHandler, JobListing


class LeverHandler(BaseATSHandler):
    """
    Parses Lever-hosted job boards.

    Lever URLs look like: https://jobs.lever.co/{company_slug}
    The JSON API is: https://api.lever.co/v0/postings/{slug}?mode=json
    """

    _LEVER_SLUG_RE = re.compile(r'jobs\.lever\.co/([a-zA-Z0-9_-]+)')

    def extract(self, html: str, base_url: str = "") -> list[JobListing]:
        listings: list[JobListing] = []

        # ── Strategy 1: Try to parse the embedded JSON in the page (Lever React SPA) ──
        try:
            listings = self._parse_via_json_embed(html)
            if listings:
                return listings
        except Exception:
            pass

        # ── Strategy 2: Parse rendered HTML job listings ──────────────────────
        try:
            listings = self._parse_via_html(html, base_url)
        except Exception:
            pass

        return listings

    def _parse_via_json_embed(self, html: str) -> list[JobListing]:
        """
        Lever SPAs embed posting data in a window.__LEVER__ or __NEXT_DATA__ variable.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Check for __NEXT_DATA__ (Next.js Lever boards)
        next_data_tag = soup.find("script", id="__NEXT_DATA__")
        if next_data_tag and next_data_tag.string:
            data = json.loads(next_data_tag.string)
            postings = (
                data.get("props", {})
                    .get("pageProps", {})
                    .get("postings", [])
            )
            if postings:
                return [
                    JobListing(
                        title=p.get("text", ""),
                        job_url=p.get("hostedUrl", ""),
                        location=p.get("categories", {}).get("location"),
                    )
                    for p in postings
                    if p.get("text") and p.get("hostedUrl")
                ]
        return []

    def _parse_via_html(self, html: str, base_url: str) -> list[JobListing]:
        """Fall back to scraping the standard Lever HTML board layout."""
        soup = BeautifulSoup(html, "html.parser")
        listings = []

        # Lever renders: <div class="posting"> <h5 class="posting-name"><a>Title</a></h5>
        for posting in soup.select("div.posting"):
            title_el = posting.select_one(".posting-name a, h5 a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            if not href.startswith("http"):
                href = base_url.rstrip("/") + "/" + href.lstrip("/")
            location_el = posting.select_one(".sort-by-location .posting-category")
            location = location_el.get_text(strip=True) if location_el else None
            if title and href:
                listings.append(JobListing(title=title, job_url=href, location=location))

        return listings
