"""
Base crawler interface.

All ATS-specific crawlers must implement this abstract base class.
The scheduler calls .crawl() on each crawler without knowing the
underlying ATS platform — classic Strategy pattern.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class RawJob:
    """
    Normalised job record returned by any crawler.
    
    The crawler is responsible for populating all fields it can discover.
    Fields left None will be filled by the job extraction pipeline.
    """

    title: str
    apply_url: str
    company_id: str

    description: Optional[str] = None
    location: Optional[str] = None
    posted_date: Optional[datetime] = None
    platform: Optional[str] = None

    # Populated by duplicate detection layer
    job_hash: Optional[str] = None

    # Extra metadata some ATS platforms expose
    extra: dict = field(default_factory=dict)


class BaseCrawler(ABC):
    """
    Abstract base class for all ATS crawlers.

    Subclasses implement `crawl()` for their specific ATS platform.
    Common utilities (rate limiting, retries, logging) are provided here.
    """

    def __init__(self, company_id: str, career_url: str, headless: bool = True):
        self.company_id = company_id
        self.career_url = career_url
        self.headless = headless

    @abstractmethod
    async def crawl(self) -> List[RawJob]:
        """
        Crawl the careers page and return a list of raw job listings.

        Must be implemented by every ATS handler.
        Should never raise — return an empty list on failure and log the error.
        """
        ...

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass
