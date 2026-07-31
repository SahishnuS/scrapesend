import asyncio
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend"))

import structlog
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.application import Application
from app.models.job import Job
from app.models.company import Company
from app.models.notification import Notification
from app.services.notification_service import NotificationService

log = structlog.get_logger(__name__)


async def run_notification_pipeline():
    """
    Finds newly matched applications and sends Telegram / Email alerts.
    Saves Notification records to the database.
    """
    notifier = NotificationService()

    async with AsyncSessionLocal() as db:
        # Fetch applications with matched status
        query = (
            select(Application, Job, Company)
            .join(Job, Application.job_id == Job.id)
            .join(Company, Job.company_id == Company.id)
            .where(Application.status == "matched")
            .order_by(Application.created_at.desc())
        )

        results = (await db.execute(query)).all()

        if not results:
            log.info("No matched applications found to notify.")
            return

        log.info(f"Found {len(results)} matched applications. Checking for pending notifications...")
        new_notifications_count = 0

        for app, job, company in results:
            # Check if notification already exists for this job
            existing_notif = await db.scalar(
                select(Notification).where(Notification.job_id == job.id)
            )
            if existing_notif:
                continue

            match_pct = int((app.match_score or 0) * 100)
            ats_pct = int((app.ats_score or 0) * 100)

            # Format Telegram Message (Markdown)
            telegram_msg = (
                f"RoboHunter AI Alert\n\n"
                f"Company: {company.name}\n"
                f"Role: {job.title}\n"
                f"Location: {job.location or 'Remote'}\n"
                f"AI Match Score: {match_pct}%\n"
                f"ATS Match Score: {ats_pct}%\n\n"
                f"Link: {job.job_url}"
            )

            # Format Email Subject & Body
            email_subject = f"RoboHunter Match: {job.title} at {company.name} ({match_pct}%)"
            email_body = (
                f"RoboHunter AI discovered a matching internship.\n\n"
                f"Company: {company.name}\n"
                f"Role: {job.title}\n"
                f"Location: {job.location or 'Remote'}\n"
                f"Match Score: {match_pct}%\n"
                f"ATS Score: {ats_pct}%\n\n"
                f"Apply here: {job.job_url}\n"
            )

            log.info(f"Dispatching notification for: {job.title} at {company.name}")

            # 1. Telegram Dispatch
            tg_sent = await notifier.send_telegram(telegram_msg)
            db.add(
                Notification(
                    job_id=job.id,
                    platform="telegram",
                    message=f"Alert sent for {job.title} at {company.name} (Match: {match_pct}%)",
                    is_sent=tg_sent,
                    sent_at=datetime.now(tz=timezone.utc) if tg_sent else None,
                )
            )

            # 2. Email Dispatch
            email_sent = await notifier.send_email(email_subject, email_body)
            db.add(
                Notification(
                    job_id=job.id,
                    platform="email",
                    message=f"Email sent for {job.title} at {company.name} (Match: {match_pct}%)",
                    is_sent=email_sent,
                    sent_at=datetime.now(tz=timezone.utc) if email_sent else None,
                )
            )

            new_notifications_count += 2

            # Commit after each job so that if the script is interrupted (e.g., Telegram timeout),
            # we don't rollback the database and send duplicate emails next time.
            await db.commit()

        log.info(f"Notification pipeline complete. Recorded {new_notifications_count} notifications.")


if __name__ == "__main__":
    asyncio.run(run_notification_pipeline())
