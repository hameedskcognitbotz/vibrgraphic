import asyncio
import sys
import logging

logging.basicConfig(level=logging.INFO)

from app.services.ai_service import generate_structured_content

async def main():
    try:
        topic = "The Future of Web Development"
        print(f"Testing generation for topic: {topic}")
        result = await generate_structured_content(topic)
        print("Successfully generated valid output!")
        print(f"Title: {result.get('title')}")
        print(f"Sections Count: {len(result.get('sections', []))}")
        print(f"First Section Image Prompt: {result['sections'][0].get('image_prompt')}")
    except Exception as e:
        print(f"Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
