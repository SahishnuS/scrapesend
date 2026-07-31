"""
Generic ATS Handler.

Used for companies with custom-built career pages. Uses heuristic keyword
matching on <a> tags scoped to the target intern domains only.
After extraction, queue_manager.py applies the strict relevance filter.
"""

import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base import BaseATSHandler, JobListing

# ── Link discovery keywords ────────────────────────────────────────────────────
# We use a broad set here to avoid missing things; the strict filter in
# filters.py does the final relevance check.
LINK_KEYWORDS = re.compile(
    r"\b("
    r"intern|internship|trainee|fresher|apprentice|"
    r"robot(?:ics?)?|autonomous|drone|uav|ros\b|slam|"
    r"iot\b|embedded|firmware|rtos|microcontroller|fpga\b|"
    r"ai\b|machine\s*learning|deep\s*learning|neural|"
    r"opencv|computer\s*vision|image\s*processing|perception|"
    r"software\s*engineer|developer|sde\b|swe\b|"
    r"python|c\+\+|backend|full[\s-]?stack"
    r")\b",
    re.IGNORECASE,
)

# URLs that should always be skipped
SKIP_PATTERNS = re.compile(
    r"(linkedin|twitter|facebook|instagram|youtube|"
    r"privacy|terms|cookie|mailto:|tel:|javascript:)",
    re.IGNORECASE,
)

LOCATION_PATTERN = re.compile(
    r"\b(bengaluru|bangalore|chennai|hyderabad|pune|mumbai|delhi|noida|"
    r"remote|india|usa|us|uk|london|san\s*francisco|new\s*york|hybrid)\b",
    re.IGNORECASE,
)


class GenericHandler(BaseATSHandler):
    """
    Heuristic-based job extractor for custom career pages.
    Scans <a> tags for intern/domain keywords and returns candidates.
    The final relevance filter is applied in queue_manager.py.
    """

    def extract(self, html: str, base_url: str = "") -> list[JobListing]:
        soup = BeautifulSoup(html, "html.parser")
        seen_urls: set[str] = set()
        listings: list[JobListing] = []

        for tag in soup.find_all("a", href=True):
            title = tag.get_text(separator=" ", strip=True)
            href = tag["href"]

            # Resolve relative URLs
            if not href.startswith("http"):
                href = urljoin(base_url, href)

            # Skip noise
            if SKIP_PATTERNS.search(href):
                continue
            if href in seen_urls:
                continue
            if not (5 <= len(title) <= 200):
                continue

            # Must match at least one relevant keyword in the link text
            if not LINK_KEYWORDS.search(title):
                continue

            seen_urls.add(href)
            location = self._find_nearby_location(tag)
            listings.append(JobListing(title=title, job_url=href, location=location))

        return listings

    def _find_nearby_location(self, tag) -> str | None:
        """Scan sibling/parent elements for a recognisable location string."""
        candidates: list[str] = []
        parent = tag.parent
        if parent:
            candidates.extend(t.strip() for t in parent.strings)
            if parent.parent:
                candidates.extend(t.strip() for t in parent.parent.strings)

        for text in candidates:
            if LOCATION_PATTERN.search(text):
                return text[:100]
        return None
