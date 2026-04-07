import asyncio
from app.worker.celery_app import celery_app
from app.core.database import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.job import Job
from app.services.ai_service import generate_structured_content
import logging

logger = logging.getLogger(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sync_db_url = settings.SQLALCHEMY_DATABASE_URI.replace("postgresql+asyncpg", "postgresql").replace("sqlite+aiosqlite", "sqlite")

def process_infographic_generation(job_id: int):
    """Sync inner logic for the processing task."""
    local_engine = create_engine(sync_db_url, echo=False)
    local_session_maker = sessionmaker(local_engine, expire_on_commit=False)
    
    with local_session_maker() as session:
        job = session.get(Job, job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        try:
            # 1. Update status to processing
            job.status = "processing"
            session.commit()

            logger.info(f"Processing job {job_id}: Topic '{job.topic}'")

            # 2. Extract structured content (AI Layer)
            import asyncio
            structured_data = asyncio.run(generate_structured_content(job.topic))
            job.metadata_json = structured_data
            
            # 3. Mark Completed (Rendering is now handled on the frontend)
            job.status = "completed"
            session.commit()

            logger.info(f"Job {job_id} completed successfully with JSON structure.")

        except Exception as e:
            logger.error(f"Job {job_id} failed: {str(e)}")
            job.status = "failed"
            job.error_message = str(e)
            session.commit()

@celery_app.task(name="app.worker.tasks.process_infographic_generation")
def process_task_wrapper(job_id: int):
    process_infographic_generation(job_id)
