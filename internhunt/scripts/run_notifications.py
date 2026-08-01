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

# How many job alerts leave the mailbox per pipeline run. The pipeline fires
# every 2 hours, so the rest of the backlog goes out on the following runs
# rather than arriving as one flood (and staying well inside Gmail's limits).
MAX_EMAILS_PER_RUN = 10


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


async def fetch_unnotified_jobs(db, limit: int = MAX_EMAILS_PER_RUN) -> list:
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


def render_job_email(job, remaining: int = 0) -> tuple[str, str]:
    """Build the (subject, body) for a single new posting."""
    company = job.company.name if job.company else "Unknown company"
    subject = f"InternHunt: {job.title} — {company}"

    lines = [
        "InternHunt found a new internship posting.",
        "",
        f"Role:     {job.title}",
        f"Company:  {company}",
    ]
    if job.location:
        lines.append(f"Location: {job.location}")

    score = _best_match_score(job)
    if score is not None:
        lines.append(f"Resume match: {int(score * 100)}%")

    lines += ["", f"Apply here: {job.job_url}", ""]

    if remaining > 0:
        lines.append(
            f"({remaining} more new posting(s) queued — they arrive on the next runs.)"
        )

    return subject, "\n".join(lines)


def render_job_telegram(job) -> str:
    company = job.company.name if job.company else "Unknown company"
    parts = [f"InternHunt: {job.title}", f"Company: {company}"]
    if job.location:
        parts.append(f"Location: {job.location}")
    score = _best_match_score(job)
    if score is not None:
        parts.append(f"Resume match: {int(score * 100)}%")
    parts.append(job.job_url)
    return "\n".join(parts)


async def run_notification_pipeline() -> int:
    """
    Email up to MAX_EMAILS_PER_RUN new postings, one message per posting, then
    record each one so it is never sent again. The remainder stays queued for
    the next scheduled run.

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
            log.info("No new postings to alert on.")
            return 0

        jobs = await fetch_unnotified_jobs(db)
        log.info("Sending alerts", backlog=backlog, sending=len(jobs))

        notifier = NotificationService()
        sent = 0

        for index, job in enumerate(jobs):
            remaining = backlog - index - 1
            subject, body = render_job_email(job, remaining=remaining)

            if not await notifier.send_email(subject, body):
                # Leave this job unrecorded so the next run retries it, and stop
                # early rather than hammering a mail server that is refusing us.
                log.error("Email failed; leaving job queued", job_id=str(job.id))
                break

            now = datetime.now(tz=UTC)
            db.add(
                Notification(
                    job_id=job.id,
                    platform="email",
                    message=f"Alert sent for {job.title}",
                    is_sent=True,
                    sent_at=now,
                )
            )

            if await notifier.send_telegram(render_job_telegram(job)):
                db.add(
                    Notification(
                        job_id=job.id,
                        platform="telegram",
                        message=f"Alert sent for {job.title}",
                        is_sent=True,
                        sent_at=now,
                    )
                )

            # Commit per job: an interruption must not replay alerts that the
            # user has already received.
            await db.commit()
            sent += 1

        log.info("Notification run complete", sent=sent, still_queued=backlog - sent)
        return sent


if __name__ == "__main__":
    asyncio.run(run_notification_pipeline())
