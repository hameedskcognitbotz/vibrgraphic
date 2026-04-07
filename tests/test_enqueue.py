import asyncio
from app.core.database import async_session_maker
from app.services.infographic_service import create_and_enqueue_job

async def main():
    async with async_session_maker() as db:
        print("Enqueuing job...")
        job = await create_and_enqueue_job(db, "Artificial General Intelligence", None)
        print(f"Job {job.id} enqueued!")

if __name__ == "__main__":
    asyncio.run(main())
