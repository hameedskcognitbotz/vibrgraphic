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

from app.services.rendering_engine import render_image, render_carousel
import os
import uuid
import json

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

            logger.info(f"Processing job {job_id}: Topic '{job.topic}', Format: {job.format}")

            # Fetch user branding if user_id exists
            job_metadata = job.metadata_json or {}
            brand_kit = job_metadata.get("brand_kit") or {}
            author_handle = "@VibeGraphic"
            if job.user_id:
                from app.models.user import User
                user = session.get(User, job.user_id)
                if user and user.social_handle:
                    author_handle = user.social_handle
            author_handle = brand_kit.get("social_handle") or author_handle

            # 2. Extract structured content (AI Layer)
            is_carousel = job.format == "carousel"
            generation_mode = job_metadata.get("generation_mode", "creative")
            structured_data = asyncio.run(generate_structured_content(
                job.topic, 
                audience=job.audience, 
                is_carousel=is_carousel,
                tone=job.tone or "Educational",
                template_key=job_metadata.get("template_key"),
                export_preset=job_metadata.get("export_preset"),
                brand_context=brand_kit,
                generation_mode=generation_mode,
            ))
            
            # Inject Branding
            structured_data["author_handle"] = author_handle
            if brand_kit.get("brand_name"):
                structured_data["brand_name"] = brand_kit["brand_name"]
            if brand_kit.get("cta_text"):
                structured_data["cta_text"] = brand_kit["cta_text"]
            if brand_kit.get("primary_color") or brand_kit.get("accent_color"):
                theme = structured_data.setdefault("theme", {})
                if brand_kit.get("primary_color"):
                    theme["primary_color"] = brand_kit["primary_color"]
                if brand_kit.get("accent_color"):
                    theme["secondary_color"] = brand_kit["accent_color"]
            job.metadata_json = {
                **job_metadata,
                "structured_content": structured_data,
            }
            
            # 3. Render Image(s)
            media_path = "media"
            os.makedirs(media_path, exist_ok=True)
            unique_id = str(uuid.uuid4())
            
            from app.services.storage_service import storage_service
            
            export_preset = job_metadata.get("export_preset")

            if is_carousel:
                rendered_slides = render_carousel(
                    structured_data,
                    export_preset=export_preset,
                    generation_mode=generation_mode,
                )
                urls = []
                for i, img_bytes in enumerate(rendered_slides):
                    filename = f"carousel_{unique_id}_{i}.png"
                    # Try to upload to GCS
                    try:
                        url = asyncio.run(storage_service.upload_file(img_bytes, filename))
                        if not url:
                            raise Exception("GCS storage not configured")
                    except Exception as storage_err:
                        logger.warning(f"Storage failed, using local fallback: {storage_err}")
                        filepath = os.path.join(media_path, filename)
                        with open(filepath, "wb") as f:
                            f.write(img_bytes)
                        url = f"/media/{filename}"
                    urls.append(url)
                job.result_url = json.dumps(urls) # Store as list of urls
            else:
                img_bytes = render_image(
                    structured_data,
                    export_preset=export_preset,
                    generation_mode=generation_mode,
                )
                filename = f"infographic_{unique_id}.png"
                # Try to upload to GCS
                try:
                    url = asyncio.run(storage_service.upload_file(img_bytes, filename))
                    if not url:
                        raise Exception("GCS storage not configured")
                except Exception as storage_err:
                    logger.warning(f"Storage failed, using local fallback: {storage_err}")
                    filepath = os.path.join(media_path, filename)
                    with open(filepath, "wb") as f:
                        f.write(img_bytes)
                    url = f"/media/{filename}"
                job.result_url = url
            
            # 4. Mark Completed
            job.status = "completed"
            session.commit()

            logger.info(f"Job {job_id} completed successfully.")

        except Exception as e:
            logger.error(f"Job {job_id} failed: {str(e)}")
            job.status = "failed"
            job.error_message = str(e)
            session.commit()
            raise e

@celery_app.task(bind=True, name="app.worker.tasks.process_infographic_generation", max_retries=3)
def process_task_wrapper(self, job_id: int):
    try:
        process_infographic_generation(job_id)
    except Exception as exc:
        logger.warning(f"Task {job_id} failed with error '{str(exc)}'. Retrying.")
        raise self.retry(exc=exc, countdown=5 * (2 ** self.request.retries))
