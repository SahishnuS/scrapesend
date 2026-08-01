import asyncio
import os
import sys
from datetime import UTC, datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend"))

import structlog

# The database, model and SMTP imports live inside the functions that need
# them. That keeps the message-rendering helpers below importable — and unit
# testable — without a database driver or mail library installed.

log = structlog.get_logger(__name__)

# One email per pipeline run, listing at most this many openings. The pipeline
# fires every 2 hours, so a backlog is drained 10 openings at a time across the
# following runs rather than arriving as one flood.
MAX_JOBS_PER_EMAIL = 10


def _unnotified_jobs_filter():
    """Jobs that have never had a successful email alert."""
    from sqlalchemy import select

    from app.models.job import Job
    from app.models.notification import Notification

    already_emailed = (
        select(Notification.job_id)
        .where(Notification.platform == "email")
        .where(Notification.is_sent.is_(True))
    )
    return (Job.status == "open"), Job.id.notin_(already_emailed)


async def count_unnotified_jobs(db) -> int:
    """Size of the alert backlog, used only for logging and the email footer."""
    from sqlalchemy import func, select

    from app.models.job import Job

    is_open, not_emailed = _unnotified_jobs_filter()
    return await db.scalar(select(func.count()).select_from(Job).where(is_open, not_emailed)) or 0


async def fetch_unnotified_jobs(db, limit: int = MAX_JOBS_PER_EMAIL) -> list:
    """
    The next batch of jobs to alert on, newest first.

    This is the deduplication boundary for alerting. The crawler already makes a
    job row unique per (company, url) through job_hash; this query makes sure
    each of those rows is emailed at most once, no matter how often the pipeline
    runs. Newest first so the freshest postings reach the inbox soonest.
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.models.job import Job

    is_open, not_emailed = _unnotified_jobs_filter()
    result = await db.execute(
        select(Job)
        .options(selectinload(Job.company), selectinload(Job.applications))
        .where(is_open, not_emailed)
        .order_by(Job.discovered_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


def _best_match_score(job) -> float | None:
    """Highest resume match score for this job, if it has been scored at all."""
    scores = [app.match_score for app in job.applications if app.match_score is not None]
    return max(scores) if scores else None


def _company_of(job) -> str:
    return job.company.name if job.company else "Unknown company"


def render_digest(jobs: list, remaining: int = 0) -> tuple[str, str]:
    """
    Build the (subject, body) of one email listing this run's openings.

    `remaining` is how many further openings are still queued behind this
    batch; they go out on the next scheduled run.
    """
    count = len(jobs)
    subject = f"InternHunt: {count} new internship opening{'s' if count != 1 else ''}"

    lines = [
        f"InternHunt found {count} new internship opening(s).",
        "",
    ]

    for index, job in enumerate(jobs, start=1):
        lines.append(f"{index}. {job.title} — {_company_of(job)}")
        if job.location:
            lines.append(f"   Location: {job.location}")
        score = _best_match_score(job)
        if score is not None:
            lines.append(f"   Resume match: {int(score * 100)}%")
        lines.append(f"   Apply: {job.job_url}")
        lines.append("")

    if remaining > 0:
        lines.append(
            f"{remaining} more opening(s) are queued and will arrive in the next email."
        )

    return subject, "\n".join(lines)


def render_digest_telegram(jobs: list, remaining: int = 0) -> str:
    """Same batch, condensed for Telegram."""
    lines = [f"InternHunt: {len(jobs)} new internship opening(s)", ""]
    for job in jobs:
        lines.append(f"• {job.title} — {_company_of(job)}")
        lines.append(f"  {job.job_url}")
    if remaining > 0:
        lines.append(f"\n{remaining} more queued for the next run.")
    return "\n".join(lines)


async def run_notification_pipeline() -> int:
    """
    Send ONE email listing up to MAX_JOBS_PER_EMAIL new openings, then record
    those openings so they are never included again. Anything beyond the batch
    stays queued for the next scheduled run.

    Deliberately not gated on the AI matcher: the alert is about new postings. A
    resume match score is included when the matcher has already scored the job,
    but a missing resume must not mean silence.
    """
    from app.db.session import AsyncSessionLocal
    from app.models.notification import Notification
    from app.services.notification_service import NotificationService

    async with AsyncSessionLocal() as db:
        backlog = await count_unnotified_jobs(db)
        if backlog == 0:
            log.info("No new openings to alert on.")
            return 0

        jobs = await fetch_unnotified_jobs(db)
        remaining = backlog - len(jobs)
        log.info("Sending digest", backlog=backlog, in_this_email=len(jobs), queued=remaining)

        notifier = NotificationService()
        subject, body = render_digest(jobs, remaining=remaining)

        if not await notifier.send_email(subject, body):
            # Record nothing, so this batch is retried on the next run instead
            # of being silently swallowed.
            log.error("Digest email failed to send; batch stays queued.")
            return 0

        telegram_sent = await notifier.send_telegram(
            render_digest_telegram(jobs, remaining=remaining)
        )

        now = datetime.now(tz=UTC)
        for job in jobs:
            db.add(
                Notification(
                    job_id=job.id,
                    platform="email",
                    message=f"Included in digest: {job.title}",
                    is_sent=True,
                    sent_at=now,
                )
            )
            if telegram_sent:
                db.add(
                    Notification(
                        job_id=job.id,
                        platform="telegram",
                        message=f"Included in digest: {job.title}",
                        is_sent=True,
                        sent_at=now,
                    )
                )
        await db.commit()

        log.info("Digest sent", openings=len(jobs), still_queued=remaining)
        return len(jobs)


if __name__ == "__main__":
    asyncio.run(run_notification_pipeline())
