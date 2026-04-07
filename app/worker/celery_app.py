from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.task_routes = {
    "app.worker.tasks.process_infographic_generation": "main-queue"
}

# Optional: Configuration for concurrency, prefetch, etc. can go here.
celery_app.autodiscover_tasks(["app.worker.tasks"])
