import json
import re
import random
from google import genai
from google.genai import types
from app.core.config import settings
from app.schemas.infographic import InfographicData
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Gemini client (re-used across requests)
# ---------------------------------------------------------------------------
_client: genai.Client | None = None

def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


# ---------------------------------------------------------------------------
# LLM prompt
# ---------------------------------------------------------------------------

SYSTEM_INSTRUCTION = """
You are a senior AI backend engineer and expert data visualizer.
Your goal is to extract the most fascinating, counter-intuitive, and high-impact metrics about the given topic.
"""

USER_PROMPT_TEMPLATE = """
Generate a highly detailed infographic design in JSON format.

Topic: "{topic}"

Requirements:
* Generate 6–8 sections
* Each section must include:
  * heading (topic-specific)
  * description (short)
  * 2–4 bullet points
  * icon name (e.g., "robot", "chart", "education")
  * illustration_prompt (for image/icon)
  * color (hex code)
  * layout_position (left, right, center, grid-1, grid-2, etc.)
* Choose a layout type dynamically:
  * "grid"
  * "circular"
  * "step-flow"
  * "timeline"
* Add theme:
  * background_color
  * primary_color
  * secondary_color
* Add charts:
  {{"type": "bar" or "pie", "title": "", "labels": [], "data": []}}
* Add statistics:
  Example: "75% adoption rate"
* Add center highlight element

IMPORTANT:
* Output must be unique for each topic
* No generic content
* Include real-world insights
"""


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

async def generate_structured_content(topic: str) -> dict:
    """
    Calls Gemini to generate rich, single-design infographic content for *topic*.
    Utilizes Gemini's Native Structured Outputs with Pydantic for speed and accuracy.
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("No GEMINI_API_KEY found.")

    client = _get_client()
    
    prompt = USER_PROMPT_TEMPLATE.format(topic=topic)
    
    logger.info(f"Received request to generate infographic content for topic: '{topic}'")
    
    max_retries = 2
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}: Calling Gemini API for '{topic}'")
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=InfographicData,
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.9,
                    top_p=0.9,
                )
            )

            raw_content = response.text
            logger.info(f"Raw response from Gemini for '{topic}':\n{raw_content}")
            
            # Validate and parse directly via Pydantic
            parsed_data = InfographicData.model_validate_json(raw_content)
            result = parsed_data.model_dump()

            logger.info(
                f"Gemini successfully natively generated infographic: '{result['title']}' "
                f"with {len(result['sections'])} sections for topic='{topic}'"
            )
            return result

        except ValidationError as ve:
            logger.error(f"Pydantic validation error for topic '{topic}' on attempt {attempt + 1}: {ve}")
            if attempt == max_retries - 1:
                raise ValueError(f"AI response failed schema validation after {max_retries} attempts: {ve}")
            logger.info("Retrying with corrected prompt...")
            prompt += "\n\nError in previous run (ensure strict JSON format and schema compliance):\n" + str(ve)
            
        except Exception as e:
            logger.error(f"Gemini API Error for topic '{topic}' on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise ValueError(f"Gemini API Error: {e}")
            logger.info("Retrying due to API error...")
