from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import Job
from app.worker.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

async def create_and_enqueue_job(db: AsyncSession, topic: str, user_id: int = None, audience: str = "general", format: str = "infographic", tone: str = "Educational") -> Job:
    """
    Creates a new job in the database and queues it for processing in Celery.
    """
    new_job = Job(
        topic=topic,
        user_id=user_id,
        audience=audience,
        format=format,
        tone=tone,
        status="pending"
    )
    
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    
    logger.info(f"Created Job {new_job.id} for topic '{topic}'. Dispatching to queue...")

    # Dispatch to Celery Queue
    try:
        celery_app.send_task(
            "app.worker.tasks.process_infographic_generation",
            args=[new_job.id],
            queue="main-queue"
        )
    except Exception as e:
        logger.error(f"Failed to queue job {new_job.id}: {str(e)}")
        # Optionally, mark status as failed immediately if queuing fails
        new_job.status = "failed"
        new_job.error_message = f"Failed to enqueue: {str(e)}"
        await db.commit()

    return new_job
