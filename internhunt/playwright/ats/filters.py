"""
Job relevance filter for InternHunt.

Filters job listings to only keep internship/trainee roles in the
target technical domains:
  - Robotics / Autonomous Systems / Drones
  - IoT / Internet of Things
  - Embedded Systems / Firmware / RTOS
  - AI / ML / Deep Learning
  - OpenCV / Computer Vision / Image Processing
  - SDE / Software Engineering (general)
"""

import re
from .base import JobListing

# ── Internship Indicator Terms ────────────────────────────────────────────────
# A listing must match at least ONE of these to be considered an internship role.
INTERN_PATTERN = re.compile(
    r"\b("
    r"intern|internship|interns|interning|"
    r"trainee|apprentice|fresher|"
    r"summer\s*(?:intern|program|project)|"
    r"graduate\s*(?:trainee|program)|"
    r"entry[\s-]?level|"
    r"campus\s*(?:hire|recruit)"
    r")\b",
    re.IGNORECASE,
)

# ── Target Domain Terms ───────────────────────────────────────────────────────
# A listing must match at least ONE of these to be in a domain we care about.
DOMAIN_PATTERN = re.compile(
    r"\b("
    # Robotics / Autonomous
    r"robot(?:ics?)?|autonomous|self[\s-]?driving|"
    r"drone|uav|uavs|unmanned|"
    r"ros\b|ros2|gazebo|slam|"
    r"mechatron(?:ics?)?|"
    # IoT
    r"iot\b|internet[\s-]of[\s-]things|"
    r"smart\s*device|connected\s*device|"
    # Embedded / Firmware
    r"embedded|firmware|rtos|"
    r"microcontroller|mcu\b|esp32|arduino|stm32|"
    r"fpga\b|vhdl|verilog|baremetal|bare[\s-]?metal|"
    r"device\s*driver|bsp\b|"
    # AI / ML / DL
    r"machine\s*learning|deep\s*learning|"
    r"neural\s*net(?:work)?|"
    r"ai\b|artificial\s*intelligence|"
    r"nlp\b|natural\s*language|"
    r"llm\b|generative\s*ai|"
    r"data\s*science|"
    # Computer Vision / OpenCV
    r"opencv|computer\s*vision|"
    r"image\s*processing|object\s*detection|"
    r"perception|lidar|point\s*cloud|"
    r"3d\s*vision|stereo\s*vision|"
    # SDE / Software Engineering
    r"software\s*(?:development|engineer|developer)|"
    r"\bsde\b|\bswe\b|"
    r"backend|front[\s-]?end|full[\s-]?stack|"
    r"python|c\+\+|java\b|javascript|golang\b"
    r")\b",
    re.IGNORECASE,
)

# ── Exclusion Terms ───────────────────────────────────────────────────────────
# Immediately reject listings with these terms (regardless of domain match).
EXCLUDE_PATTERN = re.compile(
    r"\b("
    r"senior|sr\.|lead\b|principal|staff\b|"
    r"director|vp\b|vice\s*president|cto|ceo|cfo|coo|"
    r"manager\b|head\s*of|"
    r"legal|finance|accounting|hr\b|human\s*resource|"
    r"sales|marketing|content\s*writer|"
    r"chef|cook|driver|security\s*guard|"
    r"business\s*analyst|operations\s*manager"
    r")\b",
    re.IGNORECASE,
)


# ── Editorial content ─────────────────────────────────────────────────────────
# Career sites mix blog posts and guides in with their listings. Titles like
# "How to build a career in Embedded Systems as a Fresher?" satisfy both the
# intern and domain patterns, so they must be rejected explicitly.
ARTICLE_TITLE_PATTERN = re.compile(
    r"(^\s*(how|why|what|when|where|top\s+\d+|\d+\s+(?:ways|tips|things))\b|\?\s*$|"
    r"\b(blogs?|webinars?|case\s*stud(?:y|ies)|newsletters?|podcasts?|ebooks?|"
    r"whitepapers?|guide\s+to|success\s+stor(?:y|ies)|testimonials?|reviews?|faqs?)\b)",
    re.IGNORECASE,
)

ARTICLE_URL_PATTERN = re.compile(
    r"/(blog|news|article|press|webinar|event|resource|story|stories|insight)s?/",
    re.IGNORECASE,
)


def is_editorial(listing: JobListing) -> bool:
    """True if the listing is really a blog post / guide rather than a job."""
    return bool(
        ARTICLE_TITLE_PATTERN.search(listing.title or "")
        or ARTICLE_URL_PATTERN.search(listing.job_url or "")
    )


def is_relevant_internship(listing: JobListing) -> bool:
    """
    Return True only if the listing:
      1. Is an internship/trainee role (must match INTERN_PATTERN), AND
      2. Falls in a target technical domain (must match DOMAIN_PATTERN), AND
      3. Does NOT match any exclusion terms.

    The check is done on the combined title + location + the opening of the
    description. We read a generous slice of the description because when a
    listing is enriched from its job-detail page the domain keywords ("ROS",
    "embedded", "computer vision") often appear well below the first paragraph.
    """
    text_blob = " ".join(filter(None, [
        listing.title,
        listing.location,
        (listing.description or "")[:2000],
    ]))

    # Blog posts and guides are not jobs, however well they match below.
    if is_editorial(listing):
        return False

    # Must contain an internship indicator
    if not INTERN_PATTERN.search(text_blob):
        return False

    # Must be in a relevant technical domain
    if not DOMAIN_PATTERN.search(text_blob):
        return False

    # Must NOT be a senior/management/irrelevant role
    if EXCLUDE_PATTERN.search(listing.title or ""):
        return False

    return True


def filter_listings(listings: list[JobListing]) -> list[JobListing]:
    """Filter a list of JobListings, keeping only relevant internships."""
    return [l for l in listings if is_relevant_internship(l)]


def looks_like_early_career(listing: JobListing) -> bool:
    """
    True if a listing smells like an internship but can't be confirmed from the
    link alone — e.g. a card whose only text is "Intern" or "Graduate Trainee",
    with no clue which domain it belongs to.

    Career pages very often render exactly that, and the strict filter drops
    them because DOMAIN_PATTERN never matches. These are the listings worth
    spending a job-detail page fetch on; everything else is not.
    """
    if EXCLUDE_PATTERN.search(listing.title or "") or is_editorial(listing):
        return False

    # The URL slug is usually the most reliable hint ("/jobs/robotics-intern-24").
    blob = " ".join(filter(None, [listing.title, listing.job_url]))
    return bool(INTERN_PATTERN.search(blob))
