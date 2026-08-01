"""
Tests for the intern-discovery pipeline: relevance filtering, the registry ->
database sync plan, and the new-postings digest.

All offline - no browser, no database, no network.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "playwright"))
sys.path.insert(0, str(ROOT / "scripts"))

from ats.base import JobListing  # noqa: E402
from ats.filters import (  # noqa: E402
    filter_listings,
    is_editorial,
    is_relevant_internship,
    looks_like_early_career,
)
from sync_companies import plan_sync  # noqa: E402


def listing(title, url="https://example.com/jobs/1", location=None, description=None):
    return JobListing(title=title, job_url=url, location=location, description=description)


# ── Relevance filtering ───────────────────────────────────────────────────────

def test_keeps_internship_that_names_its_domain_in_the_title():
    assert is_relevant_internship(listing("Robotics Software Intern"))


def test_rejects_senior_role_even_in_target_domain():
    assert not is_relevant_internship(listing("Senior Robotics Engineer"))


def test_rejects_internship_outside_target_domains():
    assert not is_relevant_internship(listing("Marketing Intern"))


def test_bare_intern_card_is_not_relevant_until_enriched():
    """A card reading only 'Intern' has no domain, so it must not pass alone."""
    bare = listing("Intern", url="https://example.com/careers/intern-2026")
    assert not is_relevant_internship(bare)
    # ...but it is exactly the kind of listing worth fetching the detail page for.
    assert looks_like_early_career(bare)


def test_enriched_description_turns_a_bare_card_into_a_match():
    bare = listing("Intern", url="https://example.com/careers/intern-2026")
    bare.description = (
        "We are looking for an intern to join our perception team. You will "
        "work on ROS2, SLAM and computer vision pipelines for our mobile robots."
    )
    assert is_relevant_internship(bare)


def test_domain_keyword_deep_in_description_is_still_found():
    """The description slice must be wide enough to reach the requirements."""
    bare = listing("Graduate Trainee", url="https://example.com/jobs/gt")
    bare.description = ("About us. " * 120) + "Requirements: strong embedded C and RTOS experience."
    assert is_relevant_internship(bare)


def test_listings_beyond_the_description_window_are_not_matched():
    bare = listing("Graduate Trainee", url="https://example.com/jobs/gt")
    bare.description = ("About us. " * 400) + "Requirements: embedded firmware."
    assert not is_relevant_internship(bare)


# ── Editorial rejection ───────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "title",
    [
        "How to build a career in Embedded Systems as a Fresher?",
        "Top 10 tips for robotics interns",
        "What does an AI intern actually do?",
        "Case study: our embedded internship programme",
        # Plural forms: both of these were observed leaking into real results.
        "Internship Student Testimonials and Reviews",
        "Success stories from our embedded interns",
    ],
)
def test_blog_posts_are_not_jobs(title):
    assert is_editorial(listing(title))
    assert not is_relevant_internship(listing(title))


def test_blog_url_is_rejected_even_with_a_job_like_title():
    blog = listing("Robotics Intern", url="https://example.com/blog/robotics-intern-diaries")
    assert is_editorial(blog)
    assert not is_relevant_internship(blog)


def test_genuine_posting_is_not_mistaken_for_editorial():
    real = listing("Robotics Intern", url="https://example.com/careers/robotics-intern")
    assert not is_editorial(real)
    assert is_relevant_internship(real)


def test_filter_listings_keeps_only_relevant_entries():
    listings = [
        listing("Robotics Software Intern"),
        listing("Senior Robotics Engineer"),
        listing("How to become a robotics intern?"),
        listing("Embedded Systems Intern"),
    ]
    assert len(filter_listings(listings)) == 2


# ── Registry -> database sync ─────────────────────────────────────────────────

def _registry(*entries):
    return [
        {"name": n, "careers_url": u, "ats_provider": a}
        for n, u, a in entries
    ]


def test_sync_inserts_companies_missing_from_the_database():
    plan = plan_sync(_registry(("Acme", "https://acme.com/careers", "other")), existing={})
    assert [i["name"] for i in plan["insert"]] == ["Acme"]
    assert plan["update"] == [] and plan["deactivate"] == []


def test_sync_skips_registry_entries_without_a_portal():
    plan = plan_sync(_registry(("Ghost", None, None)), existing={})
    assert plan["insert"] == []


def test_sync_updates_a_changed_portal_url():
    existing = {"Acme": {"careers_url": "https://old.example/careers",
                         "ats_provider": "other", "is_active": True}}
    plan = plan_sync(_registry(("Acme", "https://acme.com/careers", "other")), existing)
    assert plan["update"] == [
        {"name": "Acme", "changes": {"careers_url": "https://acme.com/careers"}}
    ]


def test_sync_reactivates_a_company_whose_portal_came_back():
    existing = {"Acme": {"careers_url": "https://acme.com/careers",
                         "ats_provider": "other", "is_active": False}}
    plan = plan_sync(_registry(("Acme", "https://acme.com/careers", "other")), existing)
    assert plan["update"] == [{"name": "Acme", "changes": {"is_active": True}}]


def test_sync_deactivates_a_company_whose_portal_died():
    existing = {"Dead": {"careers_url": "https://dead.example/careers",
                         "ats_provider": "other", "is_active": True}}
    plan = plan_sync(_registry(("Dead", None, None)), existing)
    assert plan["deactivate"] == ["Dead"]


def test_sync_is_idempotent_when_nothing_changed():
    existing = {"Acme": {"careers_url": "https://acme.com/careers",
                         "ats_provider": "other", "is_active": True}}
    plan = plan_sync(_registry(("Acme", "https://acme.com/careers", "other")), existing)
    assert plan == {"insert": [], "update": [], "deactivate": []}


def test_sync_does_not_redeactivate_an_already_inactive_company():
    existing = {"Dead": {"careers_url": None, "ats_provider": None, "is_active": False}}
    plan = plan_sync(_registry(("Dead", None, None)), existing)
    assert plan["deactivate"] == []


# ── Per-posting alerts, batched per run ───────────────────────────────────────

class _Stub:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def job(title, company="Acme", location=None, score=None, url="https://x.test/j"):
    apps = [_Stub(match_score=score)] if score is not None else []
    return _Stub(
        title=title,
        job_url=url,
        location=location,
        company=_Stub(name=company),
        applications=apps,
    )


def test_one_email_carries_the_whole_batch_of_openings():
    """The core promise: 10 openings arrive as ONE email, not ten emails."""
    from run_notifications import render_digest

    jobs = [job(f"Intern {i}", url=f"https://x.test/j{i}") for i in range(10)]
    subject, body = render_digest(jobs)

    assert subject == "InternHunt: 10 new internship openings"
    for i in range(10):
        assert f"https://x.test/j{i}" in body


def test_openings_are_numbered_in_the_email():
    from run_notifications import render_digest

    _, body = render_digest([job("A"), job("B"), job("C")])
    assert "1. A —" in body and "2. B —" in body and "3. C —" in body


def test_subject_is_singular_for_a_single_opening():
    from run_notifications import render_digest

    subject, _ = render_digest([job("Robotics Intern")])
    assert subject == "InternHunt: 1 new internship opening"


def test_email_lists_role_company_and_apply_link():
    from run_notifications import render_digest

    _, body = render_digest([job("Robotics Intern", company="CynLr", url="https://cynlr.test/j1")])
    assert "Robotics Intern — CynLr" in body
    assert "Apply: https://cynlr.test/j1" in body


def test_email_includes_match_score_only_when_scored():
    from run_notifications import render_digest

    _, scored = render_digest([job("A", score=0.72)])
    _, unscored = render_digest([job("B")])
    assert "Resume match: 72%" in scored
    assert "Resume match" not in unscored


def test_email_tells_you_how_many_openings_are_still_queued():
    from run_notifications import render_digest

    _, body = render_digest([job("A")], remaining=37)
    assert "37 more opening(s) are queued" in body


def test_email_omits_the_queued_line_when_the_backlog_is_drained():
    from run_notifications import render_digest

    _, body = render_digest([job("A")], remaining=0)
    assert "queued" not in body


def test_batch_size_is_ten_openings_per_email():
    """A 200-job backlog must become 10 openings in one email, not 200 emails."""
    from run_notifications import MAX_JOBS_PER_EMAIL

    assert MAX_JOBS_PER_EMAIL == 10


def test_telegram_mirrors_the_same_batch():
    from run_notifications import render_digest_telegram

    jobs = [job("Robotics Intern", company="CynLr"), job("Embedded Intern")]
    text = render_digest_telegram(jobs, remaining=5)
    assert text.count("•") == 2
    assert "CynLr" in text
    assert "5 more queued" in text


def test_sync_plan_against_the_real_registry_is_all_inserts_on_a_fresh_db():
    """Guards the JSON -> DB contract against a schema drift in the registry."""
    from sync_companies import load_registry

    registry = load_registry()
    plan = plan_sync(registry, existing={})
    crawlable = [c for c in registry if c["careers_url"]]
    assert len(plan["insert"]) == len(crawlable)
    assert all(i["careers_url"] and i["ats_provider"] for i in plan["insert"])
