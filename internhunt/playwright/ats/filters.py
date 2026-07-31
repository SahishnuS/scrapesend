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


def is_relevant_internship(listing: JobListing) -> bool:
    """
    Return True only if the listing:
      1. Is an internship/trainee role (must match INTERN_PATTERN), AND
      2. Falls in a target technical domain (must match DOMAIN_PATTERN), AND
      3. Does NOT match any exclusion terms.

    The check is done on the combined title + location + first 500 chars of description.
    """
    text_blob = " ".join(filter(None, [
        listing.title,
        listing.location,
        (listing.description or "")[:500],
    ]))

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
