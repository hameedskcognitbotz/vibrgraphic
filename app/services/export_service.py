import os
import uuid
import boto3
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Fallback local storage directory
LOCAL_STORAGE_DIR = os.path.join(os.getcwd(), "media", "infographics")
os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)

async def upload_to_storage(image_data: bytes, filename: str) -> str:
    """
    Uploads to S3 if configured. Otherwise, saves to a local media folder.
    """
    if not settings.AWS_ACCESS_KEY_ID or not settings.S3_BUCKET_NAME:
        logger.info("AWS/S3 Config missing. Saving locally...")
        
        filepath = os.path.join(LOCAL_STORAGE_DIR, filename)
        
        # Async write (simulated with standard open for simplicity, or we can use aiofiles if installed)
        with open(filepath, "wb") as f:
            f.write(image_data)
            
        logger.info(f"Saved locally to {filepath}")
        # Return a relative URL that a static route could serve
        return f"/media/infographics/{filename}"
    
    logger.info(f"Uploading {filename} to S3 bucket {settings.S3_BUCKET_NAME}...")
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME
        )
        
        import asyncio
        loop = asyncio.get_event_loop()
        
        await loop.run_in_executor(
            None,
            lambda: s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=filename,
                Body=image_data,
                ContentType="image/png"
            )
        )
        
        url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/{filename}"
        return url
        
    except Exception as e:
        logger.error(f"S3 Upload Error: {str(e)}")
        raise e
