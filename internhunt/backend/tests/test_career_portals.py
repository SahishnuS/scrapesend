"""
Integrity tests for data/career_portals.json.

These run offline - they check the registry's shape, not whether the sites
are up. Live reachability is checked by `python scripts/verify_portals.py`.
"""

import json
from pathlib import Path
from urllib.parse import urlparse

import pytest

PORTALS_FILE = Path(__file__).resolve().parents[2] / "data" / "career_portals.json"

VALID_ATS_PROVIDERS = {"greenhouse", "lever", "workable", "zoho", "freshteam", "other"}


@pytest.fixture(scope="module")
def companies() -> list[dict]:
    return json.loads(PORTALS_FILE.read_text())["companies"]


def test_registry_is_not_empty(companies):
    assert len(companies) > 0


def test_company_names_are_unique(companies):
    names = [c["name"] for c in companies]
    duplicates = {n for n in names if names.count(n) > 1}
    assert not duplicates, f"duplicate company names: {duplicates}"


@pytest.mark.parametrize("field", ["name", "careers_url", "ats_provider", "fallback_urls"])
def test_every_entry_has_required_fields(companies, field):
    missing = [c.get("name", "<unnamed>") for c in companies if field not in c]
    assert not missing, f"entries missing '{field}': {missing}"


def test_urls_are_absolute_http_urls(companies):
    bad = []
    for company in companies:
        urls = [company["careers_url"], *company["fallback_urls"]]
        for url in urls:
            if url is None:
                continue
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                bad.append((company["name"], url))
    assert not bad, f"non-absolute or non-http URLs: {bad}"


def test_ats_provider_is_known(companies):
    bad = [
        (c["name"], c["ats_provider"])
        for c in companies
        if c["ats_provider"] is not None and c["ats_provider"] not in VALID_ATS_PROVIDERS
    ]
    assert not bad, f"unknown ats_provider values: {bad}"


def test_unreachable_entries_are_fully_nulled_and_explained(companies):
    """A null careers_url means 'no crawlable portal' - it must say why."""
    bad = [
        c["name"]
        for c in companies
        if c["careers_url"] is None
        and (c["ats_provider"] is not None or not c.get("note") or c["fallback_urls"])
    ]
    assert not bad, f"entries with a null careers_url need a note and no ats_provider/fallbacks: {bad}"


def test_crawlable_entries_declare_an_ats_provider(companies):
    bad = [c["name"] for c in companies if c["careers_url"] and not c["ats_provider"]]
    assert not bad, f"entries with a careers_url need an ats_provider: {bad}"


def test_seed_script_only_loads_crawlable_companies():
    import sys

    sys.path.insert(0, str(PORTALS_FILE.parents[1] / "scripts"))
    from seed_companies import load_companies

    loaded = load_companies()
    assert loaded
    assert all(c["careers_url"] for c in loaded)
    assert all(c["ats_provider"] for c in loaded)
