import asyncio
import json
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app.services.ai_service import generate_structured_content
from app.core.config import settings

async def main():
    topic = "Artificial Intelligence in Healthcare"
    print(f"--- Testing infographic data generation for: {topic} ---")
    
    try:
        result = await generate_structured_content(topic)
        print("\n[SUCCESS] Generated JSON structure:")
        print(json.dumps(result, indent=2))
        
        # Basic validation checks
        assert "title" in result
        assert "layout" in result
        assert "sections" in result
        assert len(result["sections"]) >= 6
        assert "charts" in result
        
        print("\n[PASSED] All basic structure checks.")
        
    except Exception as e:
        print(f"\n[ERROR] Generation failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
