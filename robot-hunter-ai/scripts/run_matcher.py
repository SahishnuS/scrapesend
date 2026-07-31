import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend"))

import structlog
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.resume import Resume
from app.models.job import Job
from app.models.application import Application
from app.services.ai_matcher import AIMatcher

log = structlog.get_logger(__name__)


async def run_matching_pipeline():
    """
    1. Fetch the active resume.
    2. Fetch all jobs that don't have an Application record for this resume.
    3. Score the jobs.
    4. Create Application records.
    """
    
    async with AsyncSessionLocal() as db:
        # 1. Fetch active resume
        result = await db.execute(select(Resume).where(Resume.is_active == True))
        resume = result.scalar_one_or_none()
        
        if not resume:
            log.warning("No active resume found! Please upload and activate a resume in the dashboard first.")
            return
            
        if not resume.extracted_text:
            log.warning("Active resume has no extracted text! The AI Matcher requires text to compare.")
            return
            
        resume_text = resume.extracted_text
        
        # 2. Fetch all jobs that lack an application for THIS resume
        # Subquery: Find all job_ids that already have an application for this resume
        existing_apps_query = select(Application.job_id).where(Application.resume_id == resume.id)
        
        # Main query: Find open jobs not in the subquery
        jobs_result = await db.execute(
            select(Job)
            .where(Job.status == "open")
            .where(Job.id.notin_(existing_apps_query))
        )
        jobs_to_score = jobs_result.scalars().all()
        
        if not jobs_to_score:
            log.info("No new jobs to score for the active resume.")
            return
            
        log.info(f"Found {len(jobs_to_score)} new jobs to score. Booting AI Matcher...")
        matcher = AIMatcher()
        
        scored_count = 0
        
        for job in jobs_to_score:
            job_text = f"{job.title} {job.description or ''}"
            
            # 3. Calculate Scores
            match_score = matcher.calculate_match_score(resume_text, job_text)
            ats_score, ats_keywords_matched = matcher.calculate_ats_score(resume_text, job_text)
            
            from app.core.config import settings
            
            # 4. Create Application record
            status = "matched" if match_score >= settings.MATCH_THRESHOLD else "rejected"
            
            app = Application(
                job_id=job.id,
                resume_id=resume.id,
                status=status,
                match_score=match_score,
                ats_score=ats_score,
                ats_keywords_matched=ats_keywords_matched
            )
            db.add(app)
            scored_count += 1
            
            log.info(
                f"Scored Job: {job.title[:30]}...", 
                match=f"{match_score:.2f}", 
                ats=f"{ats_score:.2f}"
            )
            
        await db.commit()
        log.info(f"Successfully scored and created {scored_count} new application records.")


if __name__ == "__main__":
    asyncio.run(run_matching_pipeline())
