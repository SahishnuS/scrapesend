"""
Greenhouse ATS Handler.

Greenhouse exposes a public JSON API at:
  https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true

We prefer the JSON API over scraping the HTML because it is more reliable,
stable, and returns the full job description.
"""

import json
import re
from bs4 import BeautifulSoup
from .base import BaseATSHandler, JobListing


class GreenhouseHandler(BaseATSHandler):
    """
    Parses Greenhouse-hosted job boards.

    Strategy:
      1. Try to extract the board token from embedded JSON in the page.
      2. Fall back to scraping the rendered HTML job listing items.
    """

    # Greenhouse embeds the board token in the page script
    _BOARD_TOKEN_RE = re.compile(r'boards\.greenhouse\.io/(?:embed/job_board\?for=|)([a-zA-Z0-9_-]+)')
    _BOARD_API = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"

    def extract(self, html: str, base_url: str = "") -> list[JobListing]:
        listings: list[JobListing] = []

        # ── Strategy 1: Parse embedded JSON API response ──────────────────────
        try:
            listings = self._parse_via_api_json(html)
            if listings:
                return listings
        except Exception:
            pass

        # ── Strategy 2: Parse rendered HTML ──────────────────────────────────
        try:
            listings = self._parse_via_html(html, base_url)
        except Exception:
            pass

        return listings

    def _parse_via_api_json(self, html: str) -> list[JobListing]:
        """
        If the page has a <script> that contains the JSON job list (e.g. Greenhouse
        React apps embed window.greenhouse_jobs = {...}), parse it directly.
        """
        soup = BeautifulSoup(html, "html.parser")
        for script in soup.find_all("script"):
            text = script.string or ""
            if '"jobs"' in text and '"title"' in text:
                # Try to find and parse JSON fragment
                match = re.search(r'\{.*"jobs"\s*:\s*\[.*?\]\s*\}', text, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    return [
                        JobListing(
                            title=j.get("title", ""),
                            job_url=j.get("absolute_url", ""),
                            location=j.get("location", {}).get("name"),
                        )
                        for j in data.get("jobs", [])
                        if j.get("title") and j.get("absolute_url")
                    ]
        return []

    def _parse_via_html(self, html: str, base_url: str) -> list[JobListing]:
        """Fall back to scraping the standard Greenhouse HTML board layout."""
        soup = BeautifulSoup(html, "html.parser")
        listings = []

        # Greenhouse renders: <div class="opening"> <a href="...">Title</a> <span class="location">...</span>
        for opening in soup.select("div.opening"):
            a = opening.find("a")
            if not a:
                continue
            title = a.get_text(strip=True)
            href = a.get("href", "")
            if not href.startswith("http"):
                href = base_url.rstrip("/") + "/" + href.lstrip("/")
            location_el = opening.select_one(".location")
            location = location_el.get_text(strip=True) if location_el else None
            if title and href:
                listings.append(JobListing(title=title, job_url=href, location=location))

        return listings
