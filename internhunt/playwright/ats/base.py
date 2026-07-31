"""
Abstract base class for all ATS handlers.
Every handler must implement the `extract` method, which receives raw HTML
and returns a list of JobListing dataclasses.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class JobListing:
    """Canonical representation of a single job opening extracted by any ATS handler."""
    title: str
    job_url: str
    location: Optional[str] = None
    description: Optional[str] = None


class BaseATSHandler(ABC):
    """All ATS parsers must subclass this and implement `extract`."""

    @abstractmethod
    def extract(self, html: str, base_url: str = "") -> list[JobListing]:
        """
        Parse raw HTML and return a list of JobListing objects.

        Args:
            html:     The rendered HTML of the careers page.
            base_url: The origin URL of the careers page (used to resolve relative links).

        Returns:
            A list of JobListing dataclasses. Empty list if nothing found.
        """
        ...
