from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Any
import json
import os
import uuid
import zipfile
from pydantic import BaseModel

from app.schemas.job import JobCreate, JobResponse, JobStatusResponse
from app.core.database import get_db
from app.models.job import Job
from app.models.user import User
from app.api.deps import get_current_user
from app.services.rendering_engine import render_image, render_carousel

router = APIRouter()

from app.services.infographic_service import create_and_enqueue_job


def _deserialize_result_url(result_url: Optional[str]) -> Optional[Any]:
    if not result_url:
        return None

    try:
        parsed = json.loads(result_url)
        if isinstance(parsed, list):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass

    return result_url


def _job_filename_base(job: Job) -> str:
    safe_topic = "".join(ch.lower() if ch.isalnum() else "-" for ch in (job.topic or "vibegraphic"))
    safe_topic = "-".join(part for part in safe_topic.split("-") if part) or "vibegraphic"
    return safe_topic[:80]


class RenderRequest(BaseModel):
    data: dict
    is_carousel: bool = False
    export_preset: Optional[str] = None
    generation_mode: Optional[str] = "creative"


@router.post("/generate", status_code=202, response_model=JobResponse)
async def generate_infographic(
    job_in: JobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a new infographic generation topic. Returns a JOB object immediately.
    """
    if current_user.usage_count >= current_user.limit_month:
        raise HTTPException(
            status_code=403, 
            detail=f"Usage limit exceeded. Current usage: {current_user.usage_count}/{current_user.limit_month}"
        )

    try:
        # Create background JOB
        job = await create_and_enqueue_job(
            db, 
            topic=job_in.topic, 
            user_id=current_user.id,
            audience=job_in.audience or "general",
            format=job_in.format or "infographic",
            tone=job_in.tone or "Educational",
            metadata_json={
                "template_key": job_in.template_key,
                "export_preset": job_in.export_preset,
                "source_job_id": job_in.source_job_id,
                "brand_kit": job_in.brand_kit.model_dump(exclude_none=True) if job_in.brand_kit else None,
                "generation_mode": job_in.generation_mode or "creative",
            },
        )
        
        # Increment usage
        current_user.usage_count += 1
        await db.commit()
        
        return job

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.get("/download/{job_id}")
async def get_job_download(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "completed" or not job.result_url:
        raise HTTPException(status_code=409, detail="Job is not ready for download")

    return {"url": _deserialize_result_url(job.result_url)}


@router.get("/export/{job_id}")
async def get_job_export(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "completed" or not job.result_url:
        raise HTTPException(status_code=409, detail="Job is not ready for export")

    urls = _deserialize_result_url(job.result_url)
    metadata = job.metadata_json or {}
    export_preset = metadata.get("export_preset") or "instagram_carousel"

    if isinstance(urls, list) and len(urls) > 1:
        media_root = os.path.join(os.getcwd(), "media")
        exports_dir = os.path.join(media_root, "exports")
        os.makedirs(exports_dir, exist_ok=True)

        archive_name = f"{_job_filename_base(job)}-{export_preset}.zip"
        archive_path = os.path.join(exports_dir, archive_name)

        written_files = 0
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            for index, url in enumerate(urls, start=1):
                if not isinstance(url, str) or not url.startswith("/media/"):
                    continue
                file_path = os.path.join(os.getcwd(), url.lstrip("/"))
                if os.path.exists(file_path):
                    written_files += 1
                    zip_file.write(
                        file_path,
                        arcname=f"{_job_filename_base(job)}-{export_preset}-slide-{index}.png",
                    )

        if written_files > 0:
            return {"url": f"/media/exports/{archive_name}", "filename": archive_name}

        # Remote-only URLs (for example cloud storage) cannot be zipped locally.
        return {
            "url": urls[0],
            "filename": f"{_job_filename_base(job)}-{export_preset}-slide-1.png",
        }

    if isinstance(urls, list):
        urls = urls[0] if urls else None

    return {
        "url": urls,
        "filename": f"{_job_filename_base(job)}-{export_preset}.png",
    }

@router.post("/render", status_code=200)
async def render_content(
    request: RenderRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Renders structured data into images.
    """
    media_path = "media"
    os.makedirs(media_path, exist_ok=True)
    
    unique_id = str(uuid.uuid4())
    
    if request.is_carousel:
        images = render_carousel(
            request.data,
            export_preset=request.export_preset,
            generation_mode=request.generation_mode,
        )
        urls = []
        for i, img_bytes in enumerate(images):
            filename = f"carousel_{unique_id}_{i}.png"
            filepath = os.path.join(media_path, filename)
            with open(filepath, "wb") as f:
                f.write(img_bytes)
            urls.append(f"/media/{filename}")
        return {"urls": urls}
    else:
        img_bytes = render_image(
            request.data,
            export_preset=request.export_preset,
            generation_mode=request.generation_mode,
        )
        filename = f"infographic_{unique_id}.png"
        filepath = os.path.join(media_path, filename)
        with open(filepath, "wb") as f:
            f.write(img_bytes)
        return {"url": f"/media/{filename}"}

@router.get("/gallery")
async def get_user_gallery(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all jobs generated by the user.
    """
    result = await db.execute(
        select(Job).where(Job.user_id == current_user.id).order_by(Job.created_at.desc())
    )
    jobs = result.scalars().all()

    return [
        {
            "id": job.id,
            "topic": job.topic,
            "status": job.status,
            "tone": job.tone,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "result_url": _deserialize_result_url(job.result_url),
            "error_message": job.error_message,
            "metadata_json": job.metadata_json,
        }
        for job in jobs
    ]


@router.post("/refine")
async def refine_content(
    refine_data: dict, # contains current data and refinement instruction
    current_user: User = Depends(get_current_user)
):
    """
    Refines existing content with a specific instruction (e.g. \"make it more punchy\").
    """
    data = refine_data.get("data")
    instruction = refine_data.get("instruction", "make it more engaging")
    is_carousel = refine_data.get("is_carousel", False)
    
    from app.services.ai_service import refine_structured_content
    result = await refine_structured_content(data, instruction, is_carousel)
    return result
