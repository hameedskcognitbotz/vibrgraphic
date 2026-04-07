import os
import logging
from google.cloud import storage
from app.core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.bucket_name = settings.GS_BUCKET_NAME
        if settings.GCP_SERVICE_ACCOUNT_JSON:
            # Check if it's a file path or a string
            if os.path.exists(settings.GCP_SERVICE_ACCOUNT_JSON):
                self.client = storage.Client.from_service_account_json(settings.GCP_SERVICE_ACCOUNT_JSON)
            else:
                # Assume it's a JSON string
                import json
                service_account_info = json.loads(settings.GCP_SERVICE_ACCOUNT_JSON)
                self.client = storage.Client.from_service_account_info(service_account_info)
        else:
            # Try default credentials
            self.client = storage.Client(project=settings.GCP_PROJECT_ID)

    async def upload_file(self, content: bytes, destination_blob_name: str, content_type: str = "image/png") -> str:
        """Uploads a file to the bucket and returns the public URL."""
        if not self.bucket_name:
            logger.warning("GS_BUCKET_NAME not configured, skipping GCS upload.")
            return ""
            
        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(destination_blob_name)
            
            # Synchronous GCS upload (can be wrapped in run_in_executor if needed, 
            # but usually okay in worker context)
            blob.upload_from_string(content, content_type=content_type)
            
            # Make the blob public if needed, or use a signed URL
            # For this MVP, we'll assume public read is allowed or use public URL
            return f"https://storage.googleapis.com/{self.bucket_name}/{destination_blob_name}"
        except Exception as e:
            logger.error(f"Failed to upload to GCS: {e}")
            raise e

storage_service = StorageService()
